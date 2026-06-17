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


SOURCE_COL = "low_regime_roll7diff_restore_target15_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
OUTPUT_COL = "low_regime_daytime_target15_deep_pred"

PRICE_BINS = [-1, 10, 25, 50, 75, 100, 150, 250, 400, 600, 1000, 1500, 3000, 7000, 100000]
COARSE_PRICE_BINS = [-1, 10, 50, 100, 250, 500, 1000, 1500, 3000, 7000, 100000]
DIFF_BINS = [
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
RATIO_BINS = [0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1, 1.5, 2, 4, 10, 100]


DEEP_REPAIR_STEPS = [
    {
        "name": "h16_lag24_ratio_q75_w21_s100_1000_b075",
        "kind": "ratio",
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 21,
        "stat": "q75",
        "hours": [16],
        "source_min": 100.0,
        "source_max": 1000.0,
        "strength": 0.75,
    },
    {
        "name": "h10_srcroll7_ratio_q25_w1_s500_1500_b100",
        "kind": "ratio",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 1,
        "stat": "q25",
        "hours": [10],
        "source_min": 500.0,
        "source_max": 1500.0,
        "strength": 1.0,
    },
    {
        "name": "h10_16_srcroll7_ratio_mean_w3_s100_250_b100",
        "kind": "ratio",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 3,
        "stat": "mean",
        "hours": [10, 11, 12, 13, 14, 15, 16],
        "source_min": 100.0,
        "source_max": 250.0,
        "strength": 1.0,
    },
    {
        "name": "h12_lag168_resid_q25_w5_s250_600_bn125",
        "kind": "resid",
        "group_keys": ["hour", "lag168_bin"],
        "rolling_rows": 5,
        "stat": "q25",
        "hours": [12],
        "source_min": 250.0,
        "source_max": 600.0,
        "strength": -1.25,
    },
    {
        "name": "h15_16_roll7_resid_q75_w5_s10_250_bn100",
        "kind": "resid",
        "group_keys": ["hour", "roll7_bin"],
        "rolling_rows": 5,
        "stat": "q75",
        "hours": [15, 16],
        "source_min": 10.0,
        "source_max": 250.0,
        "strength": -1.0,
    },
    {
        "name": "h10_lag24_resid_q25_w3_s250_1000_b075",
        "kind": "resid",
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 3,
        "stat": "q25",
        "hours": [10],
        "source_min": 250.0,
        "source_max": 1000.0,
        "strength": 0.75,
    },
    {
        "name": "h16_rollmin_resid_mean_w13_s10_500_bn100",
        "kind": "resid",
        "group_keys": ["hour", "rollmin_bin"],
        "rolling_rows": 13,
        "stat": "mean",
        "hours": [16],
        "source_min": 10.0,
        "source_max": 500.0,
        "strength": -1.0,
    },
    {
        "name": "h15_srclag24_resid_median_w21_s10_500_b075",
        "kind": "resid",
        "group_keys": ["hour", "src_lag24_diff_bin"],
        "rolling_rows": 21,
        "stat": "median",
        "hours": [15],
        "source_min": 10.0,
        "source_max": 500.0,
        "strength": 0.75,
    },
    {
        "name": "h12_13_roll14_resid_median_w13_s500_1500_bn125",
        "kind": "resid",
        "group_keys": ["hour", "roll14_bin"],
        "rolling_rows": 13,
        "stat": "median",
        "hours": [12, 13],
        "source_min": 500.0,
        "source_max": 1500.0,
        "strength": -1.25,
    },
    {
        "name": "h10_16_lag24_ratio_q25_w8_s500_1500_b025",
        "kind": "ratio",
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 8,
        "stat": "q25",
        "hours": [10, 11, 12, 13, 14, 15, 16],
        "source_min": 500.0,
        "source_max": 1500.0,
        "strength": 0.25,
    },
    {
        "name": "h13_15_srcroll3_resid_q25_w5_s50_250_bn075",
        "kind": "resid",
        "group_keys": ["hour", "src_roll3_diff_bin"],
        "rolling_rows": 5,
        "stat": "q25",
        "hours": [13, 14, 15],
        "source_min": 50.0,
        "source_max": 250.0,
        "strength": -0.75,
    },
    {
        "name": "h12_samehour_resid_q75_w3_s500_1500_bn025",
        "kind": "resid",
        "group_keys": ["hour"],
        "rolling_rows": 3,
        "stat": "q75",
        "hours": [12],
        "source_min": 500.0,
        "source_max": 1500.0,
        "strength": -0.25,
    },
    {
        "name": "h11_analog_polish_s50_250",
        "kind": "candidate",
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "hours": [11],
        "source_min": 50.0,
        "source_max": 250.0,
        "alpha": 1.0,
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


def _cut(values, bins):
    return pd.cut(values, bins, labels=False, include_lowest=True).astype("float64")


def _field_frame(frame, source):
    rolling_mean_3d = pd.to_numeric(frame["f_rolling_mean_hour_3d"], errors="coerce").to_numpy(dtype="float64")
    rolling_mean_7d = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")
    rolling_mean_14d = pd.to_numeric(frame["f_rolling_mean_hour_14d"], errors="coerce").to_numpy(dtype="float64")
    rolling_min_24 = pd.to_numeric(frame["f_rolling_min_24"], errors="coerce").to_numpy(dtype="float64")
    lag24 = pd.to_numeric(frame["f_price_lag_24"], errors="coerce").to_numpy(dtype="float64")
    lag168 = pd.to_numeric(frame["f_price_lag_168"], errors="coerce").to_numpy(dtype="float64")

    fields = pd.DataFrame(index=frame.index)
    fields["hour"] = frame["datetime"].dt.hour.astype("int64")
    fields["source_bin"] = _cut(source, COARSE_PRICE_BINS)
    fields["fine_source_bin"] = _cut(source, PRICE_BINS)
    fields["roll3_bin"] = _cut(rolling_mean_3d, COARSE_PRICE_BINS)
    fields["roll7_bin"] = _cut(rolling_mean_7d, COARSE_PRICE_BINS)
    fields["roll14_bin"] = _cut(rolling_mean_14d, COARSE_PRICE_BINS)
    fields["rollmin_bin"] = _cut(rolling_min_24, COARSE_PRICE_BINS)
    fields["lag24_bin"] = _cut(lag24, COARSE_PRICE_BINS)
    fields["lag168_bin"] = _cut(lag168, COARSE_PRICE_BINS)
    fields["src_roll3_diff_bin"] = _cut(source - rolling_mean_3d, DIFF_BINS)
    fields["src_roll7_diff_bin"] = _cut(source - rolling_mean_7d, DIFF_BINS)
    fields["src_lag24_diff_bin"] = _cut(source - lag24, DIFF_BINS)
    fields["source_roll7_ratio_bin"] = _cut(np.maximum(source, 10.0) / np.maximum(rolling_mean_7d, 10.0), RATIO_BINS)
    return fields


def _step_mask(frame, source, step):
    selected = frame["datetime"].dt.hour.isin(step["hours"]).to_numpy()
    if "source_min" in step:
        selected &= source >= float(step["source_min"])
    if "source_max" in step:
        selected &= source < float(step["source_max"])
    return selected


def _apply_shifted_step(frame, source, step):
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    fields = _field_frame(frame, source)
    groups = [fields[key] for key in step["group_keys"]]

    if step["kind"] == "resid":
        values = actual - source
    elif step["kind"] == "ratio":
        values = np.maximum(actual, 10.0) / np.maximum(source, 10.0)
    else:
        raise ValueError(f"Unsupported shifted step kind: {step['kind']}")

    signal = _rolling_signal(values, groups, step["rolling_rows"], step["stat"])
    selected = _step_mask(frame, source, step) & np.isfinite(signal)

    if step["kind"] == "resid":
        candidate = source + float(step["strength"]) * signal
    else:
        ratio_signal = np.clip(signal, 0.0, 4.0)
        candidate = source * ((1.0 - float(step["strength"])) + float(step["strength"]) * ratio_signal)

    repaired = source.copy()
    clipped_candidate = clip_price_forecast(candidate, cap)
    repaired[selected] = clipped_candidate[selected]
    return clip_price_forecast(repaired, cap), signal, selected


def _apply_candidate_step(frame, source, step):
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    candidate = clip_price_forecast(
        pd.to_numeric(frame[step["candidate_col"]], errors="coerce").to_numpy(dtype="float64"),
        cap,
    )
    selected = _step_mask(frame, source, step) & np.isfinite(candidate)
    blended = (1.0 - float(step["alpha"])) * source + float(step["alpha"]) * candidate

    repaired = source.copy()
    clipped_candidate = clip_price_forecast(blended, cap)
    repaired[selected] = clipped_candidate[selected]
    return clip_price_forecast(repaired, cap), candidate, selected


def build_daytime_deep_repair(predictions, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    required = {
        "datetime",
        "actual",
        "price_cap",
        source_col,
        PRODUCTION_BASE_COL,
        "f_price_lag_24",
        "f_price_lag_168",
        "f_rolling_mean_hour_3d",
        "f_rolling_mean_hour_7d",
        "f_rolling_mean_hour_14d",
        "f_rolling_min_24",
    }
    for step in DEEP_REPAIR_STEPS:
        if step["kind"] == "candidate":
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
    source = clip_price_forecast(pd.to_numeric(frame[source_col], errors="coerce"), cap)
    step_summaries = []

    for step in DEEP_REPAIR_STEPS:
        if step["kind"] == "candidate":
            source, signal, selected = _apply_candidate_step(frame, source, step)
        else:
            source, signal, selected = _apply_shifted_step(frame, source, step)
        frame[f"{output_col}_{step['name']}_signal"] = signal
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        step_summaries.append({**step, "applied_rows": int(selected.sum())})

    evening = frame["datetime"].dt.hour.between(19, 23).to_numpy()
    source[evening] = pd.to_numeric(frame.loc[evening, PRODUCTION_BASE_COL], errors="coerce")
    frame[output_col] = clip_price_forecast(source, cap)
    frame[f"{output_col}_used_base_evening"] = evening.astype("int64")
    return frame, step_summaries


def main():
    parser = argparse.ArgumentParser(description="Build deeper daytime low-regime repair for the target15 track.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_low_regime_roll7diff_restore_target15_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_daytime_target15_deep_v1")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    repaired, step_summaries = build_daytime_deep_repair(
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
    payload["deep_repair_steps"] = step_summaries
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
