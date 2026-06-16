# Neural Hybrid Best Summary

Updated: 2026-06-16

Current best saved artifact:

- Experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`
- Primary prediction column: `daybias31_hb22_midday_d8_b050_abs250_pred`
- 3m WMAPE: `5.9937%`
- 14d WMAPE: `10.3096%`
- All available WMAPE: `6.0571%`
- Evaluation rows: `2232`
- Duplicate datetimes: `0`

Files:

- `output/neural_best_predictions.csv`
- `output/neural_best_metrics.json`
- `output/neural_best_plot.png`
- Source predictions: `output/neural_experiment_daybias31_hb22_midday_d8_b050_abs250_v1_predictions.csv`
- Source metrics: `output/neural_experiment_daybias31_hb22_midday_d8_b050_abs250_v1_metrics.json`
- Date forecast helper: `src/predict_current_best.py`

What improved after `daybias30`:

- Previous promoted best `daybias30`: `6.0941% / 10.5940%`.
- Lag24 profile blend + anti-lag48 evening + morning anti-profile through `lagprofile4`: `6.0218% / 10.3585%`.
- Shifted same-hour repairs through `hourbias22`: `6.0027% / 10.3096%`.
- Final midday shifted daily-bias repair `daybias31`: `5.9937% / 10.3096%`.

Current target status:

- 14d short-term WMAPE target `10-15%`: reached at `10.3096%`.
- 3m long-term WMAPE target `5-6%`: reached at `5.9937%` on the current evaluation window.

Applied adjustment counts added after `daybias30`:

- `lagprofile1_db30_lag24_profabs2000_midday_a005`: `426`
- `lagprofile3_lag24_then_antilag48_eve`: `40`
- `lagprofile4_lp3_roll7_abs1000_morning_an015`: `156`
- `hourbias21_lp4_peakerr_r2_bn015_wmape40`: `260`
- `hourbias22_hb21_peakerr_r8_bn020_wmape40`: `384`
- `daybias31_hb22_midday_d8_b050_abs250`: `24`

Key current regimes:

- `summer_daytime_low`: `35.19%`
- `daytime_low_lt_1000`: `49.77%`
- `cap_spike_evening`: `0.99%`
- `evening_19_23`: `2.76%`

Leakage notes:

- The evaluator enforces one row per factual `datetime`; current best has `0` duplicate datetimes.
- `price_cap` in the promoted artifact is clipped per `price_caps.py`; sanity checks found `0` actual-over-cap rows and `0` pred-over-cap rows.
- Future raw market columns are not used as known future.
- Day-bias corrections use only complete earlier days via shifted rolling daily source bias/WMAPE.
- Same-hour bias corrections use only earlier observations of the same delivery hour via `shift(1).rolling(...)`.
- Candidate/lag/profile corrections use only forecast-time source/candidate/cap groups, lagged prices, historical rolling profiles, and shifted historical advantage signals.
- The current target fact is not used for any forecast-time selector signal.

Remaining issue:

- The 3m target is reached with a narrow margin. The promoted chain should be checked on the next holdout block before treating the last post-processing parameters as production-stable.
