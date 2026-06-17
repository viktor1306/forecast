import argparse
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from prediction_limits import clip_price_forecast  # noqa: E402
from rolling_origin_nonlinear_stacker import (  # noqa: E402
    apply_source_error_outlier_weights,
    build_stacker_frame,
    finite_frame,
    invert_prediction,
    make_model,
    numeric_feature_columns,
    sample_weights,
    target_values,
)


def parse_target_date(value):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return pd.Timestamp(pd.to_datetime(value, format=fmt).date())
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}. Use DD.MM.YYYY or YYYY-MM-DD.")


def load_history(path, target_day):
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    if "datetime" not in frame.columns:
        raise ValueError(f"{path} does not contain datetime.")
    return frame[frame["datetime"].dt.normalize() < target_day].copy()


def load_target_rows(path, target_day):
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    if "datetime" not in frame.columns:
        raise ValueError(f"{path} does not contain datetime.")
    frame = frame[frame["datetime"].dt.normalize() == target_day].copy()
    if len(frame) != 24:
        raise ValueError(f"Expected 24 target rows for {target_day.date()}, found {len(frame)} in {path}.")
    if "actual" not in frame.columns:
        frame["actual"] = np.nan
    frame["actual"] = np.nan
    return frame


def build_future_stacker_candidate(predictions, args, target_day):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = build_stacker_frame(predictions, args.source_col)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")

    feature_cols = numeric_feature_columns(frame, args.output_col)
    day_key = frame["datetime"].dt.normalize()
    target_mask = (day_key == target_day).to_numpy()
    train_start = target_day - pd.Timedelta(days=args.lookback_days)
    train_mask = ((frame["datetime"] < target_day) & (frame["datetime"] >= train_start)).to_numpy()
    if train_mask.sum() < args.min_train_days * 24:
        raise ValueError(
            f"Not enough train rows for {target_day.date()}: "
            f"{int(train_mask.sum())} < {args.min_train_days * 24}"
        )

    X_train = finite_frame(frame.loc[train_mask, feature_cols])
    X_target = finite_frame(frame.loc[target_mask, feature_cols])
    y_actual = frame.loc[train_mask, "actual"].to_numpy(dtype="float64")
    y_source = frame.loc[train_mask, args.source_col].to_numpy(dtype="float64")
    y_train = target_values(y_actual, y_source, args.target)
    weights = sample_weights(
        frame=frame,
        train_mask=train_mask,
        day=target_day,
        half_life_days=args.half_life_days,
        low_weight=args.low_weight,
        high_weight=args.high_weight,
        daytime_weight=args.daytime_weight,
        evening_weight=args.evening_weight,
        daytime_low_weight=args.daytime_low_weight,
    )
    weights = apply_source_error_outlier_weights(
        frame=frame,
        train_mask=train_mask,
        source_col=args.source_col,
        weights=weights,
        quantile=args.source_error_outlier_quantile,
        outlier_weight=args.source_error_outlier_weight,
    )

    model = make_model(args.model_type, args.seed, args)
    model.fit(X_train, y_train, sample_weight=weights)

    raw_pred = model.predict(X_target)
    source = clip_price_forecast(
        frame[args.source_col].to_numpy(dtype="float64"),
        frame["price_cap"].to_numpy(dtype="float64"),
    )
    day_source = source[target_mask]
    day_pred = invert_prediction(day_source, raw_pred, args.target)
    candidate = (1.0 - args.blend) * day_source + args.blend * day_pred
    candidate = clip_price_forecast(candidate, frame.loc[target_mask, "price_cap"].to_numpy(dtype="float64"))

    target_frame = frame.loc[target_mask, ["datetime"]].copy()
    target_frame[args.output_col] = candidate
    target_frame[f"{args.output_col}_applied"] = 1
    return target_frame


def main():
    parser = argparse.ArgumentParser(description="Build one nonlinear rolling-origin stacker candidate for a future date.")
    parser.add_argument("target_date")
    parser.add_argument("--target-input-csv", required=True)
    parser.add_argument("--history-csv", default=os.path.join(ROOT_DIR, "output", "neural_best_predictions.csv"))
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", required=True)
    parser.add_argument("--model-type", choices=["hgb", "rf", "et", "mlp"], default="hgb")
    parser.add_argument("--target", choices=["resid", "ratio", "logresid", "log"], default="resid")
    parser.add_argument("--lookback-days", type=int, default=45)
    parser.add_argument("--min-train-days", type=int, default=21)
    parser.add_argument("--blend", type=float, default=0.2)
    parser.add_argument("--half-life-days", type=float, default=21.0)
    parser.add_argument("--low-weight", type=float, default=1.2)
    parser.add_argument("--high-weight", type=float, default=1.2)
    parser.add_argument("--daytime-weight", type=float, default=1.1)
    parser.add_argument("--daytime-low-weight", type=float, default=1.0)
    parser.add_argument("--evening-weight", type=float, default=1.1)
    parser.add_argument("--source-error-outlier-quantile", type=float, default=0.0)
    parser.add_argument("--source-error-outlier-weight", type=float, default=1.0)
    parser.add_argument("--loss", default="squared_error")
    parser.add_argument("--learning-rate", type=float, default=0.04)
    parser.add_argument("--max-iter", type=int, default=80)
    parser.add_argument("--max-leaf-nodes", type=int, default=15)
    parser.add_argument("--min-samples-leaf", type=int, default=20)
    parser.add_argument("--l2-regularization", type=float, default=1.0)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--hidden-layers", default="64,32")
    parser.add_argument("--activation", choices=["identity", "logistic", "tanh", "relu"], default="relu")
    parser.add_argument("--mlp-alpha", type=float, default=0.001)
    parser.add_argument("--mlp-early-stopping", action="store_true")
    parser.add_argument("--mlp-validation-fraction", type=float, default=0.12)
    parser.add_argument("--mlp-n-iter-no-change", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    target_day = parse_target_date(args.target_date)
    history = load_history(args.history_csv, target_day)
    target_rows = load_target_rows(args.target_input_csv, target_day)
    combined = pd.concat([history, target_rows], ignore_index=True, sort=False)
    candidate = build_future_stacker_candidate(combined, SimpleNamespace(**vars(args)), target_day)

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    candidate.to_csv(output_csv, index=False)
    print(candidate.to_string(index=False))
    print(f"output_csv={output_csv}")


if __name__ == "__main__":
    main()
