import argparse
import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from predict_tomorrow_v1 import clean_prediction_inputs, load_and_prepare_data  # noqa: E402
from prediction_limits import clip_price_series  # noqa: E402
from train_model_v1 import enforce_limits, generate_features  # noqa: E402
from train_neural_hybrid import (  # noqa: E402
    NeuralResidualDayModel,
    add_neural_engineered_features,
    add_pre_feature_flags,
    add_calibrated_variants,
    apply_blend,
    predict_arrays,
    predict_tree_ensemble,
)


DEFAULT_MEMBERS = ["tcn_reslog_guard_v1", "tcn336_reslog_guard_v1"]


def parse_target_date(value):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return pd.Timestamp(pd.to_datetime(value, format=fmt).date())
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}. Use DD.MM.YYYY or YYYY-MM-DD.")


def _checkpoint_paths(output_dir, experiment_id):
    output_dir = Path(output_dir)
    return (
        output_dir / f"neural_experiment_{experiment_id}_model.pt",
        output_dir / f"neural_experiment_{experiment_id}_scalers.joblib",
    )


def load_checkpoint(output_dir, experiment_id, device):
    model_path, scaler_path = _checkpoint_paths(output_dir, experiment_id)
    if not model_path.exists():
        raise FileNotFoundError(model_path)
    if not scaler_path.exists():
        raise FileNotFoundError(scaler_path)

    checkpoint = torch.load(model_path, map_location=device)
    scalers = joblib.load(scaler_path)
    config = checkpoint["config"]
    history_features = checkpoint["history_features"]
    future_features = checkpoint["future_features"]

    model = NeuralResidualDayModel(
        history_dim=len(history_features),
        future_dim=len(future_features),
        hidden_dim=int(config.get("hidden_dim", 96)),
        dropout=float(config.get("dropout", 0.18)),
        horizon=int(config.get("horizon", 24)),
    ).to(device)
    load_result = model.load_state_dict(checkpoint["model_state"], strict=False)
    checkpoint["load_missing_keys"] = list(load_result.missing_keys)
    checkpoint["load_unexpected_keys"] = list(load_result.unexpected_keys)
    model.eval()
    return checkpoint, scalers, model


def prepare_feature_frame(target_day, data_csv, models_dir):
    df_all = load_and_prepare_data(data_csv)
    if df_all is None:
        raise FileNotFoundError(data_csv)
    if "rdn_price" not in df_all.columns:
        raise ValueError("Input data does not contain rdn_price.")

    future_index = pd.date_range(target_day, periods=24, freq="h")
    df_hist = df_all[df_all.index < target_day].dropna(subset=["rdn_price"]).copy()
    if df_hist.empty:
        raise ValueError(f"No factual history before {target_day.date()}.")

    df_future = df_all[df_all.index.normalize() == target_day].copy().reindex(future_index)
    if len(df_future) != 24:
        raise ValueError(f"Expected 24 future rows for {target_day.date()}, found {len(df_future)}.")
    if "price_cap" not in df_future.columns or df_future["price_cap"].isna().any():
        raise ValueError(f"Future rows for {target_day.date()} must contain price_cap.")

    actual_target = pd.to_numeric(df_future.get("rdn_price"), errors="coerce")
    df_full = pd.concat([df_hist, df_future], sort=False)
    df_full = df_full[~df_full.index.duplicated(keep="last")].sort_index()
    df_full = add_pre_feature_flags(df_full)
    df_full = clean_prediction_inputs(df_full)
    df_full = enforce_limits(df_full)
    df_full.loc[future_index, "rdn_price"] = np.nan
    df_full = generate_features(df_full)
    df_full = add_neural_engineered_features(df_full)

    df_full, tree_base = predict_tree_ensemble(df_full, models_dir)
    df_full["tree_base_pred"] = tree_base
    df_full["tree_base_ratio"] = (
        df_full["tree_base_pred"] / df_full["price_cap"].replace(0, np.nan)
    ).clip(0.0, 1.2)
    return df_full, future_index, actual_target


def _ensure_features(frame, features, fill_missing):
    missing = [col for col in features if col not in frame.columns]
    if missing and not fill_missing:
        raise ValueError(f"Missing model features: {missing}")
    if missing:
        frame = frame.copy()
        for col in missing:
            frame[col] = 0.0
    return frame, missing


