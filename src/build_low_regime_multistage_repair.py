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


SOURCE_COL = "low_regime_shifted_actual_repair_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
OUTPUT_COL = "low_regime_multistage_target15_repair_pred"

PRICE_BINS = [-1, 10, 50, 100, 250, 500, 1000, 1500, 3000, 7000, 100000]
FINE_PRICE_BINS = [-1, 10, 25, 50, 75, 100, 150, 250, 400, 600, 1000, 1500, 3000, 7000, 100000]


REPAIR_STEPS = [
    {
        "name": "h15_16_lag24_weekend_ratio_mean3",
        "kind": "ratio",
        "group_keys": ["hour", "lag24_bin", "weekend"],
        "rolling_rows": 3,
        "stat": "mean",
        "hours": [15, 16],
        "source_max": 500.0,
        "strength": 0.75,
    },
    {
        "name": "h11_12_source_rollmin_resid_q25_8",
        "kind": "resid",
        "group_keys": ["hour", "source_bin", "rollmin_bin"],
        "rolling_rows": 8,
        "stat": "q25",
        "hours": [11, 12],
        "source_max": 1000.0,
        "strength": -1.0,
    },
    {
        "name": "h10_samehour_resid_mean21",
        "kind": "resid",
        "group_keys": ["hour"],
        "rolling_rows": 21,
        "stat": "mean",
        "hours": [10],
        "source_max": 2000.0,
        "strength": -1.0,
    },
    {
        "name": "h10_16_samehour_resid_q75_5",
        "kind": "resid",
        "group_keys": ["hour"],
        "rolling_rows": 5,
        "stat": "q75",
        "hours": [10, 11, 12, 13, 14, 15, 16],
        "source_max": 1000.0,
        "strength": -0.25,
    },
    {
        "name": "h10_lag24_weekend_resid_q25_2",
        "kind": "resid",
        "group_keys": ["hour", "lag24_bin", "weekend"],
        "rolling_rows": 2,
        "stat": "q25",
        "hours": [10],
        "source_max": 250.0,
        "strength": -1.0,
    },
    {
        "name": "h15_16_fine_source_ratio_median3",
        "kind": "ratio",
        "group_keys": ["hour", "fine_source_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "hours": [15, 16],
        "source_max": 2000.0,
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
    fields = pd.DataFrame(index=frame.index)
    fields["hour"] = frame["datetime"].dt.hour.astype("int64")
    fields["weekend"] = frame["datetime"].dt.dayofweek.isin([5, 6]).astype("int64")
    fields["source_bin"] = pd.cut(source, PRICE_BINS, labels=False, include_lowest=True).astype("float64")
    fields["fine_source_bin"] = pd.cut(source, FINE_PRICE_BINS, labels=False, include_lowest=True).astype("float64")
    fields["lag24_bin"] = pd.cut(
        pd.to_numeric(frame["f_price_lag_24"], errors="coerce"),
        PRICE_BINS,
        labels=False,
        include_lowest=True,
    ).astype("float64")
    fields["rollmin_bin"] = pd.cut(
        pd.to_numeric(frame["f_rolling_min_24"], errors="coerce"),
        PRICE_BINS,
        labels=False,
        include_lowest=True,
    ).astype("float64")
    return fields


def _apply_step(frame, source, step):
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    fields = _field_frame(frame, source)
    groups = [fields[key] for key in step["group_keys"]]

    if step["kind"] == "actual":
        values = actual
    elif step["kind"] == "resid":
        values = actual - source
    elif step["kind"] == "ratio":
        values = np.maximum(actual, 10.0) / np.maximum(source, 10.0)
    else:
        raise ValueError(f"Unsupported repair kind: {step['kind']}")

    signal = _rolling_signal(values, groups, step["rolling_rows"], step["stat"])
    selected = fields["hour"].isin(step["hours"]).to_numpy() & np.isfinite(signal)
    selected &= source <= float(step["source_max"])

    if step["kind"] == "actual":
        candidate = (1.0 - step["strength"]) * source + step["strength"] * signal
    elif step["kind"] == "resid":
        candidate = source + step["strength"] * signal
    else:
        ratio_signal = np.clip(signal, 0.0, 4.0)
        candidate = source * ((1.0 - step["strength"]) + step["strength"] * ratio_signal)

    repaired = source.copy()
    clipped_candidate = clip_price_forecast(candidate, cap)
    repaired[selected] = clipped_candidate[selected]
    return clip_price_forecast(repaired, cap), signal, selected


def build_multistage_repair(predictions, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    required = {
        "datetime",
        "actual",
        "price_cap",
        source_col,
        PRODUCTION_BASE_COL,
        "f_price_lag_24",
        "f_rolling_min_24",
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

    for step in REPAIR_STEPS:
        source, signal, selected = _apply_step(frame, source, step)
        frame[f"{output_col}_{step['name']}_signal"] = signal
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        step_summaries.append({**step, "applied_rows": int(selected.sum())})

    hour = frame["datetime"].dt.hour
    evening = hour.between(19, 23).to_numpy()
    source[evening] = pd.to_numeric(frame.loc[evening, PRODUCTION_BASE_COL], errors="coerce")
    frame[output_col] = clip_price_forecast(source, cap)
    frame[f"{output_col}_used_base_evening"] = evening.astype("int64")
    return frame, step_summaries


def main():
    parser = argparse.ArgumentParser(description="Build multistage shifted low-regime repair for the ~15% target track.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_low_regime_shifted_actual_repair_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_multistage_target15_repair_v1")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    repaired, step_summaries = build_multistage_repair(
        predictions,
        source_col=args.source_col,
        output_col=args.output_col,
    )
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
    payload["input_csv"] = args.input_csv
    payload["source_col"] = args.source_col
    payload["output_col"] = args.output_col
    payload["repair_steps"] = step_summaries
    payload["evening_guard_source_col"] = PRODUCTION_BASE_COL
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
        f"evening_19_23={regimes['evening_19_23']['wmape']:.4f}%"
    )
    for step in step_summaries:
        print(f"{step['name']}_applied_rows={step['applied_rows']}")
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
