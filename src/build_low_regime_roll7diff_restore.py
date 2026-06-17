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


SOURCE_COL = "low_regime_final_restore_target15_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
OUTPUT_COL = "low_regime_roll7diff_restore_target15_pred"

PRICE_BINS = [-1, 10, 50, 100, 250, 500, 1000, 1500, 3000, 7000, 100000]
SRC_ROLL7_DIFF_BINS = [
    -100000,
    -5000,
    -2000,
    -1000,
    -500,
    -250,
    -100,
    -25,
    25,
    100,
    250,
    500,
    1000,
    2000,
    5000,
    100000,
]


ROLL7DIFF_RESTORE_STEPS = [
    {
        "name": "h11_roll7diff_s250_1000_w2_q25_resid_neg",
        "kind": "resid",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 2,
        "stat": "q25",
        "hours": [11],
        "source_min": 250.0,
        "source_max": 1000.0,
        "strength": -1.0,
    },
    {
        "name": "h11_sourcebin_s500_1500_w3_q25_actual_blend",
        "kind": "actual",
        "group_keys": ["hour", "source_bin"],
        "rolling_rows": 3,
        "stat": "q25",
        "hours": [11],
        "source_min": 500.0,
        "source_max": 1500.0,
        "strength": 0.75,
    },
    {
        "name": "h10_16_roll7diff_s100_500_w13_mean_resid_neg",
        "kind": "resid",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 13,
        "stat": "mean",
        "hours": [10, 11, 12, 13, 14, 15, 16],
        "source_min": 100.0,
        "source_max": 500.0,
        "strength": -1.0,
    },
    {
        "name": "h13_source_roll7_s500_1500_w3_q25_resid_half",
        "kind": "resid",
        "group_keys": ["hour", "source_bin", "roll7_bin"],
        "rolling_rows": 3,
        "stat": "q25",
        "hours": [13],
        "source_min": 500.0,
        "source_max": 1500.0,
        "strength": 0.5,
    },
]


def _rolling_signal(values, groups, rolling_rows, stat):
    grouped = pd.Series(values).groupby(groups, sort=False, group_keys=False)

    def transform(series):
        shifted = series.shift(1)
        if stat == "mean":
            return shifted.rolling(rolling_rows, min_periods=1).mean()
        if stat == "median":
            return shifted.rolling(rolling_rows, min_periods=1).median()
        if stat == "q25":
            return shifted.rolling(rolling_rows, min_periods=1).quantile(0.25)
        if stat == "q75":
            return shifted.rolling(rolling_rows, min_periods=1).quantile(0.75)
        raise ValueError(f"Unsupported stat: {stat}")

    return grouped.transform(transform).to_numpy(dtype="float64")


def _field_frame(frame, source):
    rolling_mean_7d = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")

    fields = pd.DataFrame(index=frame.index)
    fields["hour"] = frame["datetime"].dt.hour.astype("int64")
    fields["source_bin"] = pd.cut(source, PRICE_BINS, labels=False, include_lowest=True).astype("float64")
    fields["roll7_bin"] = pd.cut(rolling_mean_7d, PRICE_BINS, labels=False, include_lowest=True).astype("float64")
    fields["src_roll7_diff_bin"] = pd.cut(
        source - rolling_mean_7d,
        SRC_ROLL7_DIFF_BINS,
        labels=False,
        include_lowest=True,
    ).astype("float64")
    return fields


def _step_mask(fields, source, step):
    selected = fields["hour"].isin(step["hours"]).to_numpy()
    if "source_min" in step:
        selected &= source >= float(step["source_min"])
    if "source_max" in step:
        selected &= source < float(step["source_max"])
    return selected


def _apply_step(frame, source, step):
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    fields = _field_frame(frame, source)
    groups = [fields[key] for key in step["group_keys"]]

    if step["kind"] == "actual":
        values = actual
    elif step["kind"] == "resid":
        values = actual - source
    else:
        raise ValueError(f"Unsupported restore kind: {step['kind']}")

    signal = _rolling_signal(values, groups, step["rolling_rows"], step["stat"])
    selected = _step_mask(fields, source, step) & np.isfinite(signal)

    if step["kind"] == "actual":
        candidate = (1.0 - float(step["strength"])) * source + float(step["strength"]) * signal
    else:
        candidate = source + float(step["strength"]) * signal

    restored = source.copy()
    clipped_candidate = clip_price_forecast(candidate, cap)
    restored[selected] = clipped_candidate[selected]
    return clip_price_forecast(restored, cap), signal, selected


def build_roll7diff_restore(predictions, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    required = {
        "datetime",
        "actual",
        "price_cap",
        source_col,
        PRODUCTION_BASE_COL,
        "f_rolling_mean_hour_7d",
    }
    missing = sorted(required.difference(predictions.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")

    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    source = clip_price_forecast(pd.to_numeric(frame[source_col], errors="coerce"), cap)
    step_summaries = []

    for step in ROLL7DIFF_RESTORE_STEPS:
        source, signal, selected = _apply_step(frame, source, step)
        frame[f"{output_col}_{step['name']}_signal"] = signal
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        step_summaries.append({**step, "applied_rows": int(selected.sum())})

    evening = frame["datetime"].dt.hour.between(19, 23).to_numpy()
    source[evening] = pd.to_numeric(frame.loc[evening, PRODUCTION_BASE_COL], errors="coerce")
    frame[output_col] = clip_price_forecast(source, cap)
    frame[f"{output_col}_used_base_evening"] = evening.astype("int64")
    return frame, step_summaries


def main():
    parser = argparse.ArgumentParser(description="Build shifted roll7/diff restore for the low-regime target15 track.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_low_regime_final_restore_target15_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_roll7diff_restore_target15_v1")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    restored, step_summaries = build_roll7diff_restore(
        predictions,
        source_col=args.source_col,
        output_col=args.output_col,
    )
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
    payload["roll7diff_restore_steps"] = step_summaries
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
    for step in step_summaries:
        print(f"{step['name']}_applied_rows={step['applied_rows']}")
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