def build_future_arrays(frame, future_index, actual_target, checkpoint, fill_missing_features=False):
    config = checkpoint["config"]
    history_len = int(config.get("history_len", 168))
    horizon = int(config.get("horizon", 24))
    if horizon != 24:
        raise ValueError(f"Only 24-hour horizon is supported, got {horizon}.")

    history_features = checkpoint["history_features"]
    future_features = checkpoint["future_features"]
    frame, missing_history = _ensure_features(frame, history_features, fill_missing_features)
    frame, missing_future = _ensure_features(frame, future_features, fill_missing_features)

    day = future_index[0].normalize()
    hist_idx = pd.date_range(day - pd.Timedelta(hours=history_len), periods=history_len, freq="h")
    if not hist_idx.isin(frame.index).all():
        missing_hours = hist_idx[~hist_idx.isin(frame.index)]
        raise ValueError(f"Missing history hours for neural inference: {missing_hours[:5].tolist()}")
    if not future_index.isin(frame.index).all():
        missing_hours = future_index[~future_index.isin(frame.index)]
        raise ValueError(f"Missing future hours for neural inference: {missing_hours[:5].tolist()}")

    x_history = frame.loc[hist_idx, history_features].to_numpy(dtype="float32")[None, :, :]
    x_future = frame.loc[future_index, future_features].to_numpy(dtype="float32")[None, :, :]
    base_pred = frame.loc[future_index, "tree_base_pred"].to_numpy(dtype="float32")[None, :]
    caps = frame.loc[future_index, "price_cap"].to_numpy(dtype="float32")[None, :]
    y_price = actual_target.reindex(future_index).to_numpy(dtype="float32")[None, :]

    return {
        "x_history": x_history,
        "x_future": x_future,
        "y_price": y_price,
        "base_pred": base_pred,
        "caps": caps,
        "weights": np.ones((1, horizon), dtype="float32"),
        "low_label": np.zeros((1, horizon), dtype="float32"),
        "daytime_low_label": np.zeros((1, horizon), dtype="float32"),
        "high_label": np.zeros((1, horizon), dtype="float32"),
        "datetimes": pd.DatetimeIndex(future_index),
        "days": pd.DatetimeIndex([day]),
        "missing_history_features": missing_history,
        "missing_future_features": missing_future,
    }


def transform_arrays(arrays, scalers):
    transformed = dict(arrays)
    n_h = transformed["x_history"].shape[-1]
    n_f = transformed["x_future"].shape[-1]
    transformed["x_history"] = scalers["history"].transform(
        transformed["x_history"].reshape(-1, n_h)
    ).reshape(transformed["x_history"].shape).astype("float32")
    transformed["x_future"] = scalers["future"].transform(
        transformed["x_future"].reshape(-1, n_f)
    ).reshape(transformed["x_future"].shape).astype("float32")
    transformed["x_history"] = np.nan_to_num(transformed["x_history"], nan=0.0, posinf=0.0, neginf=0.0)
    transformed["x_future"] = np.nan_to_num(transformed["x_future"], nan=0.0, posinf=0.0, neginf=0.0)
    return transformed


def predict_member(frame, future_index, actual_target, output_dir, experiment_id, device, fill_missing_features=False):
    checkpoint, scalers, model = load_checkpoint(output_dir, experiment_id, device)
    arrays = build_future_arrays(
        frame,
        future_index,
        actual_target,
        checkpoint,
        fill_missing_features=fill_missing_features,
    )
    transformed = transform_arrays(arrays, scalers)
    raw = predict_arrays(
        model,
        transformed,
        device=torch.device(device),
        batch_size=int(checkpoint["config"].get("batch_size", 16)),
    )
    blended = apply_blend(raw, checkpoint["blend"])
    calibrated = add_calibrated_variants(frame, blended)
    calibrated["member_experiment_id"] = experiment_id
    return calibrated, {
        "experiment_id": experiment_id,
        "model_config": checkpoint["config"],
        "load_missing_keys": checkpoint.get("load_missing_keys", []),
        "load_unexpected_keys": checkpoint.get("load_unexpected_keys", []),
        "missing_history_features": arrays["missing_history_features"],
        "missing_future_features": arrays["missing_future_features"],
    }


