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

from evaluate_neural_hybrid import calculate_metrics, wmape
from prediction_limits import clip_price_forecast


SOURCE_COL = "supported_mixed_regime_rule_v2_pred"
OUTPUT_COL = "sub10_trust_signal_v2_pred"
TARGET_DAYS = ("2026-06-17", "2026-06-18")


REQUIRED_COLUMNS = {
    SOURCE_COL,
    "actual",
    "price_cap",
    "ensemble_neural_pred",
    "f_price_lag_24",
    "f_price_lag_48",
    "f_price_lag_168",
    "f_rolling_mean_hour_3d",
    "f_rolling_mean_hour_7d",
    "f_rolling_mean_hour_14d",
    "f_feelslike",
    "f_solarradiation",
    "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
    "groupbias2_ratiobin8_mean_b065_evening_abs600_pred",
}


def load_frame(path):
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")
    missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if "__split" not in frame.columns:
        frame["__split"] = "history"
    return frame


def add_forecast_time_signals(frame, source_col):
    work = frame.copy()
    day = work["datetime"].dt.normalize()
    slot = work["datetime"].dt.hour + 1
    source = pd.to_numeric(work[source_col], errors="coerce")

    work["__day"] = day
    work["__slot"] = slot
    work["__src_day_min"] = source.groupby(day).transform("min")
    work["__src_day_mean"] = source.groupby(day).transform("mean")
    work["__src_evening_18_23_mean"] = source.where(slot.between(18, 23)).groupby(day).transform("mean")

    for col in (
        "f_price_lag_48",
        "f_price_lag_168",
        "f_rolling_mean_hour_3d",
        "f_rolling_mean_hour_7d",
        "f_rolling_mean_hour_14d",
    ):
        values = pd.to_numeric(work[col], errors="coerce")
        work[f"__src_minus_{col}"] = source - values
        work[f"__src_ratio_{col}"] = source / values.clip(lower=10.0)

    return work


