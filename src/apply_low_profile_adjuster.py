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
from train_neural_hybrid import prepare_dataframe


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def hour_mask(datetimes, hours):
    hour_values = pd.DatetimeIndex(datetimes).hour
    selected = np.zeros(len(hour_values), dtype=bool)
    for part in hours.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(value) for value in part.split("-", 1)]
            selected |= (hour_values >= start) & (hour_values <= end)
        else:
            selected |= hour_values == int(part)
    return selected


def parse_feature_thresholds(items):
    parsed = []
    for item in items or []:
        if ":" not in item:
            raise ValueError(f"Feature threshold must use name:value format, got {item!r}")
        name, raw_value = item.split(":", 1)
        parsed.append((name.strip(), float(raw_value)))
    return parsed


def feature_values(name, frame, feature_frame, dt_index):
    if name in frame.columns:
        return pd.to_numeric(frame[name], errors="coerce").to_numpy(dtype="float64")
    if name in feature_frame.columns:
        features = feature_frame.reindex(dt_index)
        return pd.to_numeric(features[name], errors="coerce").to_numpy(dtype="float64")
    raise ValueError(f"Missing filter feature column: {name}")


def add_low_profile_adjustment(
    predictions,
    feature_frame,
    source_col,
    output_col,
    anchor_col="price_lag_24",
    anchor_output_col="low_profile_anchor",
    flag_col="low_profile_applied",
    anchor_threshold=500.0,
    min_gap=1000.0,
    blend=0.15,
    start_month=5,
    end_month=8,
    hours="10-16",
    apply_recent_days=None,
    min_features=None,
    max_features=None,
):
    frame = predictions.copy()
    if source_col not in frame.columns:
        raise ValueError(f"Missing source prediction column: {source_col}")
    if anchor_col not in frame.columns and anchor_col not in feature_frame.columns:
        raise ValueError(f"Missing anchor feature column: {anchor_col}")

    dt_index = pd.DatetimeIndex(pd.to_datetime(frame["datetime"]))
    if anchor_col in frame.columns:
        anchor = pd.to_numeric(frame[anchor_col], errors="coerce").to_numpy(dtype="float64")
    else:
        features = feature_frame.reindex(dt_index)
        anchor = pd.to_numeric(features[anchor_col], errors="coerce").to_numpy(dtype="float64")
    month = dt_index.month
    recent_mask = np.ones(len(frame), dtype=bool)
    if apply_recent_days is not None and apply_recent_days > 0:
        recent_start = dt_index.max() - pd.Timedelta(days=apply_recent_days)
        recent_mask = dt_index >= recent_start
    extra_mask = np.ones(len(frame), dtype=bool)
    for name, threshold in min_features or []:
        values = feature_values(name, frame, feature_frame, dt_index)
        extra_mask &= np.isfinite(values) & (values >= threshold)
    for name, threshold in max_features or []:
        values = feature_values(name, frame, feature_frame, dt_index)
        extra_mask &= np.isfinite(values) & (values <= threshold)

    pred = pd.to_numeric(frame[source_col], errors="coerce").to_numpy(dtype="float64")
    target = np.maximum(anchor, 10.0)
    risk = (
        recent_mask
        & extra_mask
        & hour_mask(dt_index, hours)
        & (month >= start_month)
        & (month <= end_month)
        & np.isfinite(anchor)
        & (anchor <= anchor_threshold)
        & ((pred - anchor) >= min_gap)
    )

    adjusted = pred.copy()
    adjusted[risk] = np.minimum(pred[risk], (1.0 - blend) * pred[risk] + blend * target[risk])
    adjusted = np.clip(adjusted, 0.0, pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64"))

    frame[anchor_output_col] = anchor
    frame[flag_col] = risk.astype(int)
    frame[output_col] = adjusted
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_count):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Low-profile rule: "
            f"`{params['anchor_col']} <= {params['anchor_threshold']}`, "
            f"`pred - anchor >= {params['min_gap']}`, "
            f"`blend={params['blend']}`, months `{params['start_month']}-{params['end_month']}`, "
            f"hours `{params['hours']}`, recent days `{params['apply_recent_days']}`.\n"
        )
        f.write(f"- Adjusted rows: `{applied_count}`.\n")
        f.write(f"- Flag column: `{params['flag_col']}`; output column: `{params['output_col']}`.\n")
        if params.get("min_features") or params.get("max_features"):
            f.write(f"- Extra min filters: `{params.get('min_features')}`; max filters: `{params.get('max_features')}`.\n")
        f.write("- Rule uses lagged/same-hour profile only; no future raw market columns.\n\n")
        f.write("| variant | 3m WMAPE | 14d WMAPE | 3m rows |\n")
        f.write("|---|---:|---:|---:|\n")
        for col, metrics in variant_metrics.items():
            f.write(
                f"| `{col}` | {metrics['last_3m']['wmape']:.2f}% | "
                f"{metrics['last_14d']['wmape']:.2f}% | {metrics['last_3m']['n']} |\n"
            )
        f.write(f"\n- Predictions: `{artifacts['predictions_csv']}`\n")
        f.write(f"- Metrics: `{artifacts['metrics_json']}`\n")
        f.write(f"- Plot: `{artifacts['plot_png']}`\n")
    return os.fspath(log_path)


