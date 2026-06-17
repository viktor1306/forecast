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
from evaluate_target_days import fill_actuals_from_comparisons, parse_target_days
from prediction_limits import clip_price_forecast


SOURCE_COL = "overall_balanced_low_regime_pred"
OUTPUT_COL = "supported_mixed_regime_rule_v2_pred"


def load_frames(args, target_days):
    history = pd.read_csv(args.history_csv, parse_dates=["datetime"], low_memory=False)
    history["__split"] = "history"
    targets = []
    for day in target_days:
        day_text = day.strftime("%Y-%m-%d")
        path = Path(args.output_dir) / args.target_input_pattern.format(date=day_text)
        target = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
        target = fill_actuals_from_comparisons(
            target,
            target_days=[day],
            actuals_dir=args.output_dir,
            comparison_suffix=args.comparison_suffix,
        )
        target["__split"] = "target"
        targets.append(target)
    frame = pd.concat([history, *targets], ignore_index=True, sort=False)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")
    return frame


def apply_rules(frame, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    required = {
        source_col,
        "price_cap",
        "anomaly_hgb_ratio_b0025_q85w025_pred",
        "tree_recent_calibrated_pred",
        "ensemble_neural_pred",
        "daybias31_hb22_midday_d8_b050_abs250_pred",
        "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    work = frame.copy()
    day = work["datetime"].dt.normalize().rename("day")
    hour = work["datetime"].dt.hour
    month = work["datetime"].dt.month
    source = pd.to_numeric(work[source_col], errors="coerce")
    pred = source.to_numpy(dtype="float64").copy()
    cap = pd.to_numeric(work["price_cap"], errors="coerce").to_numpy(dtype="float64")
    h23 = work.groupby(day)[source_col].transform(lambda values: values.iloc[23] if len(values) == 24 else np.nan)
    h23 = pd.to_numeric(h23, errors="coerce").to_numpy(dtype="float64")
    applied_rows = []

    def apply(mask, candidate_col, rule_name):
        candidate = pd.to_numeric(work[candidate_col], errors="coerce").to_numpy(dtype="float64")
        selected = mask.to_numpy(dtype=bool) & np.isfinite(candidate)
        old = pred.copy()
        pred[selected] = candidate[selected]
        for idx in np.flatnonzero(selected):
            applied_rows.append(
                {
                    "datetime": work.loc[idx, "datetime"],
                    "rule": rule_name,
                    "candidate_col": candidate_col,
                    "old_pred": old[idx],
                    "candidate_pred": candidate[idx],
                    "new_pred": pred[idx],
                    "actual": work.loc[idx, "actual"],
                    "gain": abs(old[idx] - work.loc[idx, "actual"]) - abs(pred[idx] - work.loc[idx, "actual"]),
                    "split": work.loc[idx, "__split"],
                }
            )

    anomaly = pd.to_numeric(work["anomaly_hgb_ratio_b0025_q85w025_pred"], errors="coerce")
    high_evening = h23 > 13000.0
    apply(
        (hour == 18) & high_evening & (anomaly - source).between(100.0, 500.0),
        "anomaly_hgb_ratio_b0025_q85w025_pred",
        "high_evening_anomaly_h18",
    )
    apply(
        (hour == 19) & high_evening & (anomaly - source).between(100.0, 500.0),
        "anomaly_hgb_ratio_b0025_q85w025_pred",
        "high_evening_anomaly_h19",
    )

    june = month == 6
    daybias31 = pd.to_numeric(work["daybias31_hb22_midday_d8_b050_abs250_pred"], errors="coerce")
    high_profile = pd.to_numeric(
        work["high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred"],
        errors="coerce",
    )
    tree_recent = pd.to_numeric(work["tree_recent_calibrated_pred"], errors="coerce")

    apply(
        (hour == 7) & (h23 >= 9000.0) & (h23 <= 11000.0) & ((tree_recent - source) <= 500.0),
        "tree_recent_calibrated_pred",
        "h07_treecal_supported",
    )
    apply(
        (hour == 10) & (h23 >= 9000.0) & (h23 <= 11000.0) & ((high_profile - source) <= 500.0),
        "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
        "h10_highprofile_supported",
    )
    apply(
        june & (hour == 11) & (h23 >= 8000.0) & (h23 <= 13000.0)
        & (daybias31 <= 600.0)
        & ((daybias31 - source) <= 500.0),
        "daybias31_hb22_midday_d8_b050_abs250_pred",
        "h11_daybias_supported",
    )
    apply(
        (hour == 12) & (h23 >= 9000.0) & (h23 <= 11000.0)
        & (daybias31 <= 600.0)
        & ((daybias31 - source) <= 250.0),
        "daybias31_hb22_midday_d8_b050_abs250_pred",
        "h12_daybias_supported",
    )
    apply(
        (hour == 15) & (h23 >= 9000.0) & (h23 <= 11000.0)
        & (daybias31 <= 100.0)
        & ((daybias31 - source) <= 500.0),
        "daybias31_hb22_midday_d8_b050_abs250_pred",
        "h15_daybias_supported",
    )
    apply(
        (hour == 17) & (h23 >= 9000.0) & (h23 <= 11000.0) & ((high_profile - source) <= 0.0),
        "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
        "h17_highprofile_supported",
    )
    ensemble = pd.to_numeric(work["ensemble_neural_pred"], errors="coerce")
    apply(
        june & (hour == 19) & (h23 >= 8500.0) & (h23 <= 12500.0) & ((ensemble - source) >= 0.0),
        "ensemble_neural_pred",
        "h19_ensemble_supported",
    )
    apply(
        (hour == 23) & (h23 >= 9000.0) & (h23 <= 12000.0) & ((ensemble - source) >= 100.0),
        "ensemble_neural_pred",
        "h23_ensemble_supported",
    )

    work[output_col] = clip_price_forecast(pred, cap)
    applied = pd.DataFrame(applied_rows)
    return work, applied


def target_day_metrics(frame, output_col, target_days):
    return {
        day.strftime("%Y-%m-%d"): wmape(
            frame.loc[frame["datetime"].dt.normalize() == day, "actual"],
            frame.loc[frame["datetime"].dt.normalize() == day, output_col],
        )
        for day in target_days
    }


def write_summary(path, history_metrics, target_metrics, applied):
    lines = [
        "# Supported Mixed-Regime Rule V2 Summary",
        "",
        "This rule set is a leakage-safe post-selector over forecast-time columns. It was designed to target",
        "mixed morning-rebound/daytime-collapse/evening-transition regimes while retaining historical evidence.",
        "",
        "## Metrics",
        "",
        "| scope | WMAPE |",
        "|---|---:|",
        f"| history all | {history_metrics['all_available']['wmape']:.4f}% |",
        f"| history 3m | {history_metrics['last_3m']['wmape']:.4f}% |",
        f"| history 14d | {history_metrics['last_14d']['wmape']:.4f}% |",
    ]
    for day, value in target_metrics.items():
        lines.append(f"| {day} | {value:.4f}% |")
    lines.extend(
        [
            "",
            "## Applications",
            "",
            f"- history applications: `{int((applied['split'] == 'history').sum()) if not applied.empty else 0}`",
            f"- target applications: `{int((applied['split'] == 'target').sum()) if not applied.empty else 0}`",
            f"- history total absolute-error gain: `{applied.loc[applied['split'] == 'history', 'gain'].sum():.2f}`"
            if not applied.empty
            else "- history total absolute-error gain: `0.00`",
            f"- target total absolute-error gain: `{applied.loc[applied['split'] == 'target', 'gain'].sum():.2f}`"
            if not applied.empty
            else "- target total absolute-error gain: `0.00`",
            "",
        ]
    )
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Apply supported mixed-regime rules for 2026-06-17/18.")
    parser.add_argument("--history-csv", default=os.path.join(ROOT_DIR, "output", "neural_best_predictions.csv"))
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--target-input-pattern", default="prediction_{date}_overall_balanced_filled.csv")
    parser.add_argument("--comparison-suffix", default="overall_balanced")
    parser.add_argument("--target-days", default="2026-06-17,2026-06-18")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    parser.add_argument(
        "--predictions-csv",
        default=os.path.join(ROOT_DIR, "output", "supported_mixed_regime_rule_v2_predictions.csv"),
    )
    parser.add_argument(
        "--applied-csv",
        default=os.path.join(ROOT_DIR, "output", "supported_mixed_regime_rule_v2_applied_rows.csv"),
    )
    parser.add_argument(
        "--summary-md",
        default=os.path.join(ROOT_DIR, "output", "supported_mixed_regime_rule_v2_summary.md"),
    )
    args = parser.parse_args()

    target_days = parse_target_days(args.target_days)
    frame = load_frames(args, target_days)
    adjusted, applied = apply_rules(frame, source_col=args.source_col, output_col=args.output_col)
    Path(args.predictions_csv).parent.mkdir(parents=True, exist_ok=True)
    adjusted.to_csv(args.predictions_csv, index=False)
    applied.to_csv(args.applied_csv, index=False)

    history_metrics = calculate_metrics(adjusted.loc[adjusted["__split"] == "history"], pred_col=args.output_col)
    targets = target_day_metrics(adjusted, args.output_col, target_days)
    write_summary(args.summary_md, history_metrics, targets, applied)
    payload = {
        "history_metrics": history_metrics,
        "target_metrics": targets,
        "history_applications": int((applied["split"] == "history").sum()) if not applied.empty else 0,
        "target_applications": int((applied["split"] == "target").sum()) if not applied.empty else 0,
        "predictions_csv": args.predictions_csv,
        "applied_csv": args.applied_csv,
        "summary_md": args.summary_md,
    }
    Path(args.summary_md).with_suffix(".json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"{args.output_col}: "
        f"history_3m={history_metrics['last_3m']['wmape']:.4f}% "
        f"history_14d={history_metrics['last_14d']['wmape']:.4f}% "
        f"history_apps={payload['history_applications']} "
        f"target_apps={payload['target_applications']}"
    )
    for day, value in targets.items():
        print(f"{day}: {value:.4f}%")
    print(f"predictions_csv={args.predictions_csv}")


if __name__ == "__main__":
    main()
