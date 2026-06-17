import argparse
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from apply_day_bias_adjuster import apply_day_bias_adjustment
from apply_candidate_blend_adjuster import apply_candidate_blend_adjustment
from apply_group_bias_adjuster import apply_group_bias_adjustment
from apply_hour_bias_adjuster import apply_hour_bias_adjustment
from apply_lag24_blend_adjuster import add_lag24_from_history, apply_lag24_blend_adjustment
from prediction_limits import MIN_MARKET_PRICE, clip_price_forecast


SOURCE_COL = "analog_ratio_all_b012_k4_c050_pred"
HOURBIAS7_COL = "hourbias7_mean2_bn010_peak_wmape35_pred"
GROUPBIAS6_COL = "groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred"
LAG24BLEND1_COL = "lag24blend1_daily2_night_a100_adv0_pred"
LAG24BLEND2_COL = "lag24blend2_sim_absge500_night_an010_pred"
DAYBIAS15_COL = "daybias15_morning3_night_d5_b030_abs100_pred"
LAG24BLEND3_COL = "lag24blend3_profileabs_ge3000_all_an010_pred"
LAG24BLEND4_COL = "lag24blend4_allprof_abs100_all_a100_pred"
LAG24BLEND5_COL = "lag24blend5_night_profilele1000_a005_pred"
LAG24BLEND6_COL = "lag24blend6_nightprof_all_reldiff005_an010_pred"
DAYBIAS16_COL = "daybias16_final_critical_d5_b050_abs300_pred"
DAYBIAS17_COL = "daybias17_critical_then_all_d5_b120_wmape15_pred"
HOURBIAS8_COL = "hourbias8_final_night_r1_b010_abs300_pred"
HOURBIAS9_COL = "hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred"
HOURBIAS10_COL = "hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred"
LAG24BLEND7_COL = "lag24blend7_h10_night_abs250_a080_pred"
LAG24BLEND8_COL = "lag24blend8_abs250_then_profile750_an020_pred"
DAYBIAS18_COL = "daybias18_lag8_nooneve_d5_b150_wmape15_pred"
DAYBIAS19_COL = "daybias19_nooneve_d5_then_d1_b020_wmape12_pred"
HOURBIAS11_COL = "hourbias11_db19_evening_r3_mean_b100_wmape20_pred"
HOURBIAS12_COL = "hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred"
GROUPBIAS9_COL = "groupbias9_h12_ratiofine21_med_all_b012_abs100_pred"
GROUPBIAS10_COL = "groupbias10_ratiofine_b012_then_ratiosummer_b020_pred"
GROUPBIAS11_COL = "groupbias11_ratio2_mean_all_bn010_wmape20_pred"
HOURBIAS13_COL = "hourbias13_gb11_h78901117_r5_med_bn010_abs100_pred"
DAYBIAS20_COL = "daybias20_hb13_nooneve_d5_bn030_abs250_pred"
HOURBIAS14_COL = "hourbias14_db20_h789111718_r1_b010_wmape25_pred"
DAYBIAS21_COL = "daybias21_hb14_nooneve_d21_bn030_abs100_pred"
LAG24BLEND9_COL = "lag24blend9_db21_hourall_r3_mean_an005_advn500_pred"
LAG24BLEND10_COL = "lag24blend10_all_then_night_r2_mean_an010_advn250_pred"
HOURBIAS15_COL = "hourbias15_lag10_evening_r8_mean_bn030_abs300_pred"
HOURBIAS16_COL = "hourbias16_h15_evening_then_morning_pred"
DAYBIAS22_COL = "daybias22_h16_h789111718_d14_bn050_wmape10_pred"
DAYBIAS23_COL = "daybias23_h789_then_evening_pred"
LAG24BLEND11_COL = "lag24blend11_db23_hour21_all_an020_advn250_pred"
GROUPBIAS12_COL = "groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred"
HOURBIAS17_COL = "hourbias17_gb12_midday_r21_med_bn050_abs250_pred"
DAYBIAS24_COL = "daybias24_h17_all_d14_b120_wmape12_pred"
CANDBLEND1_COL = "candblend1_h24_sr5_med_eve_ge1000_an030_pred"
CANDBLEND2_COL = "candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred"
CANDBLEND3_COL = "candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred"
DAYBIAS25_COL = "daybias25_cb3_all_d14_b120_wmape12_pred"
CANDBLEND4_COL = "candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred"
CANDBLEND5_COL = "candblend5_cb4_prof3_srdb8_med_day_none_a030_pred"
DAYBIAS26_COL = "daybias26_cb5_all_d14_b120_wmape12_pred"
CANDBLEND6_COL = "candblend6_db26_h24_cr13_mean_day_le2000_an030_pred"
CANDBLEND7_COL = "candblend7_cb6_prof3_srdb8_med_day_none_a030_pred"
DAYBIAS27_COL = "daybias27_cb7_all_d14_b120_wmape12_pred"
CANDBLEND8_COL = "candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred"
CANDBLEND9_COL = "candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred"
DAYBIAS29_COL = "daybias29_cb9_midday_d1_b010_abs500_pred"
DAYBIAS30_COL = "daybias30_midday_then_all_d8_bn030_wmape10_pred"
LAGPROFILE1_COL = "lagprofile1_db30_lag24_profabs2000_midday_a005_pred"
LAGPROFILE3_COL = "lagprofile3_lag24_then_antilag48_eve_pred"
LAGPROFILE4_COL = "lagprofile4_lp3_roll7_abs1000_morning_an015_pred"
HOURBIAS21_COL = "hourbias21_lp4_peakerr_r2_bn015_wmape40_pred"
HOURBIAS22_COL = "hourbias22_hb21_peakerr_r8_bn020_wmape40_pred"
FINAL_COL = "daybias31_hb22_midday_d8_b050_abs250_pred"
RARE_LAG24_RESCUE_APPLIED_COL = "rare_lag24_midday_rescue_applied"
RARE_LAG24_RESCUE_DAY_GATE_COL = "rare_lag24_midday_rescue_day_gate"


