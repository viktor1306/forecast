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


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def parse_hours(text):
    text = str(text).strip().lower()
    if text in {"all", "0-23"}:
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


def bounded(values, min_value, max_value):
    if isinstance(values, pd.Series):
        arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype="float64")
    else:
        arr = np.asarray(values, dtype="float64")
    mask = np.isfinite(arr)
    if min_value > 0.0:
        mask &= arr >= min_value
    if max_value > 0.0:
        mask &= arr <= max_value
    return mask


def apply_rebound_profile_adjustment(predictions, args):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = build_stacker_frame(predictions, args.source_col)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    for col in [args.candidate_col, "f_rolling_mean_24", "f_rolling_mean_hour_7d"]:
        if col not in frame.columns:
            raise ValueError(f"Missing required feature column: {col}")

    cap = frame["price_cap"].to_numpy(dtype="float64")
    source = clip_price_forecast(frame[args.source_col].to_numpy(dtype="float64"), cap)
    candidate = clip_price_forecast(
        pd.to_numeric(frame[args.candidate_col], errors="coerce").to_numpy(dtype="float64"),
        cap,
    )
    candidate = np.where(np.isfinite(candidate), candidate, source)

    hours = parse_hours(args.hours)
    selected = frame["datetime"].dt.hour.isin(hours).to_numpy()
    selected &= bounded(source, args.source_min, args.source_max)
    rolling24 = pd.to_numeric(frame["f_rolling_mean_24"], errors="coerce").to_numpy(dtype="float64")
    rolling7h = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")
    selected &= bounded(rolling24, args.rolling24_min, args.rolling24_max)
    if args.rolling24_minus_hour7_min > 0.0:
        selected &= np.isfinite(rolling24 - rolling7h)
        selected &= (rolling24 - rolling7h) >= args.rolling24_minus_hour7_min
    candidate_delta = candidate - source
    if args.candidate_direction == "up":
        selected &= candidate_delta > 0.0
    elif args.candidate_direction == "down":
        selected &= candidate_delta < 0.0
    elif args.candidate_direction != "any":
        raise ValueError(f"Unsupported candidate direction: {args.candidate_direction}")
    if args.candidate_absdiff_min > 0.0:
        selected &= np.abs(candidate_delta) >= args.candidate_absdiff_min

    adjusted = source.copy()
    adjusted[selected] = (1.0 - args.alpha) * source[selected] + args.alpha * candidate[selected]
    frame[args.source_col] = source
    frame[args.output_col] = clip_price_forecast(adjusted, cap)
    frame[f"{args.output_col}_applied"] = selected.astype("int64")
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Forecast-time rebound profile adjuster: "
            f"source `{params['source_col']}`, candidate `{params['candidate_col']}`, "
            f"alpha `{params['alpha']}`, hours `{params['hours']}`, "
            f"source range `{params['source_min']}`-`{params['source_max']}`, "
            f"rolling24 min `{params['rolling24_min']}`, rolling24-hour7 diff min "
            f"`{params['rolling24_minus_hour7_min']}`, candidate direction "
            f"`{params.get('candidate_direction', 'any')}`, candidate absdiff min "
            f"`{params.get('candidate_absdiff_min', 0.0)}`.\n"
        )
        f.write("- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.\n")
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
    parser = argparse.ArgumentParser(description="Leakage-safe forecast-time rebound profile adjustment.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--candidate-col", default="f_rolling_mean_hour_7d")
    parser.add_argument("--output-col", default="rebound_profile_pred")
    parser.add_argument("--alpha", type=float, default=0.08)
    parser.add_argument("--hours", default="10-13")
    parser.add_argument("--source-min", type=float, default=0.0)
    parser.add_argument("--source-max", type=float, default=2000.0)
    parser.add_argument("--rolling24-min", type=float, default=6000.0)
    parser.add_argument("--rolling24-max", type=float, default=0.0)
    parser.add_argument("--rolling24-minus-hour7-min", type=float, default=3500.0)
    parser.add_argument("--candidate-direction", choices=["any", "up", "down"], default="any")
    parser.add_argument("--candidate-absdiff-min", type=float, default=0.0)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted = apply_rebound_profile_adjustment(predictions, args)
    variant_cols = [
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
    applied_rows = int(adjusted[applied_col].sum())
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["rebound_profile_params"] = vars(args).copy()
    payload["rebound_profile_applied_rows"] = applied_rows
    payload["rebound_profile_applied_days"] = int(
        adjusted.loc[adjusted[applied_col] == 1, "datetime"].dt.normalize().nunique()
    )
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    append_log(
        args.output_dir,
        args.experiment_id,
        args.input_experiment,
        vars(args).copy(),
        artifacts,
        variant_metrics,
        applied_rows,
    )

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.4f}% "
            f"14d={metrics['last_14d']['wmape']:.4f}%"
        )
    print(f"adjusted_rows={applied_rows}")


if __name__ == "__main__":
    main()
