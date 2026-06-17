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


BASE_COL = "night_hourratio_final_under5_pred"
DAY_REPAIR_COL = "low_regime_postdeep_selector_target15_pred"
OUTPUT_COL = "overall_balanced_low_regime_pred"

FIXED_HOUR_RESTORES = [
    {"hour": 0, "candidate_col": "day14_16_ratio_lowrepair_after_morning_pred"},
    {"hour": 1, "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred"},
    {"hour": 2, "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred"},
    {"hour": 5, "candidate_col": "morning7_10_hourratio_final_push_pred"},
    {"hour": 6, "candidate_col": "morning7_10_hourratio_final_push_pred"},
    {"hour": 9, "candidate_col": "morning7_10_ratio_absbias_after_summer_repair_pred"},
    {"hour": 17, "candidate_col": "hour13_wmape12_bias_after_spike_pred"},
    {"hour": 18, "candidate_col": "candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred"},
    {"hour": 19, "candidate_col": "day13_16_anchor_lowrepair_after_night_pred"},
]

DIFF_BINS = [
    -100000,
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
    100000,
]

SHIFTED_REPAIRS = [
    {
        "name": "h12_src_lag24_resid_q25_w8_b025",
        "kind": "resid",
        "hours": [12],
        "group_keys": ["hour", "src_lag24_diff_bin"],
        "rolling_rows": 8,
        "stat": "q25",
        "strength": 0.25,
    },
    {
        "name": "h15_lag24_roll7_ratio_median_w5_b025",
        "kind": "ratio",
        "hours": [15],
        "group_keys": ["hour", "lag24_roll7_diff_bin"],
        "rolling_rows": 5,
        "stat": "median",
        "strength": 0.25,
    },
]


def _cut(values, bins):
    return np.asarray(pd.cut(values, bins, labels=False, include_lowest=True).astype("float64"))


def _field_frame(frame, source):
    lag24 = pd.to_numeric(frame["f_price_lag_24"], errors="coerce").to_numpy(dtype="float64")
    roll7 = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")
    return {
        "hour": frame["datetime"].dt.hour.to_numpy(dtype="int64"),
        "src_lag24_diff_bin": _cut(source - lag24, DIFF_BINS),
        "lag24_roll7_diff_bin": _cut(lag24 - roll7, DIFF_BINS),
    }


def _shifted_stat_signal(values, groups, rolling_rows, stat):
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


def _apply_shifted_repair(frame, source, step):
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    fields = _field_frame(frame, source)
    groups = [pd.Series(fields[key], index=frame.index) for key in step["group_keys"]]

    if step["kind"] == "resid":
        values = actual - source
    elif step["kind"] == "ratio":
        values = np.maximum(actual, 10.0) / np.maximum(source, 10.0)
    else:
        raise ValueError(f"Unsupported shifted repair kind: {step['kind']}")

    signal = _shifted_stat_signal(values, groups, step["rolling_rows"], step["stat"])
    selected = np.isin(hour, step["hours"]) & np.isfinite(signal)

    if step["kind"] == "resid":
        candidate = source + float(step["strength"]) * signal
    else:
        ratio_signal = np.clip(signal, 0.0, 4.0)
        candidate = source * ((1.0 - float(step["strength"])) + float(step["strength"]) * ratio_signal)

    repaired = source.copy()
    clipped_candidate = clip_price_forecast(candidate, cap)
    repaired[selected] = clipped_candidate[selected]
    return clip_price_forecast(repaired, cap), signal, selected


def _hourly_error_frame(frame, pred_col):
    rows = []
    for hour, group in frame.groupby(frame["datetime"].dt.hour):
        actual = group["actual"].astype("float64")
        pred = group[pred_col].astype("float64")
        error = pred - actual
        denom = actual.abs().sum()
        wmape = np.nan if denom <= 0 else error.abs().sum() / denom * 100.0
        target_floor = int(np.floor(wmape / 5.0) * 5) if np.isfinite(wmape) else None
        rows.append(
            {
                "hour": int(hour),
                "n": int(len(group)),
                "wmape": float(wmape),
                "mae": float(error.abs().mean()),
                "bias": float(error.mean()),
                "target_floor": target_floor,
                "target_label": "<5" if wmape < 5.0 else f"{target_floor}",
            }
        )
    return pd.DataFrame(rows).sort_values("hour")


