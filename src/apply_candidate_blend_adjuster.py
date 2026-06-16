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


DEFAULT_PRICE_BINS = "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000"
DEFAULT_RATIO_BINS = "-0.01,0.01,0.05,0.1,0.2,0.5,0.85,0.98,1.01,2.1"
DEFAULT_DIFF_BINS = "-1,100,250,500,1000,2000,4000,8000,1000000000"


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


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
        "day": set(range(10, 17)),
        "midday": {11, 12, 13, 14, 15, 16},
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
    return pd.cut(
        values,
        bins=parse_number_list(bins),
        labels=False,
        include_lowest=True,
    ).astype("float64")


def build_group_keys(frame, source_col, candidate_col, group_by, price_bins, ratio_bins, diff_bins):
    dt = frame["datetime"]
    source = frame[source_col].astype("float64")
    candidate = frame[candidate_col].astype("float64")
    cap = frame["price_cap"].astype("float64").clip(lower=1.0)
    source_ratio = (source / cap).clip(lower=0.0)
    candidate_ratio = (candidate / cap).clip(lower=0.0)
    diff = (source - candidate).abs()

    definitions = {
        "hour": dt.dt.hour,
        "dow": dt.dt.dayofweek,
        "weekend": dt.dt.dayofweek.isin([5, 6]).astype("int64"),
        "month": dt.dt.month,
        "summer": dt.dt.month.isin([6, 7, 8]).astype("int64"),
        "source_bin": _binned(source, price_bins),
        "source_ratio_bin": _binned(source_ratio, ratio_bins),
        "candidate_bin": _binned(candidate, price_bins),
        "candidate_ratio_bin": _binned(candidate_ratio, ratio_bins),
        "diff_bin": _binned(diff, diff_bins),
        "low_source": (source < 1000.0).astype("int64"),
        "low_candidate": (candidate < 1000.0).astype("int64"),
    }

    keys = []
    for name in [part.strip() for part in group_by.split(",") if part.strip()]:
        if name not in definitions:
            raise ValueError(f"Unsupported group key `{name}`. Supported: {sorted(definitions)}")
        keys.append(definitions[name])
    if not keys:
        raise ValueError("At least one --group-by key is required.")
    return keys


def shifted_candidate_advantage(frame, source_col, candidate_col, group_keys, rolling_rows, stat):
    source = frame[source_col].astype("float64")
    candidate = frame[candidate_col].astype("float64")
    actual = frame["actual"].astype("float64")
    advantage = (source - actual).abs() - (candidate - actual).abs()

    def shifted_rolling(values):
        rolling = values.shift(1).rolling(rolling_rows, min_periods=1)
        if stat == "mean":
            return rolling.mean()
        if stat == "median":
            return rolling.median()
        raise ValueError(f"Unsupported stat: {stat}")

    return advantage.groupby(group_keys, sort=False, group_keys=False).transform(shifted_rolling)


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


def apply_candidate_blend_adjustment(predictions, args):
    for col in (args.source_col, args.candidate_col):
        if col not in predictions.columns:
            raise ValueError(f"Missing column: {col}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    group_keys = build_group_keys(
        frame=frame,
        source_col=args.source_col,
        candidate_col=args.candidate_col,
        group_by=args.group_by,
        price_bins=getattr(args, "price_bins", DEFAULT_PRICE_BINS),
        ratio_bins=getattr(args, "ratio_bins", DEFAULT_RATIO_BINS),
        diff_bins=getattr(args, "diff_bins", DEFAULT_DIFF_BINS),
    )
    advantage_signal = shifted_candidate_advantage(
        frame=frame,
        source_col=args.source_col,
        candidate_col=args.candidate_col,
        group_keys=group_keys,
        rolling_rows=args.rolling_rows,
        stat=args.stat,
    ).to_numpy(dtype="float64")

    hours = parse_hours(args.hours)
    hour_mask = frame["datetime"].dt.hour.isin(hours).to_numpy()
    source = frame[args.source_col].to_numpy(dtype="float64")
    candidate = frame[args.candidate_col].to_numpy(dtype="float64")
    cap = frame["price_cap"].to_numpy(dtype="float64")
    finite_mask = np.isfinite(source) & np.isfinite(candidate) & np.isfinite(advantage_signal)
    selected = (
        finite_mask
        & hour_mask
        & (advantage_signal >= args.advantage_threshold)
        & distance_mask(source, candidate, cap, args.distance_op, args.distance_threshold)
    )

    adjusted = source.copy()
    adjusted[selected] = (1.0 - args.alpha) * source[selected] + args.alpha * candidate[selected]
    adjusted = np.clip(adjusted, 0.0, cap)

    frame[args.output_col] = adjusted
    frame[f"{args.output_col}_applied"] = selected.astype("int64")
    frame[f"{args.output_col}_candidate_advantage_signal"] = advantage_signal
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Shifted candidate-blend adjuster: "
            f"source `{params['source_col']}`, candidate `{params['candidate_col']}`, "
            f"group `{params['group_by']}`, rolling group observations `{params['rolling_rows']}`, "
            f"stat `{params['stat']}`, advantage threshold `{params['advantage_threshold']}`, "
            f"hours `{params['hours']}`, distance `{params['distance_op']}` `{params['distance_threshold']}`, "
            f"alpha `{params['alpha']}`.\n"
        )
        f.write(
            "- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; "
            "selection uses shifted rolling historical candidate advantage in forecast-time groups only.\n"
        )
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
    parser = argparse.ArgumentParser(description="Leakage-safe shifted candidate blend adjustment.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--candidate-col", required=True)
    parser.add_argument("--output-col", default="candidate_blend_adjusted_pred")
    parser.add_argument("--group-by", default="hour")
    parser.add_argument("--price-bins", default=DEFAULT_PRICE_BINS)
    parser.add_argument("--ratio-bins", default=DEFAULT_RATIO_BINS)
    parser.add_argument("--diff-bins", default=DEFAULT_DIFF_BINS)
    parser.add_argument("--rolling-rows", type=int, default=5)
    parser.add_argument("--stat", choices=["mean", "median"], default="median")
    parser.add_argument("--advantage-threshold", type=float, default=0.0)
    parser.add_argument("--hours", default="all")
    parser.add_argument("--distance-op", choices=["none", "le_abs", "ge_abs", "le_rel", "ge_rel"], default="none")
    parser.add_argument("--distance-threshold", type=float, default=0.0)
    parser.add_argument("--alpha", type=float, default=0.2)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted = apply_candidate_blend_adjustment(predictions, args)
    variant_cols = [
        "tree_recent_calibrated_pred",
        args.source_col,
        args.candidate_col,
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
    applied_rows = int(adjusted[applied_col].sum())
    params = vars(args).copy()
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
        print(f"{col}: 3m={metrics['last_3m']['wmape']:.4f}% 14d={metrics['last_14d']['wmape']:.4f}%")
    print(f"adjusted_rows={applied_rows}")


if __name__ == "__main__":
    main()
