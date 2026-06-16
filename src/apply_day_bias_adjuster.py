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


def rolling_daily_source_error(frame, source_col, rolling_days, min_day_hours):
    all_days = pd.DatetimeIndex(pd.to_datetime(frame["datetime"]).dt.normalize().unique()).sort_values()
    valid = frame.dropna(subset=["actual", source_col]).copy()
    valid["day"] = valid["datetime"].dt.normalize()
    error = valid[source_col].astype("float64") - valid["actual"].astype("float64")
    daily = pd.DataFrame(
        {
            "day": valid["day"],
            "error": error,
            "abs_error": error.abs(),
            "actual_abs": valid["actual"].abs(),
        }
    ).groupby("day").agg(
        row_count=("error", "size"),
        bias=("error", "mean"),
        abs_error_sum=("abs_error", "sum"),
        actual_abs_sum=("actual_abs", "sum"),
    )
    daily = daily.reindex(all_days)
    daily.loc[daily["row_count"] < min_day_hours, ["bias", "abs_error_sum", "actual_abs_sum"]] = np.nan
    daily["wmape"] = daily["abs_error_sum"] / daily["actual_abs_sum"].clip(lower=1.0) * 100.0

    shifted_bias = daily["bias"].shift(1)
    shifted_wmape = daily["wmape"].shift(1)
    return pd.DataFrame(
        {
            "bias_signal": shifted_bias.rolling(rolling_days, min_periods=1).mean(),
            "wmape_signal": shifted_wmape.rolling(rolling_days, min_periods=1).mean(),
        }
    )


def gate_mask(frame, bias_signal, wmape_signal, gate, threshold):
    if gate == "none":
        return np.ones(len(frame), dtype=bool)
    if gate == "absbias":
        return np.abs(bias_signal) >= threshold
    if gate == "wmape":
        return wmape_signal >= threshold
    raise ValueError(f"Unsupported gate: {gate}")


def apply_day_bias_adjustment(predictions, args):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    daily_signals = rolling_daily_source_error(
        frame=frame,
        source_col=args.source_col,
        rolling_days=args.rolling_days,
        min_day_hours=args.min_day_hours,
    )
    day_key = frame["datetime"].dt.normalize()
    bias_signal = day_key.map(daily_signals["bias_signal"]).to_numpy(dtype="float64")
    wmape_signal = day_key.map(daily_signals["wmape_signal"]).to_numpy(dtype="float64")

    hours = parse_hours(args.hours)
    hour_mask = frame["datetime"].dt.hour.isin(hours).to_numpy()
    finite_mask = np.isfinite(bias_signal)
    selected = hour_mask & finite_mask & gate_mask(frame, bias_signal, wmape_signal, args.gate, args.gate_threshold)

    source = frame[args.source_col].to_numpy(dtype="float64")
    adjusted = source.copy()
    adjusted[selected] = adjusted[selected] - args.beta * bias_signal[selected]
    adjusted = clip_price_forecast(adjusted, frame["price_cap"].to_numpy(dtype="float64"))

    frame[args.output_col] = adjusted
    frame[f"{args.output_col}_applied"] = selected.astype("int64")
    frame[f"{args.output_col}_bias_signal"] = bias_signal
    frame[f"{args.output_col}_wmape_signal"] = wmape_signal
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Rolling day-bias adjuster: "
            f"source `{params['source_col']}`, rolling days `{params['rolling_days']}`, "
            f"beta `{params['beta']}`, hours `{params['hours']}`, gate `{params['gate']}` "
            f"threshold `{params['gate_threshold']}`.\n"
        )
        f.write(
            "- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; "
            "daily source bias is computed only from complete earlier days.\n"
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
    parser = argparse.ArgumentParser(description="Leakage-safe shifted daily source-bias adjustment.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", default="day_bias_adjusted_pred")
    parser.add_argument("--rolling-days", type=int, default=3)
    parser.add_argument("--beta", type=float, default=0.2)
    parser.add_argument("--hours", default="0-23")
    parser.add_argument("--gate", choices=["none", "absbias", "wmape"], default="none")
    parser.add_argument("--gate-threshold", type=float, default=0.0)
    parser.add_argument("--min-day-hours", type=int, default=24)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted = apply_day_bias_adjustment(predictions, args)
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
    payload["day_bias_adjuster_params"] = params
    payload["day_bias_adjuster_applied_rows"] = applied_rows
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