def build_overall_balanced(predictions, output_col=OUTPUT_COL):
    required = {
        "datetime",
        "actual",
        "price_cap",
        "f_price_lag_24",
        BASE_COL,
        DAY_REPAIR_COL,
        "f_rolling_mean_hour_7d",
        *(step["candidate_col"] for step in FIXED_HOUR_RESTORES),
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
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    source = pd.to_numeric(frame[BASE_COL], errors="coerce").to_numpy(dtype="float64").copy()
    day_mask = (hour >= 10) & (hour <= 16)
    source[day_mask] = pd.to_numeric(frame.loc[day_mask, DAY_REPAIR_COL], errors="coerce")
    source = clip_price_forecast(source, cap)
    frame[f"{output_col}_used_day_repair"] = day_mask.astype("int64")

    fixed_summaries = []
    for step in FIXED_HOUR_RESTORES:
        selected = hour == int(step["hour"])
        candidate = pd.to_numeric(frame.loc[selected, step["candidate_col"]], errors="coerce")
        source[selected] = candidate.to_numpy(dtype="float64")
        frame[f"{output_col}_fixed_h{int(step['hour']):02d}_candidate"] = np.where(
            selected,
            step["candidate_col"],
            "",
        )
        fixed_summaries.append({**step, "applied_rows": int(selected.sum())})
    source = clip_price_forecast(source, cap)

    shifted_summaries = []
    for step in SHIFTED_REPAIRS:
        source, signal, selected = _apply_shifted_repair(frame, source, step)
        frame[f"{output_col}_{step['name']}_signal"] = signal
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        shifted_summaries.append({**step, "applied_rows": int(selected.sum())})

    frame[output_col] = source
    return frame, fixed_summaries, shifted_summaries


def main():
    parser = argparse.ArgumentParser(description="Build overall-balanced low-regime composite artifact.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(
            ROOT_DIR,
            "output",
            "neural_experiment_low_regime_postdeep_selector_target15_v1_predictions.csv",
        ),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="overall_balanced_low_regime_v1")
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    selected, fixed_summaries, shifted_summaries = build_overall_balanced(predictions, output_col=args.output_col)
    artifacts = save_evaluation_artifacts(
        selected,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )

    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = {
        col: calculate_metrics(selected, pred_col=col)
        for col in [BASE_COL, DAY_REPAIR_COL, args.output_col]
        if col in selected.columns
    }
    payload["input_csv"] = args.input_csv
    payload["output_col"] = args.output_col
    payload["base_col"] = BASE_COL
    payload["day_repair_col"] = DAY_REPAIR_COL
    payload["day_repair_hours"] = list(range(10, 17))
    payload["fixed_hour_restores"] = fixed_summaries
    payload["shifted_repairs"] = shifted_summaries

    hourly = _hourly_error_frame(selected, args.output_col)
    hourly_path = Path(args.output_dir) / f"neural_experiment_{args.experiment_id}_hourly.csv"
    hourly.to_csv(hourly_path, index=False)
    payload["hourly_csv"] = os.fspath(hourly_path)
    payload["hourly_target_groups"] = {
        str(label): [int(hour) for hour in group["hour"]]
        for label, group in hourly.groupby("target_label", sort=False)
    }

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
    print(f"day_repair_rows={int(selected[f'{args.output_col}_used_day_repair'].sum())}")
    for step in fixed_summaries:
        print(f"fixed_h{int(step['hour']):02d}_rows={step['applied_rows']}")
    for step in shifted_summaries:
        print(f"{step['name']}_rows={step['applied_rows']}")
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"hourly_csv={hourly_path}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