CHAIN = [
    (
        apply_day_bias_adjustment,
        {
            "source_col": SOURCE_COL,
            "output_col": "daybias1_roll3_b042_day_abs300_pred",
            "rolling_days": 3,
            "beta": 0.42,
            "hours": "10-18",
            "gate": "absbias",
            "gate_threshold": 300.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias1_roll3_b042_day_abs300_pred",
            "output_col": "daybias2_roll1_bn021_dayeve_wmape12_pred",
            "rolling_days": 1,
            "beta": -0.21,
            "hours": "10-23",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "daybias2_roll1_bn021_dayeve_wmape12_pred",
            "output_col": "hourbias_roll3_bn020_day_wmape20_pred",
            "rolling_hours": 3,
            "stat": "mean",
            "beta": -0.2,
            "hours": "10-18",
            "gate": "wmape",
            "gate_threshold": 20.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "hourbias_roll3_bn020_day_wmape20_pred",
            "output_col": "hourbias2_roll21_b010_peak_abs150_pred",
            "rolling_hours": 21,
            "stat": "mean",
            "beta": 0.1,
            "hours": "0,7,8,9,11,12,13,14,15,16,17,21,22",
            "gate": "absbias",
            "gate_threshold": 150.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "hourbias2_roll21_b010_peak_abs150_pred",
            "output_col": "hourbias3_roll3_b015_morning_abs500_pred",
            "rolling_hours": 3,
            "stat": "mean",
            "beta": 0.15,
            "hours": "7-10",
            "gate": "absbias",
            "gate_threshold": 500.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "hourbias3_roll3_b015_morning_abs500_pred",
            "output_col": "hourbias4_roll14_bn010_all_wmape12_pred",
            "rolling_hours": 14,
            "stat": "mean",
            "beta": -0.1,
            "hours": "all",
            "gate": "wmape",
            "gate_threshold": 12.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "hourbias4_roll14_bn010_all_wmape12_pred",
            "output_col": "hourbias5_med21_b030_peak_wmape25_pred",
            "rolling_hours": 21,
            "stat": "median",
            "beta": 0.3,
            "hours": "0,7,8,9,11,12,13,14,15,16,17,21,22",
            "gate": "wmape",
            "gate_threshold": 25.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "hourbias5_med21_b030_peak_wmape25_pred",
            "output_col": "hourbias6_mean3_bn020_day_wmape30_pred",
            "rolling_hours": 3,
            "stat": "mean",
            "beta": -0.2,
            "hours": "10-18",
            "gate": "wmape",
            "gate_threshold": 30.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": "hourbias6_mean3_bn020_day_wmape30_pred",
            "output_col": HOURBIAS7_COL,
            "rolling_hours": 2,
            "stat": "mean",
            "beta": -0.1,
            "hours": "0,7,8,9,11,12,13,14,15,16,17,21,22",
            "gate": "wmape",
            "gate_threshold": 35.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": HOURBIAS7_COL,
            "output_col": "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
            "group_by": "hour,source_bin",
            "source_bins": "-1,50,250,500,1000,3000,7000,12000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 10,
            "stat": "median",
            "beta": 0.5,
            "hours": "peakerr",
            "gate": "wmape",
            "gate_threshold": 12.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
            "output_col": "groupbias2_ratiobin8_mean_b065_evening_abs600_pred",
            "group_by": "hour,source_ratio_bin",
            "source_bins": "-1,50,250,500,1000,3000,7000,12000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 8,
            "stat": "mean",
            "beta": 0.65,
            "hours": "evening",
            "gate": "absbias",
            "gate_threshold": 600.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": "groupbias2_ratiobin8_mean_b065_evening_abs600_pred",
            "output_col": "groupbias3_market1_med_b010_night_abs150_pred",
            "group_by": "hour,source_bin",
            "source_bins": "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 1,
            "stat": "median",
            "beta": 0.1,
            "hours": "night",
            "gate": "absbias",
            "gate_threshold": 150.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": "groupbias3_market1_med_b010_night_abs150_pred",
            "output_col": "groupbias4_hourweekend12_med_bn025_all_abs400_pred",
            "group_by": "hour,weekend",
            "source_bins": "-1,50,250,500,1000,3000,7000,12000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 12,
            "stat": "median",
            "beta": -0.25,
            "hours": "all",
            "gate": "absbias",
            "gate_threshold": 400.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": "groupbias4_hourweekend12_med_bn025_all_abs400_pred",
            "output_col": "groupbias5_market1_med_bn025_evening_wmape12_pred",
            "group_by": "hour,source_bin",
            "source_bins": "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 1,
            "stat": "median",
            "beta": -0.25,
            "hours": "evening",
            "gate": "wmape",
            "gate_threshold": 12.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": "groupbias5_market1_med_bn025_evening_wmape12_pred",
            "output_col": GROUPBIAS6_COL,
            "group_by": "hour,summer,source_bin",
            "source_bins": "-1,50,250,500,1000,1500,3000,7000,12000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 10,
            "stat": "mean",
            "beta": -0.4,
            "hours": "midday",
            "gate": "absbias",
            "gate_threshold": 600.0,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": GROUPBIAS6_COL,
            "output_col": LAG24BLEND1_COL,
            "lag_col": "f_price_lag_24",
            "mode": "daily",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "night",
            "advantage_threshold": 0.0,
            "alpha": 1.0,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAG24BLEND1_COL,
            "signal_source_col": GROUPBIAS6_COL,
            "output_col": LAG24BLEND2_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "night",
            "advantage_threshold": 0.0,
            "similarity_metric": "absdiff",
            "similarity_op": "ge",
            "similarity_threshold": 500.0,
            "alpha": -0.1,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": LAG24BLEND2_COL,
            "output_col": "daybias3_nm_d1_b050_wmape15_pred",
            "rolling_days": 1,
            "beta": 0.5,
            "hours": "0-4,7-9",
            "gate": "wmape",
            "gate_threshold": 15.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias3_nm_d1_b050_wmape15_pred",
            "output_col": "daybias4_all_d2_b120_wmape20_pred",
            "rolling_days": 2,
            "beta": 1.2,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 20.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias4_all_d2_b120_wmape20_pred",
            "output_col": "daybias5_midday11_d1_bn120_wmape20_pred",
            "rolling_days": 1,
            "beta": -1.2,
            "hours": "11-15",
            "gate": "wmape",
            "gate_threshold": 20.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias5_midday11_d1_bn120_wmape20_pred",
            "output_col": "daybias6_critical_d14_bn150_wmape8_pred",
            "rolling_days": 14,
            "beta": -1.5,
            "hours": "0,2,4,7,8,9,11,15,17,18,21",
            "gate": "wmape",
            "gate_threshold": 8.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias6_critical_d14_bn150_wmape8_pred",
            "output_col": "daybias7_daylow_d3_b150_wmape15_pred",
            "rolling_days": 3,
            "beta": 1.5,
            "hours": "10-16",
            "gate": "wmape",
            "gate_threshold": 15.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias7_daylow_d3_b150_wmape15_pred",
            "output_col": "daybias8_midday10_d3_b120_abs500_pred",
            "rolling_days": 3,
            "beta": 1.2,
            "hours": "10-15",
            "gate": "absbias",
            "gate_threshold": 500.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias8_midday10_d3_b120_abs500_pred",
            "output_col": "daybias9_morning79_d7_bn150_wmape12_pred",
            "rolling_days": 7,
            "beta": -1.5,
            "hours": "7-9",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias9_morning79_d7_bn150_wmape12_pred",
            "output_col": "daybias10_daylow_d2_bn020_abs100_pred",
            "rolling_days": 2,
            "beta": -0.2,
            "hours": "10-16",
            "gate": "absbias",
            "gate_threshold": 100.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias10_daylow_d2_bn020_abs100_pred",
            "output_col": "daybias11_daylow_d2_b150_abs700_pred",
            "rolling_days": 2,
            "beta": 1.5,
            "hours": "10-16",
            "gate": "absbias",
            "gate_threshold": 700.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias11_daylow_d2_b150_abs700_pred",
            "output_col": "daybias12_midday11_d5_bn150_wmape15_pred",
            "rolling_days": 5,
            "beta": -1.5,
            "hours": "11-15",
            "gate": "wmape",
            "gate_threshold": 15.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias12_midday11_d5_bn150_wmape15_pred",
            "output_col": "daybias13_nooneve_d7_bn050_abs150_pred",
            "rolling_days": 7,
            "beta": -0.5,
            "hours": "11-15,17-18",
            "gate": "absbias",
            "gate_threshold": 150.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias13_nooneve_d7_bn050_abs150_pred",
            "output_col": "daybias14_morning79_d1_bn150_wmape20_pred",
            "rolling_days": 1,
            "beta": -1.5,
            "hours": "7-9",
            "gate": "wmape",
            "gate_threshold": 20.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": "daybias14_morning79_d1_bn150_wmape20_pred",
            "output_col": DAYBIAS15_COL,
            "rolling_days": 5,
            "beta": 0.3,
            "hours": "0-6,23",
            "gate": "absbias",
            "gate_threshold": 100.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": DAYBIAS15_COL,
            "signal_source_col": DAYBIAS15_COL,
            "output_col": LAG24BLEND3_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "all",
            "advantage_threshold": 0.0,
            "similarity_metric": "profile_abs",
            "similarity_op": "ge",
            "similarity_threshold": 3000.0,
            "alpha": -0.1,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAG24BLEND3_COL,
            "signal_source_col": LAG24BLEND3_COL,
            "output_col": LAG24BLEND4_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "all",
            "advantage_threshold": 0.0,
            "similarity_metric": "absdiff",
            "similarity_op": "le",
            "similarity_threshold": 100.0,
            "alpha": 1.0,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAG24BLEND4_COL,
            "signal_source_col": LAG24BLEND4_COL,
            "output_col": LAG24BLEND5_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "night",
            "advantage_threshold": 0.0,
            "similarity_metric": "profile_abs",
            "similarity_op": "le",
            "similarity_threshold": 1000.0,
            "alpha": 0.05,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAG24BLEND5_COL,
            "signal_source_col": LAG24BLEND5_COL,
            "output_col": LAG24BLEND6_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "all",
            "advantage_threshold": 0.0,
            "similarity_metric": "reldiff",
            "similarity_op": "le",
            "similarity_threshold": 0.05,
            "alpha": -0.1,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": LAG24BLEND6_COL,
            "output_col": DAYBIAS16_COL,
            "rolling_days": 5,
            "beta": 0.5,
            "hours": "0,2,4,7,8,9,11,15,17,18,21",
            "gate": "absbias",
            "gate_threshold": 300.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": DAYBIAS16_COL,
            "output_col": DAYBIAS17_COL,
            "rolling_days": 5,
            "beta": 1.2,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 15.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": DAYBIAS17_COL,
            "output_col": HOURBIAS8_COL,
            "rolling_hours": 1,
            "stat": "mean",
            "beta": 0.1,
            "hours": "0-6,23",
            "gate": "absbias",
            "gate_threshold": 300.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": HOURBIAS8_COL,
            "output_col": HOURBIAS9_COL,
            "rolling_hours": 21,
            "stat": "median",
            "beta": -0.7,
            "hours": "10-16",
            "gate": "wmape",
            "gate_threshold": 15.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": HOURBIAS9_COL,
            "output_col": HOURBIAS10_COL,
            "rolling_hours": 3,
            "stat": "median",
            "beta": -0.3,
            "hours": "0-6,23",
            "gate": "wmape",
            "gate_threshold": 20.0,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": HOURBIAS10_COL,
            "signal_source_col": HOURBIAS10_COL,
            "output_col": LAG24BLEND7_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "night",
            "advantage_threshold": 0.0,
            "similarity_metric": "absdiff",
            "similarity_op": "le",
            "similarity_threshold": 250.0,
            "alpha": 0.8,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAG24BLEND7_COL,
            "signal_source_col": LAG24BLEND7_COL,
            "output_col": LAG24BLEND8_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "night",
            "advantage_threshold": 0.0,
            "similarity_metric": "profile_abs",
            "similarity_op": "le",
            "similarity_threshold": 750.0,
            "alpha": -0.2,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": LAG24BLEND8_COL,
            "output_col": DAYBIAS18_COL,
            "rolling_days": 5,
            "beta": 1.5,
            "hours": "11-15,17-18",
            "gate": "wmape",
            "gate_threshold": 15.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": DAYBIAS18_COL,
            "output_col": DAYBIAS19_COL,
            "rolling_days": 1,
            "beta": 0.2,
            "hours": "11-15,17-18",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": DAYBIAS19_COL,
            "output_col": HOURBIAS11_COL,
            "rolling_hours": 3,
            "stat": "mean",
            "beta": 1.0,
            "hours": "19-23",
            "gate": "wmape",
            "gate_threshold": 20.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": HOURBIAS11_COL,
            "output_col": HOURBIAS12_COL,
            "rolling_hours": 7,
            "stat": "mean",
            "beta": -0.1,
            "hours": "11-16",
            "gate": "absbias",
            "gate_threshold": 300.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": HOURBIAS12_COL,
            "output_col": GROUPBIAS9_COL,
            "group_by": "hour,source_ratio_bin",
            "source_bins": "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000",
            "ratio_bins": "-0.01,0.005,0.01,0.02,0.03,0.05,0.08,0.12,0.2,0.35,0.55,0.75,0.9,0.98,1.01",
            "rolling_rows": 21,
            "stat": "median",
            "beta": 0.12,
            "hours": "all",
            "gate": "absbias",
            "gate_threshold": 100.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": GROUPBIAS9_COL,
            "output_col": GROUPBIAS10_COL,
            "group_by": "hour,source_ratio_bin,summer",
            "source_bins": "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 3,
            "stat": "median",
            "beta": 0.2,
            "hours": "peakerr",
            "gate": "wmape",
            "gate_threshold": 35.0,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": GROUPBIAS10_COL,
            "output_col": GROUPBIAS11_COL,
            "group_by": "hour,source_ratio_bin",
            "source_bins": "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000",
            "ratio_bins": "-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01",
            "rolling_rows": 2,
            "stat": "mean",
            "beta": -0.1,
            "hours": "all",
            "gate": "wmape",
            "gate_threshold": 20.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": GROUPBIAS11_COL,
            "output_col": HOURBIAS13_COL,
            "rolling_hours": 5,
            "stat": "median",
            "beta": -0.1,
            "hours": "7-9,11,17",
            "gate": "absbias",
            "gate_threshold": 100.0,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": HOURBIAS13_COL,
            "output_col": DAYBIAS20_COL,
            "rolling_days": 5,
            "beta": -0.3,
            "hours": "11-15,17-18",
            "gate": "absbias",
            "gate_threshold": 250.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": DAYBIAS20_COL,
            "output_col": HOURBIAS14_COL,
            "rolling_hours": 1,
            "stat": "mean",
            "beta": 0.1,
            "hours": "7-9,11,17,18",
            "gate": "wmape",
            "gate_threshold": 25.0,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": HOURBIAS14_COL,
            "output_col": DAYBIAS21_COL,
            "rolling_days": 21,
            "beta": -0.3,
            "hours": "11-15,17-18",
            "gate": "absbias",
            "gate_threshold": 100.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": DAYBIAS21_COL,
            "signal_source_col": DAYBIAS21_COL,
            "output_col": LAG24BLEND9_COL,
            "lag_col": "f_price_lag_24",
            "mode": "hour",
            "rolling_window": 3,
            "stat": "mean",
            "hours": "all",
            "advantage_threshold": -500.0,
            "similarity_metric": "ratio",
            "similarity_op": "le",
            "similarity_threshold": 0.05,
            "alpha": -0.05,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAG24BLEND9_COL,
            "signal_source_col": LAG24BLEND9_COL,
            "output_col": LAG24BLEND10_COL,
            "lag_col": "f_price_lag_24",
            "mode": "hour",
            "rolling_window": 2,
            "stat": "mean",
            "hours": "night",
            "advantage_threshold": -250.0,
            "similarity_metric": "ratio",
            "similarity_op": "le",
            "similarity_threshold": 0.05,
            "alpha": -0.1,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": LAG24BLEND10_COL,
            "output_col": HOURBIAS15_COL,
            "rolling_hours": 8,
            "stat": "mean",
            "beta": -0.3,
            "hours": "19-23",
            "gate": "absbias",
            "gate_threshold": 300.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": HOURBIAS15_COL,
            "output_col": HOURBIAS16_COL,
            "rolling_hours": 1,
            "stat": "mean",
            "beta": 0.05,
            "hours": "7-9,11,17,18",
            "gate": "wmape",
            "gate_threshold": 20.0,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": HOURBIAS16_COL,
            "output_col": DAYBIAS22_COL,
            "rolling_days": 14,
            "beta": -0.5,
            "hours": "7-9,11,17,18",
            "gate": "wmape",
            "gate_threshold": 10.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": DAYBIAS22_COL,
            "output_col": DAYBIAS23_COL,
            "rolling_days": 2,
            "beta": 0.15,
            "hours": "19-23",
            "gate": "absbias",
            "gate_threshold": 250.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": DAYBIAS23_COL,
            "signal_source_col": DAYBIAS23_COL,
            "output_col": LAG24BLEND11_COL,
            "lag_col": "f_price_lag_24",
            "mode": "hour",
            "rolling_window": 21,
            "stat": "mean",
            "hours": "all",
            "advantage_threshold": -250.0,
            "similarity_metric": "ratio",
            "similarity_op": "le",
            "similarity_threshold": 0.05,
            "alpha": -0.2,
        },
    ),
    (
        apply_group_bias_adjustment,
        {
            "source_col": LAG24BLEND11_COL,
            "output_col": GROUPBIAS12_COL,
            "group_by": "hour,source_ratio_bin,weekend",
            "source_bins": "-1,100,500,1000,2000,4000,7000,10000,13000,1000000000",
            "ratio_bins": "-0.01,0.01,0.05,0.1,0.2,0.5,0.85,0.98,1.01",
            "rolling_rows": 5,
            "stat": "median",
            "beta": -0.3,
            "hours": "7-9,11,17,18",
            "gate": "wmape",
            "gate_threshold": 25.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": GROUPBIAS12_COL,
            "output_col": HOURBIAS17_COL,
            "rolling_hours": 21,
            "stat": "median",
            "beta": -0.5,
            "hours": "11-15",
            "gate": "absbias",
            "gate_threshold": 250.0,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": HOURBIAS17_COL,
            "output_col": DAYBIAS24_COL,
            "rolling_days": 14,
            "beta": 1.2,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": DAYBIAS24_COL,
            "candidate_col": "f_price_lag_24",
            "output_col": CANDBLEND1_COL,
            "group_by": "hour,source_ratio_bin",
            "rolling_rows": 5,
            "stat": "median",
            "advantage_threshold": -100.0,
            "hours": "19-23",
            "distance_op": "ge_abs",
            "distance_threshold": 1000.0,
            "alpha": -0.3,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": CANDBLEND1_COL,
            "candidate_col": "f_price_lag_24",
            "output_col": CANDBLEND2_COL,
            "group_by": "hour,candidate_ratio_bin",
            "rolling_rows": 21,
            "stat": "median",
            "advantage_threshold": -500.0,
            "hours": "night",
            "distance_op": "ge_rel",
            "distance_threshold": 0.1,
            "alpha": 0.1,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": CANDBLEND2_COL,
            "candidate_col": "f_price_lag_24",
            "output_col": CANDBLEND3_COL,
            "group_by": "hour,candidate_ratio_bin",
            "rolling_rows": 13,
            "stat": "mean",
            "advantage_threshold": -250.0,
            "hours": "day",
            "distance_op": "le_abs",
            "distance_threshold": 2000.0,
            "alpha": -0.3,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": CANDBLEND3_COL,
            "output_col": DAYBIAS25_COL,
            "rolling_days": 14,
            "beta": 1.2,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": DAYBIAS25_COL,
            "candidate_col": "f_rolling_mean_hour_3d",
            "output_col": CANDBLEND4_COL,
            "group_by": "hour,weekend",
            "rolling_rows": 3,
            "stat": "median",
            "advantage_threshold": 100.0,
            "hours": "peakerr",
            "distance_op": "ge_abs",
            "distance_threshold": 1000.0,
            "alpha": -0.2,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": CANDBLEND4_COL,
            "candidate_col": "f_rolling_mean_hour_3d",
            "output_col": CANDBLEND5_COL,
            "group_by": "hour,source_ratio_bin,diff_bin",
            "rolling_rows": 8,
            "stat": "median",
            "advantage_threshold": 0.0,
            "hours": "7-18",
            "distance_op": "none",
            "distance_threshold": 0.0,
            "alpha": 0.3,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": CANDBLEND5_COL,
            "output_col": DAYBIAS26_COL,
            "rolling_days": 14,
            "beta": 1.2,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": DAYBIAS26_COL,
            "candidate_col": "f_price_lag_24",
            "output_col": CANDBLEND6_COL,
            "group_by": "hour,candidate_ratio_bin",
            "rolling_rows": 13,
            "stat": "mean",
            "advantage_threshold": -250.0,
            "hours": "day",
            "distance_op": "le_abs",
            "distance_threshold": 2000.0,
            "alpha": -0.3,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": CANDBLEND6_COL,
            "candidate_col": "f_rolling_mean_hour_3d",
            "output_col": CANDBLEND7_COL,
            "group_by": "hour,source_ratio_bin,diff_bin",
            "rolling_rows": 8,
            "stat": "median",
            "advantage_threshold": 0.0,
            "hours": "7-18",
            "distance_op": "none",
            "distance_threshold": 0.0,
            "alpha": 0.3,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": CANDBLEND7_COL,
            "output_col": DAYBIAS27_COL,
            "rolling_days": 14,
            "beta": 1.2,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 12.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": DAYBIAS27_COL,
            "candidate_col": "f_price_lag_48",
            "output_col": CANDBLEND8_COL,
            "group_by": "hour,low_source,low_candidate",
            "rolling_rows": 3,
            "stat": "median",
            "advantage_threshold": -100.0,
            "hours": "11-15",
            "distance_op": "ge_rel",
            "distance_threshold": 0.1,
            "alpha": -0.3,
        },
    ),
    (
        apply_candidate_blend_adjustment,
        {
            "source_col": CANDBLEND8_COL,
            "candidate_col": "f_rolling_mean_hour_7d",
            "output_col": CANDBLEND9_COL,
            "group_by": "hour,summer,source_ratio_bin",
            "rolling_rows": 5,
            "stat": "median",
            "advantage_threshold": 250.0,
            "hours": "all",
            "distance_op": "ge_abs",
            "distance_threshold": 1000.0,
            "alpha": 0.3,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": CANDBLEND9_COL,
            "output_col": DAYBIAS29_COL,
            "rolling_days": 1,
            "beta": 0.1,
            "hours": "11-16",
            "gate": "absbias",
            "gate_threshold": 500.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": DAYBIAS29_COL,
            "output_col": DAYBIAS30_COL,
            "rolling_days": 8,
            "beta": -0.3,
            "hours": "0-23",
            "gate": "wmape",
            "gate_threshold": 10.0,
            "min_day_hours": 24,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": DAYBIAS30_COL,
            "signal_source_col": DAYBIAS30_COL,
            "output_col": LAGPROFILE1_COL,
            "lag_col": "f_price_lag_24",
            "mode": "similarity",
            "rolling_window": 1,
            "stat": "mean",
            "hours": "midday",
            "advantage_threshold": 0.0,
            "similarity_metric": "profile_abs",
            "similarity_op": "le",
            "similarity_threshold": 2000.0,
            "alpha": 0.05,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAGPROFILE1_COL,
            "signal_source_col": LAGPROFILE1_COL,
            "output_col": LAGPROFILE3_COL,
            "lag_col": "f_price_lag_48",
            "mode": "daily",
            "signal_op": "le",
            "rolling_window": 3,
            "stat": "mean",
            "hours": "evening",
            "advantage_threshold": -50.0,
            "similarity_metric": "ratio",
            "similarity_op": "le",
            "similarity_threshold": 0.05,
            "alpha": -0.15,
        },
    ),
    (
        apply_lag24_blend_adjustment,
        {
            "source_col": LAGPROFILE3_COL,
            "signal_source_col": LAGPROFILE3_COL,
            "output_col": LAGPROFILE4_COL,
            "lag_col": "f_rolling_mean_hour_7d",
            "mode": "similarity",
            "rolling_window": 1,
            "stat": "mean",
            "hours": "morning",
            "advantage_threshold": 0.0,
            "similarity_metric": "absdiff",
            "similarity_op": "le",
            "similarity_threshold": 1000.0,
            "alpha": -0.15,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": LAGPROFILE4_COL,
            "output_col": HOURBIAS21_COL,
            "rolling_hours": 2,
            "stat": "mean",
            "beta": -0.15,
            "hours": "0,7-9,11-17,21-22",
            "gate": "wmape",
            "gate_threshold": 40.0,
        },
    ),
    (
        apply_hour_bias_adjustment,
        {
            "source_col": HOURBIAS21_COL,
            "output_col": HOURBIAS22_COL,
            "rolling_hours": 8,
            "stat": "mean",
            "beta": -0.2,
            "hours": "0,7-9,11-17,21-22",
            "gate": "wmape",
            "gate_threshold": 40.0,
        },
    ),
    (
        apply_day_bias_adjustment,
        {
            "source_col": HOURBIAS22_COL,
            "output_col": FINAL_COL,
            "rolling_days": 8,
            "beta": 0.5,
            "hours": "11-16",
            "gate": "absbias",
            "gate_threshold": 250.0,
            "min_day_hours": 24,
        },
    ),
]


