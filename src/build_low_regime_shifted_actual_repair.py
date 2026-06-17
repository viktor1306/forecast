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
from prediction_limits import clip_price_forecast, clip_price_series


SOURCE_COL = "low_regime_group_selector_target15_eveguard_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
OUTPUT_COL = "low_regime_shifted_actual_repair_pred"

SOURCE_BINS = [-1, 10, 50, 100, 250, 500, 1000, 1500, 3000, 7000, 100000]


def build_shifted_actual_repair(
    predictions,
    source_col=SOURCE_COL,
    output_col=OUTPUT_COL,
    source_threshold=250.0,
    rolling_rows=13,
    blend=0.5,
):
    missing = [col for col in ("datetime", "actual", "price_cap", source_col, PRODUCTION_BASE_COL) if col not in predictions.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")

    source = pd.to_numeric(frame[source_col], errors="coerce")
    frame["_source_bin"] = pd.cut(source, SOURCE_BINS, labels=False, include_lowest=True).astype("float64")
    frame["_hour"] = frame["datetime"].dt.hour
    frame["_weekend"] = frame["datetime"].dt.dayofweek.isin([5, 6]).astype("int64")

    group_keys = ["_hour", "_source_bin", "_weekend"]

    def shifted_median(values):
        return values.shift(1).rolling(rolling_rows, min_periods=1).median()

    signal = frame.groupby(group_keys, sort=False, group_keys=False)["actual"].transform(shifted_median)
    hour = frame["datetime"].dt.hour
    selected = hour.between(13, 16) & (source <= source_threshold) & signal.notna()

    repaired = source.copy()
    repaired.loc[selected] = (1.0 - blend) * source.loc[selected] + blend * signal.loc[selected]
    repaired = clip_price_series(repaired, frame["price_cap"])

    evening = hour.between(19, 23)
    repaired.loc[evening] = pd.to_numeric(frame.loc[evening, PRODUCTION_BASE_COL], errors="coerce")
    repaired = clip_price_series(repaired, frame["price_cap"])

    frame[output_col] = repaired
    frame[f"{output_col}_applied"] = selected.astype("int64")
    frame[f"{output_col}_shifted_actual_signal"] = signal
    frame[f"{output_col}_used_base_evening"] = evening.astype("int64")
    return frame.drop(columns=["_source_bin", "_hour", "_weekend"])


def main():
    parser = argparse.ArgumentParser(description="Build shifted actual-median repair for low-regime target track.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_low_regime_group_selector_target15_eveguard_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_shifted_actual_repair_v1")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    repaired = build_shifted_actual_repair(predictions, source_col=args.source_col, output_col=args.output_col)

    artifacts = save_evaluation_artifacts(
        repaired,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )

    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = {
        col: calculate_metrics(repaired, pred_col=col)
        for col in [PRODUCTION_BASE_COL, args.source_col, args.output_col]
        if col in repaired.columns
    }
    payload["repair_params"] = {
        "input_csv": args.input_csv,
        "source_col": args.source_col,
        "output_col": args.output_col,
        "group_key": "hour,source_bin,weekend",
        "source_bins": SOURCE_BINS,
        "hours": "13-16",
        "source_threshold": 250.0,
        "rolling_rows": 13,
        "stat": "median",
        "blend": 0.5,
        "shifted": True,
        "evening_guard_source_col": PRODUCTION_BASE_COL,
    }
    payload["repair_applied_rows"] = int(repaired[f"{args.output_col}_applied"].sum())
    payload["evening_guard_rows"] = int(repaired[f"{args.output_col}_used_base_evening"].sum())
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    regimes = payload["regimes"]
    print(
        f"{args.output_col}: "
        f"3m={payload['last_3m']['wmape']:.4f}% "
        f"14d={payload['last_14d']['wmape']:.4f}% "
        f"13d={payload['last_13d']['wmape']:.4f}% "
        f"summer_daytime_low={regimes['summer_daytime_low']['wmape']:.4f}% "
        f"daytime_low_lt_1000={regimes['daytime_low_lt_1000']['wmape']:.4f}% "
        f"cap_spike_evening={regimes['cap_spike_evening']['wmape']:.4f}% "
        f"evening_19_23={regimes['evening_19_23']['wmape']:.4f}% "
        f"applied_rows={payload['repair_applied_rows']}"
    )
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
