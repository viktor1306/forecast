import argparse
import json
import os
import sys
from collections import Counter
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


SOURCE_COL = "low_regime_daytime_target15_deep_pred"
PRODUCTION_BASE_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
OUTPUT_COL = "low_regime_postdeep_selector_target15_pred"

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


POSTDEEP_CANDIDATE_COLS = [
    "low_regime_roll7diff_restore_target15_pred",
    "low_regime_final_restore_target15_pred",
    "low_regime_candidate_restore_target15_pred",
    "low_regime_multistage_target15_repair_pred",
    "day14_16_ratio_lowrepair_after_morning_pred",
    "low_regime_shifted_actual_repair_pred",
    "low_regime_group_selector_target15_eveguard_pred",
    "low_regime_group_selector_target15_pred",
    "sourcebin_daytime_bias_after_lowrepair_pred",
    "night_ratio_bias_after_sourcebin_daytime_pred",
    "morning7_10_summer_srcbin_bias_after_night_ratio_pred",
    "day13_16_ratio_wmape15_after_morning7_pred",
    "evening19_23_sourcebin_after_day13_16_pred",
    "morning7_10_hourweekend_after_night_sourcebin_pred",
    "night_sourcebin_bias_after_morning_long_pred",
    "morning7_10_srcbin_summer_long_after_absbias_pred",
    "morning7_10_ratio_summer_repair_after_evening_pred",
    "morning7_10_ratio_absbias_after_summer_repair_pred",
    "morning7_10_hourratio_final_push_pred",
    "night_hourratio_final_under5_pred",
    "day11_15_srcbinweekend_repair_after_morning7_pred",
    "evening19_23_hoursrcbin_after_day11_15_pred",
    "morning7_10_ratio_wmape30_after_evening_pred",
    "morning_srcbinweekend_bias_after_night_hour8_pred",
    "day14_16_hourmonth_bias_after_nightmonth_pred",
    "night_hour8_wmape12_after_day14_16_pred",
    "day13_16_anchor_lowrepair_after_night_pred",
    "night_hourmonth_bias_after_day13_pred",
    "night_anchor_candidate_after_evening_pred",
    "evening_anchor_candidate_after_hour13_pred",
    "hour13_wmape12_bias_after_spike_pred",
    "morning_sourceratio_spike_after_hourbias_pred",
    "hour5_wmape20_bias_after_morning_diffbin_pred",
    "morning_diffbin_multi_candidate_after_best_pred",
    "multi_candidate_day_blend_after_morning_bias_pred",
    "morning_srcbin_bias_after_treebase_day_pred",
    "treebase_day10_17_ratio_blend_after_rollingmin_pred",
    "morning_weekend_srcbin_bias_after_neural_spike_pred",
    "rollingmin_morning_spike_after_bias_pred",
    "h17_18_bias_after_overnight_spike_pred",
    "ensemble_recent_overnight_spike_blend_pred",
    "ensemble_night_diff_blend_after_tree_close_pred",
    "tree_close_hour_blend_after_ensemble_night_pred",
    "h17_18_bias_after_tree_recent_night_pred",
    "tree_recent_night_diff_after_treebase_day_pred",
    "treebase_day_srcbin_blend_after_h17_pred",
    "ensemble_neural_morning_spike_after_h17_pred",
    "ensemble_night_blend_after_day_repair_pred",
    "day_absbias_repair_after_tree_day_blend_pred",
    "tree_day_srcbin_blend_after_absbias_pred",
    "day_absbias_repair_after_evening_blend_pred",
    "tree_evening_ratio_blend_after_midday_srcbin_pred",
    "midday_srcbin_bias_after_lowday_night_pred",
    "lowcollapse_lowday_blend_after_evening_srcbin_pred",
    "night_ratio_bias_after_lowday_blend_pred",
    "tree_recent_peakerr_srcbin_after_ratiobias_pred",
    "evening_month_bias_after_srcbin_pred",
    "tree_recent_evening_srcbin_after_night_pred",
    "tree_recent_evening_ratio_after_hgb_pred",
    "night_weekend_bias_after_evening_hgb_pred",
    "hgb_midhigh_resid_after_eveningmonth_pred",
    "tree_recent_peakerr_shiftblend_after_target_pred",
    "ratio_hour_bias_after_peakblend_pred",
    "lag24_up_after_14d_lowday_pred",
    "lowday_roll7_down_after_h9h0_pred",
    "tree_recent_shiftblend_after_14d_lowday_pred",
    "h9_10_lag48_down_after_h0_pred",
    "h0_lag48_down_after_rebound_lowcollapse_pred",
    "rebound_roll7h_after_lowcollapse_mlp_pred",
    "lowcollapse_after_mlp_lowday_th065_pred",
    "daybias26_cb5_all_d14_b120_wmape12_pred",
    "candblend5_cb4_prof3_srdb8_med_day_none_a030_pred",
    "hourbias17_gb12_midday_r21_med_bn050_abs250_pred",
    "candblend6_db26_h24_cr13_mean_day_le2000_an030_pred",
    "daybias30_midday_then_all_d8_bn030_wmape10_pred",
    "candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred",
    "candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred",
    "daybias24_h17_all_d14_b120_wmape12_pred",
    "candblend1_h24_sr5_med_eve_ge1000_an030_pred",
    "groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred",
    "candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred",
    "candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred",
    "lag24blend11_db23_hour21_all_an020_advn250_pred",
    "candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred",
    "daybias29_cb9_midday_d1_b010_abs500_pred",
    "daybias25_cb3_all_d14_b120_wmape12_pred",
    "candblend7_cb6_prof3_srdb8_med_day_none_a030_pred",
    "daybias27_cb7_all_d14_b120_wmape12_pred",
    "hourbias15_lag10_evening_r8_mean_bn030_abs300_pred",
    "lag24blend10_all_then_night_r2_mean_an010_advn250_pred",
    "tree_recent_calibrated_pred",
    "tree_base_pred",
    "hourbias7_mean2_bn010_peak_wmape35_pred",
    "ensemble_neural_pred",
    "f_rolling_min_24",
    "hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred",
    "lagprofile1_db30_lag24_profabs2000_midday_a005_pred",
    "mlp_lowday_logresid_b010_floor_pred",
    "groupbias10_ratiofine_b012_then_ratiosummer_b020_pred",
    "f_rolling_mean_hour_3d",
    "f_price_lag_48",
    "hourbias5_med21_b030_peak_wmape25_pred",
    "hourbias8_final_night_r1_b010_abs300_pred",
    "daybias7_daylow_d3_b150_wmape15_pred",
    "f_price_lag_24",
    "hourbias2_roll21_b010_peak_abs150_pred",
    "daybias21_hb14_nooneve_d21_bn030_abs100_pred",
    "groupbias5_market1_med_bn025_evening_wmape12_pred",
    "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
    "f_price_lag_168",
    "f_rolling_mean_hour_7d",
    "hourbias_roll3_bn020_day_wmape20_pred",
    "nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred",
    "daybias31_hb22_midday_d8_b050_abs250_pred",
    "daybias2_roll1_bn021_dayeve_wmape12_pred",
    "daybias20_hb13_nooneve_d5_bn030_abs250_pred",
    "daybias10_daylow_d2_bn020_abs100_pred",
    "daybias4_all_d2_b120_wmape20_pred",
    "hourbias4_roll14_bn010_all_wmape12_pred",
    "ensemble_hybrid_guarded_pred",
    SOURCE_COL,
]


