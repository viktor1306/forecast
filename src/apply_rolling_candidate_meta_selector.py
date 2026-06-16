import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts
from prediction_limits import clip_price_forecast


DEFAULT_PRICE_BINS = "-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000"
DEFAULT_RATIO_BINS = "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01"


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"], low_memory=False)


def parse_column_list(text):
    values = [part.strip() for part in str(text).split(",") if part.strip()]
    if not values:
        raise ValueError("At least one --candidate-cols value is required.")
    return list(dict.fromkeys(values))


def parse_number_list(text):
    values = [float(part.strip()) for part in str(text).split(",") if part.strip()]
    if len(values) < 2:
        raise ValueError(f"Expected at least two numeric bin edges, got: {text}")
    if any(b <= a for a, b in zip(values, values[1:])):
        raise ValueError(f"Bin edges must be strictly increasing: {text}")
    return values


def parse_hours(text):
    text = str(text).strip().lower()
    aliases = {
        "all": set(range(24)),
        "peakerr": {0, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 21, 22},
        "day": set(range(10, 18)),
        "lowday": set(range(10, 17)),
        "midday": {11, 12, 13, 14, 15, 16},
        "morning": set(range(7, 11)),
        "evening": set(range(19, 24)),
        "night": {0, 1, 2, 3, 4, 5, 6, 23},
    }
    if text in aliases:
        return aliases[text]

    selected = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(value) for value in part.split("-", 1)]
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    unknown = sorted(hour for hour in selected if hour < 0 or hour > 23)
    if unknown:
        raise ValueError(f"Hours must be 0-23, got: {unknown}")
    return selected


def _binned(values, bins):
    return np.asarray(pd.cut(
        values,
        bins=parse_number_list(bins),
        labels=False,
        include_lowest=True,
    ).astype("float64"), dtype="float64")


def distance_mask(source, candidate, cap, op, threshold):
    diff = np.abs(source - candidate)
    rel = diff / np.clip(cap, 1.0, None)
    if op == "none":
        return np.ones(len(source), dtype=bool)
    if op == "le_abs":
        return diff <= threshold
    if op == "ge_abs":
        return diff >= threshold
    if op == "le_rel":
        return rel <= threshold
    if op == "ge_rel":
        return rel >= threshold
    raise ValueError(f"Unsupported distance op: {op}")