def parse_target_date(value):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return pd.Timestamp(pd.to_datetime(value, format=fmt).date())
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}. Use DD.MM.YYYY or YYYY-MM-DD.")


def load_best_history(path):
    frame = pd.read_csv(path, parse_dates=["datetime"])
    required = {"datetime", "actual", "price_cap", SOURCE_COL, FINAL_COL}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Best predictions file is missing columns: {sorted(missing)}")
    if frame["datetime"].duplicated().any():
        raise ValueError("Best predictions contain duplicate datetimes.")
    return frame.sort_values("datetime").reset_index(drop=True)


def rows_from_source_debug(source_debug_csv, target_day):
    source = pd.read_csv(source_debug_csv, parse_dates=["datetime"]).sort_values("datetime")
    required = {"datetime", "final_pred"}
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"Source debug CSV is missing columns: {sorted(missing)}")
    source = source[source["datetime"].dt.normalize() == target_day].copy()
    if len(source) != 24:
        raise ValueError(f"Expected 24 source rows for {target_day.date()}, found {len(source)}")

    price_cap = source["price_cap"] if "price_cap" in source.columns else pd.Series(15000.0, index=source.index)
    rows = pd.DataFrame(
        {
            "datetime": source["datetime"],
            "actual": np.nan,
            "price_cap": pd.to_numeric(price_cap, errors="coerce"),
            SOURCE_COL: pd.to_numeric(source["final_pred"], errors="coerce"),
        }
    )
    rows[SOURCE_COL] = clip_price_forecast(rows[SOURCE_COL], rows["price_cap"])
    if "production_base_pred" in source.columns:
        rows["production_base_pred"] = clip_price_forecast(
            pd.to_numeric(source["production_base_pred"], errors="coerce"),
            rows["price_cap"],
        )
    rows["forecast_source_note"] = f"{Path(source_debug_csv).name}.final_pred_as_{SOURCE_COL}"
    return rows