def build_future_ensemble(member_frames, recent_policy="tree"):
    frames = [frame.set_index("datetime").sort_index() for frame in member_frames]
    common_index = frames[0].index
    for frame in frames[1:]:
        common_index = common_index.intersection(frame.index)
    if len(common_index) != 24:
        raise ValueError(f"Expected 24 common ensemble timestamps, got {len(common_index)}.")

    frames = [frame.loc[common_index] for frame in frames]
    base = frames[0][["actual", "price_cap", "tree_base_pred", "tree_recent_calibrated_pred"]].copy()
    for col in ["neural_pred", "hybrid_pred", "hybrid_recent_calibrated_pred", "hybrid_guarded_pred"]:
        if all(col in frame.columns for frame in frames):
            base[f"ensemble_{col}"] = sum(frame[col] for frame in frames) / len(frames)

    if "ensemble_hybrid_pred" not in base.columns:
        raise ValueError("Member frames do not contain hybrid_pred.")

    base["hybrid_guarded_pred"] = base["ensemble_hybrid_pred"]
    if recent_policy == "tree":
        base["hybrid_guarded_pred"] = base["tree_recent_calibrated_pred"]
    elif recent_policy == "hybrid_recent" and "ensemble_hybrid_recent_calibrated_pred" in base.columns:
        base["hybrid_guarded_pred"] = base["ensemble_hybrid_recent_calibrated_pred"]
    else:
        raise ValueError(f"Unsupported recent policy: {recent_policy}")

    for col in [
        "tree_base_pred",
        "tree_recent_calibrated_pred",
        "ensemble_neural_pred",
        "ensemble_hybrid_pred",
        "ensemble_hybrid_recent_calibrated_pred",
        "ensemble_hybrid_guarded_pred",
        "hybrid_guarded_pred",
    ]:
        if col in base.columns:
            base[col] = clip_price_series(base[col], base["price_cap"])
    return base.reset_index().rename(columns={"index": "datetime"})


def main():
    parser = argparse.ArgumentParser(description="Run saved neural-hybrid member inference for one future date.")
    parser.add_argument("target_date")
    parser.add_argument("--data-csv", default=os.path.join(ROOT_DIR, "data", "ready_for_train.csv"))
    parser.add_argument("--models-dir", default=os.path.join(ROOT_DIR, "models_improved"))
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--members", nargs="+", default=DEFAULT_MEMBERS)
    parser.add_argument("--recent-policy", choices=["tree", "hybrid_recent"], default="tree")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--allow-missing-features", action="store_true")
    args = parser.parse_args()

    target_day = parse_target_date(args.target_date)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    frame, future_index, actual_target = prepare_feature_frame(target_day, args.data_csv, args.models_dir)
    member_frames = []
    diagnostics = {
        "target_date": str(target_day.date()),
        "members": [],
        "recent_policy": args.recent_policy,
    }
    for member in args.members:
        member_frame, member_diag = predict_member(
            frame,
            future_index,
            actual_target,
            output_dir,
            member,
            args.device,
            fill_missing_features=args.allow_missing_features,
        )
        member_frames.append(member_frame)
        diagnostics["members"].append(member_diag)

        member_path = output_dir / f"prediction_{target_day.date()}_{member}_neural_member.csv"
        member_frame.to_csv(member_path, index=False)
        member_diag["csv"] = os.fspath(member_path)

    ensemble = build_future_ensemble(member_frames, recent_policy=args.recent_policy)
    date_iso = str(target_day.date())
    ensemble_path = output_dir / f"prediction_{date_iso}_neural_hybrid_candidates.csv"
    ensemble.to_csv(ensemble_path, index=False)
    diagnostics_path = output_dir / f"prediction_{date_iso}_neural_hybrid_candidates_diagnostics.json"
    diagnostics["ensemble_csv"] = os.fspath(ensemble_path)
    with open(diagnostics_path, "w", encoding="utf-8") as f:
        json.dump(diagnostics, f, indent=2, ensure_ascii=False)

    print(f"ensemble_csv={ensemble_path}")
    print(f"diagnostics_json={diagnostics_path}")
    print(ensemble[["datetime", "tree_base_pred", "tree_recent_calibrated_pred", "ensemble_neural_pred", "ensemble_hybrid_pred"]])


if __name__ == "__main__":
    main()
