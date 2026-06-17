import argparse
import json
import os
import sys
from collections import defaultdict
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
OUTPUT_COL = "low_regime_group_selector_target15_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
EVEGUARD_OUTPUT_COL = "low_regime_group_selector_target15_eveguard_pred"

CANDIDATE_COLS = [
    BASE_COL,
    "lag24blend4_allprof_abs100_all_a100_pred",
    "lowcollapse_after_mlp_lowday_th065_pred",
    "mlp_lowday_logresid_b010_floor_pred",
    "tree_recent_calibrated_pred",
    "tree_base_pred",
    "hourbias7_mean2_bn010_peak_wmape35_pred",
    "sourcebin_daytime_bias_after_lowrepair_pred",
    "f_rolling_min_24",
    "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
    "ensemble_neural_pred",
    "f_price_lag_24",
    "hour13_wmape12_bias_after_spike_pred",
    "groupbias11_ratio2_mean_all_bn010_wmape20_pred",
    "hour5_wmape20_bias_after_morning_diffbin_pred",
    "groupbias10_ratiofine_b012_then_ratiosummer_b020_pred",
    "hourbias5_med21_b030_peak_wmape25_pred",
    "lagprofile1_db30_lag24_profabs2000_midday_a005_pred",
    "f_price_lag_168",
    "day14_16_ratio_lowrepair_after_morning_pred",
    "f_rolling_mean_hour_7d",
    "high_profile_lag168_day_down_weather_pred",
    "day13_16_ratio_wmape15_after_morning7_pred",
    "tree_recent_shiftblend_after_14d_lowday_pred",
    "hourbias4_roll14_bn010_all_wmape12_pred",
    "f_rolling_mean_hour_3d",
    "f_price_lag_48",
    "hourbias2_roll21_b010_peak_abs150_pred",
    "hourbias_roll3_bn020_day_wmape20_pred",
    "nonlinear_hgb_ratio_all_b015_pred",
    "hourbias22_hb21_peakerr_r8_bn020_wmape40_pred",
    "morning7_10_ratio_summer_repair_after_evening_pred",
    "day11_15_srcbinweekend_repair_after_morning7_pred",
    "evening19_23_hoursrcbin_after_day11_15_pred",
]

SOURCE_BINS = [-1, 50, 100, 250, 500, 1000, 1500, 2500, 5000, 100000]
LAG_BINS = [-1, 50, 100, 250, 500, 1000, 1500, 2500, 5000, 100000]