def apply_current_best_chain(history, target_rows):
    frame = pd.concat([history, target_rows], ignore_index=True, sort=False)
    frame = frame.sort_values("datetime").reset_index(drop=True)
    for func, params in CHAIN:
        frame = func(frame, SimpleNamespace(**params))
    frame = apply_rare_lag24_midday_rescue(frame)
    return frame


def apply_rare_lag24_midday_rescue(frame):
    frame = add_lag24_from_history(frame, "f_price_lag_24").copy()
    if FINAL_COL not in frame.columns or "f_price_lag_24" not in frame.columns:
        return frame

    source = pd.to_numeric(frame[FINAL_COL], errors="coerce")
    lag24 = pd.to_numeric(frame["f_price_lag_24"], errors="coerce")
    hour = frame["datetime"].dt.hour
    day_key = frame["datetime"].dt.normalize()
    rescue_hours = hour.between(9, 15)

    day_profile = pd.DataFrame(
        {
            "date": day_key,
            "hour": hour,
            "source": source,
            "lag24": lag24,
        }
    )
    day_profile = day_profile[day_profile["hour"].between(9, 15)].groupby("date").agg(
        rows=("source", "size"),
        source_mean=("source", "mean"),
        source_median=("source", "median"),
        source_le100=("source", lambda values: int((values <= 100.0).sum())),
        lag_min=("lag24", "min"),
        lag_max=("lag24", "max"),
        lag_up_mean=("lag24", lambda values: float(np.nan)),
    )
    up_mean = (lag24 - source).where(rescue_hours).groupby(day_key).mean()
    day_profile["lag_up_mean"] = up_mean
    day_profile["dow"] = pd.Series(day_profile.index, index=day_profile.index).dt.dayofweek

    day_gate = (
        (day_profile["rows"] == 7)
        & day_profile["dow"].between(0, 4)
        & (day_profile["source_mean"] <= 800.0)
        & (day_profile["source_median"] <= 100.0)
        & (day_profile["source_le100"] >= 4)
        & (day_profile["lag_min"] >= 500.0)
        & (day_profile["lag_max"] <= 4500.0)
        & (day_profile["lag_up_mean"] >= 500.0)
    )
    gate_by_row = day_key.map(day_gate).fillna(False).to_numpy(dtype=bool)
    selected = gate_by_row & rescue_hours.to_numpy() & lag24.notna().to_numpy()

    frame[RARE_LAG24_RESCUE_DAY_GATE_COL] = gate_by_row.astype("int64")
    frame[RARE_LAG24_RESCUE_APPLIED_COL] = selected.astype("int64")
    rescued = source.copy()
    rescued.loc[selected] = lag24.loc[selected]
    frame[FINAL_COL] = clip_price_forecast(rescued, frame["price_cap"])
    return frame