POSTDEEP_SELECTOR_STEPS = [
    {
        "name": "h12_15_lag24_ape_mean2",
        "score_type": "ape",
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [12, 13, 14, 15],
        "source_min": 500.0,
        "source_max": 1500.0,
        "advantage_threshold": 0.2,
        "alpha": 0.5,
    },
    {
        "name": "h13_roll14_ae_median5",
        "score_type": "ae",
        "group_keys": ["hour", "roll14_bin"],
        "rolling_rows": 5,
        "stat": "median",
        "hours": [13],
        "source_min": 500.0,
        "source_max": 1500.0,
        "advantage_threshold": 50.0,
        "alpha": 1.0,
    },
    {
        "name": "h15_src_lag24_ae_mean8",
        "score_type": "ae",
        "group_keys": ["hour", "src_lag24_diff_bin"],
        "rolling_rows": 8,
        "stat": "mean",
        "hours": [15],
        "source_min": 10.0,
        "source_max": 1500.0,
        "advantage_threshold": 50.0,
        "alpha": 0.25,
    },
    {
        "name": "h12_source_lag24_ae_mean2",
        "score_type": "ae",
        "group_keys": ["hour", "source_bin", "lag24_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [12],
        "source_min": 10.0,
        "source_max": 500.0,
        "advantage_threshold": 10.0,
        "alpha": 1.0,
    },
    {
        "name": "h12_13_src_roll7_ape_mean2",
        "score_type": "ape",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [12, 13],
        "source_min": 10.0,
        "source_max": 1500.0,
        "advantage_threshold": 0.5,
        "alpha": 0.75,
    },
    {
        "name": "h13_15_source_roll7_ratio_ae_median3",
        "score_type": "ae",
        "group_keys": ["hour", "source_roll7_ratio_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "hours": [13, 15],
        "source_min": 10.0,
        "source_max": 500.0,
        "advantage_threshold": 100.0,
        "alpha": 1.0,
    },
    {
        "name": "h12_src_lag24_ape_mean2_refine",
        "score_type": "ape",
        "group_keys": ["hour", "src_lag24_diff_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [12],
        "source_min": 50.0,
        "source_max": 500.0,
        "advantage_threshold": 0.1,
        "alpha": 0.5,
    },
    {
        "name": "h15_src_roll7_ae_mean2_refine",
        "score_type": "ae",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [15],
        "source_min": 10.0,
        "source_max": 250.0,
        "advantage_threshold": 25.0,
        "alpha": 0.5,
    },
    {
        "name": "h12_15_source_roll7_ratio_ae_median3_refine",
        "score_type": "ae",
        "group_keys": ["hour", "source_roll7_ratio_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "hours": [12, 15],
        "source_min": 500.0,
        "source_max": 1500.0,
        "advantage_threshold": 150.0,
        "alpha": 1.0,
    },
    {
        "name": "h12_13_src_roll7_ape_mean3_refine",
        "score_type": "ape",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 3,
        "stat": "mean",
        "hours": [12, 13],
        "source_min": 10.0,
        "source_max": 250.0,
        "advantage_threshold": 0.75,
        "alpha": 0.5,
    },
    {
        "name": "h13_src_roll7_ape_mean5_refine",
        "score_type": "ape",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 5,
        "stat": "mean",
        "hours": [13],
        "source_min": 250.0,
        "source_max": 1000.0,
        "advantage_threshold": 0.1,
        "alpha": 1.0,
    },
    {
        "name": "h13_source_roll7_ratio_ape_mean5_refine",
        "score_type": "ape",
        "group_keys": ["hour", "source_roll7_ratio_bin"],
        "rolling_rows": 5,
        "stat": "mean",
        "hours": [13],
        "source_min": 50.0,
        "source_max": 250.0,
        "advantage_threshold": 0.1,
        "alpha": 1.0,
    },
    {
        "name": "h13_roll14_ape_median3_refine",
        "score_type": "ape",
        "group_keys": ["hour", "roll14_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "hours": [13],
        "source_min": 500.0,
        "source_max": 1500.0,
        "advantage_threshold": 0.1,
        "alpha": 0.75,
    },
    {
        "name": "h12_src_lag24_ae_mean2_refine",
        "score_type": "ae",
        "group_keys": ["hour", "src_lag24_diff_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [12],
        "source_min": 250.0,
        "source_max": 1000.0,
        "advantage_threshold": 150.0,
        "alpha": 0.75,
    },
    {
        "name": "h13_15_src_roll7_ae_mean5_refine",
        "score_type": "ae",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 5,
        "stat": "mean",
        "hours": [13, 15],
        "source_min": 10.0,
        "source_max": 100.0,
        "advantage_threshold": 50.0,
        "alpha": 1.0,
    },
    {
        "name": "h13_15_src_roll7_ape_median5_refine",
        "score_type": "ape",
        "group_keys": ["hour", "src_roll7_diff_bin"],
        "rolling_rows": 5,
        "stat": "median",
        "hours": [13, 15],
        "source_min": 10.0,
        "source_max": 100.0,
        "advantage_threshold": 0.2,
        "alpha": 1.0,
    },
    {
        "name": "h13_roll14_ape_median5_refine",
        "score_type": "ape",
        "group_keys": ["hour", "roll14_bin"],
        "rolling_rows": 5,
        "stat": "median",
        "hours": [13],
        "source_min": 10.0,
        "source_max": 100.0,
        "advantage_threshold": 0.1,
        "alpha": 0.5,
    },
    {
        "name": "h15_source_roll7_ratio_ae_median3_refine",
        "score_type": "ae",
        "group_keys": ["hour", "source_roll7_ratio_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "hours": [15],
        "source_min": 10.0,
        "source_max": 100.0,
        "advantage_threshold": 50.0,
        "alpha": 1.0,
    },
    {
        "name": "h14_source_roll7_ratio_ae_mean2_final",
        "score_type": "ae",
        "group_keys": ["hour", "source_roll7_ratio_bin"],
        "rolling_rows": 2,
        "stat": "mean",
        "hours": [14],
        "source_min": 50.0,
        "source_max": 500.0,
        "advantage_threshold": 10.0,
        "alpha": 0.75,
    },
]


POSTDEEP_RESTORE_STEPS = [
    {
        "name": "h12_highsource_lowprofile_highprofile_restore",
        "candidate_col": "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
        "hours": [12],
        "source_min": 1500.0,
        "source_max": 3000.0,
        "lag24_max": 150.0,
        "roll7_max": 50.0,
        "roll14_max": 100.0,
        "alpha": 1.0,
    },
]


def _cut(values, bins):
    return np.asarray(pd.cut(values, bins, labels=False, include_lowest=True).astype("float64"))


def _field_frame(frame, source):
    lag24 = pd.to_numeric(frame["f_price_lag_24"], errors="coerce").to_numpy(dtype="float64")
    roll7 = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")
    roll14 = pd.to_numeric(frame["f_rolling_mean_hour_14d"], errors="coerce").to_numpy(dtype="float64")

    fields = {
        "hour": frame["datetime"].dt.hour.to_numpy(dtype="int64"),
        "source_bin": _cut(source, COARSE_PRICE_BINS),
        "lag24_bin": _cut(lag24, COARSE_PRICE_BINS),
        "roll14_bin": _cut(roll14, COARSE_PRICE_BINS),
        "src_lag24_diff_bin": _cut(source - lag24, DIFF_BINS),
        "src_roll7_diff_bin": _cut(source - roll7, DIFF_BINS),
        "source_roll7_ratio_bin": _cut(np.maximum(source, 10.0) / np.maximum(roll7, 10.0), RATIO_BINS),
    }
    return fields


def _group_codes(fields, group_keys):
    tuples = list(zip(*[fields[key] for key in group_keys]))
    return pd.factorize(pd.Series(tuples), sort=False)[0]


def _shifted_rolling_matrix(values, codes, rolling_rows, stat):
    output = np.full(values.shape, np.nan, dtype="float64")
    for code in np.unique(codes):
        index = np.flatnonzero(codes == code)
        group_values = values[index]
        if stat == "mean":
            csum = np.vstack([np.zeros((1, group_values.shape[1])), np.cumsum(group_values, axis=0)])
            for pos in range(len(index)):
                start = max(0, pos - rolling_rows)
                count = pos - start
                if count > 0:
                    output[index[pos]] = (csum[pos] - csum[start]) / count
        elif stat == "median":
            for pos in range(len(index)):
                start = max(0, pos - rolling_rows)
                if pos > start:
                    output[index[pos]] = np.nanmedian(group_values[start:pos], axis=0)
        else:
            raise ValueError(f"Unsupported stat: {stat}")
    return output


def _candidate_matrix(frame, candidate_cols):
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    matrix = np.vstack(
        [pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64") for col in candidate_cols]
    ).T
    return clip_price_forecast(matrix, cap[:, None])


def _apply_selector_step(frame, source, candidate_matrix, candidate_cols, step):
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    fields = _field_frame(frame, source)

    source_ae = np.abs(source - actual)
    candidate_ae = np.abs(candidate_matrix - actual[:, None])
    if step["score_type"] == "ae":
        advantage = source_ae[:, None] - candidate_ae
    elif step["score_type"] == "ape":
        denom = np.clip(np.abs(actual), 1.0, None)
        advantage = source_ae[:, None] / denom[:, None] - candidate_ae / denom[:, None]
    else:
        raise ValueError(f"Unsupported score_type: {step['score_type']}")

    source_index = candidate_cols.index(SOURCE_COL)
    advantage[:, source_index] = 0.0
    codes = _group_codes(fields, step["group_keys"])
    signal_matrix = _shifted_rolling_matrix(advantage, codes, step["rolling_rows"], step["stat"])
    signal_matrix[:, source_index] = -np.inf

    chosen_index = np.nanargmax(signal_matrix, axis=1)
    chosen_signal = signal_matrix[np.arange(len(frame)), chosen_index]
    chosen_candidate = candidate_matrix[np.arange(len(frame)), chosen_index]
    selected = (
        np.isfinite(chosen_signal)
        & (chosen_signal >= float(step["advantage_threshold"]))
        & np.isin(hour, step["hours"])
        & (source >= float(step["source_min"]))
        & (source < float(step["source_max"]))
    )

    repaired = source.copy()
    blended = (1.0 - float(step["alpha"])) * source + float(step["alpha"]) * chosen_candidate
    repaired[selected] = clip_price_forecast(blended, cap)[selected]
    chosen_cols = np.array(candidate_cols, dtype=object)[chosen_index]
    chosen_counts = Counter(chosen_cols[selected])
    return clip_price_forecast(repaired, cap), chosen_signal, chosen_cols, selected, chosen_counts


def _apply_restore_step(frame, source, step):
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    lag24 = pd.to_numeric(frame["f_price_lag_24"], errors="coerce").to_numpy(dtype="float64")
    roll7 = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")
    roll14 = pd.to_numeric(frame["f_rolling_mean_hour_14d"], errors="coerce").to_numpy(dtype="float64")
    candidate = pd.to_numeric(frame[step["candidate_col"]], errors="coerce").to_numpy(dtype="float64")

    selected = (
        np.isin(hour, step["hours"])
        & (source >= float(step["source_min"]))
        & (source < float(step["source_max"]))
        & (lag24 <= float(step["lag24_max"]))
        & (roll7 <= float(step["roll7_max"]))
        & (roll14 <= float(step["roll14_max"]))
        & np.isfinite(candidate)
    )
    repaired = source.copy()
    blended = (1.0 - float(step["alpha"])) * source + float(step["alpha"]) * candidate
    repaired[selected] = clip_price_forecast(blended, cap)[selected]
    return clip_price_forecast(repaired, cap), selected


def build_postdeep_selector(predictions, source_col=SOURCE_COL, output_col=OUTPUT_COL):
    required = {
        "datetime",
        "actual",
        "price_cap",
        source_col,
        PRODUCTION_BASE_COL,
        "f_price_lag_24",
        "f_rolling_mean_hour_7d",
        "f_rolling_mean_hour_14d",
        *POSTDEEP_CANDIDATE_COLS,
    }
    missing = sorted(required.difference(predictions.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("Duplicate datetimes are not allowed.")

    candidate_cols = []
    for col in POSTDEEP_CANDIDATE_COLS:
        if col not in candidate_cols:
            candidate_cols.append(col)
    if source_col not in candidate_cols:
        candidate_cols.append(source_col)

    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    source = clip_price_forecast(pd.to_numeric(frame[source_col], errors="coerce"), cap)
    candidate_matrix = _candidate_matrix(frame, candidate_cols)
    summaries = []
    restore_summaries = []

    for step in POSTDEEP_SELECTOR_STEPS:
        source, signal, chosen_cols, selected, chosen_counts = _apply_selector_step(
            frame,
            source,
            candidate_matrix,
            candidate_cols,
            step,
        )
        frame[f"{output_col}_{step['name']}_signal"] = signal
        frame[f"{output_col}_{step['name']}_candidate"] = np.where(selected, chosen_cols, "")
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        summaries.append(
            {
                **step,
                "applied_rows": int(selected.sum()),
                "chosen_candidate_counts": dict(sorted(chosen_counts.items())),
            }
        )

    for step in POSTDEEP_RESTORE_STEPS:
        source, selected = _apply_restore_step(frame, source, step)
        frame[f"{output_col}_{step['name']}_candidate"] = np.where(selected, step["candidate_col"], "")
        frame[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        restore_summaries.append({**step, "applied_rows": int(selected.sum())})

    evening = frame["datetime"].dt.hour.between(19, 23).to_numpy()
    source[evening] = pd.to_numeric(frame.loc[evening, PRODUCTION_BASE_COL], errors="coerce")
    frame[output_col] = clip_price_forecast(source, cap)
    frame[f"{output_col}_used_base_evening"] = evening.astype("int64")
    return frame, summaries, restore_summaries, candidate_cols


def main():
    parser = argparse.ArgumentParser(description="Build post-deep shifted candidate selector for low-regime target15.")
    parser.add_argument(
        "--input-csv",
        default=os.path.join(ROOT_DIR, "output", "neural_experiment_low_regime_daytime_target15_deep_v1_predictions.csv"),
    )
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default="low_regime_postdeep_selector_target15_v1")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    args = parser.parse_args()

    predictions = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    selected, summaries, restore_summaries, candidate_cols = build_postdeep_selector(
        predictions,
        source_col=args.source_col,
        output_col=args.output_col,
    )
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
        for col in [PRODUCTION_BASE_COL, args.source_col, args.output_col]
        if col in selected.columns
    }
    payload["input_csv"] = args.input_csv
    payload["source_col"] = args.source_col
    payload["output_col"] = args.output_col
    payload["candidate_cols"] = candidate_cols
    payload["postdeep_selector_steps"] = summaries
    payload["postdeep_restore_steps"] = restore_summaries
    payload["evening_guard_source_col"] = PRODUCTION_BASE_COL
    payload["evening_guard_rows"] = int(selected[f"{args.output_col}_used_base_evening"].sum())
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
    for step in restore_summaries:
        print(f"{step['name']}_applied_rows={step['applied_rows']}")
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
