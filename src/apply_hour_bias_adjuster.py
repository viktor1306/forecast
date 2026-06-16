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


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def parse_hours(text):
    text = str(text).strip().lower()
    if text == "all":
        return set(range(24))

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
    return selected


def add_shifted_hour_signals(frame, source_col, rolling_hours, stat="mean"):
    error = frame[source_col].astype("float64") - frame["actual"].astype("float64")
    ape = error.abs() / frame["actual"].abs().clip(lower=1.0)
    hour = frame["datetime"].dt.hour

    def shifted_rolling(values):
        rolling = values.shift(1).rolling(rolling_hours, min_periods=1)
        if stat == "mean":
            return rolling.mean()
        if stat == "median":
            return rolling.median()
        raise ValueError(f"Unsupported hour signal stat: {stat}")

    bias_signal = error.groupby(hour, group_keys=False).transform(shifted_rolling)
    wmape_signal = ape.groupby(hour, group_keys=False).transform(shifted_rolling) * 100.0
    return bias_signal.to_numpy(dtype="float64"), wmape_signal.to_numpy(dtype="float64")


def gate_mask(bias_signal, wmape_signal, gate, threshold):
    if gate == "none":
        return np.ones(len(bias_signal), dtype=bool)
    if gate == "absbias":
        return np.abs(bias_signal) >= threshold
    if gate == "wmape":
        return wmape_signal >= threshold
    raise ValueError(f"Unsupported gate: {gate}")


def apply_hour_bias_adjustment(predictions, args):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    bias_signal, wmape_signal = add_shifted_hour_signals(
        frame=frame,
        source_col=args.source_col,
        rolling_hours=args.rolling_hours,
        stat=args.stat,
    )
    hours = parse_hours(args.hours)
    hour_mask = frame["datetime"].dt.hour.isin(hours).to_numpy()
    finite_mask = np.isfinite(bias_signal)
    selected = hour_mask & finite_mask & gate_mask(bias_signal, wmape_signal, args.gate, args.gate_threshold)

    source = frame[args.source_col].to_numpy(dtype="float64")
    adjusted = source.copy()
    adjusted[selected] = adjusted[selected] - args.beta * bias_signal[selected]
    adjusted = clip_price_forecast(adjusted, frame["price_cap"].to_numpy(dtype="float64"))

    frame[args.output_col] = adjusted
    frame[f"{args.output_col}_applied"] = selected.astype("int64")
    frame[f"{args.output_col}_hour_bias_signal"] = bias_signal
    frame[f"{args.output_col}_hour_wmape_signal"] = wmape_signal
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Shifted same-hour bias adjuster: "
            f"source `{params['source_col']}`, rolling same-hour observations `{params['rolling_hours']}`, "
            f"stat `{params.get('stat', 'mean')}`, beta `{params['beta']}`, "
            f"hours `{params['hours']}`, gate `{params['gate']}` "
            f"threshold `{params['gate_threshold']}`.\n"
        )
        f.write(
            "- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; "
            "for each row, the signal uses only earlier observations of the same delivery hour.\n"
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
    parser = argparse.ArgumentParser(description="Leakage-safe shifted same-hour source-bias adjustment.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", default="hour_bias_adjusted_pred")
    parser.add_argument("--rolling-hours", type=int, default=3)
    parser.add_argument("--stat", choices=["mean", "median"], default="mean")
    parser.add_argument("--beta", type=float, default=0.2)
    parser.add_argument("--hours", default="all")
    parser.add_argument("--gate", choices=["none", "absbias", "wmape"], default="none")
    parser.add_argument("--gate-threshold", type=float, default=0.0)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted = apply_hour_bias_adjustment(predictions, args)
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
    payload["hour_bias_adjuster_params"] = params
    payload["hour_bias_adjuster_applied_rows"] = applied_rows
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