def save_forecast(day_frame, output_dir, date_iso):
    day_frame = day_frame.copy()
    day_frame[FINAL_COL] = clip_price_forecast(day_frame[FINAL_COL], day_frame["price_cap"])
    public = pd.DataFrame(
        {
            "Hour": day_frame["datetime"].dt.hour + 1,
            "Predicted_Price": day_frame[FINAL_COL].round(2),
            "Price_Cap": day_frame["price_cap"].round(2),
        }
    )
    csv_path = output_dir / f"prediction_{date_iso}_current_best.csv"
    public.to_csv(csv_path, index=False)

    debug_cols = [
        "datetime",
        "actual",
        "price_cap",
        "production_base_pred",
        "f_price_lag_24",
        SOURCE_COL,
        "daybias1_roll3_b042_day_abs300_pred",
        "daybias2_roll1_bn021_dayeve_wmape12_pred",
        "hourbias_roll3_bn020_day_wmape20_pred",
        "hourbias2_roll21_b010_peak_abs150_pred",
        "hourbias3_roll3_b015_morning_abs500_pred",
        "hourbias4_roll14_bn010_all_wmape12_pred",
        "hourbias5_med21_b030_peak_wmape25_pred",
        "hourbias6_mean3_bn020_day_wmape30_pred",
        HOURBIAS7_COL,
        "groupbias1_srcbin10_med_b050_peak_wmape12_pred",
        "groupbias2_ratiobin8_mean_b065_evening_abs600_pred",
        "groupbias3_market1_med_b010_night_abs150_pred",
        "groupbias4_hourweekend12_med_bn025_all_abs400_pred",
        "groupbias5_market1_med_bn025_evening_wmape12_pred",
        GROUPBIAS6_COL,
        LAG24BLEND1_COL,
        f"{LAG24BLEND1_COL}_lag24_signal",
        LAG24BLEND2_COL,
        f"{LAG24BLEND2_COL}_lag24_signal",
        "daybias3_nm_d1_b050_wmape15_pred",
        "daybias4_all_d2_b120_wmape20_pred",
        "daybias5_midday11_d1_bn120_wmape20_pred",
        "daybias6_critical_d14_bn150_wmape8_pred",
        "daybias7_daylow_d3_b150_wmape15_pred",
        "daybias8_midday10_d3_b120_abs500_pred",
        "daybias9_morning79_d7_bn150_wmape12_pred",
        "daybias10_daylow_d2_bn020_abs100_pred",
        "daybias11_daylow_d2_b150_abs700_pred",
        "daybias12_midday11_d5_bn150_wmape15_pred",
        "daybias13_nooneve_d7_bn050_abs150_pred",
        "daybias14_morning79_d1_bn150_wmape20_pred",
        DAYBIAS15_COL,
        LAG24BLEND3_COL,
        f"{LAG24BLEND3_COL}_lag24_signal",
        LAG24BLEND4_COL,
        f"{LAG24BLEND4_COL}_lag24_signal",
        LAG24BLEND5_COL,
        f"{LAG24BLEND5_COL}_lag24_signal",
        LAG24BLEND6_COL,
        f"{LAG24BLEND6_COL}_lag24_signal",
        DAYBIAS16_COL,
        DAYBIAS17_COL,
        HOURBIAS8_COL,
        HOURBIAS9_COL,
        HOURBIAS10_COL,
        LAG24BLEND7_COL,
        f"{LAG24BLEND7_COL}_lag24_signal",
        LAG24BLEND8_COL,
        f"{LAG24BLEND8_COL}_lag24_signal",
        DAYBIAS18_COL,
        DAYBIAS19_COL,
        HOURBIAS11_COL,
        HOURBIAS12_COL,
        GROUPBIAS9_COL,
        GROUPBIAS10_COL,
        GROUPBIAS11_COL,
        HOURBIAS13_COL,
        DAYBIAS20_COL,
        HOURBIAS14_COL,
        DAYBIAS21_COL,
        LAG24BLEND9_COL,
        f"{LAG24BLEND9_COL}_lag24_signal",
        LAG24BLEND10_COL,
        f"{LAG24BLEND10_COL}_lag24_signal",
        HOURBIAS15_COL,
        HOURBIAS16_COL,
        DAYBIAS22_COL,
        DAYBIAS23_COL,
        LAG24BLEND11_COL,
        f"{LAG24BLEND11_COL}_lag24_signal",
        GROUPBIAS12_COL,
        HOURBIAS17_COL,
        DAYBIAS24_COL,
        CANDBLEND1_COL,
        CANDBLEND2_COL,
        CANDBLEND3_COL,
        DAYBIAS25_COL,
        CANDBLEND4_COL,
        CANDBLEND5_COL,
        DAYBIAS26_COL,
        CANDBLEND6_COL,
        CANDBLEND7_COL,
        DAYBIAS27_COL,
        CANDBLEND8_COL,
        CANDBLEND9_COL,
        DAYBIAS29_COL,
        DAYBIAS30_COL,
        LAGPROFILE1_COL,
        f"{LAGPROFILE1_COL}_lag24_signal",
        LAGPROFILE3_COL,
        f"{LAGPROFILE3_COL}_lag24_signal",
        LAGPROFILE4_COL,
        f"{LAGPROFILE4_COL}_lag24_signal",
        HOURBIAS21_COL,
        f"{HOURBIAS21_COL}_hour_wmape_signal",
        HOURBIAS22_COL,
        f"{HOURBIAS22_COL}_hour_wmape_signal",
        FINAL_COL,
    ]
    debug_cols += [col for col in day_frame.columns if col.endswith("_applied")]
    debug_cols = [col for col in dict.fromkeys(debug_cols) if col in day_frame.columns]
    debug_path = output_dir / f"prediction_{date_iso}_current_best_debug.csv"
    day_frame[debug_cols].to_csv(debug_path, index=False)

    plot_path = output_dir / f"prediction_{date_iso}_current_best.png"
    plt.figure(figsize=(13, 6))
    plt.plot(public["Hour"], public["Predicted_Price"], marker="o", label="Current best forecast")
    plt.plot(public["Hour"], public["Price_Cap"], linestyle="--", alpha=0.5, label="Price cap")
    plt.axhline(MIN_MARKET_PRICE, linestyle=":", alpha=0.5, color="gray", label="Price floor")
    plt.xticks(range(1, 25))
    plt.grid(True, alpha=0.25)
    plt.title(f"Current best forecast for {date_iso}")
    plt.xlabel("Hour")
    plt.ylabel("UAH/MWh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=140)
    plt.close()
    return public, csv_path, debug_path, plot_path


def save_comparison(day_frame, output_dir, date_iso):
    day_frame = day_frame.copy()
    day_frame[FINAL_COL] = clip_price_forecast(day_frame[FINAL_COL], day_frame["price_cap"])
    actual_rows = day_frame.dropna(subset=["actual", FINAL_COL]).copy()
    if actual_rows.empty:
        return None

    comparison = pd.DataFrame(
        {
            "Hour": actual_rows["datetime"].dt.hour + 1,
            "Actual_Price": actual_rows["actual"].astype(float),
            "Predicted_Price": actual_rows[FINAL_COL].astype(float),
            "Price_Cap": actual_rows["price_cap"].astype(float),
        }
    )
    comparison["Abs_Error"] = (comparison["Predicted_Price"] - comparison["Actual_Price"]).abs()
    comparison["APE_pct"] = np.where(
        comparison["Actual_Price"].abs() > 1e-9,
        comparison["Abs_Error"] / comparison["Actual_Price"].abs() * 100.0,
        np.nan,
    )
    wmape = comparison["Abs_Error"].sum() / comparison["Actual_Price"].abs().sum() * 100.0
    mae = comparison["Abs_Error"].mean()
    bias = (comparison["Predicted_Price"] - comparison["Actual_Price"]).mean()

    rounded = comparison.copy()
    for col in ["Actual_Price", "Predicted_Price", "Price_Cap", "Abs_Error", "APE_pct"]:
        rounded[col] = rounded[col].round(2)
    comparison_path = output_dir / f"comparison_{date_iso}_current_best.csv"
    rounded.to_csv(comparison_path, index=False)

    metrics = {
        "date": date_iso,
        "prediction_column": FINAL_COL,
        "rows": int(len(comparison)),
        "wmape": float(wmape),
        "mae": float(mae),
        "bias": float(bias),
    }
    metrics_path = output_dir / f"comparison_{date_iso}_current_best_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    plot_path = output_dir / f"comparison_{date_iso}_current_best.png"
    plt.figure(figsize=(13, 6))
    plt.plot(comparison["Hour"], comparison["Actual_Price"], marker="o", label="Actual")
    plt.plot(comparison["Hour"], comparison["Predicted_Price"], marker="x", linestyle="--", label="Current best forecast")
    plt.xticks(range(1, 25))
    plt.grid(True, alpha=0.25)
    plt.title(f"{date_iso} current best vs actual, WMAPE={wmape:.2f}%")
    plt.xlabel("Hour")
    plt.ylabel("UAH/MWh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=140)
    plt.close()
    return metrics, comparison_path, metrics_path, plot_path


def main():
    parser = argparse.ArgumentParser(description="Create current-best forecast/comparison artifacts for one date.")
    parser.add_argument("date", help="Target date in DD.MM.YYYY or YYYY-MM-DD format.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--best-predictions", default=os.path.join(ROOT_DIR, "output", "neural_best_predictions.csv"))
    parser.add_argument(
        "--source-debug-csv",
        default=None,
        help="Required for dates not present in neural_best_predictions.csv. Expected columns: datetime, final_pred, optional price_cap.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target_day = parse_target_date(args.date)
    date_iso = target_day.strftime("%Y-%m-%d")
    history = load_best_history(args.best_predictions)

    day_mask = history["datetime"].dt.normalize() == target_day
    if day_mask.sum() == 24 and history.loc[day_mask, FINAL_COL].notna().all():
        result_frame = history.copy()
    else:
        source_debug = args.source_debug_csv
        if source_debug is None:
            default_source = output_dir / f"prediction_{date_iso}_best_chain_debug.csv"
            if default_source.exists():
                source_debug = os.fspath(default_source)
        if source_debug is None:
            raise FileNotFoundError(
                f"No backtest rows for {date_iso} and no source debug CSV. "
                f"Pass --source-debug-csv or create output/prediction_{date_iso}_best_chain_debug.csv."
            )
        target_rows = rows_from_source_debug(source_debug, target_day)
        result_frame = apply_current_best_chain(history, target_rows)

    day_frame = result_frame[result_frame["datetime"].dt.normalize() == target_day].copy().sort_values("datetime")
    if len(day_frame) != 24:
        raise ValueError(f"Expected 24 output rows for {date_iso}, found {len(day_frame)}")

    public, csv_path, debug_path, plot_path = save_forecast(day_frame, output_dir, date_iso)
    comparison = save_comparison(day_frame, output_dir, date_iso)

    print(public.to_string(index=False))
    print(f"forecast_csv={csv_path}")
    print(f"debug_csv={debug_path}")
    print(f"plot_png={plot_path}")
    if comparison is not None:
        metrics, comparison_path, metrics_path, comparison_plot = comparison
        print(f"comparison_csv={comparison_path}")
        print(f"comparison_metrics_json={metrics_path}")
        print(f"comparison_plot_png={comparison_plot}")
        print(f"wmape={metrics['wmape']:.4f}% mae={metrics['mae']:.2f} bias={metrics['bias']:.2f}")


if __name__ == "__main__":
    main()
