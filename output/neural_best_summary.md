# Neural Hybrid Best Summary

Updated: 2026-06-16

Promoted production artifact:

- Experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`
- Primary prediction column: `daybias31_hb22_midday_d8_b050_abs250_pred`
- 3m WMAPE: `5.9937%`
- 14d WMAPE: `10.3096%`
- All available WMAPE: `6.0571%`
- Evaluation rows: `2232`
- Duplicate datetimes: `0`

Best research target artifact:

- Experiment: `night_hourratio_final_under5_v1`
- Primary prediction column: `night_hourratio_final_under5_pred`
- 3m WMAPE: `4.9896%`
- 14d WMAPE: `8.6172%`
- All available WMAPE: `5.0634%`
- Evaluation rows: `2232`
- Duplicate datetimes: `0`
- Min prediction: `10.0`
- Predictions below `10`: `0`
- Predictions above cap: `0`

Files:

- Research predictions: `output/neural_experiment_night_hourratio_final_under5_v1_predictions.csv`
- Research metrics: `output/neural_experiment_night_hourratio_final_under5_v1_metrics.json`
- Research plot: `output/neural_experiment_night_hourratio_final_under5_v1_plot.png`
- Promoted predictions: `output/neural_best_predictions.csv`
- Promoted metrics: `output/neural_best_metrics.json`
- Date forecast helper: `src/predict_current_best.py`

Research status:

- Strict 14d WMAPE target `< 10%`: reached at `8.6172%`.
- Strict 3m WMAPE target `< 5%`: reached at `4.9896%`.
- Production promotion is still separate work because the research chain depends on intermediate tree/ensemble/anchor/current-chain columns that are not yet emitted for future-date forecasts.

Key research regimes:

- `summer_daytime_low`: `24.74%`
- `daytime_low_lt_1000`: `38.45%`
- `cap_spike_evening`: `1.08%`
- `evening_19_23`: `2.15%`

Final research chain after `day13_16_anchor_lowrepair_after_night_v1`:

- `night_hourmonth_bias_after_day13_v1`: `5.3781% / 9.4179%`.
- `day14_16_hourmonth_bias_after_nightmonth_v1`: `5.3726% / 9.4015%`.
- `morning_srcbinweekend_bias_after_night_hour8_v1`: `5.3573% / 9.4146%`.
- `sourcebin_daytime_bias_after_lowrepair_v1`: `5.2665% / 9.1716%`.
- `night_ratio_bias_after_sourcebin_daytime_v1`: `5.2316% / 9.1304%`.
- `day13_16_ratio_wmape15_after_morning7_v1`: `5.1749% / 8.9936%`.
- `day11_15_srcbinweekend_repair_after_morning7_v1`: `5.1086% / 8.7518%`.
- `morning7_10_hourratio_final_push_v1`: `5.0027% / 8.6566%`.
- `night_hourratio_final_under5_v1`: `4.9896% / 8.6172%`.

Leakage and bounds notes:

- The evaluator enforces one row per factual `datetime`; target artifact has `0` duplicate datetimes.
- Forecasts are clipped to `[10, price_cap]`; validation found `0` rows below `10` and `0` rows above cap.
- Shifted group-bias corrections use only forecast-time groups and previous observations via `shift(1).rolling(...)`; the current target fact is not used for any selector signal.

Next production step:

- Recreate the research chain in the future-date forecast pipeline, or replace it with an equivalent production-feasible rolling repair built only from available forecast-time features.
