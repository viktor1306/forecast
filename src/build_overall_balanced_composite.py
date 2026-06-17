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

PRICE_BINS = [-1, 10, 50, 100, 250, 500, 1000, 1500, 3000, 7000, 100000]

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
    {
        "name": "h13_hour_ratio_q25_w5_b015",
        "kind": "ratio",
        "hours": [13],
        "group_keys": ["hour"],
        "rolling_rows": 5,
        "stat": "q25",
        "strength": 0.15,
    },
    {
        "name": "h15_lag24_ratio_median_w3_b010",
        "kind": "ratio",
        "hours": [15],
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "strength": 0.10,
    },
    {
        "name": "h14_hour_resid_median_w8_b015",
        "kind": "resid",
        "hours": [14],
        "group_keys": ["hour"],
        "rolling_rows": 8,
        "stat": "median",
        "strength": 0.15,
    },
    {
        "name": "h09_lag24_ratio_q75_w5_b025",
        "kind": "ratio",
        "hours": [9],
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 5,
        "stat": "q75",
        "strength": 0.25,
    },
    {
        "name": "h08_hour_ratio_mean_w34_b035",
        "kind": "ratio",
        "hours": [8],
        "group_keys": ["hour"],
        "rolling_rows": 34,
        "stat": "mean",
        "strength": 0.35,
    },
    {
        "name": "h11_lag24_ratio_median_w13_b010",
        "kind": "ratio",
        "hours": [11],
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 13,
        "stat": "median",
        "strength": 0.10,
    },
    {
        "name": "h17_src_lag24_ratio_q75_w21_b015",
        "kind": "ratio",
        "hours": [17],
        "group_keys": ["hour", "src_lag24_diff_bin"],
        "rolling_rows": 21,
        "stat": "q75",
        "strength": 0.15,
    },
]

CANDIDATE_BLEND_REPAIRS = [
    {
        "name": "h06_lag24blend10_blend_b010",
        "hours": [6],
        "candidate_col": "lag24blend10_all_then_night_r2_mean_an010_advn250_pred",
        "alpha": 0.10,
    },
    {
        "name": "h02_daybias29_blend_b025",
        "hours": [2],
        "candidate_col": "daybias29_cb9_midday_d1_b010_abs500_pred",
        "alpha": 0.25,
    },
    {
        "name": "h12_postdeep_blend_b035",
        "hours": [12],
        "candidate_col": "low_regime_postdeep_selector_target15_pred",
        "alpha": 0.35,
    },
    {
        "name": "h11_hourbias21_blend_b005",
        "hours": [11],
        "candidate_col": "hourbias21_lp4_peakerr_r2_bn015_wmape40_pred",
        "alpha": 0.05,
    },
    {
        "name": "h13_roll7diff_blend_b005",
        "hours": [13],
        "candidate_col": "low_regime_roll7diff_restore_target15_pred",
        "alpha": 0.05,
    },
    {
        "name": "h14_hgb_midhigh_blend_b010",
        "hours": [14],
        "candidate_col": "hgb_midhigh_resid_after_eveningmonth_pred",
        "alpha": 0.10,
    },
    {
        "name": "h15_postdeep_blend_b005",
        "hours": [15],
        "candidate_col": "low_regime_postdeep_selector_target15_pred",
        "alpha": 0.05,
    },
    {
        "name": "h14_shifted_actual_blend_b001",
        "hours": [14],
        "candidate_col": "low_regime_shifted_actual_repair_pred",
        "alpha": 0.01,
    },
    {
        "name": "h17_sourcebin_daytime_blend_b025",
        "hours": [17],
        "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred",
        "alpha": 0.25,
    },
    {
        "name": "h02_night_ratio_blend_b008",
        "hours": [2],
        "candidate_col": "night_ratio_bias_after_sourcebin_daytime_pred",
        "alpha": 0.08,
    },
    {
        "name": "h00_sourcebin_daytime_blend_b020",
        "hours": [0],
        "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred",
        "alpha": 0.20,
    },
    {
        "name": "h06_night_hour8_blend_b035",
        "hours": [6],
        "candidate_col": "night_hour8_wmape12_after_day14_16_pred",
        "alpha": 0.35,
    },
]