def build_base_features(frame, source_col, price_bins, ratio_bins):
    dt = pd.to_datetime(frame["datetime"])
    source = pd.to_numeric(frame[source_col], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    cap_safe = np.clip(cap, 1.0, None)
    source_ratio = np.clip(source / cap_safe, 0.0, 2.0)

    feature_parts = [
        dt.dt.hour.to_numpy(dtype="float64"),
        np.sin(2.0 * np.pi * dt.dt.hour.to_numpy(dtype="float64") / 24.0),
        np.cos(2.0 * np.pi * dt.dt.hour.to_numpy(dtype="float64") / 24.0),
        dt.dt.dayofweek.to_numpy(dtype="float64"),
        dt.dt.dayofweek.isin([5, 6]).astype("float64").to_numpy(),
        dt.dt.month.to_numpy(dtype="float64"),
        dt.dt.month.isin([6, 7, 8]).astype("float64").to_numpy(),
        cap,
        source,
        source_ratio,
        _binned(source, price_bins),
        _binned(source_ratio, ratio_bins),
        (source < 1000.0).astype("float64"),
    ]

    optional_cols = [
        "f_price_lag_24",
        "f_price_lag_48",
        "f_price_lag_168",
        "f_rolling_mean_hour_3d",
        "f_rolling_mean_hour_7d",
        "f_rolling_mean_hour_14d",
        "f_rolling_mean_24",
        "f_rolling_min_24",
        "f_rolling_std_24",
        "f_renewable_pressure_index",
        "f_cloudcover",
        "f_solarradiation",
        "f_windspeed",
    ]
    for col in optional_cols:
        if col in frame.columns:
            feature_parts.append(pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64"))

    base = np.column_stack(feature_parts)
    return np.nan_to_num(base, nan=0.0, posinf=0.0, neginf=0.0)


def expanded_features(
    base_features,
    row_indices,
    candidate_indices,
    source,
    cap,
    candidate_matrix,
    candidate_onehot,
    price_bins,
    ratio_bins,
):
    row_indices = np.asarray(row_indices, dtype="int64")
    candidate_indices = np.asarray(candidate_indices, dtype="int64")
    base = base_features[row_indices]
    source_values = source[row_indices]
    cap_values = cap[row_indices]
    candidate_values = candidate_matrix[row_indices, candidate_indices]
    cap_safe = np.clip(cap_values, 1.0, None)
    diff = candidate_values - source_values
    absdiff = np.abs(diff)
    candidate_ratio = np.clip(candidate_values / cap_safe, 0.0, 2.0)
    rel_absdiff = absdiff / cap_safe

    candidate_features = np.column_stack([
        candidate_values,
        candidate_ratio,
        diff,
        absdiff,
        rel_absdiff,
        _binned(candidate_values, price_bins),
        _binned(candidate_ratio, ratio_bins),
    ])
    onehot = candidate_onehot[candidate_indices]
    return np.nan_to_num(np.column_stack([base, candidate_features, onehot]), nan=0.0, posinf=0.0, neginf=0.0)


def row_sample_weights(frame, row_indices, source, actual, day, half_life_days, low_weight, daytime_low_weight):
    row_indices = np.asarray(row_indices, dtype="int64")
    dt = pd.to_datetime(frame.loc[row_indices, "datetime"])
    age_days = (pd.Timestamp(day) - dt).dt.total_seconds().to_numpy(dtype="float64") / 86400.0
    if half_life_days > 0:
        weights = np.power(0.5, age_days / half_life_days)
    else:
        weights = np.ones(len(row_indices), dtype="float64")
    source_error = np.abs(source[row_indices] - actual[row_indices])
    scale = np.nanmedian(source_error[np.isfinite(source_error)])
    if not np.isfinite(scale) or scale <= 0.0:
        scale = 300.0
    weights *= np.clip(0.5 + source_error / scale, 0.5, 6.0)
    hours = dt.dt.hour.to_numpy()
    weights[actual[row_indices] < 1000.0] *= low_weight
    weights[(actual[row_indices] < 1000.0) & (hours >= 10) & (hours <= 16)] *= daytime_low_weight
    return np.clip(weights, 0.05, 20.0)


def apply_rolling_candidate_meta_selector(predictions, args):
    candidate_cols = parse_column_list(args.candidate_cols)
    missing = [col for col in [args.source_col, *candidate_cols] if col not in predictions.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    source = pd.to_numeric(frame[args.source_col], errors="coerce").to_numpy(dtype="float64")
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    source = clip_price_forecast(source, cap)
    candidate_matrix = np.column_stack([
        clip_price_forecast(pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64"), cap)
        for col in candidate_cols
    ])
    candidate_onehot = np.eye(len(candidate_cols), dtype="float64")
    base_features = build_base_features(frame, args.source_col, args.price_bins, args.ratio_bins)

    adjusted = source.copy()
    applied = np.zeros(len(frame), dtype="int64")
    chosen_idx = np.full(len(frame), -1, dtype="int64")
    chosen_signal = np.full(len(frame), np.nan, dtype="float64")
    hours = parse_hours(args.hours)
    day_key = frame["datetime"].dt.normalize()
    unique_days = pd.DatetimeIndex(day_key.unique()).sort_values()
    all_candidate_indices = np.arange(len(candidate_cols), dtype="int64")

    for day in unique_days:
        target_mask = (day_key == day).to_numpy()
        train_start = pd.Timestamp(day) - pd.Timedelta(days=args.lookback_days)
        train_mask = ((frame["datetime"] < day) & (frame["datetime"] >= train_start)).to_numpy()
        train_mask &= np.isfinite(actual) & np.isfinite(source)
        train_rows = np.flatnonzero(train_mask)
        target_rows = np.flatnonzero(target_mask)
        if len(target_rows) == 0 or len(train_rows) < args.min_train_days * 24:
            continue

        train_row_rep = np.repeat(train_rows, len(candidate_cols))
        train_candidate_rep = np.tile(all_candidate_indices, len(train_rows))
        source_error = np.abs(source[train_rows] - actual[train_rows])
        candidate_error = np.abs(candidate_matrix[train_rows] - actual[train_rows, None])
        y_train = (source_error[:, None] - candidate_error).reshape(-1)
        finite_y = np.isfinite(y_train)
        if finite_y.sum() < args.min_train_days * 24:
            continue

        X_train = expanded_features(
            base_features,
            train_row_rep[finite_y],
            train_candidate_rep[finite_y],
            source,
            cap,
            candidate_matrix,
            candidate_onehot,
            args.price_bins,
            args.ratio_bins,
        )
        row_weights = row_sample_weights(
            frame,
            train_rows,
            source,
            actual,
            day,
            args.half_life_days,
            args.low_weight,
            args.daytime_low_weight,
        )
        sample_weight = np.repeat(row_weights, len(candidate_cols))[finite_y]
        model = make_pipeline(StandardScaler(), Ridge(alpha=args.ridge_alpha))
        model.fit(X_train, y_train[finite_y], ridge__sample_weight=sample_weight)

        target_row_rep = np.repeat(target_rows, len(candidate_cols))
        target_candidate_rep = np.tile(all_candidate_indices, len(target_rows))
        X_target = expanded_features(
            base_features,
            target_row_rep,
            target_candidate_rep,
            source,
            cap,
            candidate_matrix,
            candidate_onehot,
            args.price_bins,
            args.ratio_bins,
        )
        pred_advantage = model.predict(X_target).reshape(len(target_rows), len(candidate_cols))
        finite_candidates = np.isfinite(candidate_matrix[target_rows])
        pred_advantage = np.where(finite_candidates, pred_advantage, -np.inf)
        best_idx = np.argmax(pred_advantage, axis=1)
        best_signal = pred_advantage[np.arange(len(target_rows)), best_idx]
        best_candidate = candidate_matrix[target_rows, best_idx]
        row_source = source[target_rows]
        row_cap = cap[target_rows]

        hour_selected = frame.loc[target_rows, "datetime"].dt.hour.isin(hours).to_numpy()
        selected = (
            hour_selected
            & np.isfinite(best_signal)
            & (best_signal >= args.advantage_threshold)
            & distance_mask(row_source, best_candidate, row_cap, args.distance_op, args.distance_threshold)
        )
        if not selected.any():
            continue

        selected_rows = target_rows[selected]
        selected_best_idx = best_idx[selected]
        selected_candidate = best_candidate[selected]
        adjusted[selected_rows] = (
            (1.0 - args.alpha) * source[selected_rows]
            + args.alpha * selected_candidate
        )
        applied[selected_rows] = 1
        chosen_idx[selected_rows] = selected_best_idx
        chosen_signal[selected_rows] = best_signal[selected]

    if args.apply_recent_days > 0:
        recent_start = frame["datetime"].max() - pd.Timedelta(days=args.apply_recent_days)
        recent_mask = (frame["datetime"] >= recent_start).to_numpy()
        adjusted = np.where(recent_mask, adjusted, source)
        applied = np.where(recent_mask, applied, 0)
        chosen_idx = np.where(recent_mask, chosen_idx, -1)
        chosen_signal = np.where(recent_mask, chosen_signal, np.nan)

    frame[args.output_col] = clip_price_forecast(adjusted, cap)
    frame[f"{args.output_col}_applied"] = applied
    frame[f"{args.output_col}_candidate_index"] = chosen_idx
    candidate_names = np.array(candidate_cols, dtype=object)
    chosen_names = np.full(len(frame), "", dtype=object)
    selected = chosen_idx >= 0
    chosen_names[selected] = candidate_names[chosen_idx[selected]]
    frame[f"{args.output_col}_candidate"] = chosen_names
    frame[f"{args.output_col}_predicted_advantage"] = chosen_signal
    return frame, candidate_cols


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows, candidate_counts):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Rolling-origin candidate meta-selector: "
            f"source `{params['source_col']}`, candidates `{params['candidate_cols']}`, "
            f"lookback `{params['lookback_days']}` days, min train `{params['min_train_days']}` days, "
            f"ridge alpha `{params['ridge_alpha']}`, predicted advantage threshold "
            f"`{params['advantage_threshold']}`, hours `{params['hours']}`, "
            f"distance `{params['distance_op']}` `{params['distance_threshold']}`, blend alpha `{params['alpha']}`.\n"
        )
        f.write(
            "- For each target day, the model trains only on earlier rows and predicts candidate advantage "
            "from forecast-time source/candidate/lag/profile features.\n"
        )
        f.write(f"- Adjusted rows: `{applied_rows}`.\n")
        f.write(f"- Selected candidates: `{candidate_counts}`.\n\n")
        f.write("| variant | 3m WMAPE | 14d WMAPE | 3m rows |\n")
        f.write("|---|---:|---:|---:|\n")
        for col, metrics in variant_metrics.items():
            f.write(
                f"| `{col}` | {metrics['last_3m']['wmape']:.4f}% | "
                f"{metrics['last_14d']['wmape']:.4f}% | {metrics['last_3m']['n']} |\n"
            )
        f.write(f"\n- Predictions: `{artifacts['predictions_csv']}`\n")
        f.write(f"- Metrics: `{artifacts['metrics_json']}`\n")
        f.write(f"- Plot: `{artifacts['plot_png']}`\n")
    return os.fspath(log_path)


def main():
    parser = argparse.ArgumentParser(description="Leakage-safe rolling-origin candidate advantage meta-selector.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--candidate-cols", required=True)
    parser.add_argument("--output-col", default="rolling_candidate_meta_pred")
    parser.add_argument("--price-bins", default=DEFAULT_PRICE_BINS)
    parser.add_argument("--ratio-bins", default=DEFAULT_RATIO_BINS)
    parser.add_argument("--lookback-days", type=int, default=45)
    parser.add_argument("--min-train-days", type=int, default=14)
    parser.add_argument("--ridge-alpha", type=float, default=1000.0)
    parser.add_argument("--half-life-days", type=float, default=21.0)
    parser.add_argument("--low-weight", type=float, default=1.2)
    parser.add_argument("--daytime-low-weight", type=float, default=1.5)
    parser.add_argument("--advantage-threshold", type=float, default=100.0)
    parser.add_argument("--hours", default="all")
    parser.add_argument("--distance-op", choices=["none", "le_abs", "ge_abs", "le_rel", "ge_rel"], default="none")
    parser.add_argument("--distance-threshold", type=float, default=0.0)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--apply-recent-days", type=int, default=0)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted, candidate_cols = apply_rolling_candidate_meta_selector(predictions, args)
    variant_cols = [
        "tree_recent_calibrated_pred",
        args.source_col,
        args.output_col,
    ]
    variant_metrics = {
        col: calculate_metrics(adjusted, pred_col=col)
        for col in variant_cols
        if col in adjusted.columns
    }
    artifacts = save_evaluation_artifacts(
        adjusted,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )

    applied_col = f"{args.output_col}_applied"
    candidate_col = f"{args.output_col}_candidate"
    applied_rows = int(adjusted[applied_col].fillna(0).astype(bool).sum())
    candidate_counts = {
        str(key): int(value)
        for key, value in adjusted.loc[adjusted[applied_col].astype(bool), candidate_col].value_counts().items()
    }
    params = vars(args).copy()
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["rolling_candidate_meta_selector_params"] = params
    payload["rolling_candidate_meta_selector_applied_rows"] = applied_rows
    payload["rolling_candidate_meta_selector_candidate_counts"] = candidate_counts
    for flag_col in sorted(col for col in adjusted.columns if col.endswith("_applied")):
        payload[f"{flag_col}_rows"] = int(adjusted[flag_col].fillna(0).astype(bool).sum())
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    append_log(
        output_dir=args.output_dir,
        experiment_id=args.experiment_id,
        input_experiment=args.input_experiment,
        params=params,
        artifacts=artifacts,
        variant_metrics=variant_metrics,
        applied_rows=applied_rows,
        candidate_counts=candidate_counts,
    )

    for col, metrics in variant_metrics.items():
        print(f"{col}: 3m={metrics['last_3m']['wmape']:.4f}% 14d={metrics['last_14d']['wmape']:.4f}%")
    print(f"adjusted_rows={applied_rows}")
    print(f"selected_candidates={candidate_counts}")


if __name__ == "__main__":
    main()
