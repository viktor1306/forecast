import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts
from prediction_limits import clip_price_forecast
from rolling_origin_stacker import build_stacker_frame
from rolling_origin_nonlinear_stacker import target_values, invert_prediction


HOURLY_PROFILE_COLUMNS = [
    "f_price_lag_24",
    "f_price_lag_48",
    "f_price_lag_168",
    "f_rolling_mean_hour_3d",
    "f_rolling_mean_hour_7d",
    "f_rolling_mean_hour_14d",
    "f_price_cap",
    "f_feelslike",
    "f_windspeed",
    "f_windgust",
    "f_cloudcover",
    "f_solarradiation",
    "f_uvindex",
    "f_renewable_pressure_index",
    "f_wind_cloud_interaction",
]

DAY_SCALAR_COLUMNS = [
    "f_month",
    "f_day_of_week_num",
    "f_is_weekend",
    "f_is_off_day",
    "f_is_summer",
]


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def parse_hours(text):
    selected = set()
    for part in str(text).split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(value) for value in part.split("-", 1)]
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    return selected


def full_day_keys(frame):
    counts = frame.groupby(frame["datetime"].dt.normalize()).size()
    return pd.DatetimeIndex(counts[counts == 24].index).sort_values()


def price_like_column(name, source_col):
    return (
        name == source_col
        or name == "f_price_cap"
        or "price_lag" in name
        or "rolling_mean_hour" in name
    )


def add_day_vector_features(frame, source_col):
    frame = frame.copy()
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").replace(0, np.nan)
    for col in [source_col, *HOURLY_PROFILE_COLUMNS]:
        if col not in frame.columns:
            continue
        values = pd.to_numeric(frame[col], errors="coerce")
        if price_like_column(col, source_col):
            frame[f"analog_{col}_ratio"] = values / cap
        else:
            frame[f"analog_{col}"] = values
    return frame


def day_feature_columns(frame, source_col):
    columns = []
    for col in [source_col, *HOURLY_PROFILE_COLUMNS]:
        ratio_col = f"analog_{col}_ratio"
        raw_col = f"analog_{col}"
        if ratio_col in frame.columns:
            columns.append(ratio_col)
        elif raw_col in frame.columns:
            columns.append(raw_col)

    scalar_cols = [col for col in DAY_SCALAR_COLUMNS if col in frame.columns]
    for suffix in [
        "day_wmape_lag_1",
        "day_wmape_roll_7",
        "day_wmape_std_7",
        "day_bias_lag_1",
        "day_bias_roll_7",
    ]:
        col = f"{source_col}_{suffix}"
        if col in frame.columns:
            scalar_cols.append(col)
    return columns, scalar_cols


def build_day_matrix(frame, source_col):
    frame = add_day_vector_features(frame, source_col)
    hourly_cols, scalar_cols = day_feature_columns(frame, source_col)
    rows = []
    day_keys = []
    for day, group in frame.groupby(frame["datetime"].dt.normalize(), sort=True):
        if len(group) != 24:
            continue
        group = group.sort_values("datetime")
        vector_parts = []
        for col in hourly_cols:
            vector_parts.append(pd.to_numeric(group[col], errors="coerce").to_numpy(dtype="float64"))
        for col in scalar_cols:
            vector_parts.append(np.array([pd.to_numeric(group[col], errors="coerce").iloc[0]], dtype="float64"))
        if not vector_parts:
            continue
        rows.append(np.concatenate(vector_parts))
        day_keys.append(pd.Timestamp(day))
    matrix = np.vstack(rows) if rows else np.empty((0, 0), dtype="float64")
    return frame, pd.DatetimeIndex(day_keys), matrix


def robust_scale(train_matrix, target_vector):
    med = np.nanmedian(train_matrix, axis=0)
    q75 = np.nanpercentile(train_matrix, 75, axis=0)
    q25 = np.nanpercentile(train_matrix, 25, axis=0)
    scale = q75 - q25
    scale[~np.isfinite(scale) | (scale < 1e-6)] = 1.0
    train = (np.where(np.isfinite(train_matrix), train_matrix, med) - med) / scale
    target = (np.where(np.isfinite(target_vector), target_vector, med) - med) / scale
    return train, target


def weighted_mean_and_std(values, weights):
    values = np.asarray(values, dtype="float64")
    weights = np.asarray(weights, dtype="float64")
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return np.nan, np.nan
    values = values[mask]
    weights = weights[mask]
    weights = weights / max(weights.sum(), 1e-12)
    mean = float(np.sum(values * weights))
    variance = float(np.sum(weights * np.square(values - mean)))
    return mean, float(np.sqrt(max(variance, 0.0)))


def consistency_shrink(target, std_value, scale):
    if scale <= 0 or not np.isfinite(std_value):
        return 1.0
    return float(1.0 / (1.0 + std_value / scale))