FINAL_SHIFTED_REPAIRS = [
    {
        "name": "h13_final_lag24_resid_median_w3_b002",
        "kind": "resid",
        "hours": [13],
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 3,
        "stat": "median",
        "strength": 0.02,
    },
    {
        "name": "h14_final_lag24_resid_median_w8_b005",
        "kind": "resid",
        "hours": [14],
        "group_keys": ["hour", "lag24_bin"],
        "rolling_rows": 8,
        "stat": "median",
        "strength": 0.05,
    },
    {
        "name": "h15_final_hour_resid_q25_w21_b001",
        "kind": "resid",
        "hours": [15],
        "group_keys": ["hour"],
        "rolling_rows": 21,
        "stat": "q25",
        "strength": 0.01,
    },
]

FINAL_GATED_BLEND_REPAIRS = [
    {
        "name": "h12_sourcebin8_daybias31_restore_a100",
        "hours": [12],
        "candidate_col": "daybias31_hb22_midday_d8_b050_abs250_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin"],
        "gate_values": [8.0],
    },
    {
        "name": "h11_lag24roll7bin12_lagprofile1_restore_a100",
        "hours": [11],
        "candidate_col": "lagprofile1_db30_lag24_profabs2000_midday_a005_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin"],
        "gate_values": [12.0],
    },
    {
        "name": "h14_srclag24bin12_daybias21_blend_b035",
        "hours": [14],
        "candidate_col": "daybias21_hb14_nooneve_d21_bn030_abs100_pred",
        "alpha": 0.35,
        "gate_keys": ["src_lag24_diff_bin"],
        "gate_values": [12.0],
    },
    {
        "name": "h11_sourcebin8_lag24bin8_daybias31_restore_a100",
        "hours": [11],
        "candidate_col": "daybias31_hb22_midday_d8_b050_abs250_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [8.0, 8.0],
    },
    {
        "name": "h12_lag24roll7bin0_daybias10_restore_a100",
        "hours": [12],
        "candidate_col": "daybias10_daylow_d2_bn020_abs100_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin"],
        "gate_values": [0.0],
    },
    {
        "name": "h13_srclag24bin11_daybias30_blend_b075",
        "hours": [13],
        "candidate_col": "daybias30_midday_then_all_d8_bn030_wmape10_pred",
        "alpha": 0.75,
        "gate_keys": ["src_lag24_diff_bin"],
        "gate_values": [11.0],
    },
    {
        "name": "h15_lag24bin9_groupbias1_blend_b035",
        "hours": [15],
        "candidate_col": "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
        "alpha": 0.35,
        "gate_keys": ["lag24_bin"],
        "gate_values": [9.0],
    },
    {
        "name": "h11_sourcebin7_srclag24bin0_hourbias9_restore_a100",
        "hours": [11],
        "candidate_col": "hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 0.0],
    },
    {
        "name": "h12_lag24bin0_srclag24bin10_candblend5_restore_a100",
        "hours": [12],
        "candidate_col": "candblend5_cb4_prof3_srdb8_med_day_none_a030_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [0.0, 10.0],
    },
    {
        "name": "h13_sourcebin8_srclag24bin12_hourbias2_restore_a100",
        "hours": [13],
        "candidate_col": "hourbias2_roll21_b010_peak_abs150_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [8.0, 12.0],
    },
    {
        "name": "h14_lag24bin8_srclag24bin11_hourbias6_restore_a100",
        "hours": [14],
        "candidate_col": "hourbias6_mean3_bn020_day_wmape30_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [8.0, 11.0],
    },
    {
        "name": "h15_lag24bin5_srclag24bin12_hourbias9_restore_a100",
        "hours": [15],
        "candidate_col": "hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [5.0, 12.0],
    },
    {
        "name": "h11_sourcebin7_srclag24bin9_lag24blend9_restore_a100",
        "hours": [11],
        "candidate_col": "lag24blend9_db21_hourall_r3_mean_an005_advn500_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 9.0],
    },
    {
        "name": "h12_sourcebin7_lag24bin8_daybias31_blend_b075",
        "hours": [12],
        "candidate_col": "daybias31_hb22_midday_d8_b050_abs250_pred",
        "alpha": 0.75,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [7.0, 8.0],
    },
    {
        "name": "h13_lag24roll7bin2_srclag24bin12_hourbias21_restore_a100",
        "hours": [13],
        "candidate_col": "hourbias21_lp4_peakerr_r2_bn015_wmape40_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [2.0, 12.0],
    },
    {
        "name": "h15_sourcebin7_lag24bin7_analog_blend_b035",
        "hours": [15],
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "alpha": 0.35,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [7.0, 7.0],
    },
    {
        "name": "h11_lag24roll7bin1_srclag24bin10_daybias10_blend_b050",
        "hours": [11],
        "candidate_col": "daybias10_daylow_d2_bn020_abs100_pred",
        "alpha": 0.5,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [1.0, 10.0],
    },
    {
        "name": "h12_lag24bin5_srclag24bin12_hourbias17_restore_a100",
        "hours": [12],
        "candidate_col": "hourbias17_gb12_midday_r21_med_bn050_abs250_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [5.0, 12.0],
    },
    {
        "name": "h13_lag24bin7_srclag24bin2_analog_blend_b025",
        "hours": [13],
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "alpha": 0.25,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 2.0],
    },
    {
        "name": "h15_sourcebin9_lag24bin8_hourbias17_restore_a100",
        "hours": [15],
        "candidate_col": "hourbias17_gb12_midday_r21_med_bn050_abs250_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [9.0, 8.0],
    },
    {
        "name": "h11_sourcebin6_lag24roll7bin1_daybias30_restore_a100",
        "hours": [11],
        "candidate_col": "daybias30_midday_then_all_d8_bn030_wmape10_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [6.0, 1.0],
    },
    {
        "name": "h12_sourcebin8_lag24roll7bin1_daybias10_blend_b075",
        "hours": [12],
        "candidate_col": "daybias10_daylow_d2_bn020_abs100_pred",
        "alpha": 0.75,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [8.0, 1.0],
    },
    {
        "name": "h13_lag24roll7bin11_srclag24bin12_lag24blend9_restore_a100",
        "hours": [13],
        "candidate_col": "lag24blend9_db21_hourall_r3_mean_an005_advn500_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [11.0, 12.0],
    },
    {
        "name": "h15_sourcebin8_lag24roll7bin2_groupbias9_restore_a100",
        "hours": [15],
        "candidate_col": "groupbias9_h12_ratiofine21_med_all_b012_abs100_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [8.0, 2.0],
    },
    {
        "name": "h11_lag24roll7bin2_srclag24bin1_analog_blend_b035",
        "hours": [11],
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "alpha": 0.35,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [2.0, 1.0],
    },
    {
        "name": "h12_sourcebin5_lag24roll7bin1_groupbias10_blend_b075",
        "hours": [12],
        "candidate_col": "groupbias10_ratiofine_b012_then_ratiosummer_b020_pred",
        "alpha": 0.75,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [5.0, 1.0],
    },
    {
        "name": "h13_sourcebin6_lag24roll7bin2_analog_blend_b020",
        "hours": [13],
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "alpha": 0.2,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [6.0, 2.0],
    },
    {
        "name": "h11_lag24roll7bin0_srclag24bin12_hourbias21_blend_b075",
        "hours": [11],
        "candidate_col": "hourbias21_lp4_peakerr_r2_bn015_wmape40_pred",
        "alpha": 0.75,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [0.0, 12.0],
    },
    {
        "name": "h12_sourcebin6_lag24roll7bin11_groupbias9_blend_b075",
        "hours": [12],
        "candidate_col": "groupbias9_h12_ratiofine21_med_all_b012_abs100_pred",
        "alpha": 0.75,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [6.0, 11.0],
    },
    {
        "name": "h13_lag24roll7bin3_srclag24bin6_lagprofile1_blend_b050",
        "hours": [13],
        "candidate_col": "lagprofile1_db30_lag24_profabs2000_midday_a005_pred",
        "alpha": 0.5,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [3.0, 6.0],
    },
    {
        "name": "h11_lag24bin7_srclag24bin3_groupbias1_blend_b050",
        "hours": [11],
        "candidate_col": "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
        "alpha": 0.5,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 3.0],
    },
    {
        "name": "h12_sourcebin7_lag24roll7bin3_candblend6_restore_a100",
        "hours": [12],
        "candidate_col": "candblend6_db26_h24_cr13_mean_day_le2000_an030_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 3.0],
    },
    {
        "name": "h13_sourcebin5_lag24roll7bin11_analog_blend_b035",
        "hours": [13],
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "alpha": 0.35,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [5.0, 11.0],
    },
    {
        "name": "h11_sourcebin1_srclag24bin2_groupbias12_restore_a100",
        "hours": [11],
        "candidate_col": "groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [1.0, 2.0],
    },
    {
        "name": "h12_lag24roll7bin10_srclag24bin12_daybias31_restore_a100",
        "hours": [12],
        "candidate_col": "daybias31_hb22_midday_d8_b050_abs250_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [10.0, 12.0],
    },
    {
        "name": "h13_lag24roll7bin10_srclag24bin12_daybias31_restore_a100",
        "hours": [13],
        "candidate_col": "daybias31_hb22_midday_d8_b050_abs250_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [10.0, 12.0],
    },
    {
        "name": "h11_lag24roll7bin3_lag24blend6_blend_b050",
        "hours": [11],
        "candidate_col": "lag24blend6_nightprof_all_reldiff005_an010_pred",
        "alpha": 0.5,
        "gate_keys": ["lag24_roll7_diff_bin"],
        "gate_values": [3.0],
    },
    {
        "name": "h12_lag24roll7bin11_srclag24bin0_groupbias1_blend_b015",
        "hours": [12],
        "candidate_col": "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
        "alpha": 0.15,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [11.0, 0.0],
    },
    {
        "name": "h13_treebase_lagroll1_srclag9_restore_a100",
        "hours": [13],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [1.0, 9.0],
    },
    {
        "name": "h14_treebase_src7_lagroll12_restore_a100",
        "hours": [14],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 12.0],
    },
    {
        "name": "h14_lowprofile_src8_lagroll7_restore_a100",
        "hours": [14],
        "candidate_col": "hybrid_low_profile_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [8.0, 7.0],
    },
    {
        "name": "h10_ensemble_source9_restore_a100",
        "hours": [10],
        "candidate_col": "ensemble_neural_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin"],
        "gate_values": [9.0],
    },
    {
        "name": "h09_daybias3_lag8_srclag11_restore_a100",
        "hours": [9],
        "candidate_col": "daybias3_nm_d1_b050_wmape15_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [8.0, 11.0],
    },
    {
        "name": "h11_treebase_lag2_blend_b075",
        "hours": [11],
        "candidate_col": "tree_base_pred",
        "alpha": 0.75,
        "gate_keys": ["lag24_bin"],
        "gate_values": [2.0],
    },
    {
        "name": "h15_ensemblehybrid_src5_lagroll10_blend_b020",
        "hours": [15],
        "candidate_col": "ensemble_hybrid_pred",
        "alpha": 0.2,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [5.0, 10.0],
    },
    {
        "name": "h09_treecal_lagroll1_srclag12_blend_b075",
        "hours": [9],
        "candidate_col": "tree_recent_calibrated_pred",
        "alpha": 0.75,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [1.0, 12.0],
    },
    {
        "name": "h11_treebase_src7_lagroll11_restore_a100",
        "hours": [11],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 11.0],
    },
    {
        "name": "h08_treebase_lagroll10_blend_b020",
        "hours": [8],
        "candidate_col": "tree_base_pred",
        "alpha": 0.2,
        "gate_keys": ["lag24_roll7_diff_bin"],
        "gate_values": [10.0],
    },
    {
        "name": "h08_morningweekend_src9_lagroll12_restore_a100",
        "hours": [8],
        "candidate_col": "morning_weekend_srcbin_bias_after_neural_spike_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [9.0, 12.0],
    },
    {
        "name": "h16_treebase_src9_lagroll11_blend_b035",
        "hours": [16],
        "candidate_col": "tree_base_pred",
        "alpha": 0.35,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [9.0, 11.0],
    },
    {
        "name": "h16_treebase_src7_lag7_blend_b025",
        "hours": [16],
        "candidate_col": "tree_base_pred",
        "alpha": 0.25,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [7.0, 7.0],
    },
    {
        "name": "h08_treebase_lagroll2_restore_a100",
        "hours": [8],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin"],
        "gate_values": [2.0],
    },
    {
        "name": "h17_treecal_srclag1_restore_a100",
        "hours": [17],
        "candidate_col": "tree_recent_calibrated_pred",
        "alpha": 1.0,
        "gate_keys": ["src_lag24_diff_bin"],
        "gate_values": [1.0],
    },
    {
        "name": "h13_treebase_src7_srclag12_blend_b050",
        "hours": [13],
        "candidate_col": "tree_base_pred",
        "alpha": 0.5,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 12.0],
    },
    {
        "name": "h07_daybias16_lag9_srclag12_blend_b075",
        "hours": [7],
        "candidate_col": "daybias16_final_critical_d5_b050_abs300_pred",
        "alpha": 0.75,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [9.0, 12.0],
    },
    {
        "name": "h02_analog_src8_lagroll1_restore_a100",
        "hours": [2],
        "candidate_col": "analog_ratio_all_b012_k4_c050_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [8.0, 1.0],
    },
    {
        "name": "h14_lowprofile_lagroll7_blend_b025",
        "hours": [14],
        "candidate_col": "hybrid_low_profile_pred",
        "alpha": 0.25,
        "gate_keys": ["lag24_roll7_diff_bin"],
        "gate_values": [7.0],
    },
    {
        "name": "h12_treebase_src6_lag7_restore_a100",
        "hours": [12],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [6.0, 7.0],
    },
    {
        "name": "h12_postdeep_src6_lag7_restore_a100",
        "hours": [12],
        "candidate_col": "low_regime_postdeep_selector_target15_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [6.0, 7.0],
    },
    {
        "name": "h11_sourcebin_lag7_srclag12_restore_a100",
        "hours": [11],
        "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 12.0],
    },
    {
        "name": "h12_peakerr_src5_lag7_restore_a100",
        "hours": [12],
        "candidate_col": "tree_recent_peakerr_srcbin_after_ratiobias_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [5.0, 7.0],
    },
    {
        "name": "h11_lag24blend6_lag5_srclag9_restore_a100",
        "hours": [11],
        "candidate_col": "lag24blend6_nightprof_all_reldiff005_an010_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin", "src_lag24_diff_bin"],
        "gate_values": [5.0, 9.0],
    },
    {
        "name": "h12_sourcebin_src7_lagroll1_restore_a100",
        "hours": [12],
        "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 1.0],
    },
    {
        "name": "h11_hourbias22_lagroll1_srclag12_blend_b015",
        "hours": [11],
        "candidate_col": "hourbias22_hb21_peakerr_r8_bn020_wmape40_pred",
        "alpha": 0.15,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [1.0, 12.0],
    },
    {
        "name": "h11_lowregimefinal_lagroll11_srclag0_blend_b035",
        "hours": [11],
        "candidate_col": "low_regime_final_restore_target15_pred",
        "alpha": 0.35,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [11.0, 0.0],
    },
    {
        "name": "h11_lag24up_lag9_restore_a100",
        "hours": [11],
        "candidate_col": "lag24_up_after_14d_lowday_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_bin"],
        "gate_values": [9.0],
    },
    {
        "name": "h12_day1115_src8_lag5_blend_b025",
        "hours": [12],
        "candidate_col": "day11_15_srcbinweekend_repair_after_morning7_pred",
        "alpha": 0.25,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [8.0, 5.0],
    },
    {
        "name": "h12_sourcebin_lag9_blend_b075",
        "hours": [12],
        "candidate_col": "sourcebin_daytime_bias_after_lowrepair_pred",
        "alpha": 0.75,
        "gate_keys": ["lag24_bin"],
        "gate_values": [9.0],
    },
    {
        "name": "h12_treebase_lagroll8_srclag3_restore_a100",
        "hours": [12],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["lag24_roll7_diff_bin", "src_lag24_diff_bin"],
        "gate_values": [8.0, 3.0],
    },
    {
        "name": "h11_ensemble_src7_srclag8_restore_a100",
        "hours": [11],
        "candidate_col": "ensemble_neural_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 8.0],
    },
    {
        "name": "h12_ensemblehybrid_src8_lag2_restore_a100",
        "hours": [12],
        "candidate_col": "ensemble_hybrid_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [8.0, 2.0],
    },
    {
        "name": "h11_groupbias10_src7_lagroll0_restore_a100",
        "hours": [11],
        "candidate_col": "groupbias10_ratiofine_b012_then_ratiosummer_b020_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 0.0],
    },
    {
        "name": "h11_treebase_src0_lag0_srclag6_lagroll4_restore_a100",
        "hours": [11],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin", "src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [0.0, 0.0, 6.0, 4.0],
    },
    {
        "name": "h11_ensemble_src7_lag7_srclag2_lagroll2_restore_a100",
        "hours": [11],
        "candidate_col": "ensemble_neural_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin", "src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 7.0, 2.0, 2.0],
    },
    {
        "name": "h11_treecal_src5_lag6_srclag2_lagroll2_restore_a100",
        "hours": [11],
        "candidate_col": "tree_recent_calibrated_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin", "src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [5.0, 6.0, 2.0, 2.0],
    },
    {
        "name": "h11_day1115_src7_lag8_srclag2_lagroll9_restore_a100",
        "hours": [11],
        "candidate_col": "day11_15_srcbinweekend_repair_after_morning7_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin", "src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 8.0, 2.0, 9.0],
    },
    {
        "name": "h11_anomaly_src7_lag7_srclag1_lagroll11_restore_a100",
        "hours": [11],
        "candidate_col": "anomaly_hgb_ratio_b0025_q85w025_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin", "src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [7.0, 7.0, 1.0, 11.0],
    },
    {
        "name": "h13_rebound_source7_lag0_restore_a100",
        "hours": [13],
        "candidate_col": "rebound_roll7h_after_lowcollapse_mlp_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [7.0, 0.0],
    },
    {
        "name": "h00_groupbias3_source8_srclag12_restore_a100",
        "hours": [0],
        "candidate_col": "groupbias3_market1_med_b010_night_abs150_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [8.0, 12.0],
    },
    {
        "name": "h14_hourbias22_source7_srclag1_blend_b075",
        "hours": [14],
        "candidate_col": "hourbias22_hb21_peakerr_r8_bn020_wmape40_pred",
        "alpha": 0.75,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [7.0, 1.0],
    },
    {
        "name": "h02_treecal_source5_lagroll4_restore_a100",
        "hours": [2],
        "candidate_col": "tree_recent_calibrated_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [5.0, 4.0],
    },
    {
        "name": "h16_hourbias14_source8_srclag0_restore_a100",
        "hours": [16],
        "candidate_col": "hourbias14_db20_h789111718_r1_b010_wmape25_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [8.0, 0.0],
    },
    {
        "name": "h04_ensemble_source8_lagroll8_restore_a100",
        "hours": [4],
        "candidate_col": "ensemble_neural_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [8.0, 8.0],
    },
    {
        "name": "h06_ensemblehybrid_srclag12_lagroll0_restore_a100",
        "hours": [6],
        "candidate_col": "ensemble_hybrid_pred",
        "alpha": 1.0,
        "gate_keys": ["src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [12.0, 0.0],
    },
    {
        "name": "h15_groupbias5_source8_lag6_restore_a100",
        "hours": [15],
        "candidate_col": "groupbias5_market1_med_bn025_evening_wmape12_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [8.0, 6.0],
    },
    {
        "name": "h09_lowday_srclag1_lagroll3_restore_a100",
        "hours": [9],
        "candidate_col": "lowday_roll7_down_after_h9h0_pred",
        "alpha": 1.0,
        "gate_keys": ["src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [1.0, 3.0],
    },
    {
        "name": "h10_lag24blend5_source8_lagroll1_restore_a100",
        "hours": [10],
        "candidate_col": "lag24blend5_night_profilele1000_a005_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [8.0, 1.0],
    },
    {
        "name": "h03_lowprofile_source8_lag2_restore_a100",
        "hours": [3],
        "candidate_col": "hybrid_low_profile_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_bin"],
        "gate_values": [8.0, 2.0],
    },
    {
        "name": "h07_treebase_srclag11_lagroll2_restore_a100",
        "hours": [7],
        "candidate_col": "tree_base_pred",
        "alpha": 1.0,
        "gate_keys": ["src_lag24_diff_bin", "lag24_roll7_diff_bin"],
        "gate_values": [11.0, 2.0],
    },
    {
        "name": "h17_treecal_source9_lagroll8_blend_b075",
        "hours": [17],
        "candidate_col": "tree_recent_calibrated_pred",
        "alpha": 0.75,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [9.0, 8.0],
    },
    {
        "name": "h12_hourbias4_source6_srclag3_restore_a100",
        "hours": [12],
        "candidate_col": "hourbias4_roll14_bn010_all_wmape12_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "src_lag24_diff_bin"],
        "gate_values": [6.0, 3.0],
    },
    {
        "name": "h11_lowregimecand_source3_lagroll4_restore_a100",
        "hours": [11],
        "candidate_col": "low_regime_candidate_restore_target15_pred",
        "alpha": 1.0,
        "gate_keys": ["source_bin", "lag24_roll7_diff_bin"],
        "gate_values": [3.0, 4.0],
    },
    {
        "name": "h08_treecal_source9_lag8_lagroll0_blend_b015",
        "hours": [8],
        "candidate_col": "tree_recent_calibrated_pred",
        "alpha": 0.15,
        "gate_keys": ["source_bin", "lag24_bin", "lag24_roll7_diff_bin"],
        "gate_values": [9.0, 8.0, 0.0],
    },
]


