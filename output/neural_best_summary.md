# Neural Hybrid Best Summary

Updated: 2026-06-17

Canonical best artifact now used as `neural_best`:

- Experiment: `overall_balanced_low_regime_v1`
- Primary prediction column: `overall_balanced_low_regime_pred`
- All available WMAPE: `4.4052%`
- 3m WMAPE: `4.3380%`
- 14d WMAPE: `7.5560%`
- 13d WMAPE: `7.6687%`
- Evaluation rows: `2232`
- Duplicate datetimes: `0`

Why this is the active branch:

- It improves the previous research branch `night_hourratio_final_under5_v1` from `4.9896% / 8.6172% / 8.6138%` to `4.3380% / 7.5560% / 7.6687%` on `3m / 14d / 13d`.
- It improves the old promoted helper `daybias31_hb22_midday_d8_b050_abs250_v1` from `5.9937% / 10.3096%` to `4.3380% / 7.5560%` on `3m / 14d`.
- It keeps the low-regime target close to the requested `~15%`: `summer_daytime_low=10.52%`, `daytime_low_lt_1000=12.77%`.
- It keeps guardrail regimes stable: `cap_spike_evening=1.07%`, `evening_19_23=2.13%`.

Files currently mapped to this canonical best:

- Predictions: `output/neural_best_predictions.csv`
- Metrics: `output/neural_best_metrics.json`
- Plot: `output/neural_best_plot.png`
- Source predictions: `output/neural_experiment_overall_balanced_low_regime_v1_predictions.csv`
- Source metrics: `output/neural_experiment_overall_balanced_low_regime_v1_metrics.json`
- Source plot: `output/neural_experiment_overall_balanced_low_regime_v1_plot.png`

Future-date usage:

- All new validation and forecast comparisons should use `overall_balanced_low_regime_pred` as the canonical model.
- `src/predict_current_best.py` reads the canonical prediction column from `output/neural_best_metrics.json`; it no longer silently replaces missing future rows with the old `daybias31` chain.
- Explicit `daybias31_hb22_midday_d8_b050_abs250_pred` runs are legacy diagnostics only and must be requested with `--allow-legacy-future-fallback`.
- For future dates, use `src/predict_overall_balanced_future.py` with an input CSV that passes the required-column readiness check for `build_overall_balanced_composite.py`.

Next production step:

- Continue improving one unified `overall_balanced_low_regime_v1` pipeline for all dates; do not create date-specific branches.
