import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts


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


def add_high_profile_adjustment(
    predictions,
    source_col,
    output_col,
    anchor_col="f_price_lag_24",
    anchor_output_col="high_profile_anchor",
    flag_col="high_profile_applied",
    anchor_threshold=6500.0,
    min_gap=1000.0,
    blend=0.6,
    hours="18-23",
    apply_recent_days=14,
    min_features=None,
    max_features=None,
):
    frame = predictions.copy()
    if source_col not in frame.columns:
        raise ValueError(f"Missing source prediction column: {source_col}")
    if anchor_col not in frame.columns:
        raise ValueError(f"Missing anchor column in predictions: {anchor_col}")

    dt = pd.DatetimeIndex(pd.to_datetime(frame["datetime"]))
    source = pd.to_numeric(frame[source_col], errors="coerce").to_numpy(dtype="float64")
    anchor = pd.to_numeric(frame[anchor_col], errors="coerce").to_numpy(dtype="float64")
    caps = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")

    recent_start = dt.max() - pd.Timedelta(days=apply_recent_days)
    extra_mask = np.ones(len(frame), dtype=bool)
    for name, threshold in min_features or []:
        if name not in frame.columns:
            raise ValueError(f"Missing min filter feature column: {name}")
        values = pd.to_numeric(frame[name], errors="coerce").to_numpy(dtype="float64")
        extra_mask &= np.isfinite(values) & (values >= threshold)
    for name, threshold in max_features or []:
        if name not in frame.columns:
            raise ValueError(f"Missing max filter feature column: {name}")
        values = pd.to_numeric(frame[name], errors="coerce").to_numpy(dtype="float64")
        extra_mask &= np.isfinite(values) & (values <= threshold)

    risk = (
        (dt >= recent_start)
        & extra_mask
        & hour_mask(dt, hours)
        & np.isfinite(anchor)
        & (anchor >= anchor_threshold)
        & ((anchor - source) >= min_gap)
    )

    adjusted = source.copy()
    adjusted[risk] = np.maximum(source[risk], (1.0 - blend) * source[risk] + blend * anchor[risk])
    frame[anchor_output_col] = anchor
    frame[flag_col] = risk.astype(int)
    frame[output_col] = np.clip(adjusted, 0.0, caps)
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- High-profile rule: "
            f"`{params['anchor_col']} >= {params['anchor_threshold']}`, "
            f"`anchor - pred >= {params['min_gap']}`, "
            f"`blend={params['blend']}`, hours `{params['hours']}`, "
            f"recent days `{params['apply_recent_days']}`.\n"
        )
        f.write(f"- Adjusted rows: `{applied_rows}`.\n")
        f.write(f"- Flag column: `{params['flag_col']}`; output column: `{params['output_col']}`.\n")
        if params.get("min_features") or params.get("max_features"):
            f.write(f"- Extra min filters: `{params.get('min_features')}`; max filters: `{params.get('max_features')}`.\n")
        f.write("- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.\n\n")
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
    parser = argparse.ArgumentParser(description="Apply a deterministic recent high/cap profile adjustment.")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", default="rolling_stack_pred")
    parser.add_argument("--output-col", default="high_profile_pred")
    parser.add_argument("--anchor-col", default="f_price_lag_24")
    parser.add_argument("--anchor-output-col", default="high_profile_anchor")
    parser.add_argument("--flag-col", default="high_profile_applied")
    parser.add_argument("--anchor-threshold", type=float, default=6500.0)
    parser.add_argument("--min-gap", type=float, default=1000.0)
    parser.add_argument("--blend", type=float, default=0.6)
    parser.add_argument("--hours", default="18-23")
    parser.add_argument("--apply-recent-days", type=int, default=14)
    parser.add_argument("--min-feature", action="append", default=[])
    parser.add_argument("--max-feature", action="append", default=[])
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    min_features = parse_feature_thresholds(args.min_feature)
    max_features = parse_feature_thresholds(args.max_feature)
    params = {
        "anchor_col": args.anchor_col,
        "anchor_output_col": args.anchor_output_col,
        "flag_col": args.flag_col,
        "anchor_threshold": args.anchor_threshold,
        "min_gap": args.min_gap,
        "blend": args.blend,
        "hours": args.hours,
        "apply_recent_days": args.apply_recent_days,
        "min_features": min_features,
        "max_features": max_features,
    }
    adjusted = add_high_profile_adjustment(
        predictions=predictions,
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
    payload["high_profile_params"] = log_params
    applied_rows = int(adjusted[args.flag_col].fillna(False).astype(bool).sum())
    payload["profile_adjustment_applied_rows"] = applied_rows
    payload[f"{args.flag_col}_rows"] = applied_rows
    if args.flag_col == "high_profile_applied":
        payload["high_profile_applied_rows"] = applied_rows
    inherited_flag_cols = [
        col for col in adjusted.columns
        if col.endswith("_applied") and col != args.flag_col
    ]
    for flag_col in sorted(inherited_flag_cols):
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
        applied_rows=applied_rows,
    )

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.3f}% "
            f"14d={metrics['last_14d']['wmape']:.3f}%"
        )
    print(f"adjusted_rows={applied_rows}")


if __name__ == "__main__":
    main()
