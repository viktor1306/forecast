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


SOURCE_COL = "low_regime_candidate_restore_target15_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
OUTPUT_COL = "low_regime_final_restore_target15_pred"

FINAL_RESTORE_STEPS = [
    {
        "name": "h10_partial_multistage_restore",
        "candidate_col": "low_regime_multistage_target15_repair_pred",
        "hours": [10],
        "alpha": 0.75,
    },
    {
        "name": "h10_12_highsource_day14_blend",
        "candidate_col": "day14_16_ratio_lowrepair_after_morning_pred",
        "hours": [10, 11, 12],
        "source_min": 1000.0,
        "source_max": 3000.0,
        "alpha": 0.75,
    },
    {
        "name": "h13_16_midsource_day14_blend",
        "candidate_col": "day14_16_ratio_lowrepair_after_morning_pred",
        "hours": [13, 14, 15, 16],
        "source_min": 250.0,
        "source_max": 500.0,
        "alpha": 0.75,
    },
    {
        "name": "h16_rebound_day14_restore",
        "candidate_col": "day14_16_ratio_lowrepair_after_morning_pred",
        "hours": [16],
        "source_min": 500.0,
        "source_max": 1000.0,
        "alpha": 1.0,
    },
]


def _step_mask(frame, source, step):
    selected = frame["datetime"].dt.hour.isin(step["hours"]).to_numpy()
    if "source_min" in step:
        selected &= source >= float(step["source_min"])
    if "source_max" in step:
        selected &= source < float(step["source_max"])
    return selected


def build_final_restore(predictions, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    required = {"datetime", "actual", "price_cap", source_col, PRODUCTION_BASE_COL}
    for step in FINAL_RESTORE_STEPS:
        required.add(step["candidate_col"])
    missing = sorted(required.difference(predictions.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")

    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    restored = clip_price_forecast(pd.to_numeric(frame[source_col], errors="coerce"), cap)
    summaries = []

    for step in FINAL_RESTORE_STEPS:
        candidate = clip_price_forecast(
            pd.to_numeric(frame[step["candidate_col"]], errors="coerce").to_numpy(dtype="float64"),
            cap,
        )
        selected = _step_mask(frame, restored, step) & np.isfinite(candidate)
        blended = (1.0 - float(step["alpha"])) * restored + float(step["alpha"]) * candidate
        restored[selected] = clip_price_forecast(blended, cap)[selected]
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        summaries.append({**step, "applied_rows": int(selected.sum())})

    evening = frame["datetime"].dt.hour.between(19, 23).to_numpy()
    restored[evening] = pd.to_numeric(frame.loc[evening, PRODUCTION_BASE_COL], errors="coerce")
    frame[output_col] = clip_price_forecast(restored, cap)
    frame[f"{output_col}_used_base_evening"] = evening.astype("int64")
    return frame, summaries


def main():
    parser = argparse.ArgumentParser(description="Final candidate restore after low-regime candidate restore v1.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_low_regime_candidate_restore_target15_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_final_restore_target15_v1")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    restored, summaries = build_final_restore(predictions, source_col=args.source_col, output_col=args.output_col)
    artifacts = save_evaluation_artifacts(
        restored,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )

    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = {
        col: calculate_metrics(restored, pred_col=col)
        for col in [PRODUCTION_BASE_COL, args.source_col, args.output_col]
        if col in restored.columns
    }
    payload["input_csv"] = args.input_csv
    payload["source_col"] = args.source_col
    payload["output_col"] = args.output_col
    payload["final_restore_steps"] = summaries
    payload["evening_guard_source_col"] = PRODUCTION_BASE_COL
    payload["evening_guard_rows"] = int(restored[f"{args.output_col}_used_base_evening"].sum())
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
        f"evening_19_23={regimes['evening_19_23']['wmape']:.4f}%"
    )
    for step in summaries:
        print(f"{step['name']}_applied_rows={step['applied_rows']}")
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