def overall_balanced_required_columns():
    return {
        "datetime",
        "actual",
        "price_cap",
        "f_price_lag_24",
        "f_rolling_mean_hour_7d",
        BASE_COL,
        DAY_REPAIR_COL,
        *(step["candidate_col"] for step in FIXED_HOUR_RESTORES),
        *(step["candidate_col"] for step in CANDIDATE_BLEND_REPAIRS),
        *(step["candidate_col"] for step in FINAL_GATED_BLEND_REPAIRS),
    }


def missing_overall_balanced_columns(columns):
    return sorted(overall_balanced_required_columns().difference(set(columns)))


def _cut(values, bins):
    return np.asarray(pd.cut(values, bins, labels=False, include_lowest=True).astype("float64"))


def _field_frame(frame, source):
    lag24 = pd.to_numeric(frame["f_price_lag_24"], errors="coerce").to_numpy(dtype="float64")
    roll7 = pd.to_numeric(frame["f_rolling_mean_hour_7d"], errors="coerce").to_numpy(dtype="float64")
    return {
        "hour": frame["datetime"].dt.hour.to_numpy(dtype="int64"),
        "source_bin": _cut(source, PRICE_BINS),
        "lag24_bin": _cut(lag24, PRICE_BINS),
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


def _apply_candidate_blend_repair(frame, source, step):
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    candidate = pd.to_numeric(frame[step["candidate_col"]], errors="coerce").to_numpy(dtype="float64")
    selected = np.isin(hour, step["hours"]) & np.isfinite(candidate)
    blended = (1.0 - float(step["alpha"])) * source + float(step["alpha"]) * candidate

    repaired = source.copy()
    clipped = clip_price_forecast(blended, cap)
    repaired[selected] = clipped[selected]
    return clip_price_forecast(repaired, cap), candidate, selected


def _apply_gated_candidate_blend_repair(frame, source, step):
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    candidate = pd.to_numeric(frame[step["candidate_col"]], errors="coerce").to_numpy(dtype="float64")
    fields = _field_frame(frame, source)
    selected = np.isin(hour, step["hours"]) & np.isfinite(candidate)
    for key, value in zip(step["gate_keys"], step["gate_values"]):
        selected &= fields[key] == float(value)

    blended = (1.0 - float(step["alpha"])) * source + float(step["alpha"]) * candidate
    repaired = source.copy()
    clipped = clip_price_forecast(blended, cap)
    repaired[selected] = clipped[selected]
    return clip_price_forecast(repaired, cap), candidate, selected


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
    missing = missing_overall_balanced_columns(predictions.columns)
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
    diagnostic_columns = {f"{output_col}_used_day_repair": day_mask.astype("int64")}

    fixed_summaries = []
    for step in FIXED_HOUR_RESTORES:
        selected = hour == int(step["hour"])
        candidate = pd.to_numeric(frame.loc[selected, step["candidate_col"]], errors="coerce")
        source[selected] = candidate.to_numpy(dtype="float64")
        diagnostic_columns[f"{output_col}_fixed_h{int(step['hour']):02d}_candidate"] = np.where(
            selected,
            step["candidate_col"],
            "",
        )
        fixed_summaries.append({**step, "applied_rows": int(selected.sum())})
    source = clip_price_forecast(source, cap)

    shifted_summaries = []
    for step in SHIFTED_REPAIRS:
        source, signal, selected = _apply_shifted_repair(frame, source, step)
        diagnostic_columns[f"{output_col}_{step['name']}_signal"] = signal
        diagnostic_columns[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        shifted_summaries.append({**step, "applied_rows": int(selected.sum())})

    candidate_blend_summaries = []
    for step in CANDIDATE_BLEND_REPAIRS:
        source, candidate, selected = _apply_candidate_blend_repair(frame, source, step)
        diagnostic_columns[f"{output_col}_{step['name']}_candidate"] = candidate
        diagnostic_columns[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        candidate_blend_summaries.append({**step, "applied_rows": int(selected.sum())})

    final_shifted_summaries = []
    for step in FINAL_SHIFTED_REPAIRS:
        source, signal, selected = _apply_shifted_repair(frame, source, step)
        diagnostic_columns[f"{output_col}_{step['name']}_signal"] = signal
        diagnostic_columns[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        final_shifted_summaries.append({**step, "applied_rows": int(selected.sum())})

    final_gated_blend_summaries = []
    for step in FINAL_GATED_BLEND_REPAIRS:
        source, candidate, selected = _apply_gated_candidate_blend_repair(frame, source, step)
        diagnostic_columns[f"{output_col}_{step['name']}_candidate"] = candidate
        diagnostic_columns[f"{output_col}_{step['name']}_applied"] = selected.astype("int64")
        final_gated_blend_summaries.append({**step, "applied_rows": int(selected.sum())})

    if diagnostic_columns:
        frame = pd.concat([frame, pd.DataFrame(diagnostic_columns, index=frame.index)], axis=1)
    frame[output_col] = source
    return (
        frame,
        fixed_summaries,
        shifted_summaries,
        candidate_blend_summaries,
        final_shifted_summaries,
        final_gated_blend_summaries,
    )


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
    (
        selected,
        fixed_summaries,
        shifted_summaries,
        candidate_blend_summaries,
        final_shifted_summaries,
        final_gated_blend_summaries,
    ) = build_overall_balanced(
        predictions,
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
    payload["candidate_blend_repairs"] = candidate_blend_summaries
    payload["final_shifted_repairs"] = final_shifted_summaries
    payload["final_gated_blend_repairs"] = final_gated_blend_summaries

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
    for step in candidate_blend_summaries:
        print(f"{step['name']}_rows={step['applied_rows']}")
    for step in final_shifted_summaries:
        print(f"{step['name']}_rows={step['applied_rows']}")
    for step in final_gated_blend_summaries:
        print(f"{step['name']}_rows={step['applied_rows']}")
    print(f"predictions_csv={artifacts['predictions_csv']}")
    print(f"metrics_json={artifacts['metrics_json']}")
    print(f"hourly_csv={hourly_path}")
    print(f"plot_png={artifacts['plot_png']}")


if __name__ == "__main__":
    main()