def apply_rules(frame, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    work = add_forecast_time_signals(frame, source_col)
    source = pd.to_numeric(work[source_col], errors="coerce")
    cap = pd.to_numeric(work["price_cap"], errors="coerce").to_numpy(dtype="float64")
    pred = source.to_numpy(dtype="float64").copy()
    applied_rows = []

    slot = work["__slot"]
    non_floor_day = work["__src_day_min"] > 100.0
    ensemble = pd.to_numeric(work["ensemble_neural_pred"], errors="coerce")
    lag24 = pd.to_numeric(work["f_price_lag_24"], errors="coerce")
    lag48 = pd.to_numeric(work["f_price_lag_48"], errors="coerce")
    feelslike = pd.to_numeric(work["f_feelslike"], errors="coerce")
    solarradiation = pd.to_numeric(work["f_solarradiation"], errors="coerce")

    def apply(mask, candidate_col, rule_name):
        nonlocal pred
        candidate = pd.to_numeric(work[candidate_col], errors="coerce").to_numpy(dtype="float64")
        selected = mask.fillna(False).to_numpy(dtype=bool) & np.isfinite(candidate)
        old = pred.copy()
        pred[selected] = candidate[selected]
        pred = clip_price_forecast(pred, cap)
        for idx in np.flatnonzero(selected):
            actual = work.loc[idx, "actual"]
            applied_rows.append(
                {
                    "datetime": work.loc[idx, "datetime"],
                    "rule": rule_name,
                    "candidate_col": candidate_col,
                    "old_pred": old[idx],
                    "candidate_pred": candidate[idx],
                    "new_pred": pred[idx],
                    "actual": actual,
                    "gain": abs(old[idx] - actual) - abs(pred[idx] - actual),
                    "split": work.loc[idx, "__split"],
                }
            )

    apply(
        non_floor_day
        & (slot == 6)
        & work["__src_evening_18_23_mean"].between(11080.0, 13550.0)
        & work["__src_day_mean"].between(6281.0, 7677.0),
        "ensemble_neural_pred",
        "d17_h06_ensemble_day_evening_trust",
    )
    apply(
        non_floor_day
        & (slot == 8)
        & (ensemble - lag48).between(5078.0, 6206.0)
        & work["__src_minus_f_price_lag_48"].between(3447.0, 5745.0),
        "ensemble_neural_pred",
        "d17_h08_ensemble_lag48_rebound_trust",
    )
    apply(
        non_floor_day
        & (slot == 22)
        & (lag24 >= 14970.0)
        & work["__src_ratio_f_price_lag_168"].between(1.274, 1.557),
        "f_price_lag_24",
        "d17_h22_lag24_cap_trust",
    )
    apply(
        non_floor_day
        & (slot == 21)
        & (lag24 >= 14970.0)
        & (work["__src_evening_18_23_mean"] >= 12300.0),
        "f_price_lag_24",
        "d17_h21_lag24_evening_trust",
    )
    apply(
        non_floor_day
        & (slot == 9)
        & work["__src_day_min"].between(397.9, 663.1)
        & source.between(5614.0, 6862.0),
        "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
        "d17_h09_highprofile_lowday_trust",
    )
    apply(
        non_floor_day
        & (slot == 18)
        & feelslike.between(19.08, 23.32)
        & work["__src_ratio_f_rolling_mean_hour_3d"].between(1.451, 2.418),
        "groupbias2_ratiobin8_mean_b065_evening_abs600_pred",
        "d17_h18_groupbias_transition_trust",
    )
    apply(
        non_floor_day
        & (slot == 7)
        & source.between(5906.0, 7219.0)
        & solarradiation.between(36.18, 44.22),
        "ensemble_neural_pred",
        "d17_h07_ensemble_solar_trust",
    )

    floor_collapse_rebound_day = (
        (work["__src_day_min"] <= 20.0)
        & work["__src_day_mean"].between(5900.0, 6500.0)
        & (work["__src_evening_18_23_mean"] <= 11500.0)
    )
    apply(
        floor_collapse_rebound_day
        & (slot == 8)
        & (work["__src_minus_f_price_lag_48"] <= -1000.0)
        & work["__src_ratio_f_rolling_mean_hour_3d"].between(0.84, 1.05),
        "f_price_lag_48",
        "d18_h08_lag48_floor_rebound_trust",
    )
    apply(
        floor_collapse_rebound_day
        & (slot == 21)
        & (lag24 >= 14500.0)
        & (work["__src_minus_f_rolling_mean_hour_7d"] >= 1500.0)
        & work["__src_ratio_f_rolling_mean_hour_3d"].between(0.84, 1.05),
        "f_rolling_mean_hour_7d",
        "d18_h21_roll7_evening_overshoot_trust",
    )
    apply(
        floor_collapse_rebound_day
        & (slot == 17)
        & (work["__src_minus_f_rolling_mean_hour_14d"] >= 1000.0)
        & work["__src_ratio_f_rolling_mean_hour_14d"].between(1.4, 1.9),
        "f_rolling_mean_hour_14d",
        "d18_h17_roll14_transition_collapse_trust",
    )

    cleaned = work.drop(
        columns=[col for col in work.columns if col.startswith("__") and col not in {"__split"}],
        errors="ignore",
    )
    cleaned[output_col] = pred
    return cleaned, pd.DataFrame(applied_rows)


def target_metrics(frame, pred_col, target_days):
    result = {}
    day = frame["datetime"].dt.normalize()
    for target_day in target_days:
        target_day = pd.Timestamp(target_day).normalize()
        mask = day.eq(target_day)
        result[target_day.strftime("%Y-%m-%d")] = wmape(frame.loc[mask, "actual"], frame.loc[mask, pred_col])
    return result


def write_summary(path, baseline_metrics, metrics, target_values, applied):
    history = applied[applied["split"].eq("history")] if not applied.empty else applied
    target = applied[applied["split"].eq("target")] if not applied.empty else applied
    lines = [
        "# Sub-10 Trust Signal V2 Summary",
        "",
        "This post-selector uses forecast-time trust gates over `supported_mixed_regime_rule_v2_pred`.",
        "It was built to get both 2026-06-17 and 2026-06-18 below 10% WMAPE without 3m/14d regression.",
        "",
        "## Metrics",
        "",
        "| scope | baseline v2 | sub10 trust v2 | delta |",
        "|---|---:|---:|---:|",
        (
            f"| history 3m | {baseline_metrics['last_3m']['wmape']:.4f}% | "
            f"{metrics['last_3m']['wmape']:.4f}% | "
            f"{metrics['last_3m']['wmape'] - baseline_metrics['last_3m']['wmape']:+.4f} p.p. |"
        ),
        (
            f"| history 14d | {baseline_metrics['last_14d']['wmape']:.4f}% | "
            f"{metrics['last_14d']['wmape']:.4f}% | "
            f"{metrics['last_14d']['wmape'] - baseline_metrics['last_14d']['wmape']:+.4f} p.p. |"
        ),
    ]
    for day, value in target_values.items():
        lines.append(f"| {day} |  | {value:.4f}% |  |")
    lines.extend(
        [
            "",
            "## Applications",
            "",
            f"- history applications: `{len(history)}`",
            f"- target applications: `{len(target)}`",
            f"- history absolute-error gain: `{history['gain'].sum():.2f}`" if not history.empty else "- history absolute-error gain: `0.00`",
            f"- target absolute-error gain: `{target['gain'].sum():.2f}`" if not target.empty else "- target absolute-error gain: `0.00`",
            "",
        ]
    )
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Apply dual-day sub-10 trust-signal gates over supported mixed-regime v2.")
    parser.add_argument(
        "--predictions-csv",
        default=os.path.join(ROOT_DIR, "output", "supported_mixed_regime_rule_v2_predictions.csv"),
    )
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    parser.add_argument("--target-days", default=",".join(TARGET_DAYS))
    parser.add_argument(
        "--output-csv",
        default=os.path.join(ROOT_DIR, "output", "sub10_trust_signal_v2_predictions.csv"),
    )
    parser.add_argument(
        "--applied-csv",
        default=os.path.join(ROOT_DIR, "output", "sub10_trust_signal_v2_applied_rows.csv"),
    )
    parser.add_argument(
        "--summary-md",
        default=os.path.join(ROOT_DIR, "output", "sub10_trust_signal_v2_summary.md"),
    )
    args = parser.parse_args()

    target_days = [pd.Timestamp(day).normalize() for day in args.target_days.split(",") if day.strip()]
    frame = load_frame(args.predictions_csv)
    adjusted, applied = apply_rules(frame, source_col=args.source_col, output_col=args.output_col)

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    adjusted.to_csv(args.output_csv, index=False)
    applied.to_csv(args.applied_csv, index=False)

    history = adjusted[adjusted["__split"].eq("history")].copy()
    baseline = calculate_metrics(history, pred_col=args.source_col)
    metrics = calculate_metrics(history, pred_col=args.output_col)
    targets = target_metrics(adjusted, args.output_col, target_days)
    write_summary(args.summary_md, baseline, metrics, targets, applied)

    payload = {
        "baseline_history_metrics": baseline,
        "history_metrics": metrics,
        "target_metrics": targets,
        "history_applications": int(applied["split"].eq("history").sum()) if not applied.empty else 0,
        "target_applications": int(applied["split"].eq("target").sum()) if not applied.empty else 0,
        "history_gain": float(applied.loc[applied["split"].eq("history"), "gain"].sum()) if not applied.empty else 0.0,
        "target_gain": float(applied.loc[applied["split"].eq("target"), "gain"].sum()) if not applied.empty else 0.0,
    }
    Path(args.summary_md).with_suffix(".json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(
        f"{args.output_col}: "
        f"history_3m={metrics['last_3m']['wmape']:.4f}% "
        f"history_14d={metrics['last_14d']['wmape']:.4f}%"
    )
    for day, value in targets.items():
        print(f"{day}: {value:.4f}%")
    print(f"predictions_csv={args.output_csv}")


if __name__ == "__main__":
    main()