def main():
    parser = argparse.ArgumentParser(description="Apply a deterministic low-day profile adjustment to neural hybrid predictions.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", default="hybrid_guarded_pred")
    parser.add_argument("--output-col", default="hybrid_low_profile_pred")
    parser.add_argument("--anchor-col", default="price_lag_24")
    parser.add_argument("--anchor-output-col", default="low_profile_anchor")
    parser.add_argument("--flag-col", default="low_profile_applied")
    parser.add_argument("--anchor-threshold", type=float, default=500.0)
    parser.add_argument("--min-gap", type=float, default=1000.0)
    parser.add_argument("--blend", type=float, default=0.15)
    parser.add_argument("--start-month", type=int, default=5)
    parser.add_argument("--end-month", type=int, default=8)
    parser.add_argument("--hours", default="10-16")
    parser.add_argument("--apply-recent-days", type=int, default=0)
    parser.add_argument("--min-feature", action="append", default=[])
    parser.add_argument("--max-feature", action="append", default=[])
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    feature_frame = prepare_dataframe()
    min_features = parse_feature_thresholds(args.min_feature)
    max_features = parse_feature_thresholds(args.max_feature)
    params = {
        "anchor_col": args.anchor_col,
        "anchor_threshold": args.anchor_threshold,
        "min_gap": args.min_gap,
        "blend": args.blend,
        "start_month": args.start_month,
        "end_month": args.end_month,
        "hours": args.hours,
        "apply_recent_days": args.apply_recent_days or None,
        "anchor_output_col": args.anchor_output_col,
        "flag_col": args.flag_col,
        "min_features": min_features,
        "max_features": max_features,
    }
    adjusted = add_low_profile_adjustment(
        predictions=predictions,
        feature_frame=feature_frame,
        source_col=args.source_col,
        output_col=args.output_col,
        **params,
    )
    log_params = {
        **params,
        "source_col": args.source_col,
        "output_col": args.output_col,
    }
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
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["low_profile_params"] = log_params
    applied_count = int(adjusted[args.flag_col].fillna(False).astype(bool).sum())
    payload["profile_adjustment_applied_rows"] = applied_count
    payload[f"{args.flag_col}_rows"] = applied_count
    if args.flag_col == "low_profile_applied":
        payload["low_profile_applied_rows"] = applied_count
    for flag_col in sorted(col for col in adjusted.columns if col.endswith("_applied") and col != args.flag_col):
        payload[f"{flag_col}_rows"] = int(adjusted[flag_col].fillna(False).astype(bool).sum())
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    append_log(
        output_dir=args.output_dir,
        experiment_id=args.experiment_id,
        input_experiment=args.input_experiment,
        params=log_params,
        artifacts=artifacts,
        variant_metrics=variant_metrics,
        applied_count=applied_count,
    )

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.3f}% "
            f"14d={metrics['last_14d']['wmape']:.3f}%"
        )
    print(f"adjusted_rows={applied_count}")


if __name__ == "__main__":
    main()