def apply_analog_adjustment(predictions, args):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = build_stacker_frame(predictions, args.source_col)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    frame, day_keys, day_matrix = build_day_matrix(frame, args.source_col)
    day_to_pos = {day: pos for pos, day in enumerate(day_keys)}
    valid_days = full_day_keys(frame)
    hours_to_apply = parse_hours(args.hours)

    source = pd.to_numeric(frame[args.source_col], errors="coerce").to_numpy(dtype="float64")
    adjusted = source.copy()
    applied = np.zeros(len(frame), dtype="int64")
    distance_out = np.full(len(frame), np.nan, dtype="float64")

    frame_day = frame["datetime"].dt.normalize()
    frame_hour = frame["datetime"].dt.hour
    source_values = frame[args.source_col].to_numpy(dtype="float64")
    actual_values = frame["actual"].to_numpy(dtype="float64")
    target_labels = target_values(actual_values, source_values, args.target)
    if args.target == "ratio":
        target_labels = np.clip(target_labels, 0.0, args.target_clip)
    elif args.target == "logresid":
        target_labels = np.clip(target_labels, -args.target_clip, args.target_clip)
    elif args.target == "resid":
        target_labels = np.clip(target_labels, -args.target_clip, args.target_clip)

    for day in valid_days:
        if day not in day_to_pos:
            continue
        train_start = day - pd.Timedelta(days=args.lookback_days)
        candidate_days = valid_days[(valid_days < day) & (valid_days >= train_start)]
        candidate_days = pd.DatetimeIndex([d for d in candidate_days if d in day_to_pos])
        if len(candidate_days) < args.min_train_days:
            continue

        train_positions = np.array([day_to_pos[d] for d in candidate_days], dtype="int64")
        target_position = day_to_pos[day]
        train_scaled, target_scaled = robust_scale(day_matrix[train_positions], day_matrix[target_position])
        distances = np.sqrt(np.nanmean(np.square(train_scaled - target_scaled), axis=1))
        finite = np.isfinite(distances)
        if finite.sum() < args.min_train_days:
            continue

        order = np.argsort(np.where(finite, distances, np.inf))
        nearest = order[: min(args.k, len(order))]
        nearest = nearest[np.isfinite(distances[nearest])]
        if len(nearest) < max(2, min(args.min_train_days, args.k // 2)):
            continue

        nearest_days = candidate_days[nearest]
        nearest_dist = distances[nearest]
        distance_weights = np.exp(-nearest_dist / max(args.distance_temperature, 1e-6))
        age_days = np.asarray((day - nearest_days).days, dtype="float64")
        if args.half_life_days > 0:
            recency_weights = np.power(0.5, age_days / args.half_life_days)
        else:
            recency_weights = np.ones_like(distance_weights)
        weights = distance_weights * recency_weights
        if not np.isfinite(weights).any() or weights.sum() <= 0:
            continue

        day_mask = (frame_day == day).to_numpy()
        day_indices = np.flatnonzero(day_mask)
        for row_idx in day_indices:
            hour = int(frame_hour.iloc[row_idx])
            if hour not in hours_to_apply:
                continue
            label_values = []
            label_weights = []
            for candidate_day, weight in zip(nearest_days, weights):
                match = ((frame_day == candidate_day) & (frame_hour == hour)).to_numpy()
                if not match.any():
                    continue
                candidate_idx = int(np.flatnonzero(match)[0])
                label_values.append(target_labels[candidate_idx])
                label_weights.append(weight)
            label_mean, label_std = weighted_mean_and_std(label_values, label_weights)
            if not np.isfinite(label_mean):
                continue

            raw_pred = invert_prediction(
                np.array([source[row_idx]], dtype="float64"),
                np.array([label_mean], dtype="float64"),
                args.target,
            )[0]
            shrink = consistency_shrink(args.target, label_std, args.consistency_scale)
            effective_blend = args.blend * shrink
            adjusted[row_idx] = (1.0 - effective_blend) * source[row_idx] + effective_blend * raw_pred
            applied[row_idx] = 1
            distance_out[row_idx] = float(np.nanmean(nearest_dist))

    if args.apply_recent_days > 0:
        recent_start = frame["datetime"].max() - pd.Timedelta(days=args.apply_recent_days)
        recent_mask = (frame["datetime"] >= recent_start).to_numpy()
        adjusted = np.where(recent_mask, adjusted, source)
        applied = np.where(recent_mask, applied, 0)

    frame[args.output_col] = clip_price_forecast(adjusted, frame["price_cap"].to_numpy(dtype="float64"))
    frame[f"{args.output_col}_applied"] = applied
    frame[f"{args.output_col}_mean_analog_distance"] = distance_out
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Analog day profile correction: "
            f"source `{params['source_col']}`, target `{params['target']}`, "
            f"lookback `{params['lookback_days']}` days, k `{params['k']}`, "
            f"blend `{params['blend']}`, hours `{params['hours']}`.\n"
        )
        f.write(
            "- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, "
            "and shifted source-error anomaly features only.\n"
        )
        f.write("- For each target day, analog days are strictly earlier than the target day.\n")
        f.write(f"- Adjusted rows: `{applied_rows}`.\n\n")
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
    parser = argparse.ArgumentParser(description="Leakage-safe analog-day residual profile correction.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", default="analog_day_profile_pred")
    parser.add_argument("--target", choices=["ratio", "resid", "logresid"], default="ratio")
    parser.add_argument("--lookback-days", type=int, default=75)
    parser.add_argument("--min-train-days", type=int, default=21)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--blend", type=float, default=0.08)
    parser.add_argument("--hours", default="0-23")
    parser.add_argument("--half-life-days", type=float, default=45.0)
    parser.add_argument("--distance-temperature", type=float, default=0.8)
    parser.add_argument("--consistency-scale", type=float, default=0.35)
    parser.add_argument("--target-clip", type=float, default=3.0)
    parser.add_argument("--apply-recent-days", type=int, default=0)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted = apply_analog_adjustment(predictions, args)
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
    applied_rows = int(adjusted[applied_col].fillna(0).astype(bool).sum())
    params = vars(args).copy()
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["analog_day_profile_params"] = params
    payload["analog_day_profile_applied_rows"] = applied_rows
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
    )

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.4f}% "
            f"14d={metrics['last_14d']['wmape']:.4f}%"
        )
    print(f"adjusted_rows={applied_rows}")


if __name__ == "__main__":
    main()
