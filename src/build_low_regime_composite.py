import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts
from prediction_limits import clip_price_forecast


BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
LOW_REPAIR_COL = "day14_16_ratio_lowrepair_after_morning_pred"
OUTPUT_COL = "low_regime_composite_dayrepair_eveguard_pred"


def build_composite(predictions, base_col=BASE_COL, low_repair_col=LOW_REPAIR_COL, output_col=OUTPUT_COL):
    missing = [col for col in ("datetime", "price_cap", base_col, low_repair_col) if col not in predictions.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)

    hour = frame["datetime"].dt.hour
    use_base = hour.between(19, 23)
    combined = frame[low_repair_col].where(~use_base, frame[base_col])
    frame[output_col] = clip_price_forecast(combined, frame["price_cap"])
    frame[f"{output_col}_used_base_evening"] = use_base.astype("int64")
    return frame


def main():
    parser = argparse.ArgumentParser(description="Build low-regime research composite with production evening guard.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_day14_16_ratio_lowrepair_after_morning_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_composite_dayrepair_eveguard_v1")
    parser.add_argument("--base-col", default=BASE_COL)
    parser.add_argument("--low-repair-col", default=LOW_REPAIR_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"])
    composite = build_composite(
        predictions,
        base_col=args.base_col,
        low_repair_col=args.low_repair_col,
        output_col=args.output_col,
    )

    artifacts = save_evaluation_artifacts(
        composite,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )
    variant_metrics = {
        col: calculate_metrics(composite, pred_col=col)
        for col in [args.base_col, args.low_repair_col, args.output_col]
        if col in composite.columns
    }

    evening_rows = int(composite[f"{args.output_col}_used_base_evening"].sum())
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["composite_params"] = {
        "input_csv": args.input_csv,
        "base_col": args.base_col,
        "low_repair_col": args.low_repair_col,
        "output_col": args.output_col,
        "evening_guard_hours": "19-23",
    }
    payload["evening_guard_rows"] = evening_rows
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    metrics = payload
    regimes = metrics["regimes"]
    print(
        f"{args.output_col}: "
        f"3m={metrics['last_3m']['wmape']:.4f}% "
        f"14d={metrics['last_14d']['wmape']:.4f}% "
        f"13d={metrics['last_13d']['wmape']:.4f}% "
        f"summer_daytime_low={regimes['summer_daytime_low']['wmape']:.4f}% "
        f"daytime_low_lt_1000={regimes['daytime_low_lt_1000']['wmape']:.4f}% "
        f"cap_spike_evening={regimes['cap_spike_evening']['wmape']:.4f}% "
        f"evening_19_23={regimes['evening_19_23']['wmape']:.4f}%"
    )
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")
    print(f"evening_guard_rows={evening_rows}")


if __name__ == "__main__":
    main()