def build_selector(
    predictions,
    base_col=BASE_COL,
    output_col=OUTPUT_COL,
    source_threshold=250.0,
    min_group_count=2,
    min_ape_advantage=0.05,
    hours=range(11, 16),
):
    missing = [col for col in ("datetime", "actual", "price_cap", base_col, "f_price_lag_24") if col not in predictions.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")

    candidate_cols = []
    for col in CANDIDATE_COLS:
        if col in frame.columns and col not in candidate_cols:
            candidate_cols.append(col)
    if base_col not in candidate_cols:
        candidate_cols.insert(0, base_col)
    base_index = candidate_cols.index(base_col)

    cap = frame["price_cap"].astype("float64").to_numpy()
    actual = frame["actual"].astype("float64").to_numpy()
    base = frame[base_col].astype("float64").to_numpy()
    lag24 = frame["f_price_lag_24"].astype("float64").to_numpy()
    hour = frame["datetime"].dt.hour.to_numpy()

    candidate_matrix = np.vstack(
        [pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64") for col in candidate_cols]
    ).T
    candidate_matrix = clip_price_forecast(candidate_matrix, cap[:, None])
    candidate_ape = np.abs(actual[:, None] - candidate_matrix) / np.clip(np.abs(actual[:, None]), 1.0, None)
    candidate_ape = np.where(np.isfinite(candidate_ape), candidate_ape, 1e6)

    source_bin = np.digitize(base, SOURCE_BINS) - 1
    lag_bin = np.digitize(lag24, LAG_BINS) - 1
    keys = list(zip(hour, source_bin, lag_bin))

    score_sums = {}
    score_counts = defaultdict(int)
    selected = np.zeros(len(frame), dtype=bool)
    chosen_index = np.full(len(frame), -1, dtype=int)
    chosen_score = np.full(len(frame), np.nan, dtype="float64")
    base_score = np.full(len(frame), np.nan, dtype="float64")
    output = base.copy()
    hour_set = set(hours)

    for row_idx, key in enumerate(keys):
        if (
            hour[row_idx] in hour_set
            and base[row_idx] <= source_threshold
            and score_counts[key] >= min_group_count
        ):
            scores = score_sums[key] / score_counts[key]
            best_index = int(np.argmin(scores))
            chosen_score[row_idx] = scores[best_index]
            base_score[row_idx] = scores[base_index]
            if scores[best_index] <= scores[base_index] - min_ape_advantage:
                output[row_idx] = candidate_matrix[row_idx, best_index]
                selected[row_idx] = True
                chosen_index[row_idx] = best_index

        if key not in score_sums:
            score_sums[key] = candidate_ape[row_idx].copy()
        else:
            score_sums[key] += candidate_ape[row_idx]
        score_counts[key] += 1

    frame[output_col] = clip_price_forecast(output, cap)
    frame[f"{output_col}_applied"] = selected.astype("int64")
    frame[f"{output_col}_candidate_index"] = chosen_index
    frame[f"{output_col}_candidate"] = [
        candidate_cols[idx] if idx >= 0 else "" for idx in chosen_index
    ]
    frame[f"{output_col}_candidate_ape_signal"] = chosen_score
    frame[f"{output_col}_base_ape_signal"] = base_score
    return frame, candidate_cols


def main():
    parser = argparse.ArgumentParser(description="Build shifted low-regime candidate selector for the ~15% target track.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_night_hourratio_final_under5_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_group_selector_target15_v1")
    parser.add_argument("--eveguard-experiment-id", default="low_regime_group_selector_target15_eveguard_v1")
    parser.add_argument("--base-col", default=BASE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    parser.add_argument("--eveguard-output-col", default=EVEGUARD_OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    selected, candidate_cols = build_selector(
        predictions,
        base_col=args.base_col,
        output_col=args.output_col,
    )

    artifacts = save_evaluation_artifacts(
        selected,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )
    variant_metrics = {
        col: calculate_metrics(selected, pred_col=col)
        for col in [args.base_col, args.output_col]
        if col in selected.columns
    }

    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["selector_params"] = {
        "input_csv": args.input_csv,
        "base_col": args.base_col,
        "output_col": args.output_col,
        "candidate_cols": candidate_cols,
        "group_key": "hour,source_bin,lag24_bin",
        "hours": "11-15",
        "source_threshold": 250.0,
        "min_group_count": 2,
        "min_ape_advantage": 0.05,
        "shifted": True,
    }
    payload["selector_applied_rows"] = int(selected[f"{args.output_col}_applied"].sum())
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
        f"applied_rows={payload['selector_applied_rows']}"
    )
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")

    if PRODUCTION_BASE_COL in selected.columns:
        hour = selected["datetime"].dt.hour
        use_base_evening = hour.between(19, 23)
        selected[args.eveguard_output_col] = clip_price_forecast(
            selected[args.output_col].where(~use_base_evening, selected[PRODUCTION_BASE_COL]),
            selected["price_cap"],
        )
        selected[f"{args.eveguard_output_col}_used_base_evening"] = use_base_evening.astype("int64")
        eveguard_artifacts = save_evaluation_artifacts(
            selected,
            experiment_id=args.eveguard_experiment_id,
            output_dir=args.output_dir,
            pred_col=args.eveguard_output_col,
        )
        eveguard_metrics_path = Path(eveguard_artifacts["metrics_json"])
        with open(eveguard_metrics_path, "r", encoding="utf-8") as f:
            eveguard_payload = json.load(f)
        eveguard_payload["variant_metrics"] = {
            col: calculate_metrics(selected, pred_col=col)
            for col in [PRODUCTION_BASE_COL, args.output_col, args.eveguard_output_col]
            if col in selected.columns
        }
        eveguard_payload["evening_guard_rows"] = int(use_base_evening.sum())
        eveguard_payload["evening_guard_source_col"] = PRODUCTION_BASE_COL
        with open(eveguard_metrics_path, "w", encoding="utf-8") as f:
            json.dump(eveguard_payload, f, indent=2, ensure_ascii=False)
        eveguard_regimes = eveguard_payload["regimes"]
        print(
            f"{args.eveguard_output_col}: "
            f"3m={eveguard_payload['last_3m']['wmape']:.4f}% "
            f"14d={eveguard_payload['last_14d']['wmape']:.4f}% "
            f"13d={eveguard_payload['last_13d']['wmape']:.4f}% "
            f"summer_daytime_low={eveguard_regimes['summer_daytime_low']['wmape']:.4f}% "
            f"daytime_low_lt_1000={eveguard_regimes['daytime_low_lt_1000']['wmape']:.4f}% "
            f"cap_spike_evening={eveguard_regimes['cap_spike_evening']['wmape']:.4f}% "
            f"evening_19_23={eveguard_regimes['evening_19_23']['wmape']:.4f}%"
        )
        print(f"eveguard_predictions_csv={eveguard_artifacts['predictions_csv']}")
        print(f"eveguard_metrics_json={eveguard_artifacts['metrics_json']}")
        print(f"eveguard_plot_png={eveguard_artifacts['plot_png']}")


if __name__ == "__main__":
    main()
