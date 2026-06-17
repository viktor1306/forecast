
### tcn_reslog_v1

- Split: train days `752`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `96`, history `168`, dropout `0.18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `neural_pred` | 10.77% | 29.63% | 2209 |
| `hybrid_pred` | 10.12% | 29.67% | 2209 |
| `hybrid_recent_calibrated_pred` | 8.94% | 20.85% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_reslog_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_reslog_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_reslog_v1_plot.png`

### tcn_reslog_guard_v1

- Split: train days `752`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `96`, history `168`, dropout `0.18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `neural_pred` | 10.54% | 29.99% | 2209 |
| `hybrid_pred` | 10.01% | 30.07% | 2209 |
| `hybrid_recent_calibrated_pred` | 8.74% | 20.61% | 2209 |
| `hybrid_guarded_pred` | 8.67% | 20.13% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_reslog_guard_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_reslog_guard_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_reslog_guard_v1_plot.png`

### tcn336_reslog_guard_v1

- Split: train days `745`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `128`, history `336`, dropout `0.22`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `neural_pred` | 10.61% | 29.82% | 2209 |
| `hybrid_pred` | 9.86% | 29.75% | 2209 |
| `hybrid_recent_calibrated_pred` | 8.63% | 20.58% | 2209 |
| `hybrid_guarded_pred` | 8.57% | 20.13% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_reslog_guard_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_reslog_guard_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_reslog_guard_v1_plot.png`

### tcn336_reslog_guard_seed123

- Split: train days `745`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `128`, history `336`, dropout `0.22`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `neural_pred` | 10.60% | 30.03% | 2209 |
| `hybrid_pred` | 10.04% | 30.10% | 2209 |
| `hybrid_recent_calibrated_pred` | 8.76% | 20.55% | 2209 |
| `hybrid_guarded_pred` | 8.70% | 20.13% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_reslog_guard_seed123_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_reslog_guard_seed123_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_reslog_guard_seed123_plot.png`

### ensemble_tcn168_336_guard_v1

- Ensemble members: `tcn_reslog_guard_v1`, `tcn336_reslog_guard_v1`.
- Rule: average neural/hybrid predictions outside recent window; keep tree recent calibrator for last 14 days.
- Evaluator still has one row per factual hour.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `ensemble_neural_pred` | 10.47% | 29.81% | 2209 |
| `ensemble_hybrid_pred` | 9.85% | 29.83% | 2209 |
| `ensemble_hybrid_recent_calibrated_pred` | 8.60% | 20.53% | 2209 |
| `hybrid_guarded_pred` | 8.55% | 20.13% | 2209 |

- Predictions: `output\neural_experiment_ensemble_tcn168_336_guard_v1_predictions.csv`
- Metrics: `output\neural_experiment_ensemble_tcn168_336_guard_v1_metrics.json`
- Plot: `output\neural_experiment_ensemble_tcn168_336_guard_v1_plot.png`

### tcn336_val90_guard_v1

- Split: train days `700`, val days `90`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `128`, history `336`, dropout `0.22`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `neural_pred` | 10.72% | 29.79% | 2209 |
| `hybrid_pred` | 10.66% | 29.89% | 2209 |
| `hybrid_recent_calibrated_pred` | 9.38% | 20.40% | 2209 |
| `hybrid_guarded_pred` | 9.35% | 20.13% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_val90_guard_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_val90_guard_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_val90_guard_v1_plot.png`

### split_safe_lgbm_tcn168_v1

- Split: train days `752`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- Tree teacher source: `split-safe`.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `96`, history `168`, dropout `0.18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 58.32% | 92.11% | 2209 |
| `tree_recent_calibrated_pred` | 49.99% | 29.99% | 2209 |
| `neural_pred` | 57.62% | 90.67% | 2209 |
| `hybrid_pred` | 57.68% | 90.75% | 2209 |
| `hybrid_recent_calibrated_pred` | 49.59% | 30.49% | 2209 |
| `hybrid_guarded_pred` | 49.52% | 29.99% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_split_safe_lgbm_tcn168_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_split_safe_lgbm_tcn168_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_split_safe_lgbm_tcn168_v1_plot.png`

### ensemble_tcn168_336_lowprofile_v1

- Input experiment: `ensemble_tcn168_336_guard_v1`.
- Low-profile rule: `price_lag_24 <= 500.0`, `pred - anchor >= 1000.0`, `blend=0.15`, months `5-8`, hours `10-16`.
- Adjusted rows: `23`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_guarded_pred` | 8.55% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.11% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollmin_v1

- Input experiment: `ensemble_tcn168_336_guard_v1`.
- Low-profile rule: `rolling_min_24 <= 500.0`, `pred - anchor >= 1000.0`, `blend=0.15`, months `5-8`, hours `10-16`.
- Adjusted rows: `69`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_guarded_pred` | 8.55% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.59% | 20.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollmin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollmin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollmin_v1_plot.png`

### ensemble_tcn168_336_lowprofile_lag24_v2

- Input experiment: `ensemble_tcn168_336_guard_v1`.
- Low-profile rule: `price_lag_24 <= 500.0`, `pred - anchor >= 0.0`, `blend=0.15`, months `5-8`, hours `10-16`.
- Adjusted rows: `126`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_guarded_pred` | 8.55% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_lag24_v2_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_lag24_v2_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_lag24_v2_plot.png`

### tcn336_lowweighted_guard_v1

- Split: train days `745`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- Tree teacher source: `current`.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `128`, history `336`, dropout `0.22`.
- Weights: daytime `1.8`, evening `1.35`, low-price `2.8`, high-price `1.45`, low BCE `0.1`, high BCE `0.05`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 10.65% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `neural_pred` | 10.79% | 30.85% | 2209 |
| `hybrid_pred` | 10.35% | 30.47% | 2209 |
| `hybrid_recent_calibrated_pred` | 9.03% | 20.64% | 2209 |
| `hybrid_guarded_pred` | 8.97% | 20.13% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_lowweighted_guard_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_lowweighted_guard_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn336_lowweighted_guard_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `1000.0`, blend `0.25`.
- Applied target days: `79`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.51% | 19.84% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge_v1_plot.png`

### ensemble_tcn168_336_lowprofile_recentridge_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `20.0`, blend `0.6`, apply recent days `14`.
- Applied target days: `15`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.42% | 19.16% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v1_plot.png`

### ensemble_tcn168_336_lowprofile_recentridge_v2

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `3.0`, blend `0.7`, apply recent days `14`.
- Applied target days: `15`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.41% | 19.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v2_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v2_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v2_plot.png`

### ensemble_tcn168_336_lowprofile_recentridge_v3

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `3.0`, blend `0.6`, apply recent days `14`.
- Applied target days: `15`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.41% | 19.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v3_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v3_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v3_plot.png`

### ensemble_tcn168_336_lowprofile_recentridge_v5

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `3.0`, blend `0.7`, apply recent days `15`.
- Applied target days: `16`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.39% | 19.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v5_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v5_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v5_plot.png`

### ensemble_tcn168_336_lowprofile_recentridge_v4

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `3.0`, blend `0.6`, apply recent days `15`.
- Applied target days: `16`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.40% | 19.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v4_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v4_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_recentridge_v4_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `3.0`, blend `0.7`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.37% | 19.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_v2

- Input experiment: `ensemble_tcn168_336_lowprofile_lag24_v2`.
- Rolling-origin stacker: source `hybrid_low_profile_pred`, target `resid`, lookback `30` days, min train `14` days, alpha `3.0`, blend `0.6`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `hybrid_low_profile_pred` | 8.54% | 20.07% | 2209 |
| `rolling_stack_pred` | 8.36% | 19.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_v2_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_v2_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_v2_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_v2`.
- High-profile rule: `f_price_lag_24 >= 6500.0`, `anchor - pred >= 1000.0`, `blend=0.6`, hours `18-23`, recent days `14`.
- Adjusted rows: `18`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `rolling_stack_pred` | 8.36% | 19.08% | 2209 |
| `high_profile_pred` | 8.32% | 18.76% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_v1`.
- High-profile rule: `f_price_lag_168 >= 5000.0`, `anchor - pred >= 1250.0`, `blend=1.0`, hours `17-23`, recent days `7`.
- Adjusted rows: `6`.
- Flag column: `high_profile_lag168_applied`; output column: `high_profile_lag168_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_pred` | 8.32% | 18.76% | 2209 |
| `high_profile_lag168_pred` | 8.22% | 18.02% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_v1`.
- High-profile rule: `f_price_lag_168 >= 3000.0`, `anchor - pred >= 3000.0`, `blend=0.6`, hours `9-16`, recent days `14`.
- Adjusted rows: `3`.
- Flag column: `high_profile_lag168_day_applied`; output column: `high_profile_lag168_day_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_pred` | 8.22% | 18.02% | 2209 |
| `high_profile_lag168_day_pred` | 8.19% | 17.75% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_v1`.
- Low-profile rule: `f_rolling_mean_hour_7d <= 2000.0`, `pred - anchor >= 2000.0`, `blend=0.6`, months `5-8`, hours `10-16`, recent days `14`.
- Adjusted rows: `2`.
- Flag column: `low_profile_rolling7_applied`; output column: `high_profile_lag168_day_down_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_pred` | 8.19% | 17.75% | 2209 |
| `high_profile_lag168_day_down_pred` | 8.16% | 17.54% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_v1`.
- Low-profile rule: `f_price_lag_168 <= 1000.0`, `pred - anchor >= 250.0`, `blend=1.0`, months `5-8`, hours `10-16`, recent days `14`.
- Adjusted rows: `5`.
- Flag column: `low_profile_weather_applied`; output column: `high_profile_lag168_day_down_weather_pred`.
- Extra min filters: `[('f_rolling_mean_hour_3d', 2500.0), ('f_solarradiation', 300.0)]`; max filters: `[('f_rolling_mean_hour_7d', 2000.0), ('f_renewable_pressure_index', 800.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_pred` | 8.16% | 17.54% | 2209 |
| `high_profile_lag168_day_down_weather_pred` | 8.10% | 17.14% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_v1`.
- Low-profile rule: `f_price_lag_168 <= 4000.0`, `pred - anchor >= 250.0`, `blend=1.0`, months `5-8`, hours `9-17`, recent days `14`.
- Adjusted rows: `2`.
- Flag column: `low_profile_lowcollapse_applied`; output column: `high_profile_lag168_day_down_weather_lowcollapse_pred`.
- Extra min filters: `[('f_rolling_mean_hour_3d', 2500.0)]`; max filters: `[('f_renewable_pressure_index', 300.0), ('f_rolling_mean_hour_7d', 4000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_pred` | 8.10% | 17.14% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_pred` | 8.08% | 16.94% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_v1`.
- High-profile rule: `price_cap >= 14900.0`, `anchor - pred >= 3000.0`, `blend=1.0`, hours `0`, recent days `14`.
- Adjusted rows: `2`.
- Flag column: `high_profile_cap00_applied`; output column: `high_profile_lag168_day_down_weather_lowcollapse_cap00_pred`.
- Extra min filters: `[('f_price_lag_24', 12000.0)]`; max filters: `[('f_price_lag_48', 7000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_pred` | 8.08% | 16.94% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_pred` | 8.00% | 16.39% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_v1`.
- High-profile rule: `f_price_lag_48 >= 6500.0`, `anchor - pred >= 3000.0`, `blend=0.6`, hours `19-23`, recent days `7`.
- Adjusted rows: `1`.
- Flag column: `high_profile_lag48eve_applied`; output column: `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_pred` | 8.00% | 16.39% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_pred` | 7.98% | 16.24% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_v1_plot.png`

### ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_v1`.
- High-profile rule: `price_cap >= 14900.0`, `anchor - pred >= 1000.0`, `blend=1.0`, hours `19-23`, recent days `7`.
- Adjusted rows: `3`.
- Flag column: `high_profile_capnight_applied`; output column: `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`.
- Extra min filters: `[('f_price_lag_24', 8000.0), ('f_price_lag_168', 6500.0)]`; max filters: `[('f_price_lag_48', 7000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_pred` | 7.98% | 16.24% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1_plot.png`

### nonlinear_hgb_best_resid_recent45_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `resid`, lookback `45` days, min train `21` days, blend `0.15`, apply recent days `45`.
- Applied target days: `46`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_pred` | 7.86% | 15.54% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_resid_recent45_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_resid_recent45_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_resid_recent45_v1_plot.png`

### nonlinear_hgb_best_logresid_recent30_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `logresid`, lookback `45` days, min train `21` days, blend `0.1`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_logresid_pred` | 7.87% | 15.49% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_logresid_recent30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_logresid_recent30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_logresid_recent30_v1_plot.png`

### nonlinear_hgb_best_ratio_recent30_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.1`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_pred` | 7.87% | 15.40% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_v1_plot.png`

### nonlinear_hgb_best_resid_recent14_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `resid`, lookback `30` days, min train `14` days, blend `0.1`, apply recent days `14`.
- Applied target days: `15`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_resid14_pred` | 7.88% | 15.49% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_resid_recent14_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_resid_recent14_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_resid_recent14_v1_plot.png`

### nonlinear_hgb_best_ratio_recent30_b015_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.15`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_b015_pred` | 7.87% | 15.38% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b015_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b015_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b015_v1_plot.png`

### nonlinear_hgb_best_ratio_recent30_b020_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.2`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_b020_pred` | 7.87% | 15.37% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b020_v1_plot.png`

### nonlinear_et_best_ratio_recent30_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `et`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.1`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_et_ratio_pred` | 7.88% | 15.49% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_et_best_ratio_recent30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_et_best_ratio_recent30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_et_best_ratio_recent30_v1_plot.png`

### nonlinear_hgb_best_ratio_recent30_b025_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.25`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_b025_pred` | 7.87% | 15.36% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b025_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b025_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b025_v1_plot.png`

### nonlinear_hgb_best_ratio_recent30_b030_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.3`, apply recent days `30`.
- Applied target days: `31`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_b030_pred` | 7.88% | 15.35% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent30_b030_v1_plot.png`

### nonlinear_hgb_best_ratio_recent14_b025_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `30` days, min train `14` days, blend `0.25`, apply recent days `14`.
- Applied target days: `15`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_r14_b025_pred` | 7.88% | 15.46% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent14_b025_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent14_b025_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_recent14_b025_v1_plot.png`

### nonlinear_hgb_ratio_b025_cap00_roll7_v1

- Input experiment: `nonlinear_hgb_best_ratio_recent30_b025_v1`.
- High-profile rule: `price_cap >= 14900.0`, `anchor - pred >= 3000.0`, `blend=1.0`, hours `0`, recent days `7`.
- Adjusted rows: `2`.
- Flag column: `high_profile_cap00_roll7_applied`; output column: `nonlinear_hgb_ratio_b025_cap00_roll7_pred`.
- Extra min filters: `[('f_rolling_mean_hour_7d', 6000.0), ('f_price_lag_48', 7000.0)]`; max filters: `[('f_price_lag_24', 7000.0), ('f_price_lag_168', 7000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_b025_pred` | 7.87% | 15.36% | 2209 |
| `nonlinear_hgb_ratio_b025_cap00_roll7_pred` | 7.76% | 14.54% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_b025_cap00_roll7_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_b025_cap00_roll7_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_b025_cap00_roll7_v1_plot.png`

### nonlinear_hgb_best_ratio_all_b015_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.15`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_all_b015_pred` | 7.85% | 15.38% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b015_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b015_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b015_v1_plot.png`

### nonlinear_hgb_ratio_all_b015_cap00_roll7_v1

- Input experiment: `nonlinear_hgb_best_ratio_all_b015_v1`.
- High-profile rule: `price_cap >= 14900.0`, `anchor - pred >= 3000.0`, `blend=1.0`, hours `0`, recent days `7`.
- Adjusted rows: `2`.
- Flag column: `high_profile_cap00_roll7_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_pred`.
- Extra min filters: `[('f_rolling_mean_hour_7d', 6000.0), ('f_price_lag_48', 7000.0)]`; max filters: `[('f_price_lag_24', 7000.0), ('f_price_lag_168', 7000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_pred` | 7.85% | 15.38% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_pred` | 7.74% | 14.56% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b015_cap00_roll7_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b015_cap00_roll7_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b015_cap00_roll7_v1_plot.png`

### nonlinear_hgb_best_ratio_all_b020_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.2`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_all_b020_pred` | 7.86% | 15.37% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b020_v1_plot.png`

### nonlinear_hgb_best_ratio_all_b025_v1

- Input experiment: `ensemble_tcn168_336_lowprofile_rollingridge30_highprofile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.25`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | 7.88% | 15.44% | 2209 |
| `nonlinear_hgb_ratio_all_b025_pred` | 7.88% | 15.36% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b025_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b025_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_nonlinear_hgb_best_ratio_all_b025_v1_plot.png`

### nonlinear_hgb_ratio_all_b020_cap00_roll7_v1

- Input experiment: `nonlinear_hgb_best_ratio_all_b020_v1`.
- High-profile rule: `price_cap >= 14900.0`, `anchor - pred >= 3000.0`, `blend=1.0`, hours `0`, recent days `7`.
- Adjusted rows: `2`.
- Flag column: `high_profile_cap00_roll7_applied`; output column: `nonlinear_hgb_ratio_all_b020_cap00_roll7_pred`.
- Extra min filters: `[('f_rolling_mean_hour_7d', 6000.0), ('f_price_lag_48', 7000.0)]`; max filters: `[('f_price_lag_24', 7000.0), ('f_price_lag_168', 7000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b020_pred` | 7.86% | 15.37% | 2209 |
| `nonlinear_hgb_ratio_all_b020_cap00_roll7_pred` | 7.75% | 14.55% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b020_cap00_roll7_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b020_cap00_roll7_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b020_cap00_roll7_v1_plot.png`

### nonlinear_hgb_ratio_all_b025_cap00_roll7_v1

- Input experiment: `nonlinear_hgb_best_ratio_all_b025_v1`.
- High-profile rule: `price_cap >= 14900.0`, `anchor - pred >= 3000.0`, `blend=1.0`, hours `0`, recent days `7`.
- Adjusted rows: `2`.
- Flag column: `high_profile_cap00_roll7_applied`; output column: `nonlinear_hgb_ratio_all_b025_cap00_roll7_pred`.
- Extra min filters: `[('f_rolling_mean_hour_7d', 6000.0), ('f_price_lag_48', 7000.0)]`; max filters: `[('f_price_lag_24', 7000.0), ('f_price_lag_168', 7000.0)]`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b025_pred` | 7.88% | 15.36% | 2209 |
| `nonlinear_hgb_ratio_all_b025_cap00_roll7_pred` | 7.77% | 14.54% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b025_cap00_roll7_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b025_cap00_roll7_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\src\..\output\neural_experiment_nonlinear_hgb_ratio_all_b025_cap00_roll7_v1_plot.png`

### candidate_high_lag168_h17_18_recent14_b100_v1

- Input experiment: `nonlinear_hgb_ratio_all_b015_cap00_roll7_v1`.
- High-profile rule: `f_price_lag_168 >= 5000.0`, `anchor - pred >= 1000.0`, `blend=1.0`, hours `17-18`, recent days `14`.
- Adjusted rows: `5`.
- Flag column: `high_profile_lag168_h1718_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_highlag168_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_pred` | 7.74% | 14.56% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_highlag168_pred` | 7.71% | 14.27% | 2209 |

- Predictions: `output\neural_experiment_candidate_high_lag168_h17_18_recent14_b100_v1_predictions.csv`
- Metrics: `output\neural_experiment_candidate_high_lag168_h17_18_recent14_b100_v1_metrics.json`
- Plot: `output\neural_experiment_candidate_high_lag168_h17_18_recent14_b100_v1_plot.png`

### candidate_low_roll7_h10_16_recent30_b020_v1

- Input experiment: `nonlinear_hgb_ratio_all_b015_cap00_roll7_v1`.
- Low-profile rule: `f_rolling_mean_hour_7d <= 2500.0`, `pred - anchor >= 2000.0`, `blend=0.2`, months `5-8`, hours `10-16`, recent days `30`.
- Adjusted rows: `23`.
- Flag column: `low_profile_roll7_h1016_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowroll7_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_pred` | 7.74% | 14.56% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowroll7_pred` | 7.69% | 14.53% | 2209 |

- Predictions: `output\neural_experiment_candidate_low_roll7_h10_16_recent30_b020_v1_predictions.csv`
- Metrics: `output\neural_experiment_candidate_low_roll7_h10_16_recent30_b020_v1_metrics.json`
- Plot: `output\neural_experiment_candidate_low_roll7_h10_16_recent30_b020_v1_plot.png`

### candidate_lowroll7_plus_highlag168_v1

- Input experiment: `candidate_low_roll7_h10_16_recent30_b020_v1`.
- High-profile rule: `f_price_lag_168 >= 5000.0`, `anchor - pred >= 1000.0`, `blend=1.0`, hours `17-18`, recent days `14`.
- Adjusted rows: `5`.
- Flag column: `high_profile_lag168_h1718_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowroll7_highlag168_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowroll7_pred` | 7.69% | 14.53% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowroll7_highlag168_pred` | 7.65% | 14.25% | 2209 |

- Predictions: `output\neural_experiment_candidate_lowroll7_plus_highlag168_v1_predictions.csv`
- Metrics: `output\neural_experiment_candidate_lowroll7_plus_highlag168_v1_metrics.json`
- Plot: `output\neural_experiment_candidate_lowroll7_plus_highlag168_v1_plot.png`

### candidate_lowcompact_h11_13_15_16_b025_v1

- Input experiment: `nonlinear_hgb_ratio_all_b015_cap00_roll7_v1`.
- Low-profile rule: `f_rolling_mean_hour_7d <= 2500.0`, `pred - anchor >= 2000.0`, `blend=0.25`, months `5-8`, hours `11-13,15-16`, recent days `30`.
- Adjusted rows: `17`.
- Flag column: `low_profile_compact_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_pred` | 7.74% | 14.56% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_pred` | 7.68% | 14.53% | 2209 |

- Predictions: `output\neural_experiment_candidate_lowcompact_h11_13_15_16_b025_v1_predictions.csv`
- Metrics: `output\neural_experiment_candidate_lowcompact_h11_13_15_16_b025_v1_metrics.json`
- Plot: `output\neural_experiment_candidate_lowcompact_h11_13_15_16_b025_v1_plot.png`

### candidate_lowcompact_plus_highlag168_aggressive_v1

- Input experiment: `candidate_lowcompact_h11_13_15_16_b025_v1`.
- High-profile rule: `f_price_lag_168 >= 5000.0`, `anchor - pred >= 1000.0`, `blend=1.0`, hours `17-18`, recent days `14`.
- Adjusted rows: `5`.
- Flag column: `high_profile_lag168_h1718_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_pred` | 7.68% | 14.53% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |

- Predictions: `output\neural_experiment_candidate_lowcompact_plus_highlag168_aggressive_v1_predictions.csv`
- Metrics: `output\neural_experiment_candidate_lowcompact_plus_highlag168_aggressive_v1_metrics.json`
- Plot: `output\neural_experiment_candidate_lowcompact_plus_highlag168_aggressive_v1_plot.png`

### candidate_lowcompact_plus_highlag168_stable_v1

- Input experiment: `candidate_lowcompact_h11_13_15_16_b025_v1`.
- High-profile rule: `f_price_lag_168 >= 6000.0`, `anchor - pred >= 500.0`, `blend=1.0`, hours `18`, recent days `14`.
- Adjusted rows: `3`.
- Flag column: `high_profile_lag168_h18_stable_applied`; output column: `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_stable_pred`.
- Rule uses lagged/same-hour profile only; no future raw market columns or target-day facts.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_pred` | 7.68% | 14.53% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_stable_pred` | 7.64% | 14.30% | 2209 |

- Predictions: `output\neural_experiment_candidate_lowcompact_plus_highlag168_stable_v1_predictions.csv`
- Metrics: `output\neural_experiment_candidate_lowcompact_plus_highlag168_stable_v1_metrics.json`
- Plot: `output\neural_experiment_candidate_lowcompact_plus_highlag168_stable_v1_plot.png`

### nonlinear_hgb_best2_logresid_all_b005_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `logresid`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `nonlinear_hgb_best2_logresid_all_b005_pred` | 7.64% | 14.25% | 2209 |

- Predictions: `output\neural_experiment_nonlinear_hgb_best2_logresid_all_b005_v1_predictions.csv`
- Metrics: `output\neural_experiment_nonlinear_hgb_best2_logresid_all_b005_v1_metrics.json`
- Plot: `output\neural_experiment_nonlinear_hgb_best2_logresid_all_b005_v1_plot.png`

### nonlinear_hgb_best2_ratio_all_b005_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `nonlinear_hgb_best2_ratio_all_b005_pred` | 7.64% | 14.28% | 2209 |

- Predictions: `output\neural_experiment_nonlinear_hgb_best2_ratio_all_b005_v1_predictions.csv`
- Metrics: `output\neural_experiment_nonlinear_hgb_best2_ratio_all_b005_v1_metrics.json`
- Plot: `output\neural_experiment_nonlinear_hgb_best2_ratio_all_b005_v1_plot.png`

### nonlinear_hgb_best2_resid_all_b005_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `resid`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `nonlinear_hgb_best2_resid_all_b005_pred` | 7.63% | 14.27% | 2209 |

- Predictions: `output\neural_experiment_nonlinear_hgb_best2_resid_all_b005_v1_predictions.csv`
- Metrics: `output\neural_experiment_nonlinear_hgb_best2_resid_all_b005_v1_metrics.json`
- Plot: `output\neural_experiment_nonlinear_hgb_best2_resid_all_b005_v1_plot.png`

### nonlinear_hgb_best2_logresid_all_b0025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `logresid`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `nonlinear_hgb_best2_logresid_all_b0025_pred` | 7.64% | 14.25% | 2209 |

- Predictions: `output\neural_experiment_nonlinear_hgb_best2_logresid_all_b0025_v1_predictions.csv`
- Metrics: `output\neural_experiment_nonlinear_hgb_best2_logresid_all_b0025_v1_metrics.json`
- Plot: `output\neural_experiment_nonlinear_hgb_best2_logresid_all_b0025_v1_plot.png`

### nonlinear_hgb_best2_ratio_all_b0025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `nonlinear_hgb_best2_ratio_all_b0025_pred` | 7.64% | 14.26% | 2209 |

- Predictions: `output\neural_experiment_nonlinear_hgb_best2_ratio_all_b0025_v1_predictions.csv`
- Metrics: `output\neural_experiment_nonlinear_hgb_best2_ratio_all_b0025_v1_metrics.json`
- Plot: `output\neural_experiment_nonlinear_hgb_best2_ratio_all_b0025_v1_plot.png`

### nonlinear_hgb_best2_resid_all_b0025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `resid`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `nonlinear_hgb_best2_resid_all_b0025_pred` | 7.64% | 14.26% | 2209 |

- Predictions: `output\neural_experiment_nonlinear_hgb_best2_resid_all_b0025_v1_predictions.csv`
- Metrics: `output\neural_experiment_nonlinear_hgb_best2_resid_all_b0025_v1_metrics.json`
- Plot: `output\neural_experiment_nonlinear_hgb_best2_resid_all_b0025_v1_plot.png`

### capfix_tree_recent_guard_v1

- Tree-only cap-fix base generated after correcting delivery-day cap start dates. `hybrid_guarded_pred` mirrors the recent-calibrated tree guard for downstream compatibility.
- No future raw market columns are used; this is the existing tree ensemble plus recent historical calibration.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 11.10% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.75% | 20.27% | 2209 |
| `hybrid_pred` | 11.10% | 30.37% | 2209 |
| `hybrid_recent_calibrated_pred` | 9.75% | 20.27% | 2209 |
| `hybrid_guarded_pred` | 9.75% | 20.27% | 2209 |

- Predictions: `output\neural_experiment_capfix_tree_recent_guard_v1_predictions.csv`
- Metrics: `output\neural_experiment_capfix_tree_recent_guard_v1_metrics.json`
- Plot: `output\neural_experiment_capfix_tree_recent_guard_v1_plot.png`

### anomaly_hgb_logresid_b0025_features_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `logresid`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_logresid_b0025_features_pred` | 7.64% | 14.25% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_logresid_b0025_features_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_logresid_b0025_features_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_logresid_b0025_features_v1_plot.png`

### anomaly_hgb_logresid_b0025_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `logresid`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_logresid_b0025_q85w025_pred` | 7.64% | 14.24% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_logresid_b0025_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_logresid_b0025_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_logresid_b0025_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0025_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.64% | 14.23% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w025_v1_plot.png`

### anomaly_hgb_resid_b005_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `resid`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_resid_b005_q85w025_pred` | 7.62% | 14.26% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_resid_b005_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_resid_b005_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_resid_b005_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0025_q80w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.8`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0025_q80w025_pred` | 7.64% | 14.24% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0025_q80w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0025_q80w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0025_q80w025_v1_plot.png`

### anomaly_hgb_ratio_b0025_q90w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.9`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0025_q90w025_pred` | 7.64% | 14.25% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0025_q90w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0025_q90w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0025_q90w025_v1_plot.png`

### anomaly_hgb_ratio_b0025_q85w050_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.5`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w050_pred` | 7.64% | 14.24% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w050_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w050_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w050_v1_plot.png`

### anomaly_hgb_ratio_b005_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b005_q85w025_pred` | 7.64% | 14.22% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b005_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b005_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b005_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0020_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.02`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0020_q85w025_pred` | 7.64% | 14.24% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0020_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0020_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0020_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0035_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.035`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0035_q85w025_pred` | 7.64% | 14.23% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0035_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0035_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0035_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0030_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.03`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0030_q85w025_pred` | 7.64% | 14.23% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0030_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0030_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0030_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0015_q85w025_v1

- Input experiment: `candidate_lowcompact_plus_highlag168_aggressive_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.015`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.27% | 20.13% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.64% | 14.25% | 2209 |
| `anomaly_hgb_ratio_b0015_q85w025_pred` | 7.64% | 14.24% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0015_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0015_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0015_q85w025_v1_plot.png`

### anomaly_hgb_ratio_b0025_q85w025_capfix_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_v1`.
- Cap-corrected artifact: `price_cap` refreshed from `price_caps.py`; all prediction columns clipped to the refreshed cap.
- Anomaly logic: rolling-origin HGB ratio stacker uses lagged source residual features and downweights high source-error training days.
- Leakage check: residual features are shifted (`24/48/168h`, previous-day WMAPE/bias); each target day trains only on earlier rows.
- Cap changed rows: `36`; actual > cap rows: `0`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred` | 7.5794% | 14.2495% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |

- Predictions: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w025_capfix_v1_predictions.csv`
- Metrics: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w025_capfix_v1_metrics.json`
- Plot: `output\neural_experiment_anomaly_hgb_ratio_b0025_q85w025_capfix_v1_plot.png`

### analog_ratio_all_b004_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `10`, blend `0.04`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b004_k10_pred` | 7.5698% | 14.2296% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b004_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b004_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b004_k10_v1_plot.png`

### analog_ratio_peak_b006_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `10`, blend `0.06`, hours `17-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `504`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_peak_b006_k10_pred` | 7.5716% | 14.2348% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_peak_b006_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_peak_b006_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_peak_b006_k10_v1_plot.png`

### analog_ratio_day_b006_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `10`, blend `0.06`, hours `10-17`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `576`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_day_b006_k10_pred` | 7.5730% | 14.2365% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_day_b006_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_day_b006_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_day_b006_k10_v1_plot.png`

### analog_logresid_all_b004_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `logresid`, lookback `75` days, k `10`, blend `0.04`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_logresid_all_b004_k10_pred` | 7.5712% | 14.2259% | 2209 |

- Predictions: `output\neural_experiment_analog_logresid_all_b004_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_logresid_all_b004_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_logresid_all_b004_k10_v1_plot.png`

### analog_ratio_all_b008_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `10`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k10_pred` | 7.5663% | 14.2310% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k10_v1_plot.png`

### analog_ratio_all_b008_k6_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `6`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k6_pred` | 7.5648% | 14.2221% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k6_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k6_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k6_v1_plot.png`

### analog_ratio_all_b010_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `10`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k10_pred` | 7.5655% | 14.2317% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k10_v1_plot.png`

### analog_ratio_all_b012_k10_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `10`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k10_pred` | 7.5651% | 14.2325% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k10_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k10_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k10_v1_plot.png`

### analog_ratio_all_b008_k15_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `15`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k15_pred` | 7.5668% | 14.2264% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k15_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k15_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k15_v1_plot.png`

### analog_ratio_all_b008_k4_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k4_pred` | 7.5567% | 14.1906% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k4_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k4_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k4_v1_plot.png`

### analog_ratio_all_b006_k6_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `6`, blend `0.06`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b006_k6_pred` | 7.5664% | 14.2236% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b006_k6_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b006_k6_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b006_k6_v1_plot.png`

### analog_ratio_all_b010_k6_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `6`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k6_pred` | 7.5640% | 14.2206% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k6_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k6_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k6_v1_plot.png`

### analog_ratio_all_b008_k8_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `8`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k8_pred` | 7.5660% | 14.2237% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k8_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k8_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k8_v1_plot.png`

### analog_ratio_all_b008_k3_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `3`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k3_pred` | 7.5587% | 14.1866% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k3_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k3_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k3_v1_plot.png`

### analog_ratio_all_b006_k4_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.06`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b006_k4_pred` | 7.5599% | 14.1994% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b006_k4_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b006_k4_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b006_k4_v1_plot.png`

### analog_ratio_all_b012_k4_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_pred` | 7.5536% | 14.1786% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_v1_plot.png`

### analog_ratio_all_b010_k4_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k4_pred` | 7.5547% | 14.1835% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k4_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k4_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k4_v1_plot.png`

### analog_ratio_all_b012_k4_c020_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_c020_pred` | 7.5550% | 14.1914% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_c020_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_c020_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_c020_v1_plot.png`

### analog_ratio_all_b012_k4_c050_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.5536% | 14.1719% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_c050_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_c050_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_c050_v1_plot.png`

### analog_ratio_all_b020_k4_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.2`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b020_k4_pred` | 7.5575% | 14.1771% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b020_k4_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b020_k4_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b020_k4_v1_plot.png`

### analog_ratio_all_b016_k4_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.16`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b016_k4_pred` | 7.5541% | 14.1738% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b016_k4_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b016_k4_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b016_k4_v1_plot.png`

### analog_ratio_all_b012_k3_c050_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `3`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k3_c050_pred` | 7.5615% | 14.1804% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k3_c050_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k3_c050_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k3_c050_v1_plot.png`

### analog_ratio_all_b014_k4_c050_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.14`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b014_k4_c050_pred` | 7.5544% | 14.1705% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b014_k4_c050_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b014_k4_c050_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b014_k4_c050_v1_plot.png`

### analog_ratio_all_b012_k4_c070_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_c070_pred` | 7.5543% | 14.1687% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_c070_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_c070_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_c070_v1_plot.png`

### analog_ratio_all_b016_k4_c050_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.16`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b016_k4_c050_pred` | 7.5558% | 14.1712% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b016_k4_c050_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b016_k4_c050_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b016_k4_c050_v1_plot.png`

### analog_ratio_all_b010_k4_c100_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k4_c100_pred` | 7.5543% | 14.1680% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k4_c100_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k4_c100_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k4_c100_v1_plot.png`

### analog_ratio_all_b010_k4_c070_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k4_c070_pred` | 7.5539% | 14.1717% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k4_c070_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k4_c070_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k4_c070_v1_plot.png`

### analog_ratio_all_b012_k4_c100_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_c100_pred` | 7.5556% | 14.1670% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_c100_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_c100_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_c100_v1_plot.png`

### analog_ratio_all_b008_k4_c070_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.08`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b008_k4_c070_pred` | 7.5553% | 14.1792% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b008_k4_c070_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b008_k4_c070_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b008_k4_c070_v1_plot.png`

### analog_ratio_all_b012_k4_c070_t050_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_c070_t050_pred` | 7.5558% | 14.1702% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_c070_t050_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_c070_t050_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_c070_t050_v1_plot.png`

### analog_ratio_all_b010_k4_c100_t050_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k4_c100_t050_pred` | 7.5557% | 14.1700% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k4_c100_t050_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k4_c100_t050_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k4_c100_t050_v1_plot.png`

### analog_ratio_all_b010_k4_c100_t120_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.1`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b010_k4_c100_t120_pred` | 7.5538% | 14.1680% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b010_k4_c100_t120_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b010_k4_c100_t120_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b010_k4_c100_t120_v1_plot.png`

### analog_ratio_all_b012_k4_c070_t120_v1

- Input experiment: `anomaly_hgb_ratio_b0025_q85w025_capfix_v1`.
- Analog day profile correction: source `anomaly_hgb_ratio_b0025_q85w025_pred`, target `ratio`, lookback `75` days, k `4`, blend `0.12`, hours `0-23`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `1728`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `anomaly_hgb_ratio_b0025_q85w025_pred` | 7.5765% | 14.2329% | 2209 |
| `analog_ratio_all_b012_k4_c070_t120_pred` | 7.5536% | 14.1680% | 2209 |

- Predictions: `output\neural_experiment_analog_ratio_all_b012_k4_c070_t120_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog_ratio_all_b012_k4_c070_t120_v1_metrics.json`
- Plot: `output\neural_experiment_analog_ratio_all_b012_k4_c070_t120_v1_plot.png`

### analog2_hgb_logresid_b0025_q85w025_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `analog_ratio_all_b012_k4_c050_pred`, target `logresid`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.55% | 14.17% | 2209 |
| `analog2_hgb_logresid_b0025_q85w025_pred` | 7.56% | 14.18% | 2209 |

- Predictions: `output\neural_experiment_analog2_hgb_logresid_b0025_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog2_hgb_logresid_b0025_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_analog2_hgb_logresid_b0025_q85w025_v1_plot.png`

### analog2_hgb_ratio_b005_q85w025_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `analog_ratio_all_b012_k4_c050_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.55% | 14.17% | 2209 |
| `analog2_hgb_ratio_b005_q85w025_pred` | 7.57% | 14.17% | 2209 |

- Predictions: `output\neural_experiment_analog2_hgb_ratio_b005_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog2_hgb_ratio_b005_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_analog2_hgb_ratio_b005_q85w025_v1_plot.png`

### analog2_hgb_ratio_b0025_q85w025_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `analog_ratio_all_b012_k4_c050_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.55% | 14.17% | 2209 |
| `analog2_hgb_ratio_b0025_q85w025_pred` | 7.56% | 14.16% | 2209 |

- Predictions: `output\neural_experiment_analog2_hgb_ratio_b0025_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog2_hgb_ratio_b0025_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_analog2_hgb_ratio_b0025_q85w025_v1_plot.png`

### analog2_hgb_resid_b0025_q85w025_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `analog_ratio_all_b012_k4_c050_pred`, target `resid`, lookback `45` days, min train `21` days, blend `0.025`, apply recent days `0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.85`, outlier weight `0.25`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.55% | 14.17% | 2209 |
| `analog2_hgb_resid_b0025_q85w025_pred` | 7.55% | 14.19% | 2209 |

- Predictions: `output\neural_experiment_analog2_hgb_resid_b0025_q85w025_v1_predictions.csv`
- Metrics: `output\neural_experiment_analog2_hgb_resid_b0025_q85w025_v1_metrics.json`
- Plot: `output\neural_experiment_analog2_hgb_resid_b0025_q85w025_v1_plot.png`

### analog2_resid_h0718_b006_k5_s1200_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Analog day profile correction: source `analog_ratio_all_b012_k4_c050_pred`, target `resid`, lookback `75` days, k `5`, blend `0.06`, hours `7-18`.
- Similarity uses source forecast profile, lagged price profiles, known weather/calendar/cap features, and shifted source-error anomaly features only.
- For each target day, analog days are strictly earlier than the target day.
- Adjusted rows: `864`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.5536% | 14.1719% | 2209 |
| `analog2_resid_h0718_b006_k5_s1200_pred` | 7.5588% | 14.1886% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_analog2_resid_h0718_b006_k5_s1200_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_analog2_resid_h0718_b006_k5_s1200_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_analog2_resid_h0718_b006_k5_s1200_v1_plot.png`

### daybias1_roll3_b050_day_abs300_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Rolling day-bias adjuster: source `analog_ratio_all_b012_k4_c050_pred`, rolling days `3`, beta `0.5`, hours `10-18`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `81`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.5536% | 14.1719% | 2209 |
| `daybias1_roll3_b050_day_abs300_pred` | 7.5361% | 14.1683% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b050_day_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b050_day_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b050_day_abs300_v1_plot.png`

### daybias2_roll1_bn020_dayeve_wmape10_v1

- Input experiment: `daybias1_roll3_b050_day_abs300_v1`.
- Rolling day-bias adjuster: source `daybias1_roll3_b050_day_abs300_pred`, rolling days `1`, beta `-0.2`, hours `10-23`, gate `wmape` threshold `10.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `308`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias1_roll3_b050_day_abs300_pred` | 7.5361% | 14.1683% | 2209 |
| `daybias2_roll1_bn020_dayeve_wmape10_pred` | 7.5059% | 13.9143% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn020_dayeve_wmape10_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn020_dayeve_wmape10_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn020_dayeve_wmape10_v1_plot.png`

### daybias1_roll3_b040_day_abs300_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Rolling day-bias adjuster: source `analog_ratio_all_b012_k4_c050_pred`, rolling days `3`, beta `0.4`, hours `10-18`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `81`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.5536% | 14.1719% | 2209 |
| `daybias1_roll3_b040_day_abs300_pred` | 7.5332% | 14.1597% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b040_day_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b040_day_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b040_day_abs300_v1_plot.png`

### daybias2_roll1_bn020_dayeve_wmape12_v1

- Input experiment: `daybias1_roll3_b040_day_abs300_v1`.
- Rolling day-bias adjuster: source `daybias1_roll3_b040_day_abs300_pred`, rolling days `1`, beta `-0.2`, hours `10-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `196`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias1_roll3_b040_day_abs300_pred` | 7.5332% | 14.1597% | 2209 |
| `daybias2_roll1_bn020_dayeve_wmape12_pred` | 7.5038% | 13.9292% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn020_dayeve_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn020_dayeve_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn020_dayeve_wmape12_v1_plot.png`

### daybias1_roll3_b042_day_abs300_v1

- Input experiment: `analog_ratio_all_b012_k4_c050_v1`.
- Rolling day-bias adjuster: source `analog_ratio_all_b012_k4_c050_pred`, rolling days `3`, beta `0.42`, hours `10-18`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `81`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `analog_ratio_all_b012_k4_c050_pred` | 7.5536% | 14.1719% | 2209 |
| `daybias1_roll3_b042_day_abs300_pred` | 7.5337% | 14.1614% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b042_day_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b042_day_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias1_roll3_b042_day_abs300_v1_plot.png`

### daybias2_roll1_bn021_dayeve_wmape12_v1

- Input experiment: `daybias1_roll3_b042_day_abs300_v1`.
- Rolling day-bias adjuster: source `daybias1_roll3_b042_day_abs300_pred`, rolling days `1`, beta `-0.21`, hours `10-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `196`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias1_roll3_b042_day_abs300_pred` | 7.5337% | 14.1614% | 2209 |
| `daybias2_roll1_bn021_dayeve_wmape12_pred` | 7.5037% | 13.9229% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn021_dayeve_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn021_dayeve_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias2_roll1_bn021_dayeve_wmape12_v1_plot.png`

### hourbias_roll2_bn030_day_wmape16_v1

- Input experiment: `daybias2_roll1_bn021_dayeve_wmape12_v1`.
- Shifted same-hour bias adjuster: source `daybias2_roll1_bn021_dayeve_wmape12_pred`, rolling same-hour observations `2`, beta `-0.3`, hours `10-18`, gate `wmape` threshold `16.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `493`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias2_roll1_bn021_dayeve_wmape12_pred` | 7.5037% | 13.9229% | 2209 |
| `hourbias_roll2_bn030_day_wmape16_pred` | 7.5015% | 13.5619% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias_roll2_bn030_day_wmape16_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias_roll2_bn030_day_wmape16_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias_roll2_bn030_day_wmape16_v1_plot.png`

### hourbias_roll3_bn020_day_wmape20_v1

- Input experiment: `daybias2_roll1_bn021_dayeve_wmape12_v1`.
- Shifted same-hour bias adjuster: source `daybias2_roll1_bn021_dayeve_wmape12_pred`, rolling same-hour observations `3`, beta `-0.2`, hours `10-18`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `491`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias2_roll1_bn021_dayeve_wmape12_pred` | 7.5037% | 13.9229% | 2209 |
| `hourbias_roll3_bn020_day_wmape20_pred` | 7.4815% | 13.7400% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias_roll3_bn020_day_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias_roll3_bn020_day_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias_roll3_bn020_day_wmape20_v1_plot.png`

### hourbias2_roll21_b010_peak_abs150_v1

- Input experiment: `hourbias_roll3_bn020_day_wmape20_v1`.
- Shifted same-hour bias adjuster: source `hourbias_roll3_bn020_day_wmape20_pred`, rolling same-hour observations `21`, beta `0.1`, hours `0,7,8,9,11,12,13,14,15,16,17,21,22`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `637`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias_roll3_bn020_day_wmape20_pred` | 7.4815% | 13.7400% | 2209 |
| `hourbias2_roll21_b010_peak_abs150_pred` | 7.4634% | 13.7572% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias2_roll21_b010_peak_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias2_roll21_b010_peak_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias2_roll21_b010_peak_abs150_v1_plot.png`

### hourbias3_roll3_b015_morning_abs500_v1

- Input experiment: `hourbias2_roll21_b010_peak_abs150_v1`.
- Shifted same-hour bias adjuster: source `hourbias2_roll21_b010_peak_abs150_pred`, rolling same-hour observations `3`, beta `0.15`, hours `7-10`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `74`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias2_roll21_b010_peak_abs150_pred` | 7.4634% | 13.7572% | 2209 |
| `hourbias3_roll3_b015_morning_abs500_pred` | 7.4543% | 13.7684% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias3_roll3_b015_morning_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias3_roll3_b015_morning_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias3_roll3_b015_morning_abs500_v1_plot.png`

### hourbias3_roll2_bn010_day_wmape25_v1

- Input experiment: `hourbias2_roll21_b010_peak_abs150_v1`.
- Shifted same-hour bias adjuster: source `hourbias2_roll21_b010_peak_abs150_pred`, rolling same-hour observations `2`, beta `-0.1`, hours `10-18`, gate `wmape` threshold `25.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `413`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias2_roll21_b010_peak_abs150_pred` | 7.4634% | 13.7572% | 2209 |
| `hourbias3_roll2_bn010_day_wmape25_pred` | 7.4565% | 13.6427% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias3_roll2_bn010_day_wmape25_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias3_roll2_bn010_day_wmape25_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias3_roll2_bn010_day_wmape25_v1_plot.png`

### hourbias4_roll14_bn010_all_wmape12_v1

- Input experiment: `hourbias3_roll3_b015_morning_abs500_v1`.
- Shifted same-hour bias adjuster: source `hourbias3_roll3_b015_morning_abs500_pred`, rolling same-hour observations `14`, beta `-0.1`, hours `all`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `1059`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias3_roll3_b015_morning_abs500_pred` | 7.4543% | 13.7684% | 2209 |
| `hourbias4_roll14_bn010_all_wmape12_pred` | 7.4426% | 13.7360% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias4_roll14_bn010_all_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias4_roll14_bn010_all_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias4_roll14_bn010_all_wmape12_v1_plot.png`

### hourbias4_roll2_bn020_day_wmape25_v1

- Input experiment: `hourbias3_roll3_b015_morning_abs500_v1`.
- Shifted same-hour bias adjuster: source `hourbias3_roll3_b015_morning_abs500_pred`, rolling same-hour observations `2`, beta `-0.2`, hours `10-18`, gate `wmape` threshold `25.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `413`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias3_roll3_b015_morning_abs500_pred` | 7.4543% | 13.7684% | 2209 |
| `hourbias4_roll2_bn020_day_wmape25_pred` | 7.4488% | 13.5574% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias4_roll2_bn020_day_wmape25_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias4_roll2_bn020_day_wmape25_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias4_roll2_bn020_day_wmape25_v1_plot.png`

### hourbias5_med21_b030_peak_wmape25_v1

- Input experiment: `hourbias4_roll14_bn010_all_wmape12_v1`.
- Shifted same-hour bias adjuster: source `hourbias4_roll14_bn010_all_wmape12_pred`, rolling same-hour observations `21`, stat `median`, beta `0.3`, hours `0,7,8,9,11,12,13,14,15,16,17,21,22`, gate `wmape` threshold `25.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `416`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias4_roll14_bn010_all_wmape12_pred` | 7.4426% | 13.7360% | 2209 |
| `hourbias5_med21_b030_peak_wmape25_pred` | 7.4211% | 13.7375% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias5_med21_b030_peak_wmape25_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias5_med21_b030_peak_wmape25_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias5_med21_b030_peak_wmape25_v1_plot.png`

### hourbias6_mean3_bn020_day_wmape30_v1

- Input experiment: `hourbias5_med21_b030_peak_wmape25_v1`.
- Shifted same-hour bias adjuster: source `hourbias5_med21_b030_peak_wmape25_pred`, rolling same-hour observations `3`, stat `mean`, beta `-0.2`, hours `10-18`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `384`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias5_med21_b030_peak_wmape25_pred` | 7.4211% | 13.7375% | 2209 |
| `hourbias6_mean3_bn020_day_wmape30_pred` | 7.4066% | 13.6228% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias6_mean3_bn020_day_wmape30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias6_mean3_bn020_day_wmape30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias6_mean3_bn020_day_wmape30_v1_plot.png`

### hourbias7_mean2_bn010_peak_wmape35_v1

- Input experiment: `hourbias6_mean3_bn020_day_wmape30_v1`.
- Shifted same-hour bias adjuster: source `hourbias6_mean3_bn020_day_wmape30_pred`, rolling same-hour observations `2`, stat `mean`, beta `-0.1`, hours `0,7,8,9,11,12,13,14,15,16,17,21,22`, gate `wmape` threshold `35.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `329`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias6_mean3_bn020_day_wmape30_pred` | 7.4066% | 13.6228% | 2209 |
| `hourbias7_mean2_bn010_peak_wmape35_pred` | 7.3967% | 13.5407% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias7_mean2_bn010_peak_wmape35_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias7_mean2_bn010_peak_wmape35_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias7_mean2_bn010_peak_wmape35_v1_plot.png`

### groupbias1_srcbin10_med_b050_peak_wmape12_v1

- Input experiment: `hourbias7_mean2_bn010_peak_wmape35_v1`.
- Shifted group-bias adjuster: source `hourbias7_mean2_bn010_peak_wmape35_pred`, group `hour,source_bin`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `10`, stat `median`, beta `0.5`, hours `peakerr`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `527`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias7_mean2_bn010_peak_wmape35_pred` | 7.3967% | 13.5407% | 2209 |
| `groupbias1_srcbin10_med_b050_peak_wmape12_pred` | 7.1962% | 13.5277% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias1_srcbin10_med_b050_peak_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias1_srcbin10_med_b050_peak_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias1_srcbin10_med_b050_peak_wmape12_v1_plot.png`

### groupbias2_ratiobin8_mean_b065_evening_abs600_v1

- Input experiment: `groupbias1_srcbin10_med_b050_peak_wmape12_v1`.
- Shifted group-bias adjuster: source `groupbias1_srcbin10_med_b050_peak_wmape12_pred`, group `hour,source_ratio_bin`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `8`, stat `mean`, beta `0.65`, hours `evening`, gate `absbias` threshold `600.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `28`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias1_srcbin10_med_b050_peak_wmape12_pred` | 7.1962% | 13.5277% | 2209 |
| `groupbias2_ratiobin8_mean_b065_evening_abs600_pred` | 7.1398% | 13.5355% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias2_ratiobin8_mean_b065_evening_abs600_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias2_ratiobin8_mean_b065_evening_abs600_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias2_ratiobin8_mean_b065_evening_abs600_v1_plot.png`

### groupbias3_market1_med_b010_night_abs150_v1

- Input experiment: `groupbias2_ratiobin8_mean_b065_evening_abs600_v1`.
- Shifted group-bias adjuster: source `groupbias2_ratiobin8_mean_b065_evening_abs600_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `1`, stat `median`, beta `0.1`, hours `night`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `434`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias2_ratiobin8_mean_b065_evening_abs600_pred` | 7.1398% | 13.5355% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias3_market1_med_b010_night_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias3_market1_med_b010_night_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias3_market1_med_b010_night_abs150_v1_plot.png`

### groupbias4_hourweekend12_med_bn025_all_abs400_v1

- Input experiment: `groupbias3_market1_med_b010_night_abs150_v1`.
- Shifted group-bias adjuster: source `groupbias3_market1_med_b010_night_abs150_pred`, group `hour,weekend`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `12`, stat `median`, beta `-0.25`, hours `all`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `110`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |
| `groupbias4_hourweekend12_med_bn025_all_abs400_pred` | 7.0819% | 13.4353% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias4_hourweekend12_med_bn025_all_abs400_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias4_hourweekend12_med_bn025_all_abs400_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias4_hourweekend12_med_bn025_all_abs400_v1_plot.png`

### groupbias5_market1_med_bn025_evening_wmape12_v1

- Input experiment: `groupbias4_hourweekend12_med_bn025_all_abs400_v1`.
- Shifted group-bias adjuster: source `groupbias4_hourweekend12_med_bn025_all_abs400_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `1`, stat `median`, beta `-0.25`, hours `evening`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `25`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias4_hourweekend12_med_bn025_all_abs400_pred` | 7.0819% | 13.4353% | 2209 |
| `groupbias5_market1_med_bn025_evening_wmape12_pred` | 7.0548% | 13.1660% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias5_market1_med_bn025_evening_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias5_market1_med_bn025_evening_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias5_market1_med_bn025_evening_wmape12_v1_plot.png`

### groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_v1

- Input experiment: `groupbias5_market1_med_bn025_evening_wmape12_v1`.
- Shifted group-bias adjuster: source `groupbias5_market1_med_bn025_evening_wmape12_pred`, group `hour,summer,source_bin`, source bins `-1,50,250,500,1000,1500,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `10`, stat `mean`, beta `-0.4`, hours `midday`, gate `absbias` threshold `600.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `41`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias5_market1_med_bn025_evening_wmape12_pred` | 7.0548% | 13.1660% | 2209 |
| `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred` | 7.0757% | 13.1264% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_v1_plot.png`

### lag24blend1_daily2_night_a100_adv0_v1

- Input experiment: `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_v1`.
- Shifted lag24 blend adjuster: source `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred`, lag `f_price_lag_24`, mode `daily`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, alpha `1.0`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; the selection signal is shifted and uses only prior actual errors of source vs lag24.
- Adjusted rows: `8`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred` | 7.0757% | 13.1264% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend1_daily2_night_a100_adv0_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend1_daily2_night_a100_adv0_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend1_daily2_night_a100_adv0_v1_plot.png`

### lag24blend2_sim_abs1500_night_an010_v1

- Input experiment: `lag24blend1_daily2_night_a100_adv0_v1`.
- Shifted lag24 blend adjuster: source `lag24blend1_daily2_night_a100_adv0_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `absdiff` `le` `1500.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `534`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend2_sim_abs1500_night_an010_pred` | 7.0165% | 12.8019% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_abs1500_night_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_abs1500_night_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_abs1500_night_an010_v1_plot.png`

### lag24blend2_sim_ratio05_night_a100_v1

- Input experiment: `lag24blend1_daily2_night_a100_adv0_v1`.
- Shifted lag24 blend adjuster: source `lag24blend1_daily2_night_a100_adv0_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `1.0`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `198`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend2_sim_ratio05_night_a100_pred` | 7.0192% | 12.8465% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_ratio05_night_a100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_ratio05_night_a100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_ratio05_night_a100_v1_plot.png`

### lag24blend2_sim_absge500_night_an010_v1

- Input experiment: `lag24blend1_daily2_night_a100_adv0_v1`.
- Shifted lag24 blend adjuster: source `lag24blend1_daily2_night_a100_adv0_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `absdiff` `ge` `500.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `460`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend2_sim_absge500_night_an010_pred` | 6.9894% | 12.9678% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_absge500_night_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_absge500_night_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_absge500_night_an010_v1_plot.png`

### lag24blend2_sim_ratio035_night_an010_v1

- Input experiment: `lag24blend1_daily2_night_a100_adv0_v1`.
- Shifted lag24 blend adjuster: source `lag24blend1_daily2_night_a100_adv0_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `groupbias6_lowrepair_summersrc10_mean_bn040_midday_abs600_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.35`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `561`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend2_sim_ratio035_night_an010_pred` | 7.0097% | 12.9038% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_ratio035_night_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_ratio035_night_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend2_sim_ratio035_night_an010_v1_plot.png`

### daybias3_nm_d1_b050_wmape15_v1

- Input experiment: `lag24blend2_sim_absge500_night_an010_v1`.
- Rolling day-bias adjuster: source `lag24blend2_sim_absge500_night_an010_pred`, rolling days `1`, beta `0.5`, hours `0-4,7-9`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `56`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend2_sim_absge500_night_an010_pred` | 6.9894% | 12.9678% | 2209 |
| `daybias3_nm_d1_b050_wmape15_pred` | 6.9572% | 12.8521% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias3_nm_d1_b050_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias3_nm_d1_b050_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias3_nm_d1_b050_wmape15_v1_plot.png`

### daybias4_midday_d3_b120_abs500_v1

- Input experiment: `daybias3_nm_d1_b050_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias3_nm_d1_b050_wmape15_pred`, rolling days `3`, beta `1.2`, hours `11-15`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `15`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias3_nm_d1_b050_wmape15_pred` | 6.9572% | 12.8521% | 2209 |
| `daybias4_midday_d3_b120_abs500_pred` | 6.9266% | 12.8521% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_midday_d3_b120_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_midday_d3_b120_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_midday_d3_b120_abs500_v1_plot.png`

### daybias4_all_d14_bn120_wmape8_v1

- Input experiment: `daybias3_nm_d1_b050_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias3_nm_d1_b050_wmape15_pred`, rolling days `14`, beta `-1.2`, hours `0-23`, gate `wmape` threshold `8.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `360`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias3_nm_d1_b050_wmape15_pred` | 6.9572% | 12.8521% | 2209 |
| `daybias4_all_d14_bn120_wmape8_pred` | 6.9311% | 12.7737% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_all_d14_bn120_wmape8_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_all_d14_bn120_wmape8_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_all_d14_bn120_wmape8_v1_plot.png`

### daybias4_midday_d2_bn050_abs300_v1

- Input experiment: `daybias3_nm_d1_b050_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias3_nm_d1_b050_wmape15_pred`, rolling days `2`, beta `-0.5`, hours `11-15`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `45`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias3_nm_d1_b050_wmape15_pred` | 6.9572% | 12.8521% | 2209 |
| `daybias4_midday_d2_bn050_abs300_pred` | 6.9429% | 12.6773% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_midday_d2_bn050_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_midday_d2_bn050_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_midday_d2_bn050_abs300_v1_plot.png`

### daybias4_daylow_d2_bn030_abs300_v1

- Input experiment: `daybias3_nm_d1_b050_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias3_nm_d1_b050_wmape15_pred`, rolling days `2`, beta `-0.3`, hours `10-16`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `63`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias3_nm_d1_b050_wmape15_pred` | 6.9572% | 12.8521% | 2209 |
| `daybias4_daylow_d2_bn030_abs300_pred` | 6.9450% | 12.7181% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_daylow_d2_bn030_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_daylow_d2_bn030_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_daylow_d2_bn030_abs300_v1_plot.png`

### daybias4_all_d2_b120_wmape20_v1

- Input experiment: `daybias3_nm_d1_b050_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias3_nm_d1_b050_wmape15_pred`, rolling days `2`, beta `1.2`, hours `0-23`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias3_nm_d1_b050_wmape15_pred` | 6.9572% | 12.8521% | 2209 |
| `daybias4_all_d2_b120_wmape20_pred` | 6.9380% | 12.7088% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_all_d2_b120_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_all_d2_b120_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias4_all_d2_b120_wmape20_v1_plot.png`

### daybias5_midday10_d3_b120_abs500_v1

- Input experiment: `daybias4_all_d2_b120_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias4_all_d2_b120_wmape20_pred`, rolling days `3`, beta `1.2`, hours `10-15`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias4_all_d2_b120_wmape20_pred` | 6.9380% | 12.7088% | 2209 |
| `daybias5_midday10_d3_b120_abs500_pred` | 6.9061% | 12.7088% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_midday10_d3_b120_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_midday10_d3_b120_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_midday10_d3_b120_abs500_v1_plot.png`

### daybias5_midday11_d1_bn120_wmape20_v1

- Input experiment: `daybias4_all_d2_b120_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias4_all_d2_b120_wmape20_pred`, rolling days `1`, beta `-1.2`, hours `11-15`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `5`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias4_all_d2_b120_wmape20_pred` | 6.9380% | 12.7088% | 2209 |
| `daybias5_midday11_d1_bn120_wmape20_pred` | 6.9125% | 12.5192% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_midday11_d1_bn120_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_midday11_d1_bn120_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_midday11_d1_bn120_wmape20_v1_plot.png`

### daybias5_all_d14_bn120_wmape8_v1

- Input experiment: `daybias4_all_d2_b120_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias4_all_d2_b120_wmape20_pred`, rolling days `14`, beta `-1.2`, hours `0-23`, gate `wmape` threshold `8.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `360`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias4_all_d2_b120_wmape20_pred` | 6.9380% | 12.7088% | 2209 |
| `daybias5_all_d14_bn120_wmape8_pred` | 6.9122% | 12.6330% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_all_d14_bn120_wmape8_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_all_d14_bn120_wmape8_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias5_all_d14_bn120_wmape8_v1_plot.png`

### daybias6_critical_d14_bn150_wmape8_v1

- Input experiment: `daybias5_midday11_d1_bn120_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias5_midday11_d1_bn120_wmape20_pred`, rolling days `14`, beta `-1.5`, hours `0,2,4,7,8,9,11,15,17,18,21`, gate `wmape` threshold `8.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `154`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias5_midday11_d1_bn120_wmape20_pred` | 6.9125% | 12.5192% | 2209 |
| `daybias6_critical_d14_bn150_wmape8_pred` | 6.8811% | 12.4316% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_critical_d14_bn150_wmape8_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_critical_d14_bn150_wmape8_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_critical_d14_bn150_wmape8_v1_plot.png`

### daybias6_all_d14_bn150_wmape8_v1

- Input experiment: `daybias5_midday11_d1_bn120_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias5_midday11_d1_bn120_wmape20_pred`, rolling days `14`, beta `-1.5`, hours `0-23`, gate `wmape` threshold `8.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `336`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias5_midday11_d1_bn120_wmape20_pred` | 6.9125% | 12.5192% | 2209 |
| `daybias6_all_d14_bn150_wmape8_pred` | 6.8826% | 12.3931% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_all_d14_bn150_wmape8_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_all_d14_bn150_wmape8_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_all_d14_bn150_wmape8_v1_plot.png`

### daybias6_midday10_d3_b120_abs500_v1

- Input experiment: `daybias5_midday11_d1_bn120_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias5_midday11_d1_bn120_wmape20_pred`, rolling days `3`, beta `1.2`, hours `10-15`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias5_midday11_d1_bn120_wmape20_pred` | 6.9125% | 12.5192% | 2209 |
| `daybias6_midday10_d3_b120_abs500_pred` | 6.8806% | 12.5192% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_midday10_d3_b120_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_midday10_d3_b120_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias6_midday10_d3_b120_abs500_v1_plot.png`

### daybias7_midday10_d3_b120_abs500_v1

- Input experiment: `daybias6_critical_d14_bn150_wmape8_v1`.
- Rolling day-bias adjuster: source `daybias6_critical_d14_bn150_wmape8_pred`, rolling days `3`, beta `1.2`, hours `10-15`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias6_critical_d14_bn150_wmape8_pred` | 6.8811% | 12.4316% | 2209 |
| `daybias7_midday10_d3_b120_abs500_pred` | 6.8492% | 12.4316% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_midday10_d3_b120_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_midday10_d3_b120_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_midday10_d3_b120_abs500_v1_plot.png`

### daybias7_morning79_d7_bn150_wmape12_v1

- Input experiment: `daybias6_critical_d14_bn150_wmape8_v1`.
- Rolling day-bias adjuster: source `daybias6_critical_d14_bn150_wmape8_pred`, rolling days `7`, beta `-1.5`, hours `7-9`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `30`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias6_critical_d14_bn150_wmape8_pred` | 6.8811% | 12.4316% | 2209 |
| `daybias7_morning79_d7_bn150_wmape12_pred` | 6.8666% | 12.3232% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_morning79_d7_bn150_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_morning79_d7_bn150_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_morning79_d7_bn150_wmape12_v1_plot.png`

### daybias7_night_d5_b030_abs100_v1

- Input experiment: `daybias6_critical_d14_bn150_wmape8_v1`.
- Rolling day-bias adjuster: source `daybias6_critical_d14_bn150_wmape8_pred`, rolling days `5`, beta `0.3`, hours `0-6,23`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `264`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias6_critical_d14_bn150_wmape8_pred` | 6.8811% | 12.4316% | 2209 |
| `daybias7_night_d5_b030_abs100_pred` | 6.8711% | 12.4246% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_night_d5_b030_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_night_d5_b030_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_night_d5_b030_abs100_v1_plot.png`

### daybias7_daylow_d3_b150_wmape15_v1

- Input experiment: `daybias6_critical_d14_bn150_wmape8_v1`.
- Rolling day-bias adjuster: source `daybias6_critical_d14_bn150_wmape8_pred`, rolling days `3`, beta `1.5`, hours `10-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `21`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias6_critical_d14_bn150_wmape8_pred` | 6.8811% | 12.4316% | 2209 |
| `daybias7_daylow_d3_b150_wmape15_pred` | 6.8673% | 12.3290% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_daylow_d3_b150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_daylow_d3_b150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias7_daylow_d3_b150_wmape15_v1_plot.png`

### daybias8_daylow_d7_bn150_wmape12_v1

- Input experiment: `daybias7_daylow_d3_b150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias7_daylow_d3_b150_wmape15_pred`, rolling days `7`, beta `-1.5`, hours `10-16`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `70`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias7_daylow_d3_b150_wmape15_pred` | 6.8673% | 12.3290% | 2209 |
| `daybias8_daylow_d7_bn150_wmape12_pred` | 6.8572% | 12.2531% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_daylow_d7_bn150_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_daylow_d7_bn150_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_daylow_d7_bn150_wmape12_v1_plot.png`

### daybias8_midday10_d3_b120_abs500_v1

- Input experiment: `daybias7_daylow_d3_b150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias7_daylow_d3_b150_wmape15_pred`, rolling days `3`, beta `1.2`, hours `10-15`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias7_daylow_d3_b150_wmape15_pred` | 6.8673% | 12.3290% | 2209 |
| `daybias8_midday10_d3_b120_abs500_pred` | 6.8355% | 12.3290% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_midday10_d3_b120_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_midday10_d3_b120_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_midday10_d3_b120_abs500_v1_plot.png`

### daybias8_morning79_d7_bn150_wmape12_v1

- Input experiment: `daybias7_daylow_d3_b150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias7_daylow_d3_b150_wmape15_pred`, rolling days `7`, beta `-1.5`, hours `7-9`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `30`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias7_daylow_d3_b150_wmape15_pred` | 6.8673% | 12.3290% | 2209 |
| `daybias8_morning79_d7_bn150_wmape12_pred` | 6.8532% | 12.2236% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_morning79_d7_bn150_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_morning79_d7_bn150_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias8_morning79_d7_bn150_wmape12_v1_plot.png`

### daybias9_morning79_d7_bn150_wmape12_v1

- Input experiment: `daybias8_midday10_d3_b120_abs500_v1`.
- Rolling day-bias adjuster: source `daybias8_midday10_d3_b120_abs500_pred`, rolling days `7`, beta `-1.5`, hours `7-9`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `30`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias8_midday10_d3_b120_abs500_pred` | 6.8355% | 12.3290% | 2209 |
| `daybias9_morning79_d7_bn150_wmape12_pred` | 6.8213% | 12.2236% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_morning79_d7_bn150_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_morning79_d7_bn150_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_morning79_d7_bn150_wmape12_v1_plot.png`

### daybias9_midday10_d2_bn020_abs100_v1

- Input experiment: `daybias8_midday10_d3_b120_abs500_v1`.
- Rolling day-bias adjuster: source `daybias8_midday10_d3_b120_abs500_pred`, rolling days `2`, beta `-0.2`, hours `10-15`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `264`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias8_midday10_d3_b120_abs500_pred` | 6.8355% | 12.3290% | 2209 |
| `daybias9_midday10_d2_bn020_abs100_pred` | 6.8221% | 12.3086% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_midday10_d2_bn020_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_midday10_d2_bn020_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_midday10_d2_bn020_abs100_v1_plot.png`

### daybias9_daylow_d2_bn020_abs100_v1

- Input experiment: `daybias8_midday10_d3_b120_abs500_v1`.
- Rolling day-bias adjuster: source `daybias8_midday10_d3_b120_abs500_pred`, rolling days `2`, beta `-0.2`, hours `10-16`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `308`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias8_midday10_d3_b120_abs500_pred` | 6.8355% | 12.3290% | 2209 |
| `daybias9_daylow_d2_bn020_abs100_pred` | 6.8215% | 12.2919% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_daylow_d2_bn020_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_daylow_d2_bn020_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias9_daylow_d2_bn020_abs100_v1_plot.png`

### daybias10_daylow_d2_bn020_abs100_v1

- Input experiment: `daybias9_morning79_d7_bn150_wmape12_v1`.
- Rolling day-bias adjuster: source `daybias9_morning79_d7_bn150_wmape12_pred`, rolling days `2`, beta `-0.2`, hours `10-16`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `308`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias9_morning79_d7_bn150_wmape12_pred` | 6.8213% | 12.2236% | 2209 |
| `daybias10_daylow_d2_bn020_abs100_pred` | 6.8075% | 12.1875% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_daylow_d2_bn020_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_daylow_d2_bn020_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_daylow_d2_bn020_abs100_v1_plot.png`

### daybias10_nooneve_d7_bn050_abs150_v1

- Input experiment: `daybias9_morning79_d7_bn150_wmape12_v1`.
- Rolling day-bias adjuster: source `daybias9_morning79_d7_bn150_wmape12_pred`, rolling days `7`, beta `-0.5`, hours `11-15,17-18`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `112`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias9_morning79_d7_bn150_wmape12_pred` | 6.8213% | 12.2236% | 2209 |
| `daybias10_nooneve_d7_bn050_abs150_pred` | 6.8088% | 12.1801% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_nooneve_d7_bn050_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_nooneve_d7_bn050_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_nooneve_d7_bn050_abs150_v1_plot.png`

### daybias10_midday10_d7_bn070_abs150_v1

- Input experiment: `daybias9_morning79_d7_bn150_wmape12_v1`.
- Rolling day-bias adjuster: source `daybias9_morning79_d7_bn150_wmape12_pred`, rolling days `7`, beta `-0.7`, hours `10-15`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `96`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias9_morning79_d7_bn150_wmape12_pred` | 6.8213% | 12.2236% | 2209 |
| `daybias10_midday10_d7_bn070_abs150_pred` | 6.8101% | 12.1724% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_midday10_d7_bn070_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_midday10_d7_bn070_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_midday10_d7_bn070_abs150_v1_plot.png`

### daybias10_morning79_d1_bn150_wmape20_v1

- Input experiment: `daybias9_morning79_d7_bn150_wmape12_v1`.
- Rolling day-bias adjuster: source `daybias9_morning79_d7_bn150_wmape12_pred`, rolling days `1`, beta `-1.5`, hours `7-9`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `3`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias9_morning79_d7_bn150_wmape12_pred` | 6.8213% | 12.2236% | 2209 |
| `daybias10_morning79_d1_bn150_wmape20_pred` | 6.8109% | 12.1457% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_morning79_d1_bn150_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_morning79_d1_bn150_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias10_morning79_d1_bn150_wmape20_v1_plot.png`

### daybias11_midday11_d5_bn150_wmape15_v1

- Input experiment: `daybias10_daylow_d2_bn020_abs100_v1`.
- Rolling day-bias adjuster: source `daybias10_daylow_d2_bn020_abs100_pred`, rolling days `5`, beta `-1.5`, hours `11-15`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `10`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias10_daylow_d2_bn020_abs100_pred` | 6.8075% | 12.1875% | 2209 |
| `daybias11_midday11_d5_bn150_wmape15_pred` | 6.7959% | 12.1009% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_midday11_d5_bn150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_midday11_d5_bn150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_midday11_d5_bn150_wmape15_v1_plot.png`

### daybias11_daylow_d2_b150_abs700_v1

- Input experiment: `daybias10_daylow_d2_bn020_abs100_v1`.
- Rolling day-bias adjuster: source `daybias10_daylow_d2_bn020_abs100_pred`, rolling days `2`, beta `1.5`, hours `10-16`, gate `absbias` threshold `700.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `7`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias10_daylow_d2_bn020_abs100_pred` | 6.8075% | 12.1875% | 2209 |
| `daybias11_daylow_d2_b150_abs700_pred` | 6.7901% | 12.1875% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_daylow_d2_b150_abs700_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_daylow_d2_b150_abs700_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_daylow_d2_b150_abs700_v1_plot.png`

### daybias11_nooneve_d5_bn150_wmape15_v1

- Input experiment: `daybias10_daylow_d2_bn020_abs100_v1`.
- Rolling day-bias adjuster: source `daybias10_daylow_d2_bn020_abs100_pred`, rolling days `5`, beta `-1.5`, hours `11-15,17-18`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `14`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias10_daylow_d2_bn020_abs100_pred` | 6.8075% | 12.1875% | 2209 |
| `daybias11_nooneve_d5_bn150_wmape15_pred` | 6.7964% | 12.1048% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_nooneve_d5_bn150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_nooneve_d5_bn150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias11_nooneve_d5_bn150_wmape15_v1_plot.png`

### daybias12_nooneve_d5_bn150_wmape15_v1

- Input experiment: `daybias11_daylow_d2_b150_abs700_v1`.
- Rolling day-bias adjuster: source `daybias11_daylow_d2_b150_abs700_pred`, rolling days `5`, beta `-1.5`, hours `11-15,17-18`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `14`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias11_daylow_d2_b150_abs700_pred` | 6.7901% | 12.1875% | 2209 |
| `daybias12_nooneve_d5_bn150_wmape15_pred` | 6.7790% | 12.1048% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_nooneve_d5_bn150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_nooneve_d5_bn150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_nooneve_d5_bn150_wmape15_v1_plot.png`

### daybias12_midday11_d5_bn150_wmape15_v1

- Input experiment: `daybias11_daylow_d2_b150_abs700_v1`.
- Rolling day-bias adjuster: source `daybias11_daylow_d2_b150_abs700_pred`, rolling days `5`, beta `-1.5`, hours `11-15`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `10`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias11_daylow_d2_b150_abs700_pred` | 6.7901% | 12.1875% | 2209 |
| `daybias12_midday11_d5_bn150_wmape15_pred` | 6.7785% | 12.1009% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_midday11_d5_bn150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_midday11_d5_bn150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_midday11_d5_bn150_wmape15_v1_plot.png`

### daybias12_nooneve_d7_bn050_abs150_v1

- Input experiment: `daybias11_daylow_d2_b150_abs700_v1`.
- Rolling day-bias adjuster: source `daybias11_daylow_d2_b150_abs700_pred`, rolling days `7`, beta `-0.5`, hours `11-15,17-18`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `119`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias11_daylow_d2_b150_abs700_pred` | 6.7901% | 12.1875% | 2209 |
| `daybias12_nooneve_d7_bn050_abs150_pred` | 6.7795% | 12.1497% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_nooneve_d7_bn050_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_nooneve_d7_bn050_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias12_nooneve_d7_bn050_abs150_v1_plot.png`

### daybias13_morning79_d1_bn150_wmape20_v1

- Input experiment: `daybias12_midday11_d5_bn150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias12_midday11_d5_bn150_wmape15_pred`, rolling days `1`, beta `-1.5`, hours `7-9`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `3`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias12_midday11_d5_bn150_wmape15_pred` | 6.7785% | 12.1009% | 2209 |
| `daybias13_morning79_d1_bn150_wmape20_pred` | 6.7680% | 12.0230% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_morning79_d1_bn150_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_morning79_d1_bn150_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_morning79_d1_bn150_wmape20_v1_plot.png`

### daybias13_nooneve_d7_bn050_abs150_v1

- Input experiment: `daybias12_midday11_d5_bn150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias12_midday11_d5_bn150_wmape15_pred`, rolling days `7`, beta `-0.5`, hours `11-15,17-18`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `119`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias12_midday11_d5_bn150_wmape15_pred` | 6.7785% | 12.1009% | 2209 |
| `daybias13_nooneve_d7_bn050_abs150_pred` | 6.7677% | 12.0618% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_nooneve_d7_bn050_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_nooneve_d7_bn050_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_nooneve_d7_bn050_abs150_v1_plot.png`

### daybias13_night_d5_b030_abs150_v1

- Input experiment: `daybias12_midday11_d5_bn150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias12_midday11_d5_bn150_wmape15_pred`, rolling days `5`, beta `0.3`, hours `0-6,23`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `160`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias12_midday11_d5_bn150_wmape15_pred` | 6.7785% | 12.1009% | 2209 |
| `daybias13_night_d5_b030_abs150_pred` | 6.7671% | 12.0925% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_night_d5_b030_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_night_d5_b030_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias13_night_d5_b030_abs150_v1_plot.png`

### daybias14_night_d5_b030_abs100_v1

- Input experiment: `daybias13_nooneve_d7_bn050_abs150_v1`.
- Rolling day-bias adjuster: source `daybias13_nooneve_d7_bn050_abs150_pred`, rolling days `5`, beta `0.3`, hours `0-6,23`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `240`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias13_nooneve_d7_bn050_abs150_pred` | 6.7677% | 12.0618% | 2209 |
| `daybias14_night_d5_b030_abs100_pred` | 6.7565% | 12.0617% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_night_d5_b030_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_night_d5_b030_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_night_d5_b030_abs100_v1_plot.png`

### daybias14_morning79_d1_bn150_wmape20_v1

- Input experiment: `daybias13_nooneve_d7_bn050_abs150_v1`.
- Rolling day-bias adjuster: source `daybias13_nooneve_d7_bn050_abs150_pred`, rolling days `1`, beta `-1.5`, hours `7-9`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `3`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias13_nooneve_d7_bn050_abs150_pred` | 6.7677% | 12.0618% | 2209 |
| `daybias14_morning79_d1_bn150_wmape20_pred` | 6.7573% | 11.9839% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_morning79_d1_bn150_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_morning79_d1_bn150_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_morning79_d1_bn150_wmape20_v1_plot.png`

### daybias14_night_d5_b030_abs150_v1

- Input experiment: `daybias13_nooneve_d7_bn050_abs150_v1`.
- Rolling day-bias adjuster: source `daybias13_nooneve_d7_bn050_abs150_pred`, rolling days `5`, beta `0.3`, hours `0-6,23`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `176`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias13_nooneve_d7_bn050_abs150_pred` | 6.7677% | 12.0618% | 2209 |
| `daybias14_night_d5_b030_abs150_pred` | 6.7572% | 12.0521% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_night_d5_b030_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_night_d5_b030_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias14_night_d5_b030_abs150_v1_plot.png`

### daybias15_morning3_night_d5_b030_abs100_v1

- Input experiment: `daybias14_morning79_d1_bn150_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias14_morning79_d1_bn150_wmape20_pred`, rolling days `5`, beta `0.3`, hours `0-6,23`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `248`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias14_morning79_d1_bn150_wmape20_pred` | 6.7573% | 11.9839% | 2209 |
| `daybias15_morning3_night_d5_b030_abs100_pred` | 6.7461% | 11.9844% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias15_morning3_night_d5_b030_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias15_morning3_night_d5_b030_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias15_morning3_night_d5_b030_abs100_v1_plot.png`

### daybias15_morning3_night_d5_b030_abs150_v1

- Input experiment: `daybias14_morning79_d1_bn150_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias14_morning79_d1_bn150_wmape20_pred`, rolling days `5`, beta `0.3`, hours `0-6,23`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `176`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias14_morning79_d1_bn150_wmape20_pred` | 6.7573% | 11.9839% | 2209 |
| `daybias15_morning3_night_d5_b030_abs150_pred` | 6.7469% | 11.9750% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias15_morning3_night_d5_b030_abs150_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias15_morning3_night_d5_b030_abs150_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias15_morning3_night_d5_b030_abs150_v1_plot.png`

### lag24blend3_profileabs_ge3000_all_an010_v1

- Input experiment: `daybias15_morning3_night_d5_b030_abs100_v1`.
- Shifted lag24 blend adjuster: source `daybias15_morning3_night_d5_b030_abs100_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `daybias15_morning3_night_d5_b030_abs100_pred`, rolling window `2`, stat `mean`, hours `all`, lag advantage threshold `0.0`, similarity `profile_abs` `ge` `3000.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `168`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias15_morning3_night_d5_b030_abs100_pred` | 6.7461% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_profileabs_ge3000_all_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_profileabs_ge3000_all_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_profileabs_ge3000_all_an010_v1_plot.png`

### lag24blend3_morning_profileabs_ge2000_an010_v1

- Input experiment: `daybias15_morning3_night_d5_b030_abs100_v1`.
- Shifted lag24 blend adjuster: source `daybias15_morning3_night_d5_b030_abs100_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `daybias15_morning3_night_d5_b030_abs100_pred`, rolling window `2`, stat `mean`, hours `morning`, lag advantage threshold `0.0`, similarity `profile_abs` `ge` `2000.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `84`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias15_morning3_night_d5_b030_abs100_pred` | 6.7461% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend3_morning_profileabs_ge2000_an010_pred` | 6.7343% | 11.8790% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_morning_profileabs_ge2000_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_morning_profileabs_ge2000_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_morning_profileabs_ge2000_an010_v1_plot.png`

### lag24blend3_lowday_profileabs_ge2000_an010_v1

- Input experiment: `daybias15_morning3_night_d5_b030_abs100_v1`.
- Shifted lag24 blend adjuster: source `daybias15_morning3_night_d5_b030_abs100_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `daybias15_morning3_night_d5_b030_abs100_pred`, rolling window `2`, stat `mean`, hours `lowday`, lag advantage threshold `0.0`, similarity `profile_abs` `ge` `2000.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `147`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias15_morning3_night_d5_b030_abs100_pred` | 6.7461% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend3_lowday_profileabs_ge2000_an010_pred` | 6.7206% | 11.9555% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_lowday_profileabs_ge2000_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_lowday_profileabs_ge2000_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend3_lowday_profileabs_ge2000_an010_v1_plot.png`

### lag24blend4_allprof_night_ratio005_a080_v1

- Input experiment: `lag24blend3_profileabs_ge3000_all_an010_v1`.
- Shifted lag24 blend adjuster: source `lag24blend3_profileabs_ge3000_all_an010_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend3_profileabs_ge3000_all_an010_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `199`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend4_allprof_night_ratio005_a080_pred` | 6.6767% | 12.0043% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_night_ratio005_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_night_ratio005_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_night_ratio005_a080_v1_plot.png`

### lag24blend4_allprof_morningprof_ge2000_an010_v1

- Input experiment: `lag24blend3_profileabs_ge3000_all_an010_v1`.
- Shifted lag24 blend adjuster: source `lag24blend3_profileabs_ge3000_all_an010_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend3_profileabs_ge3000_all_an010_pred`, rolling window `2`, stat `mean`, hours `morning`, lag advantage threshold `0.0`, similarity `profile_abs` `ge` `2000.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `84`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend4_allprof_morningprof_ge2000_an010_pred` | 6.7221% | 11.8790% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_morningprof_ge2000_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_morningprof_ge2000_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_morningprof_ge2000_an010_v1_plot.png`

### lag24blend4_allprof_lowdayprof_ge2000_an010_v1

- Input experiment: `lag24blend3_profileabs_ge3000_all_an010_v1`.
- Shifted lag24 blend adjuster: source `lag24blend3_profileabs_ge3000_all_an010_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend3_profileabs_ge3000_all_an010_pred`, rolling window `2`, stat `mean`, hours `lowday`, lag advantage threshold `0.0`, similarity `profile_abs` `ge` `2000.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `147`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend4_allprof_lowdayprof_ge2000_an010_pred` | 6.7272% | 11.9555% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_lowdayprof_ge2000_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_lowdayprof_ge2000_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_lowdayprof_ge2000_an010_v1_plot.png`

### lag24blend4_allprof_abs100_all_a100_v1

- Input experiment: `lag24blend3_profileabs_ge3000_all_an010_v1`.
- Shifted lag24 blend adjuster: source `lag24blend3_profileabs_ge3000_all_an010_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend3_profileabs_ge3000_all_an010_pred`, rolling window `2`, stat `mean`, hours `all`, lag advantage threshold `0.0`, similarity `absdiff` `le` `100.0`, alpha `1.0`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `370`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend4_allprof_abs100_all_a100_pred` | 6.6735% | 11.9932% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_abs100_all_a100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_abs100_all_a100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_abs100_all_a100_v1_plot.png`

### lag24blend4_allprof_abs100_all_a080_v1

- Input experiment: `lag24blend3_profileabs_ge3000_all_an010_v1`.
- Shifted lag24 blend adjuster: source `lag24blend3_profileabs_ge3000_all_an010_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend3_profileabs_ge3000_all_an010_pred`, rolling window `2`, stat `mean`, hours `all`, lag advantage threshold `0.0`, similarity `absdiff` `le` `100.0`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `370`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend4_allprof_abs100_all_a080_pred` | 6.6761% | 11.9908% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_abs100_all_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_abs100_all_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_abs100_all_a080_v1_plot.png`

### lag24blend4_allprof_ratio002_all_a100_v1

- Input experiment: `lag24blend3_profileabs_ge3000_all_an010_v1`.
- Shifted lag24 blend adjuster: source `lag24blend3_profileabs_ge3000_all_an010_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend3_profileabs_ge3000_all_an010_pred`, rolling window `2`, stat `mean`, hours `all`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.02`, alpha `1.0`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `283`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend3_profileabs_ge3000_all_an010_pred` | 6.6978% | 11.9844% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend4_allprof_ratio002_all_a100_pred` | 6.6833% | 11.9434% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_ratio002_all_a100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_ratio002_all_a100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend4_allprof_ratio002_all_a100_v1_plot.png`

### lag24blend5_night_ratio005_a080_v1

- Input experiment: `lag24blend4_allprof_abs100_all_a100_v1`.
- Shifted lag24 blend adjuster: source `lag24blend4_allprof_abs100_all_a100_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend4_allprof_abs100_all_a100_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `201`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend4_allprof_abs100_all_a100_pred` | 6.6735% | 11.9932% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend5_night_ratio005_a080_pred` | 6.6602% | 12.0174% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_night_ratio005_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_night_ratio005_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_night_ratio005_a080_v1_plot.png`

### lag24blend5_all_reldiff005_an010_v1

- Input experiment: `lag24blend4_allprof_abs100_all_a100_v1`.
- Shifted lag24 blend adjuster: source `lag24blend4_allprof_abs100_all_a100_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend4_allprof_abs100_all_a100_pred`, rolling window `2`, stat `mean`, hours `all`, lag advantage threshold `0.0`, similarity `reldiff` `le` `0.05`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `925`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend4_allprof_abs100_all_a100_pred` | 6.6735% | 11.9932% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend5_all_reldiff005_an010_pred` | 6.6619% | 11.9135% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_all_reldiff005_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_all_reldiff005_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_all_reldiff005_an010_v1_plot.png`

### lag24blend5_night_profilele1000_a005_v1

- Input experiment: `lag24blend4_allprof_abs100_all_a100_v1`.
- Shifted lag24 blend adjuster: source `lag24blend4_allprof_abs100_all_a100_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend4_allprof_abs100_all_a100_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `1000.0`, alpha `0.05`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `248`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend4_allprof_abs100_all_a100_pred` | 6.6735% | 11.9932% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend5_night_profilele1000_a005_pred` | 6.6607% | 11.9501% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_night_profilele1000_a005_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_night_profilele1000_a005_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend5_night_profilele1000_a005_v1_plot.png`

### lag24blend6_nightprof_all_reldiff005_an010_v1

- Input experiment: `lag24blend5_night_profilele1000_a005_v1`.
- Shifted lag24 blend adjuster: source `lag24blend5_night_profilele1000_a005_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend5_night_profilele1000_a005_pred`, rolling window `2`, stat `mean`, hours `all`, lag advantage threshold `0.0`, similarity `reldiff` `le` `0.05`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `929`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend5_night_profilele1000_a005_pred` | 6.6607% | 11.9501% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend6_nightprof_all_reldiff005_an010_pred` | 6.6467% | 11.8717% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_all_reldiff005_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_all_reldiff005_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_all_reldiff005_an010_v1_plot.png`

### lag24blend6_nightprof_nightratio005_a080_v1

- Input experiment: `lag24blend5_night_profilele1000_a005_v1`.
- Shifted lag24 blend adjuster: source `lag24blend5_night_profilele1000_a005_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend5_night_profilele1000_a005_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `201`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend5_night_profilele1000_a005_pred` | 6.6607% | 11.9501% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend6_nightprof_nightratio005_a080_pred` | 6.6482% | 11.9746% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_nightratio005_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_nightratio005_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_nightratio005_a080_v1_plot.png`

### lag24blend6_nightprof_peakerr_reldiff002_an030_v1

- Input experiment: `lag24blend5_night_profilele1000_a005_v1`.
- Shifted lag24 blend adjuster: source `lag24blend5_night_profilele1000_a005_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend5_night_profilele1000_a005_pred`, rolling window `2`, stat `mean`, hours `peakerr`, lag advantage threshold `0.0`, similarity `reldiff` `le` `0.02`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `338`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend5_night_profilele1000_a005_pred` | 6.6607% | 11.9501% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend6_nightprof_peakerr_reldiff002_an030_pred` | 6.6544% | 11.8997% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_peakerr_reldiff002_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_peakerr_reldiff002_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend6_nightprof_peakerr_reldiff002_an030_v1_plot.png`

### daybias16_final_nooneve_d1_b020_wmape12_v1

- Input experiment: `lag24blend6_nightprof_all_reldiff005_an010_v1`.
- Rolling day-bias adjuster: source `lag24blend6_nightprof_all_reldiff005_an010_pred`, rolling days `1`, beta `0.2`, hours `11-15,17-18`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `77`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend6_nightprof_all_reldiff005_an010_pred` | 6.6467% | 11.8717% | 2209 |
| `daybias16_final_nooneve_d1_b020_wmape12_pred` | 6.6359% | 11.8286% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_nooneve_d1_b020_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_nooneve_d1_b020_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_nooneve_d1_b020_wmape12_v1_plot.png`

### daybias16_final_critical_d5_b050_abs300_v1

- Input experiment: `lag24blend6_nightprof_all_reldiff005_an010_v1`.
- Rolling day-bias adjuster: source `lag24blend6_nightprof_all_reldiff005_an010_pred`, rolling days `5`, beta `0.5`, hours `0,2,4,7,8,9,11,15,17,18,21`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `66`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend6_nightprof_all_reldiff005_an010_pred` | 6.6467% | 11.8717% | 2209 |
| `daybias16_final_critical_d5_b050_abs300_pred` | 6.6321% | 11.8717% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_critical_d5_b050_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_critical_d5_b050_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_critical_d5_b050_abs300_v1_plot.png`

### daybias16_final_all_d5_b120_wmape15_v1

- Input experiment: `lag24blend6_nightprof_all_reldiff005_an010_v1`.
- Rolling day-bias adjuster: source `lag24blend6_nightprof_all_reldiff005_an010_pred`, rolling days `5`, beta `1.2`, hours `0-23`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend6_nightprof_all_reldiff005_an010_pred` | 6.6467% | 11.8717% | 2209 |
| `daybias16_final_all_d5_b120_wmape15_pred` | 6.6366% | 11.7966% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_all_d5_b120_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_all_d5_b120_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias16_final_all_d5_b120_wmape15_v1_plot.png`

### daybias17_all_then_critical_d5_b050_abs300_v1

- Input experiment: `daybias16_final_all_d5_b120_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias16_final_all_d5_b120_wmape15_pred`, rolling days `5`, beta `0.5`, hours `0,2,4,7,8,9,11,15,17,18,21`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `66`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias16_final_all_d5_b120_wmape15_pred` | 6.6366% | 11.7966% | 2209 |
| `daybias17_all_then_critical_d5_b050_abs300_pred` | 6.6220% | 11.7966% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias17_all_then_critical_d5_b050_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias17_all_then_critical_d5_b050_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias17_all_then_critical_d5_b050_abs300_v1_plot.png`

### daybias17_critical_then_all_d5_b120_wmape15_v1

- Input experiment: `daybias16_final_critical_d5_b050_abs300_v1`.
- Rolling day-bias adjuster: source `daybias16_final_critical_d5_b050_abs300_pred`, rolling days `5`, beta `1.2`, hours `0-23`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias16_final_critical_d5_b050_abs300_pred` | 6.6321% | 11.8717% | 2209 |
| `daybias17_critical_then_all_d5_b120_wmape15_pred` | 6.6220% | 11.7966% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias17_critical_then_all_d5_b120_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias17_critical_then_all_d5_b120_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias17_critical_then_all_d5_b120_wmape15_v1_plot.png`

### hourbias8_final_night_r1_b010_abs500_v1

- Input experiment: `daybias17_critical_then_all_d5_b120_wmape15_v1`.
- Shifted same-hour bias adjuster: source `daybias17_critical_then_all_d5_b120_wmape15_pred`, rolling same-hour observations `1`, stat `mean`, beta `0.1`, hours `0-6,23`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `190`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias17_critical_then_all_d5_b120_wmape15_pred` | 6.6220% | 11.7966% | 2209 |
| `hourbias8_final_night_r1_b010_abs500_pred` | 6.6064% | 11.7711% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r1_b010_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r1_b010_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r1_b010_abs500_v1_plot.png`

### hourbias8_final_night_r1_b010_abs300_v1

- Input experiment: `daybias17_critical_then_all_d5_b120_wmape15_v1`.
- Shifted same-hour bias adjuster: source `daybias17_critical_then_all_d5_b120_wmape15_pred`, rolling same-hour observations `1`, stat `mean`, beta `0.1`, hours `0-6,23`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `297`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias17_critical_then_all_d5_b120_wmape15_pred` | 6.6220% | 11.7966% | 2209 |
| `hourbias8_final_night_r1_b010_abs300_pred` | 6.6005% | 11.7763% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r1_b010_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r1_b010_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r1_b010_abs300_v1_plot.png`

### hourbias8_final_midday_r14_med_bn100_wmape15_v1

- Input experiment: `daybias17_critical_then_all_d5_b120_wmape15_v1`.
- Shifted same-hour bias adjuster: source `daybias17_critical_then_all_d5_b120_wmape15_pred`, rolling same-hour observations `14`, stat `median`, beta `-1.0`, hours `11-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `379`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias17_critical_then_all_d5_b120_wmape15_pred` | 6.6220% | 11.7966% | 2209 |
| `hourbias8_final_midday_r14_med_bn100_wmape15_pred` | 6.6131% | 11.7538% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_midday_r14_med_bn100_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_midday_r14_med_bn100_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_midday_r14_med_bn100_wmape15_v1_plot.png`

### hourbias8_final_night_r3_med_bn030_wmape20_v1

- Input experiment: `daybias17_critical_then_all_d5_b120_wmape15_v1`.
- Shifted same-hour bias adjuster: source `daybias17_critical_then_all_d5_b120_wmape15_pred`, rolling same-hour observations `3`, stat `median`, beta `-0.3`, hours `0-6,23`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `69`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias17_critical_then_all_d5_b120_wmape15_pred` | 6.6220% | 11.7966% | 2209 |
| `hourbias8_final_night_r3_med_bn030_wmape20_pred` | 6.6135% | 11.7106% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r3_med_bn030_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r3_med_bn030_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias8_final_night_r3_med_bn030_wmape20_v1_plot.png`

### hourbias9_night_abs300_night_r3_med_bn030_wmape20_v1

- Input experiment: `hourbias8_final_night_r1_b010_abs300_v1`.
- Shifted same-hour bias adjuster: source `hourbias8_final_night_r1_b010_abs300_pred`, rolling same-hour observations `3`, stat `median`, beta `-0.3`, hours `0-6,23`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `63`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias8_final_night_r1_b010_abs300_pred` | 6.6005% | 11.7763% | 2209 |
| `hourbias9_night_abs300_night_r3_med_bn030_wmape20_pred` | 6.5940% | 11.7301% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_night_r3_med_bn030_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_night_r3_med_bn030_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_night_r3_med_bn030_wmape20_v1_plot.png`

### hourbias9_night_abs300_midday_r14_med_bn100_wmape15_v1

- Input experiment: `hourbias8_final_night_r1_b010_abs300_v1`.
- Shifted same-hour bias adjuster: source `hourbias8_final_night_r1_b010_abs300_pred`, rolling same-hour observations `14`, stat `median`, beta `-1.0`, hours `11-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `379`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias8_final_night_r1_b010_abs300_pred` | 6.6005% | 11.7763% | 2209 |
| `hourbias9_night_abs300_midday_r14_med_bn100_wmape15_pred` | 6.5916% | 11.7336% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_midday_r14_med_bn100_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_midday_r14_med_bn100_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_midday_r14_med_bn100_wmape15_v1_plot.png`

### hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_v1

- Input experiment: `hourbias8_final_night_r1_b010_abs300_v1`.
- Shifted same-hour bias adjuster: source `hourbias8_final_night_r1_b010_abs300_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.7`, hours `10-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `381`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias8_final_night_r1_b010_abs300_pred` | 6.6005% | 11.7763% | 2209 |
| `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred` | 6.5876% | 11.7567% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_v1_plot.png`

### hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1

- Input experiment: `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_v1`.
- Shifted same-hour bias adjuster: source `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred`, rolling same-hour observations `3`, stat `median`, beta `-0.3`, hours `0-6,23`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `63`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred` | 6.5876% | 11.7567% | 2209 |
| `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred` | 6.5812% | 11.7104% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1_plot.png`

### hourbias10_lowday_then_midday_r14_med_bn100_wmape15_v1

- Input experiment: `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_v1`.
- Shifted same-hour bias adjuster: source `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred`, rolling same-hour observations `14`, stat `median`, beta `-1.0`, hours `11-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `384`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias9_night_abs300_lowday_r21_med_bn070_wmape15_pred` | 6.5876% | 11.7567% | 2209 |
| `hourbias10_lowday_then_midday_r14_med_bn100_wmape15_pred` | 6.6340% | 11.7296% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_lowday_then_midday_r14_med_bn100_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_lowday_then_midday_r14_med_bn100_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_lowday_then_midday_r14_med_bn100_wmape15_v1_plot.png`

### hourbias10_night2_then_lowday_r21_med_bn070_wmape15_v1

- Input experiment: `hourbias9_night_abs300_night_r3_med_bn030_wmape20_v1`.
- Shifted same-hour bias adjuster: source `hourbias9_night_abs300_night_r3_med_bn030_wmape20_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.7`, hours `10-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `381`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias9_night_abs300_night_r3_med_bn030_wmape20_pred` | 6.5940% | 11.7301% | 2209 |
| `hourbias10_night2_then_lowday_r21_med_bn070_wmape15_pred` | 6.5812% | 11.7104% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_night2_then_lowday_r21_med_bn070_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_night2_then_lowday_r21_med_bn070_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias10_night2_then_lowday_r21_med_bn070_wmape15_v1_plot.png`

### lag24blend7_h10_night_ratio005_a080_v1

- Input experiment: `hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1`.
- Shifted lag24 blend adjuster: source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `194`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred` | 6.5812% | 11.7104% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend7_h10_night_ratio005_a080_pred` | 6.5701% | 11.7017% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_ratio005_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_ratio005_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_ratio005_a080_v1_plot.png`

### lag24blend7_h10_night_profile750_an020_v1

- Input experiment: `hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1`.
- Shifted lag24 blend adjuster: source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `750.0`, alpha `-0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `136`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred` | 6.5812% | 11.7104% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend7_h10_night_profile750_an020_pred` | 6.5744% | 11.6215% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_profile750_an020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_profile750_an020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_profile750_an020_v1_plot.png`

### lag24blend7_h10_night_abs250_a080_v1

- Input experiment: `hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1`.
- Shifted lag24 blend adjuster: source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `absdiff` `le` `250.0`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `200`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred` | 6.5812% | 11.7104% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend7_h10_night_abs250_a080_pred` | 6.5691% | 11.7086% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_abs250_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_abs250_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_night_abs250_a080_v1_plot.png`

### lag24blend7_h10_crit_profile500_an010_v1

- Input experiment: `hourbias10_lowday_then_night_r3_med_bn030_wmape20_v1`.
- Shifted lag24 blend adjuster: source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred`, rolling window `2`, stat `mean`, hours `0,2,4,7,8,9,11,15,17,18,21`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `500.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `66`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias10_lowday_then_night_r3_med_bn030_wmape20_pred` | 6.5812% | 11.7104% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend7_h10_crit_profile500_an010_pred` | 6.5736% | 11.6840% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_crit_profile500_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_crit_profile500_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend7_h10_crit_profile500_an010_v1_plot.png`

### lag24blend8_abs250_then_ratio005_a080_v1

- Input experiment: `lag24blend7_h10_night_abs250_a080_v1`.
- Shifted lag24 blend adjuster: source `lag24blend7_h10_night_abs250_a080_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend7_h10_night_abs250_a080_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `0.8`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `210`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend7_h10_night_abs250_a080_pred` | 6.5691% | 11.7086% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend8_abs250_then_ratio005_a080_pred` | 6.5736% | 11.7120% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_ratio005_a080_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_ratio005_a080_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_ratio005_a080_v1_plot.png`

### lag24blend8_abs250_then_profile750_an020_v1

- Input experiment: `lag24blend7_h10_night_abs250_a080_v1`.
- Shifted lag24 blend adjuster: source `lag24blend7_h10_night_abs250_a080_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend7_h10_night_abs250_a080_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `750.0`, alpha `-0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `136`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend7_h10_night_abs250_a080_pred` | 6.5691% | 11.7086% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend8_abs250_then_profile750_an020_pred` | 6.5584% | 11.6145% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_profile750_an020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_profile750_an020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_profile750_an020_v1_plot.png`

### lag24blend8_abs250_then_critprofile500_an010_v1

- Input experiment: `lag24blend7_h10_night_abs250_a080_v1`.
- Shifted lag24 blend adjuster: source `lag24blend7_h10_night_abs250_a080_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lag24blend7_h10_night_abs250_a080_pred`, rolling window `2`, stat `mean`, hours `0,2,4,7,8,9,11,15,17,18,21`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `500.0`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `66`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend7_h10_night_abs250_a080_pred` | 6.5691% | 11.7086% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend8_abs250_then_critprofile500_an010_pred` | 6.5611% | 11.6821% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_critprofile500_an010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_critprofile500_an010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend8_abs250_then_critprofile500_an010_v1_plot.png`

### daybias18_lag8_nooneve_d1_b020_wmape12_v1

- Input experiment: `lag24blend8_abs250_then_profile750_an020_v1`.
- Rolling day-bias adjuster: source `lag24blend8_abs250_then_profile750_an020_pred`, rolling days `1`, beta `0.2`, hours `11-15,17-18`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `63`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend8_abs250_then_profile750_an020_pred` | 6.5584% | 11.6145% | 2209 |
| `daybias18_lag8_nooneve_d1_b020_wmape12_pred` | 6.5453% | 11.5624% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_nooneve_d1_b020_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_nooneve_d1_b020_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_nooneve_d1_b020_wmape12_v1_plot.png`

### daybias18_lag8_midday_d1_b030_wmape12_v1

- Input experiment: `lag24blend8_abs250_then_profile750_an020_v1`.
- Rolling day-bias adjuster: source `lag24blend8_abs250_then_profile750_an020_pred`, rolling days `1`, beta `0.3`, hours `11-15`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `45`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend8_abs250_then_profile750_an020_pred` | 6.5584% | 11.6145% | 2209 |
| `daybias18_lag8_midday_d1_b030_wmape12_pred` | 6.5449% | 11.5867% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_midday_d1_b030_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_midday_d1_b030_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_midday_d1_b030_wmape12_v1_plot.png`

### daybias18_lag8_nooneve_d5_b150_wmape15_v1

- Input experiment: `lag24blend8_abs250_then_profile750_an020_v1`.
- Rolling day-bias adjuster: source `lag24blend8_abs250_then_profile750_an020_pred`, rolling days `5`, beta `1.5`, hours `11-15,17-18`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `7`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend8_abs250_then_profile750_an020_pred` | 6.5584% | 11.6145% | 2209 |
| `daybias18_lag8_nooneve_d5_b150_wmape15_pred` | 6.5476% | 11.5345% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_nooneve_d5_b150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_nooneve_d5_b150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias18_lag8_nooneve_d5_b150_wmape15_v1_plot.png`

### daybias19_nooneve_d1_then_d5_b150_wmape15_v1

- Input experiment: `daybias18_lag8_nooneve_d1_b020_wmape12_v1`.
- Rolling day-bias adjuster: source `daybias18_lag8_nooneve_d1_b020_wmape12_pred`, rolling days `5`, beta `1.5`, hours `11-15,17-18`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `7`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias18_lag8_nooneve_d1_b020_wmape12_pred` | 6.5453% | 11.5624% | 2209 |
| `daybias19_nooneve_d1_then_d5_b150_wmape15_pred` | 6.5352% | 11.4873% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias19_nooneve_d1_then_d5_b150_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias19_nooneve_d1_then_d5_b150_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias19_nooneve_d1_then_d5_b150_wmape15_v1_plot.png`

### daybias19_nooneve_d5_then_d1_b020_wmape12_v1

- Input experiment: `daybias18_lag8_nooneve_d5_b150_wmape15_v1`.
- Rolling day-bias adjuster: source `daybias18_lag8_nooneve_d5_b150_wmape15_pred`, rolling days `1`, beta `0.2`, hours `11-15,17-18`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `63`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias18_lag8_nooneve_d5_b150_wmape15_pred` | 6.5476% | 11.5345% | 2209 |
| `daybias19_nooneve_d5_then_d1_b020_wmape12_pred` | 6.5346% | 11.4824% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias19_nooneve_d5_then_d1_b020_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias19_nooneve_d5_then_d1_b020_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias19_nooneve_d5_then_d1_b020_wmape12_v1_plot.png`

### hourbias11_db19_evening_r3_mean_b100_wmape20_v1

- Input experiment: `daybias19_nooneve_d5_then_d1_b020_wmape12_v1`.
- Shifted same-hour bias adjuster: source `daybias19_nooneve_d5_then_d1_b020_wmape12_pred`, rolling same-hour observations `3`, stat `mean`, beta `1.0`, hours `19-23`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `1`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias19_nooneve_d5_then_d1_b020_wmape12_pred` | 6.5346% | 11.4824% | 2209 |
| `hourbias11_db19_evening_r3_mean_b100_wmape20_pred` | 6.5262% | 11.4201% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_evening_r3_mean_b100_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_evening_r3_mean_b100_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_evening_r3_mean_b100_wmape20_v1_plot.png`

### hourbias11_db19_day_r5_mean_bn010_wmape12_v1

- Input experiment: `daybias19_nooneve_d5_then_d1_b020_wmape12_v1`.
- Shifted same-hour bias adjuster: source `daybias19_nooneve_d5_then_d1_b020_wmape12_pred`, rolling same-hour observations `5`, stat `mean`, beta `-0.1`, hours `10-17`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `558`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias19_nooneve_d5_then_d1_b020_wmape12_pred` | 6.5346% | 11.4824% | 2209 |
| `hourbias11_db19_day_r5_mean_bn010_wmape12_pred` | 6.5300% | 11.4739% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_day_r5_mean_bn010_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_day_r5_mean_bn010_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_day_r5_mean_bn010_wmape12_v1_plot.png`

### hourbias11_db19_midday_r7_mean_bn010_abs300_v1

- Input experiment: `daybias19_nooneve_d5_then_d1_b020_wmape12_v1`.
- Shifted same-hour bias adjuster: source `daybias19_nooneve_d5_then_d1_b020_wmape12_pred`, rolling same-hour observations `7`, stat `mean`, beta `-0.1`, hours `11-16`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `111`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias19_nooneve_d5_then_d1_b020_wmape12_pred` | 6.5346% | 11.4824% | 2209 |
| `hourbias11_db19_midday_r7_mean_bn010_abs300_pred` | 6.5295% | 11.4690% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_midday_r7_mean_bn010_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_midday_r7_mean_bn010_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias11_db19_midday_r7_mean_bn010_abs300_v1_plot.png`

### hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1

- Input experiment: `hourbias11_db19_evening_r3_mean_b100_wmape20_v1`.
- Shifted same-hour bias adjuster: source `hourbias11_db19_evening_r3_mean_b100_wmape20_pred`, rolling same-hour observations `7`, stat `mean`, beta `-0.1`, hours `11-16`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `111`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias11_db19_evening_r3_mean_b100_wmape20_pred` | 6.5262% | 11.4201% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1_plot.png`

### hourbias12_midday_then_evening1_r3_mean_b100_wmape20_v1

- Input experiment: `hourbias11_db19_midday_r7_mean_bn010_abs300_v1`.
- Shifted same-hour bias adjuster: source `hourbias11_db19_midday_r7_mean_bn010_abs300_pred`, rolling same-hour observations `3`, stat `mean`, beta `1.0`, hours `19-23`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `1`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias11_db19_midday_r7_mean_bn010_abs300_pred` | 6.5295% | 11.4690% | 2209 |
| `hourbias12_midday_then_evening1_r3_mean_b100_wmape20_pred` | 6.5212% | 11.4068% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias12_midday_then_evening1_r3_mean_b100_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias12_midday_then_evening1_r3_mean_b100_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias12_midday_then_evening1_r3_mean_b100_wmape20_v1_plot.png`

### groupbias7_h12_srcbin5_mean_day_b030_wmape15_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.3`, hours `day`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `401`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias7_h12_srcbin5_mean_day_b030_wmape15_pred` | 6.4912% | 11.3643% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_srcbin5_mean_day_b030_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_srcbin5_mean_day_b030_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_srcbin5_mean_day_b030_wmape15_v1_plot.png`

### groupbias7_h12_ratiobin3_med_all_b020_wmape30_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_ratio_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `all`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `290`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias7_h12_ratiobin3_med_all_b020_wmape30_pred` | 6.4969% | 11.3471% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_ratiobin3_med_all_b020_wmape30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_ratiobin3_med_all_b020_wmape30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_ratiobin3_med_all_b020_wmape30_v1_plot.png`

### groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `mean`, beta `0.3`, hours `lowday`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `431`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_pred` | 6.4900% | 11.4289% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_v1_plot.png`

### groupbias7_h12_ratiobin3_med_peak_b020_wmape30_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_ratio_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `peakerr`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `257`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias7_h12_ratiobin3_med_peak_b020_wmape30_pred` | 6.4970% | 11.3467% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_ratiobin3_med_peak_b020_wmape30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_ratiobin3_med_peak_b020_wmape30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias7_h12_ratiobin3_med_peak_b020_wmape30_v1_plot.png`

### groupbias8_src5_then_ratio3_med_all_b020_wmape30_v1

- Input experiment: `groupbias7_h12_srcbin5_mean_day_b030_wmape15_v1`.
- Shifted group-bias adjuster: source `groupbias7_h12_srcbin5_mean_day_b030_wmape15_pred`, group `hour,source_ratio_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `all`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `289`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias7_h12_srcbin5_mean_day_b030_wmape15_pred` | 6.4912% | 11.3643% | 2209 |
| `groupbias8_src5_then_ratio3_med_all_b020_wmape30_pred` | 6.4904% | 11.3415% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_src5_then_ratio3_med_all_b020_wmape30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_src5_then_ratio3_med_all_b020_wmape30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_src5_then_ratio3_med_all_b020_wmape30_v1_plot.png`

### groupbias8_ratio3_then_src5_mean_day_b030_wmape15_v1

- Input experiment: `groupbias7_h12_ratiobin3_med_all_b020_wmape30_v1`.
- Shifted group-bias adjuster: source `groupbias7_h12_ratiobin3_med_all_b020_wmape30_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.3`, hours `day`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `399`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias7_h12_ratiobin3_med_all_b020_wmape30_pred` | 6.4969% | 11.3471% | 2209 |
| `groupbias8_ratio3_then_src5_mean_day_b030_wmape15_pred` | 6.4941% | 11.3648% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_ratio3_then_src5_mean_day_b030_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_ratio3_then_src5_mean_day_b030_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_ratio3_then_src5_mean_day_b030_wmape15_v1_plot.png`

### groupbias8_src21_then_ratio3_med_peak_b020_wmape30_v1

- Input experiment: `groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_v1`.
- Shifted group-bias adjuster: source `groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_pred`, group `hour,source_ratio_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `peakerr`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `254`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias7_h12_srcbin21_mean_lowday_b030_wmape12_pred` | 6.4900% | 11.4289% | 2209 |
| `groupbias8_src21_then_ratio3_med_peak_b020_wmape30_pred` | 6.4849% | 11.4028% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_src21_then_ratio3_med_peak_b020_wmape30_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_src21_then_ratio3_med_peak_b020_wmape30_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias8_src21_then_ratio3_med_peak_b020_wmape30_v1_plot.png`

### groupbias9_h12_srcbin5_mean_day_b025_wmape15_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.25`, hours `day`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `401`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias9_h12_srcbin5_mean_day_b025_wmape15_pred` | 6.4919% | 11.3677% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_srcbin5_mean_day_b025_wmape15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_srcbin5_mean_day_b025_wmape15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_srcbin5_mean_day_b025_wmape15_v1_plot.png`

### groupbias9_h12_ratiofine21_med_all_b012_abs100_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_ratio_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.005,0.01,0.02,0.03,0.05,0.08,0.12,0.2,0.35,0.55,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `median`, beta `0.12`, hours `all`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `1040`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias9_h12_ratiofine21_med_all_b012_abs100_pred` | 6.4766% | 11.4350% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_ratiofine21_med_all_b012_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_ratiofine21_med_all_b012_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_ratiofine21_med_all_b012_abs100_v1_plot.png`

### groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_v1

- Input experiment: `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_v1`.
- Shifted group-bias adjuster: source `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred`, group `hour,source_ratio_bin,summer`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `peakerr`, gate `wmape` threshold `35.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `221`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias12_evening1_then_midday_r7_mean_bn010_abs300_pred` | 6.5212% | 11.4068% | 2209 |
| `groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_pred` | 6.4935% | 11.3121% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_v1_plot.png`

### groupbias10_ratiosummer_b020_then_srcbin_b025_v1

- Input experiment: `groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_v1`.
- Shifted group-bias adjuster: source `groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.25`, hours `day`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `398`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias9_h12_ratiosummer3_med_peak_b020_wmape35_pred` | 6.4935% | 11.3121% | 2209 |
| `groupbias10_ratiosummer_b020_then_srcbin_b025_pred` | 6.4885% | 11.3320% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiosummer_b020_then_srcbin_b025_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiosummer_b020_then_srcbin_b025_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiosummer_b020_then_srcbin_b025_v1_plot.png`

### groupbias10_srcbin_b025_then_ratiosummer_b020_v1

- Input experiment: `groupbias9_h12_srcbin5_mean_day_b025_wmape15_v1`.
- Shifted group-bias adjuster: source `groupbias9_h12_srcbin5_mean_day_b025_wmape15_pred`, group `hour,source_ratio_bin,summer`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `peakerr`, gate `wmape` threshold `35.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `223`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias9_h12_srcbin5_mean_day_b025_wmape15_pred` | 6.4919% | 11.3677% | 2209 |
| `groupbias10_srcbin_b025_then_ratiosummer_b020_pred` | 6.4844% | 11.3487% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_srcbin_b025_then_ratiosummer_b020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_srcbin_b025_then_ratiosummer_b020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_srcbin_b025_then_ratiosummer_b020_v1_plot.png`

### groupbias10_ratiofine_b012_then_srcbin_b025_v1

- Input experiment: `groupbias9_h12_ratiofine21_med_all_b012_abs100_v1`.
- Shifted group-bias adjuster: source `groupbias9_h12_ratiofine21_med_all_b012_abs100_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.25`, hours `day`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `397`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias9_h12_ratiofine21_med_all_b012_abs100_pred` | 6.4766% | 11.4350% | 2209 |
| `groupbias10_ratiofine_b012_then_srcbin_b025_pred` | 6.4676% | 11.4370% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiofine_b012_then_srcbin_b025_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiofine_b012_then_srcbin_b025_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiofine_b012_then_srcbin_b025_v1_plot.png`

### groupbias10_ratiofine_b012_then_ratiosummer_b020_v1

- Input experiment: `groupbias9_h12_ratiofine21_med_all_b012_abs100_v1`.
- Shifted group-bias adjuster: source `groupbias9_h12_ratiofine21_med_all_b012_abs100_pred`, group `hour,source_ratio_bin,summer`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `peakerr`, gate `wmape` threshold `35.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `217`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias9_h12_ratiofine21_med_all_b012_abs100_pred` | 6.4766% | 11.4350% | 2209 |
| `groupbias10_ratiofine_b012_then_ratiosummer_b020_pred` | 6.4653% | 11.3339% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiofine_b012_then_ratiosummer_b020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiofine_b012_then_ratiosummer_b020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias10_ratiofine_b012_then_ratiosummer_b020_v1_plot.png`

### groupbias11_ratio2_mean_all_bn010_wmape20_v1

- Input experiment: `groupbias10_ratiofine_b012_then_ratiosummer_b020_v1`.
- Shifted group-bias adjuster: source `groupbias10_ratiofine_b012_then_ratiosummer_b020_pred`, group `hour,source_ratio_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `2`, stat `mean`, beta `-0.1`, hours `all`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `443`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias10_ratiofine_b012_then_ratiosummer_b020_pred` | 6.4653% | 11.3339% | 2209 |
| `groupbias11_ratio2_mean_all_bn010_wmape20_pred` | 6.4608% | 11.2762% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias11_ratio2_mean_all_bn010_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias11_ratio2_mean_all_bn010_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias11_ratio2_mean_all_bn010_wmape20_v1_plot.png`

### hourbias13_gb11_h78901117_r5_med_bn010_abs100_v1

- Input experiment: `groupbias11_ratio2_mean_all_bn010_wmape20_v1`.
- Shifted same-hour bias adjuster: source `groupbias11_ratio2_mean_all_bn010_wmape20_pred`, rolling same-hour observations `5`, stat `median`, beta `-0.1`, hours `7-9,11,17`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `198`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias11_ratio2_mean_all_bn010_wmape20_pred` | 6.4608% | 11.2762% | 2209 |
| `hourbias13_gb11_h78901117_r5_med_bn010_abs100_pred` | 6.4544% | 11.2749% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias13_gb11_h78901117_r5_med_bn010_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias13_gb11_h78901117_r5_med_bn010_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias13_gb11_h78901117_r5_med_bn010_abs100_v1_plot.png`

### daybias20_hb13_nooneve_d5_bn030_abs250_v1

- Input experiment: `hourbias13_gb11_h78901117_r5_med_bn010_abs100_v1`.
- Rolling day-bias adjuster: source `hourbias13_gb11_h78901117_r5_med_bn010_abs100_pred`, rolling days `5`, beta `-0.3`, hours `11-15,17-18`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `63`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias13_gb11_h78901117_r5_med_bn010_abs100_pred` | 6.4544% | 11.2749% | 2209 |
| `daybias20_hb13_nooneve_d5_bn030_abs250_pred` | 6.4419% | 11.2431% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias20_hb13_nooneve_d5_bn030_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias20_hb13_nooneve_d5_bn030_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias20_hb13_nooneve_d5_bn030_abs250_v1_plot.png`

### hourbias14_db20_h789111718_r1_b010_wmape25_v1

- Input experiment: `daybias20_hb13_nooneve_d5_bn030_abs250_v1`.
- Shifted same-hour bias adjuster: source `daybias20_hb13_nooneve_d5_bn030_abs250_pred`, rolling same-hour observations `1`, stat `mean`, beta `0.1`, hours `7-9,11,17,18`, gate `wmape` threshold `25.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `90`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias20_hb13_nooneve_d5_bn030_abs250_pred` | 6.4419% | 11.2431% | 2209 |
| `hourbias14_db20_h789111718_r1_b010_wmape25_pred` | 6.4280% | 11.2330% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias14_db20_h789111718_r1_b010_wmape25_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias14_db20_h789111718_r1_b010_wmape25_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias14_db20_h789111718_r1_b010_wmape25_v1_plot.png`

### daybias21_hb14_nooneve_d21_bn030_abs100_v1

- Input experiment: `hourbias14_db20_h789111718_r1_b010_wmape25_v1`.
- Rolling day-bias adjuster: source `hourbias14_db20_h789111718_r1_b010_wmape25_pred`, rolling days `21`, beta `-0.3`, hours `11-15,17-18`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `119`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias14_db20_h789111718_r1_b010_wmape25_pred` | 6.4280% | 11.2330% | 2209 |
| `daybias21_hb14_nooneve_d21_bn030_abs100_pred` | 6.4249% | 11.2330% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias21_hb14_nooneve_d21_bn030_abs100_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias21_hb14_nooneve_d21_bn030_abs100_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias21_hb14_nooneve_d21_bn030_abs100_v1_plot.png`

### lag24blend9_db21_hournight_r2_mean_an010_advn250_v1

- Input experiment: `daybias21_hb14_nooneve_d21_bn030_abs100_v1`.
- Shifted lag24 blend adjuster: source `daybias21_hb14_nooneve_d21_bn030_abs100_pred`, lag `f_price_lag_24`, mode `hour`, signal source `daybias21_hb14_nooneve_d21_bn030_abs100_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `-250.0`, similarity `ratio` `le` `0.05`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `188`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias21_hb14_nooneve_d21_bn030_abs100_pred` | 6.4249% | 11.2330% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend9_db21_hournight_r2_mean_an010_advn250_pred` | 6.3970% | 11.1941% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend9_db21_hournight_r2_mean_an010_advn250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend9_db21_hournight_r2_mean_an010_advn250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend9_db21_hournight_r2_mean_an010_advn250_v1_plot.png`

### lag24blend9_db21_hourall_r3_mean_an005_advn500_v1

- Input experiment: `daybias21_hb14_nooneve_d21_bn030_abs100_v1`.
- Shifted lag24 blend adjuster: source `daybias21_hb14_nooneve_d21_bn030_abs100_pred`, lag `f_price_lag_24`, mode `hour`, signal source `daybias21_hb14_nooneve_d21_bn030_abs100_pred`, rolling window `3`, stat `mean`, hours `all`, lag advantage threshold `-500.0`, similarity `ratio` `le` `0.05`, alpha `-0.05`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `650`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias21_hb14_nooneve_d21_bn030_abs100_pred` | 6.4249% | 11.2330% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend9_db21_hourall_r3_mean_an005_advn500_pred` | 6.4021% | 11.1360% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend9_db21_hourall_r3_mean_an005_advn500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend9_db21_hourall_r3_mean_an005_advn500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend9_db21_hourall_r3_mean_an005_advn500_v1_plot.png`

### lag24blend10_night_then_all_r3_mean_an005_advn500_v1

- Input experiment: `lag24blend9_db21_hournight_r2_mean_an010_advn250_v1`.
- Shifted lag24 blend adjuster: source `lag24blend9_db21_hournight_r2_mean_an010_advn250_pred`, lag `f_price_lag_24`, mode `hour`, signal source `lag24blend9_db21_hournight_r2_mean_an010_advn250_pred`, rolling window `3`, stat `mean`, hours `all`, lag advantage threshold `-500.0`, similarity `ratio` `le` `0.05`, alpha `-0.05`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `651`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend9_db21_hournight_r2_mean_an010_advn250_pred` | 6.3970% | 11.1941% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend10_night_then_all_r3_mean_an005_advn500_pred` | 6.3918% | 11.1163% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend10_night_then_all_r3_mean_an005_advn500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend10_night_then_all_r3_mean_an005_advn500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend10_night_then_all_r3_mean_an005_advn500_v1_plot.png`

### lag24blend10_all_then_night_r2_mean_an010_advn250_v1

- Input experiment: `lag24blend9_db21_hourall_r3_mean_an005_advn500_v1`.
- Shifted lag24 blend adjuster: source `lag24blend9_db21_hourall_r3_mean_an005_advn500_pred`, lag `f_price_lag_24`, mode `hour`, signal source `lag24blend9_db21_hourall_r3_mean_an005_advn500_pred`, rolling window `2`, stat `mean`, hours `night`, lag advantage threshold `-250.0`, similarity `ratio` `le` `0.05`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `187`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend9_db21_hourall_r3_mean_an005_advn500_pred` | 6.4021% | 11.1360% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend10_all_then_night_r2_mean_an010_advn250_pred` | 6.3910% | 11.1163% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend10_all_then_night_r2_mean_an010_advn250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend10_all_then_night_r2_mean_an010_advn250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend10_all_then_night_r2_mean_an010_advn250_v1_plot.png`

### hourbias15_lag10_h789111718_r1_b005_wmape20_v1

- Input experiment: `lag24blend10_all_then_night_r2_mean_an010_advn250_v1`.
- Shifted same-hour bias adjuster: source `lag24blend10_all_then_night_r2_mean_an010_advn250_pred`, rolling same-hour observations `1`, stat `mean`, beta `0.05`, hours `7-9,11,17,18`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `117`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend10_all_then_night_r2_mean_an010_advn250_pred` | 6.3910% | 11.1163% | 2209 |
| `hourbias15_lag10_h789111718_r1_b005_wmape20_pred` | 6.3834% | 11.1206% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias15_lag10_h789111718_r1_b005_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias15_lag10_h789111718_r1_b005_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias15_lag10_h789111718_r1_b005_wmape20_v1_plot.png`

### hourbias15_lag10_evening_r8_mean_bn030_abs300_v1

- Input experiment: `lag24blend10_all_then_night_r2_mean_an010_advn250_v1`.
- Shifted same-hour bias adjuster: source `lag24blend10_all_then_night_r2_mean_an010_advn250_pred`, rolling same-hour observations `8`, stat `mean`, beta `-0.3`, hours `19-23`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `52`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend10_all_then_night_r2_mean_an010_advn250_pred` | 6.3910% | 11.1163% | 2209 |
| `hourbias15_lag10_evening_r8_mean_bn030_abs300_pred` | 6.3830% | 11.0893% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias15_lag10_evening_r8_mean_bn030_abs300_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias15_lag10_evening_r8_mean_bn030_abs300_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias15_lag10_evening_r8_mean_bn030_abs300_v1_plot.png`

### hourbias16_h15_morning_then_evening_v1

- Input experiment: `hourbias15_lag10_h789111718_r1_b005_wmape20_v1`.
- Shifted same-hour bias adjuster: source `hourbias15_lag10_h789111718_r1_b005_wmape20_pred`, rolling same-hour observations `8`, stat `mean`, beta `-0.3`, hours `19-23`, gate `absbias` threshold `300.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `52`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias15_lag10_h789111718_r1_b005_wmape20_pred` | 6.3834% | 11.1206% | 2209 |
| `hourbias16_h15_morning_then_evening_pred` | 6.3754% | 11.0936% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias16_h15_morning_then_evening_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias16_h15_morning_then_evening_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias16_h15_morning_then_evening_v1_plot.png`

### hourbias16_h15_evening_then_morning_v1

- Input experiment: `hourbias15_lag10_evening_r8_mean_bn030_abs300_v1`.
- Shifted same-hour bias adjuster: source `hourbias15_lag10_evening_r8_mean_bn030_abs300_pred`, rolling same-hour observations `1`, stat `mean`, beta `0.05`, hours `7-9,11,17,18`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `117`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias15_lag10_evening_r8_mean_bn030_abs300_pred` | 6.3830% | 11.0893% | 2209 |
| `hourbias16_h15_evening_then_morning_pred` | 6.3754% | 11.0936% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias16_h15_evening_then_morning_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias16_h15_evening_then_morning_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias16_h15_evening_then_morning_v1_plot.png`

### daybias22_h16_h789111718_d14_bn050_wmape10_v1

- Input experiment: `hourbias16_h15_evening_then_morning_v1`.
- Rolling day-bias adjuster: source `hourbias16_h15_evening_then_morning_pred`, rolling days `14`, beta `-0.5`, hours `7-9,11,17,18`, gate `wmape` threshold `10.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `36`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias16_h15_evening_then_morning_pred` | 6.3754% | 11.0936% | 2209 |
| `daybias22_h16_h789111718_d14_bn050_wmape10_pred` | 6.3709% | 11.0923% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias22_h16_h789111718_d14_bn050_wmape10_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias22_h16_h789111718_d14_bn050_wmape10_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias22_h16_h789111718_d14_bn050_wmape10_v1_plot.png`

### daybias22_h16_evening_d2_b015_abs250_v1

- Input experiment: `hourbias16_h15_evening_then_morning_v1`.
- Rolling day-bias adjuster: source `hourbias16_h15_evening_then_morning_pred`, rolling days `2`, beta `0.15`, hours `19-23`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `65`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias16_h15_evening_then_morning_pred` | 6.3754% | 11.0936% | 2209 |
| `daybias22_h16_evening_d2_b015_abs250_pred` | 6.3712% | 11.0923% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias22_h16_evening_d2_b015_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias22_h16_evening_d2_b015_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias22_h16_evening_d2_b015_abs250_v1_plot.png`

### daybias23_h789_then_evening_v1

- Input experiment: `daybias22_h16_h789111718_d14_bn050_wmape10_v1`.
- Rolling day-bias adjuster: source `daybias22_h16_h789111718_d14_bn050_wmape10_pred`, rolling days `2`, beta `0.15`, hours `19-23`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `65`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias22_h16_h789111718_d14_bn050_wmape10_pred` | 6.3709% | 11.0923% | 2209 |
| `daybias23_h789_then_evening_pred` | 6.3666% | 11.0910% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias23_h789_then_evening_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias23_h789_then_evening_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias23_h789_then_evening_v1_plot.png`

### daybias23_evening_then_h789_v1

- Input experiment: `daybias22_h16_evening_d2_b015_abs250_v1`.
- Rolling day-bias adjuster: source `daybias22_h16_evening_d2_b015_abs250_pred`, rolling days `14`, beta `-0.5`, hours `7-9,11,17,18`, gate `wmape` threshold `10.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `36`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias22_h16_evening_d2_b015_abs250_pred` | 6.3712% | 11.0923% | 2209 |
| `daybias23_evening_then_h789_pred` | 6.3667% | 11.0913% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias23_evening_then_h789_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias23_evening_then_h789_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias23_evening_then_h789_v1_plot.png`

### lag24blend11_db23_hour21_all_an020_advn250_v1

- Input experiment: `daybias23_h789_then_evening_v1`.
- Shifted lag24 blend adjuster: source `daybias23_h789_then_evening_pred`, lag `f_price_lag_24`, mode `hour`, signal source `daybias23_h789_then_evening_pred`, rolling window `21`, stat `mean`, hours `all`, lag advantage threshold `-250.0`, similarity `ratio` `le` `0.05`, alpha `-0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `35`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias23_h789_then_evening_pred` | 6.3666% | 11.0910% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend11_db23_hour21_all_an020_advn250_pred` | 6.3512% | 11.0910% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend11_db23_hour21_all_an020_advn250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend11_db23_hour21_all_an020_advn250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend11_db23_hour21_all_an020_advn250_v1_plot.png`

### lag24blend11_db23_hour5_day_an010_adv0_v1

- Input experiment: `daybias23_h789_then_evening_v1`.
- Shifted lag24 blend adjuster: source `daybias23_h789_then_evening_pred`, lag `f_price_lag_24`, mode `hour`, signal source `daybias23_h789_then_evening_pred`, rolling window `5`, stat `median`, hours `day`, lag advantage threshold `0.0`, similarity `ratio` `le` `0.05`, alpha `-0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `90`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias23_h789_then_evening_pred` | 6.3666% | 11.0910% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lag24blend11_db23_hour5_day_an010_adv0_pred` | 6.3597% | 11.0854% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend11_db23_hour5_day_an010_adv0_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend11_db23_hour5_day_an010_adv0_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24blend11_db23_hour5_day_an010_adv0_v1_plot.png`

### groupbias12_lag11_srcbin3_med_day_b025_abs700_v1

- Input experiment: `lag24blend11_db23_hour21_all_an020_advn250_v1`.
- Shifted group-bias adjuster: source `lag24blend11_db23_hour21_all_an020_advn250_pred`, group `hour,source_bin`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.25`, hours `day`, gate `absbias` threshold `700.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `43`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend11_db23_hour21_all_an020_advn250_pred` | 6.3512% | 11.0910% | 2209 |
| `groupbias12_lag11_srcbin3_med_day_b025_abs700_pred` | 6.3332% | 11.0812% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias12_lag11_srcbin3_med_day_b025_abs700_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias12_lag11_srcbin3_med_day_b025_abs700_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias12_lag11_srcbin3_med_day_b025_abs700_v1_plot.png`

### groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_v1

- Input experiment: `lag24blend11_db23_hour21_all_an020_advn250_v1`.
- Shifted group-bias adjuster: source `lag24blend11_db23_hour21_all_an020_advn250_pred`, group `hour,source_ratio_bin,weekend`, source bins `-1,100,500,1000,2000,4000,7000,10000,13000,1000000000`, ratio bins `-0.01,0.01,0.05,0.1,0.2,0.5,0.85,0.98,1.01`, rolling group observations `5`, stat `median`, beta `-0.3`, hours `7-9,11,17,18`, gate `wmape` threshold `25.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `62`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24blend11_db23_hour21_all_an020_advn250_pred` | 6.3512% | 11.0910% | 2209 |
| `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred` | 6.3284% | 11.0746% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_v1_plot.png`

### hourbias17_gb12_midday_r21_med_bn050_abs250_v1

- Input experiment: `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_v1`.
- Shifted same-hour bias adjuster: source `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.5`, hours `11-15`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `21`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred` | 6.3284% | 11.0746% | 2209 |
| `hourbias17_gb12_midday_r21_med_bn050_abs250_pred` | 6.3209% | 11.0746% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias17_gb12_midday_r21_med_bn050_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias17_gb12_midday_r21_med_bn050_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias17_gb12_midday_r21_med_bn050_abs250_v1_plot.png`

### daybias24_gb12_all_d14_b120_wmape12_v1

- Input experiment: `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_v1`.
- Rolling day-bias adjuster: source `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `groupbias12_lag11_ratweek5_med_h789111718_bn030_wmape25_pred` | 6.3284% | 11.0746% | 2209 |
| `daybias24_gb12_all_d14_b120_wmape12_pred` | 6.3232% | 11.0359% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias24_gb12_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias24_gb12_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias24_gb12_all_d14_b120_wmape12_v1_plot.png`

### daybias24_h17_all_d14_b120_wmape12_v1

- Input experiment: `hourbias17_gb12_midday_r21_med_bn050_abs250_v1`.
- Rolling day-bias adjuster: source `hourbias17_gb12_midday_r21_med_bn050_abs250_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias17_gb12_midday_r21_med_bn050_abs250_pred` | 6.3209% | 11.0746% | 2209 |
| `daybias24_h17_all_d14_b120_wmape12_pred` | 6.3157% | 11.0359% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias24_h17_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias24_h17_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias24_h17_all_d14_b120_wmape12_v1_plot.png`

### hourbias17_after_db24_midday_r21_med_bn050_abs250_v1

- Input experiment: `daybias24_gb12_all_d14_b120_wmape12_v1`.
- Shifted same-hour bias adjuster: source `daybias24_gb12_all_d14_b120_wmape12_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.5`, hours `11-15`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `21`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias24_gb12_all_d14_b120_wmape12_pred` | 6.3232% | 11.0359% | 2209 |
| `hourbias17_after_db24_midday_r21_med_bn050_abs250_pred` | 6.3157% | 11.0359% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias17_after_db24_midday_r21_med_bn050_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias17_after_db24_midday_r21_med_bn050_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias17_after_db24_midday_r21_med_bn050_abs250_v1_plot.png`

### candblend1_h24_sr5_med_eve_ge1000_an030_v1

- Input experiment: `daybias24_h17_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias24_h17_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,source_ratio_bin`, rolling group observations `5`, stat `median`, advantage threshold `-100.0`, hours `19-23`, distance `ge_abs` `1000.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `21`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias24_h17_all_d14_b120_wmape12_pred` | 6.3157% | 11.0359% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend1_h24_sr5_med_eve_ge1000_an030_pred` | 6.2887% | 10.8793% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_sr5_med_eve_ge1000_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_sr5_med_eve_ge1000_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_sr5_med_eve_ge1000_an030_v1_plot.png`

### candblend1_h24_cr21_med_night_ge010_a010_v1

- Input experiment: `daybias24_h17_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias24_h17_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `21`, stat `median`, advantage threshold `-500.0`, hours `night`, distance `ge_rel` `0.1`, alpha `0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `57`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias24_h17_all_d14_b120_wmape12_pred` | 6.3157% | 11.0359% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend1_h24_cr21_med_night_ge010_a010_pred` | 6.2917% | 10.9500% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_cr21_med_night_ge010_a010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_cr21_med_night_ge010_a010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_cr21_med_night_ge010_a010_v1_plot.png`

### candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1

- Input experiment: `candblend1_h24_sr5_med_eve_ge1000_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend1_h24_sr5_med_eve_ge1000_an030_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `21`, stat `median`, advantage threshold `-500.0`, hours `night`, distance `ge_rel` `0.1`, alpha `0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `59`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend1_h24_sr5_med_eve_ge1000_an030_pred` | 6.2887% | 10.8793% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred` | 6.2674% | 10.8033% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1_plot.png`

### candblend1_h24_cr13_mean_day_le2000_an030_v1

- Input experiment: `daybias24_h17_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias24_h17_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `13`, stat `mean`, advantage threshold `-250.0`, hours `day`, distance `le_abs` `2000.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `85`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias24_h17_all_d14_b120_wmape12_pred` | 6.3157% | 11.0359% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend1_h24_cr13_mean_day_le2000_an030_pred` | 6.2990% | 11.0359% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_cr13_mean_day_le2000_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_cr13_mean_day_le2000_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend1_h24_cr13_mean_day_le2000_an030_v1_plot.png`

### hourbias18_cb2_midday_r21_med_bn050_abs250_v1

- Input experiment: `candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1`.
- Shifted same-hour bias adjuster: source `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.5`, hours `11-15`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `23`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred` | 6.2674% | 10.8033% | 2209 |
| `hourbias18_cb2_midday_r21_med_bn050_abs250_pred` | 6.2758% | 10.8033% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias18_cb2_midday_r21_med_bn050_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias18_cb2_midday_r21_med_bn050_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias18_cb2_midday_r21_med_bn050_abs250_v1_plot.png`

### daybias25_cb2_all_d14_b120_wmape12_v1

- Input experiment: `candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1`.
- Rolling day-bias adjuster: source `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred` | 6.2674% | 10.8033% | 2209 |
| `daybias25_cb2_all_d14_b120_wmape12_pred` | 6.2645% | 10.7819% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias25_cb2_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias25_cb2_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias25_cb2_all_d14_b120_wmape12_v1_plot.png`

### candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1

- Input experiment: `candblend2_eve_then_night_h24_cr21_med_ge010_a010_v1`.
- Shifted candidate-blend adjuster: source `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `13`, stat `mean`, advantage threshold `-250.0`, hours `day`, distance `le_abs` `2000.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `85`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend2_eve_then_night_h24_cr21_med_ge010_a010_pred` | 6.2674% | 10.8033% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred` | 6.2507% | 10.8033% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1_plot.png`

### daybias25_cb3_all_d14_b120_wmape12_v1

- Input experiment: `candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1`.
- Rolling day-bias adjuster: source `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred` | 6.2507% | 10.8033% | 2209 |
| `daybias25_cb3_all_d14_b120_wmape12_pred` | 6.2478% | 10.7819% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias25_cb3_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias25_cb3_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias25_cb3_all_d14_b120_wmape12_v1_plot.png`

### candblend4_cb3_prof7_midday_hcr13_med_le1000_a010_v1

- Input experiment: `candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred`, candidate `f_rolling_mean_hour_7d`, group `hour,candidate_ratio_bin`, rolling group observations `13`, stat `median`, advantage threshold `-250.0`, hours `midday`, distance `le_abs` `1000.0`, alpha `0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `75`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred` | 6.2507% | 10.8033% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `candblend4_cb3_prof7_midday_hcr13_med_le1000_a010_pred` | 6.2512% | 10.8020% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_cb3_prof7_midday_hcr13_med_le1000_a010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_cb3_prof7_midday_hcr13_med_le1000_a010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_cb3_prof7_midday_hcr13_med_le1000_a010_v1_plot.png`

### candblend4_cb3_lag168_peak_hcr13_med_ge010_a005_v1

- Input experiment: `candblend3_cb2_day_h24_cr13_mean_le2000_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred`, candidate `f_price_lag_168`, group `hour,candidate_ratio_bin`, rolling group observations `13`, stat `median`, advantage threshold `-250.0`, hours `peakerr`, distance `ge_rel` `0.1`, alpha `0.05`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `72`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend3_cb2_day_h24_cr13_mean_le2000_an030_pred` | 6.2507% | 10.8033% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `candblend4_cb3_lag168_peak_hcr13_med_ge010_a005_pred` | 6.2550% | 10.8146% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_cb3_lag168_peak_hcr13_med_ge010_a005_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_cb3_lag168_peak_hcr13_med_ge010_a005_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_cb3_lag168_peak_hcr13_med_ge010_a005_v1_plot.png`

### candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1

- Input experiment: `daybias25_cb3_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias25_cb3_all_d14_b120_wmape12_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,weekend`, rolling group observations `3`, stat `median`, advantage threshold `100.0`, hours `peakerr`, distance `ge_abs` `1000.0`, alpha `-0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `16`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias25_cb3_all_d14_b120_wmape12_pred` | 6.2478% | 10.7819% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred` | 6.2173% | 10.6467% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1_plot.png`

### candblend4_db25_prof3_srdb5_med_day_ge1000_a050_v1

- Input experiment: `daybias25_cb3_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias25_cb3_all_d14_b120_wmape12_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `5`, stat `median`, advantage threshold `-250.0`, hours `7-18`, distance `ge_abs` `1000.0`, alpha `0.5`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `12`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias25_cb3_all_d14_b120_wmape12_pred` | 6.2478% | 10.7819% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend4_db25_prof3_srdb5_med_day_ge1000_a050_pred` | 6.2277% | 10.7819% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_srdb5_med_day_ge1000_a050_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_srdb5_med_day_ge1000_a050_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_srdb5_med_day_ge1000_a050_v1_plot.png`

### candblend4_db25_prof3_srdb8_med_day_none_a030_v1

- Input experiment: `daybias25_cb3_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias25_cb3_all_d14_b120_wmape12_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `0.0`, hours `7-18`, distance `none` `0.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `71`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias25_cb3_all_d14_b120_wmape12_pred` | 6.2478% | 10.7819% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend4_db25_prof3_srdb8_med_day_none_a030_pred` | 6.2178% | 10.8136% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_srdb8_med_day_none_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_srdb8_med_day_none_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend4_db25_prof3_srdb8_med_day_none_a030_v1_plot.png`

### daybias26_cb4_all_d14_b120_wmape12_v1

- Input experiment: `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1`.
- Rolling day-bias adjuster: source `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred` | 6.2173% | 10.6467% | 2209 |
| `daybias26_cb4_all_d14_b120_wmape12_pred` | 6.2151% | 10.6297% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb4_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb4_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb4_all_d14_b120_wmape12_v1_plot.png`

### candblend5_cb4_prof3_srdb8_med_day_none_a030_v1

- Input experiment: `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1`.
- Shifted candidate-blend adjuster: source `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `0.0`, hours `7-18`, distance `none` `0.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `71`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred` | 6.2173% | 10.6467% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend5_cb4_prof3_srdb8_med_day_none_a030_pred` | 6.1874% | 10.6784% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend5_cb4_prof3_srdb8_med_day_none_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend5_cb4_prof3_srdb8_med_day_none_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend5_cb4_prof3_srdb8_med_day_none_a030_v1_plot.png`

### candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_v1

- Input experiment: `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_v1`.
- Shifted candidate-blend adjuster: source `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `5`, stat `median`, advantage threshold `-250.0`, hours `7-18`, distance `ge_abs` `1000.0`, alpha `0.5`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `12`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend4_db25_prof3_hw3_med_peak_ge1000_an020_pred` | 6.2173% | 10.6467% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_pred` | 6.1972% | 10.6467% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_v1_plot.png`

### daybias26_cb5_all_d14_b120_wmape12_v1

- Input experiment: `candblend5_cb4_prof3_srdb8_med_day_none_a030_v1`.
- Rolling day-bias adjuster: source `candblend5_cb4_prof3_srdb8_med_day_none_a030_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend5_cb4_prof3_srdb8_med_day_none_a030_pred` | 6.1874% | 10.6784% | 2209 |
| `daybias26_cb5_all_d14_b120_wmape12_pred` | 6.1843% | 10.6559% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb5_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb5_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb5_all_d14_b120_wmape12_v1_plot.png`

### daybias26_cb5ge_all_d14_b120_wmape12_v1

- Input experiment: `candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_v1`.
- Rolling day-bias adjuster: source `candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend5_cb4_prof3_srdb5_med_day_ge1000_a050_pred` | 6.1972% | 10.6467% | 2209 |
| `daybias26_cb5ge_all_d14_b120_wmape12_pred` | 6.1950% | 10.6297% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb5ge_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb5ge_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias26_cb5ge_all_d14_b120_wmape12_v1_plot.png`

### hourbias19_cb5_midday_r21_med_bn050_abs250_v1

- Input experiment: `candblend5_cb4_prof3_srdb8_med_day_none_a030_v1`.
- Shifted same-hour bias adjuster: source `candblend5_cb4_prof3_srdb8_med_day_none_a030_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.5`, hours `11-15`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `27`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend5_cb4_prof3_srdb8_med_day_none_a030_pred` | 6.1874% | 10.6784% | 2209 |
| `hourbias19_cb5_midday_r21_med_bn050_abs250_pred` | 6.1978% | 10.6784% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias19_cb5_midday_r21_med_bn050_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias19_cb5_midday_r21_med_bn050_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias19_cb5_midday_r21_med_bn050_abs250_v1_plot.png`

### candblend6_db26_h24_cr21_med_night_ge010_a010_v1

- Input experiment: `daybias26_cb5_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias26_cb5_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `21`, stat `median`, advantage threshold `-500.0`, hours `night`, distance `ge_rel` `0.1`, alpha `0.1`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `53`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias26_cb5_all_d14_b120_wmape12_pred` | 6.1843% | 10.6559% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend6_db26_h24_cr21_med_night_ge010_a010_pred` | 6.2364% | 10.7336% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_cr21_med_night_ge010_a010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_cr21_med_night_ge010_a010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_cr21_med_night_ge010_a010_v1_plot.png`

### candblend6_db26_h24_sr5_med_eve_ge1000_an030_v1

- Input experiment: `daybias26_cb5_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias26_cb5_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,source_ratio_bin`, rolling group observations `5`, stat `median`, advantage threshold `-100.0`, hours `19-23`, distance `ge_abs` `1000.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `21`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias26_cb5_all_d14_b120_wmape12_pred` | 6.1843% | 10.6559% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend6_db26_h24_sr5_med_eve_ge1000_an030_pred` | 6.1977% | 10.7267% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_sr5_med_eve_ge1000_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_sr5_med_eve_ge1000_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_sr5_med_eve_ge1000_an030_v1_plot.png`

### candblend6_db26_h24_cr13_mean_day_le2000_an030_v1

- Input experiment: `daybias26_cb5_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias26_cb5_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `13`, stat `mean`, advantage threshold `-250.0`, hours `day`, distance `le_abs` `2000.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `77`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias26_cb5_all_d14_b120_wmape12_pred` | 6.1843% | 10.6559% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred` | 6.1717% | 10.6559% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_cr13_mean_day_le2000_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_cr13_mean_day_le2000_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend6_db26_h24_cr13_mean_day_le2000_an030_v1_plot.png`

### daybias27_cb6_all_d14_b120_wmape12_v1

- Input experiment: `candblend6_db26_h24_cr13_mean_day_le2000_an030_v1`.
- Rolling day-bias adjuster: source `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred` | 6.1717% | 10.6559% | 2209 |
| `daybias27_cb6_all_d14_b120_wmape12_pred` | 6.1704% | 10.6461% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb6_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb6_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb6_all_d14_b120_wmape12_v1_plot.png`

### candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_v1

- Input experiment: `candblend6_db26_h24_cr13_mean_day_le2000_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,weekend`, rolling group observations `3`, stat `median`, advantage threshold `100.0`, hours `peakerr`, distance `ge_abs` `1000.0`, alpha `-0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `15`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred` | 6.1717% | 10.6559% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_pred` | 6.1780% | 10.5470% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_v1_plot.png`

### candblend7_cb6_prof3_srdb8_med_day_none_a030_v1

- Input experiment: `candblend6_db26_h24_cr13_mean_day_le2000_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `0.0`, hours `7-18`, distance `none` `0.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `65`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend6_db26_h24_cr13_mean_day_le2000_an030_pred` | 6.1717% | 10.6559% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend7_cb6_prof3_srdb8_med_day_none_a030_pred` | 6.1588% | 10.6742% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend7_cb6_prof3_srdb8_med_day_none_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend7_cb6_prof3_srdb8_med_day_none_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend7_cb6_prof3_srdb8_med_day_none_a030_v1_plot.png`

### daybias27_cb7_all_d14_b120_wmape12_v1

- Input experiment: `candblend7_cb6_prof3_srdb8_med_day_none_a030_v1`.
- Rolling day-bias adjuster: source `candblend7_cb6_prof3_srdb8_med_day_none_a030_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend7_cb6_prof3_srdb8_med_day_none_a030_pred` | 6.1588% | 10.6742% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb7_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb7_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb7_all_d14_b120_wmape12_v1_plot.png`

### daybias27_cb7peak_all_d14_b120_wmape12_v1

- Input experiment: `candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_v1`.
- Rolling day-bias adjuster: source `candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend7_cb6_prof3_hw3_med_peak_ge1000_an020_pred` | 6.1780% | 10.5470% | 2209 |
| `daybias27_cb7peak_all_d14_b120_wmape12_pred` | 6.1765% | 10.5361% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb7peak_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb7peak_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias27_cb7peak_all_d14_b120_wmape12_v1_plot.png`

### hourbias20_cb7_midday_r21_med_bn050_abs250_v1

- Input experiment: `candblend7_cb6_prof3_srdb8_med_day_none_a030_v1`.
- Shifted same-hour bias adjuster: source `candblend7_cb6_prof3_srdb8_med_day_none_a030_pred`, rolling same-hour observations `21`, stat `median`, beta `-0.5`, hours `11-15`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `26`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend7_cb6_prof3_srdb8_med_day_none_a030_pred` | 6.1588% | 10.6742% | 2209 |
| `hourbias20_cb7_midday_r21_med_bn050_abs250_pred` | 6.1705% | 10.6742% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias20_cb7_midday_r21_med_bn050_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias20_cb7_midday_r21_med_bn050_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias20_cb7_midday_r21_med_bn050_abs250_v1_plot.png`

### candblend8_db27_prof3_hw3_med_peak_ge1000_an020_v1

- Input experiment: `daybias27_cb7_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias27_cb7_all_d14_b120_wmape12_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,weekend`, rolling group observations `3`, stat `median`, advantage threshold `100.0`, hours `peakerr`, distance `ge_abs` `1000.0`, alpha `-0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `15`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend8_db27_prof3_hw3_med_peak_ge1000_an020_pred` | 6.1638% | 10.5555% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_prof3_hw3_med_peak_ge1000_an020_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_prof3_hw3_med_peak_ge1000_an020_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_prof3_hw3_med_peak_ge1000_an020_v1_plot.png`

### candblend8_db27_h24_cr13_mean_day_le2000_an030_v1

- Input experiment: `daybias27_cb7_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias27_cb7_all_d14_b120_wmape12_pred`, candidate `f_price_lag_24`, group `hour,candidate_ratio_bin`, rolling group observations `13`, stat `mean`, advantage threshold `-250.0`, hours `day`, distance `le_abs` `2000.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `73`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `candblend8_db27_h24_cr13_mean_day_le2000_an030_pred` | 6.1638% | 10.6644% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_h24_cr13_mean_day_le2000_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_h24_cr13_mean_day_le2000_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_h24_cr13_mean_day_le2000_an030_v1_plot.png`

### candblend8_db27_prof3_srdb8_med_day_none_a030_v1

- Input experiment: `daybias27_cb7_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias27_cb7_all_d14_b120_wmape12_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `0.0`, hours `7-18`, distance `none` `0.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `49`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend8_db27_prof3_srdb8_med_day_none_a030_pred` | 6.1798% | 10.6687% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_prof3_srdb8_med_day_none_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_prof3_srdb8_med_day_none_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_prof3_srdb8_med_day_none_a030_v1_plot.png`

### candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1

- Input experiment: `daybias27_cb7_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias27_cb7_all_d14_b120_wmape12_pred`, candidate `f_price_lag_48`, group `hour,low_source,low_candidate`, rolling group observations `3`, stat `median`, advantage threshold `-100.0`, hours `11-15`, distance `ge_rel` `0.1`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `11`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred` | 6.1249% | 10.6644% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1_plot.png`

### candblend8_db27_lag48_hlow3_mean_h1115_ge500_an030_v1

- Input experiment: `daybias27_cb7_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias27_cb7_all_d14_b120_wmape12_pred`, candidate `f_price_lag_48`, group `hour,low_source,low_candidate`, rolling group observations `3`, stat `mean`, advantage threshold `-100.0`, hours `11-15`, distance `ge_abs` `500.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `candblend8_db27_lag48_hlow3_mean_h1115_ge500_an030_pred` | 6.1251% | 10.6425% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_mean_h1115_ge500_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_mean_h1115_ge500_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_mean_h1115_ge500_an030_v1_plot.png`

### candblend8_db27_lag48_hlow3_med_day_ge500_an030_v1

- Input experiment: `daybias27_cb7_all_d14_b120_wmape12_v1`.
- Shifted candidate-blend adjuster: source `daybias27_cb7_all_d14_b120_wmape12_pred`, candidate `f_price_lag_48`, group `hour,low_source,low_candidate`, rolling group observations `3`, stat `median`, advantage threshold `-100.0`, hours `day`, distance `ge_abs` `500.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `38`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias27_cb7_all_d14_b120_wmape12_pred` | 6.1575% | 10.6644% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `candblend8_db27_lag48_hlow3_med_day_ge500_an030_pred` | 6.1325% | 10.6248% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_med_day_ge500_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_med_day_ge500_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend8_db27_lag48_hlow3_med_day_ge500_an030_v1_plot.png`

### daybias28_cb8_all_d14_b120_wmape12_v1

- Input experiment: `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1`.
- Rolling day-bias adjuster: source `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred` | 6.1249% | 10.6644% | 2209 |
| `daybias28_cb8_all_d14_b120_wmape12_pred` | 6.1235% | 10.6538% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias28_cb8_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias28_cb8_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias28_cb8_all_d14_b120_wmape12_v1_plot.png`

### candblend9_cb8_lag48_hlow3_mean_h1115_ge500_an030_v1

- Input experiment: `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred`, candidate `f_price_lag_48`, group `hour,low_source,low_candidate`, rolling group observations `3`, stat `mean`, advantage threshold `-100.0`, hours `11-15`, distance `ge_abs` `500.0`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `18`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred` | 6.1249% | 10.6644% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `candblend9_cb8_lag48_hlow3_mean_h1115_ge500_an030_pred` | 6.1445% | 10.6425% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend9_cb8_lag48_hlow3_mean_h1115_ge500_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend9_cb8_lag48_hlow3_mean_h1115_ge500_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend9_cb8_lag48_hlow3_mean_h1115_ge500_an030_v1_plot.png`

### candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1

- Input experiment: `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_v1`.
- Shifted candidate-blend adjuster: source `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred`, candidate `f_rolling_mean_hour_7d`, group `hour,summer,source_ratio_bin`, rolling group observations `5`, stat `median`, advantage threshold `250.0`, hours `all`, distance `ge_abs` `1000.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `10`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend8_db27_lag48_hlow3_med_h1115_gerel010_an030_pred` | 6.1249% | 10.6644% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1_plot.png`

### daybias28_cb9_all_d14_b120_wmape12_v1

- Input experiment: `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1`.
- Rolling day-bias adjuster: source `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred`, rolling days `14`, beta `1.2`, hours `0-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |
| `daybias28_cb9_all_d14_b120_wmape12_pred` | 6.1033% | 10.6339% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias28_cb9_all_d14_b120_wmape12_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias28_cb9_all_d14_b120_wmape12_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias28_cb9_all_d14_b120_wmape12_v1_plot.png`

### candblend10_cb9_lag48_hlow3_med_h1115_gerel010_an030_v1

- Input experiment: `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1`.
- Shifted candidate-blend adjuster: source `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred`, candidate `f_price_lag_48`, group `hour,low_source,low_candidate`, rolling group observations `3`, stat `median`, advantage threshold `-100.0`, hours `11-15`, distance `ge_rel` `0.1`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `11`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `candblend10_cb9_lag48_hlow3_med_h1115_gerel010_an030_pred` | 6.1217% | 10.6443% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_cb9_lag48_hlow3_med_h1115_gerel010_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_cb9_lag48_hlow3_med_h1115_gerel010_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_cb9_lag48_hlow3_med_h1115_gerel010_an030_v1_plot.png`

### candblend10_cb9_prof3_srdb8_med_day_none_a030_v1

- Input experiment: `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1`.
- Shifted candidate-blend adjuster: source `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `0.0`, hours `7-18`, distance `none` `0.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `50`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend10_cb9_prof3_srdb8_med_day_none_a030_pred` | 6.1260% | 10.6486% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_cb9_prof3_srdb8_med_day_none_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_cb9_prof3_srdb8_med_day_none_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_cb9_prof3_srdb8_med_day_none_a030_v1_plot.png`

### daybias29_cb9_midday_d1_bn050_wmape20_v1

- Input experiment: `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1`.
- Rolling day-bias adjuster: source `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred`, rolling days `1`, beta `-0.5`, hours `11-16`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `6`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |
| `daybias29_cb9_midday_d1_bn050_wmape20_pred` | 6.1008% | 10.6151% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_midday_d1_bn050_wmape20_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_midday_d1_bn050_wmape20_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_midday_d1_bn050_wmape20_v1_plot.png`

### daybias29_cb9_midday_d1_b010_abs500_v1

- Input experiment: `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1`.
- Rolling day-bias adjuster: source `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred`, rolling days `1`, beta `0.1`, hours `11-16`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `36`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |
| `daybias29_cb9_midday_d1_b010_abs500_pred` | 6.0988% | 10.6426% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_midday_d1_b010_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_midday_d1_b010_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_midday_d1_b010_abs500_v1_plot.png`

### daybias29_cb9_all_d8_bn030_wmape10_v1

- Input experiment: `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_v1`.
- Rolling day-bias adjuster: source `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred`, rolling days `8`, beta `-0.3`, hours `0-23`, gate `wmape` threshold `10.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `288`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `candblend9_cb8_prof7_hss5_med_all_ge1000_a030_pred` | 6.1047% | 10.6443% | 2209 |
| `daybias29_cb9_all_d8_bn030_wmape10_pred` | 6.1009% | 10.6020% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_all_d8_bn030_wmape10_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_all_d8_bn030_wmape10_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias29_cb9_all_d8_bn030_wmape10_v1_plot.png`

### daybias30_all_then_midday_d1_b010_abs500_v1

- Input experiment: `daybias29_cb9_all_d8_bn030_wmape10_v1`.
- Rolling day-bias adjuster: source `daybias29_cb9_all_d8_bn030_wmape10_pred`, rolling days `1`, beta `0.1`, hours `11-16`, gate `absbias` threshold `500.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `30`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias29_cb9_all_d8_bn030_wmape10_pred` | 6.1009% | 10.6020% | 2209 |
| `daybias30_all_then_midday_d1_b010_abs500_pred` | 6.0959% | 10.6071% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_all_then_midday_d1_b010_abs500_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_all_then_midday_d1_b010_abs500_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_all_then_midday_d1_b010_abs500_v1_plot.png`

### daybias30_midday_then_all_d8_bn030_wmape10_v1

- Input experiment: `daybias29_cb9_midday_d1_b010_abs500_v1`.
- Rolling day-bias adjuster: source `daybias29_cb9_midday_d1_b010_abs500_pred`, rolling days `8`, beta `-0.3`, hours `0-23`, gate `wmape` threshold `10.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `288`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias29_cb9_midday_d1_b010_abs500_pred` | 6.0988% | 10.6426% | 2209 |
| `daybias30_midday_then_all_d8_bn030_wmape10_pred` | 6.0941% | 10.5940% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_midday_then_all_d8_bn030_wmape10_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_midday_then_all_d8_bn030_wmape10_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_midday_then_all_d8_bn030_wmape10_v1_plot.png`

### daybias30_midneg_then_all_d8_bn030_wmape10_v1

- Input experiment: `daybias29_cb9_midday_d1_bn050_wmape20_v1`.
- Rolling day-bias adjuster: source `daybias29_cb9_midday_d1_bn050_wmape20_pred`, rolling days `8`, beta `-0.3`, hours `0-23`, gate `wmape` threshold `10.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `288`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias29_cb9_midday_d1_bn050_wmape20_pred` | 6.1008% | 10.6151% | 2209 |
| `daybias30_midneg_then_all_d8_bn030_wmape10_pred` | 6.0970% | 10.5730% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_midneg_then_all_d8_bn030_wmape10_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_midneg_then_all_d8_bn030_wmape10_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias30_midneg_then_all_d8_bn030_wmape10_v1_plot.png`

### candblend10_db30_lag48_hlow3_med_h1115_gerel010_an030_v1

- Input experiment: `daybias30_midday_then_all_d8_bn030_wmape10_v1`.
- Shifted candidate-blend adjuster: source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, candidate `f_price_lag_48`, group `hour,low_source,low_candidate`, rolling group observations `3`, stat `median`, advantage threshold `-100.0`, hours `11-15`, distance `ge_rel` `0.1`, alpha `-0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `11`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias30_midday_then_all_d8_bn030_wmape10_pred` | 6.0941% | 10.5940% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `candblend10_db30_lag48_hlow3_med_h1115_gerel010_an030_pred` | 6.1112% | 10.5940% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_lag48_hlow3_med_h1115_gerel010_an030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_lag48_hlow3_med_h1115_gerel010_an030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_lag48_hlow3_med_h1115_gerel010_an030_v1_plot.png`

### candblend10_db30_prof7_hss5_med_all_ge1000_a030_v1

- Input experiment: `daybias30_midday_then_all_d8_bn030_wmape10_v1`.
- Shifted candidate-blend adjuster: source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, candidate `f_rolling_mean_hour_7d`, group `hour,summer,source_ratio_bin`, rolling group observations `5`, stat `median`, advantage threshold `250.0`, hours `all`, distance `ge_abs` `1000.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `5`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias30_midday_then_all_d8_bn030_wmape10_pred` | 6.0941% | 10.5940% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `candblend10_db30_prof7_hss5_med_all_ge1000_a030_pred` | 6.1087% | 10.5940% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_prof7_hss5_med_all_ge1000_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_prof7_hss5_med_all_ge1000_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_prof7_hss5_med_all_ge1000_a030_v1_plot.png`

### candblend10_db30_prof3_srdb8_med_day_none_a030_v1

- Input experiment: `daybias30_midday_then_all_d8_bn030_wmape10_v1`.
- Shifted candidate-blend adjuster: source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, candidate `f_rolling_mean_hour_3d`, group `hour,source_ratio_bin,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `0.0`, hours `7-18`, distance `none` `0.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `55`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias30_midday_then_all_d8_bn030_wmape10_pred` | 6.0941% | 10.5940% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `candblend10_db30_prof3_srdb8_med_day_none_a030_pred` | 6.1179% | 10.6162% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_prof3_srdb8_med_day_none_a030_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_prof3_srdb8_med_day_none_a030_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_candblend10_db30_prof3_srdb8_med_day_none_a030_v1_plot.png`

### lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_v1

- Input experiment: `daybias30_midday_then_all_d8_bn030_wmape10_v1`.
- Shifted lag24 blend adjuster: source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, lag `f_price_lag_48`, mode `daily`, signal source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, signal op `le`, rolling window `3`, stat `mean`, hours `evening`, lag advantage threshold `-50.0`, similarity `ratio` `le` `0.05`, alpha `-0.15`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `40`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias30_midday_then_all_d8_bn030_wmape10_pred` | 6.0941% | 10.5940% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_pred` | 6.0675% | 10.3244% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_v1_plot.png`

### lagprofile1_db30_lag24_profabs2000_midday_a005_v1

- Input experiment: `daybias30_midday_then_all_d8_bn030_wmape10_v1`.
- Shifted lag24 blend adjuster: source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `daybias30_midday_then_all_d8_bn030_wmape10_pred`, signal op `ge`, rolling window `2`, stat `mean`, hours `midday`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `2000.0`, alpha `0.05`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `426`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias30_midday_then_all_d8_bn030_wmape10_pred` | 6.0941% | 10.5940% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lagprofile1_db30_lag24_profabs2000_midday_a005_pred` | 6.0655% | 10.6248% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile1_db30_lag24_profabs2000_midday_a005_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile1_db30_lag24_profabs2000_midday_a005_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile1_db30_lag24_profabs2000_midday_a005_v1_plot.png`

### lagprofile3_lag24_then_antilag48_eve_v1

- Input experiment: `lagprofile1_db30_lag24_profabs2000_midday_a005_v1`.
- Shifted lag24 blend adjuster: source `lagprofile1_db30_lag24_profabs2000_midday_a005_pred`, lag `f_price_lag_48`, mode `daily`, signal source `lagprofile1_db30_lag24_profabs2000_midday_a005_pred`, signal op `le`, rolling window `3`, stat `mean`, hours `evening`, lag advantage threshold `-50.0`, similarity `ratio` `le` `0.05`, alpha `-0.15`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `40`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lagprofile1_db30_lag24_profabs2000_midday_a005_pred` | 6.0655% | 10.6248% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `lagprofile3_lag24_then_antilag48_eve_pred` | 6.0389% | 10.3552% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile3_lag24_then_antilag48_eve_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile3_lag24_then_antilag48_eve_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile3_lag24_then_antilag48_eve_v1_plot.png`

### lagprofile3_antilag48_then_lag24_midday_v1

- Input experiment: `lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_v1`.
- Shifted lag24 blend adjuster: source `lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_pred`, lag `f_price_lag_24`, mode `similarity`, signal source `lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_pred`, signal op `ge`, rolling window `2`, stat `mean`, hours `midday`, lag advantage threshold `0.0`, similarity `profile_abs` `le` `2000.0`, alpha `0.05`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `426`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lagprofile2_db30_lag48_daily3_le_bn050_eve_an015_pred` | 6.0675% | 10.3244% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `lagprofile3_antilag48_then_lag24_midday_pred` | 6.0389% | 10.3552% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile3_antilag48_then_lag24_midday_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile3_antilag48_then_lag24_midday_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile3_antilag48_then_lag24_midday_v1_plot.png`

### lagprofile4_lp3_roll7_abs1000_morning_an015_v1

- Input experiment: `lagprofile3_lag24_then_antilag48_eve_v1`.
- Shifted lag24 blend adjuster: source `lagprofile3_lag24_then_antilag48_eve_pred`, lag `f_rolling_mean_hour_7d`, mode `similarity`, signal source `lagprofile3_lag24_then_antilag48_eve_pred`, signal op `ge`, rolling window `2`, stat `mean`, hours `morning`, lag advantage threshold `0.0`, similarity `absdiff` `le` `1000.0`, alpha `-0.15`.
- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.
- Adjusted rows: `156`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lagprofile3_lag24_then_antilag48_eve_pred` | 6.0389% | 10.3552% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `lagprofile4_lp3_roll7_abs1000_morning_an015_pred` | 6.0218% | 10.3585% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile4_lp3_roll7_abs1000_morning_an015_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile4_lp3_roll7_abs1000_morning_an015_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lagprofile4_lp3_roll7_abs1000_morning_an015_v1_plot.png`

### hourbias21_lp4_peakerr_r2_bn015_wmape40_v1

- Input experiment: `lagprofile4_lp3_roll7_abs1000_morning_an015_v1`.
- Shifted same-hour bias adjuster: source `lagprofile4_lp3_roll7_abs1000_morning_an015_pred`, rolling same-hour observations `2`, stat `mean`, beta `-0.15`, hours `0,7-9,11-17,21-22`, gate `wmape` threshold `40.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `260`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lagprofile4_lp3_roll7_abs1000_morning_an015_pred` | 6.0218% | 10.3585% | 2209 |
| `hourbias21_lp4_peakerr_r2_bn015_wmape40_pred` | 6.0100% | 10.3243% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias21_lp4_peakerr_r2_bn015_wmape40_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias21_lp4_peakerr_r2_bn015_wmape40_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias21_lp4_peakerr_r2_bn015_wmape40_v1_plot.png`

### hourbias22_hb21_peakerr_r8_bn020_wmape40_v1

- Input experiment: `hourbias21_lp4_peakerr_r2_bn015_wmape40_v1`.
- Shifted same-hour bias adjuster: source `hourbias21_lp4_peakerr_r2_bn015_wmape40_pred`, rolling same-hour observations `8`, stat `mean`, beta `-0.2`, hours `0,7-9,11-17,21-22`, gate `wmape` threshold `40.0`.
- Formula: `prediction = source - beta * shifted_rolling_same_hour_source_bias`; for each row, the signal uses only earlier observations of the same delivery hour.
- Adjusted rows: `384`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias21_lp4_peakerr_r2_bn015_wmape40_pred` | 6.0100% | 10.3243% | 2209 |
| `hourbias22_hb21_peakerr_r8_bn020_wmape40_pred` | 6.0027% | 10.3096% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias22_hb21_peakerr_r8_bn020_wmape40_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias22_hb21_peakerr_r8_bn020_wmape40_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hourbias22_hb21_peakerr_r8_bn020_wmape40_v1_plot.png`

### daybias31_hb22_midday_d8_b050_abs250_v1

- Input experiment: `hourbias22_hb21_peakerr_r8_bn020_wmape40_v1`.
- Rolling day-bias adjuster: source `hourbias22_hb21_peakerr_r8_bn020_wmape40_pred`, rolling days `8`, beta `0.5`, hours `11-16`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_daily_source_bias`; daily source bias is computed only from complete earlier days.
- Adjusted rows: `24`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hourbias22_hb21_peakerr_r8_bn020_wmape40_pred` | 6.0027% | 10.3096% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.9937% | 10.3096% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias31_hb22_midday_d8_b050_abs250_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias31_hb22_midday_d8_b050_abs250_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_daybias31_hb22_midday_d8_b050_abs250_v1_plot.png`

### tcn_lowregime_smoke_v1

- Split: train days `752`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- Tree teacher source: `current`.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `96`, history `168`, dropout `0.18`.
- Weights: daytime `1.45`, evening `1.35`, low-price `1.7`, daytime-low `1.8`, high-price `1.45`, low rel `0.06`, daytime-low rel `0.1`, low BCE `0.06`, daytime-low BCE `0.08`, high BCE `0.05`.
- Blend: mode `hour-low`, daytime-low probability threshold `0.4`, minimum rows `4`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 11.10% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.75% | 20.27% | 2209 |
| `neural_pred` | 21.39% | 65.32% | 2209 |
| `hybrid_pred` | 12.98% | 39.95% | 2209 |
| `hybrid_recent_calibrated_pred` | 10.83% | 23.98% | 2209 |
| `hybrid_guarded_pred` | 10.34% | 20.27% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_lowregime_smoke_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_lowregime_smoke_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_lowregime_smoke_v1_plot.png`

### tcn_lowregime_hourlow_v1

- Split: train days `752`, val days `45`, test days `93`.
- Test starts from day `2026-03-16`; evaluator uses one row per factual hour.
- Tree teacher source: `current`.
- History features `145`, future features `138`.
- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.
- Model: TCN residual-log hybrid, hidden `112`, history `168`, dropout `0.2`.
- Weights: daytime `1.55`, evening `1.25`, low-price `1.9`, daytime-low `2.2`, high-price `1.35`, low rel `0.08`, daytime-low rel `0.14`, low BCE `0.07`, daytime-low BCE `0.1`, high BCE `0.04`.
- Blend: mode `hour-low`, daytime-low probability threshold `0.4`, minimum rows `4`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_base_pred` | 11.10% | 30.37% | 2209 |
| `tree_recent_calibrated_pred` | 9.75% | 20.27% | 2209 |
| `neural_pred` | 17.96% | 62.53% | 2209 |
| `hybrid_pred` | 13.28% | 43.54% | 2209 |
| `hybrid_recent_calibrated_pred` | 10.84% | 25.33% | 2209 |
| `hybrid_guarded_pred` | 10.16% | 20.27% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_lowregime_hourlow_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_lowregime_hourlow_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tcn_lowregime_hourlow_v1_plot.png`

### lowcheck_hgb_daybias31_ratio_b005_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `ratio`, lookback `45` days, min train `21` days, blend `0.05`, apply recent days `93`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `lowcheck_hgb_ratio_b005_pred` | 6.70% | 11.88% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcheck_hgb_daybias31_ratio_b005_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcheck_hgb_daybias31_ratio_b005_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcheck_hgb_daybias31_ratio_b005_v1_plot.png`

### mlp_lowday_daybias31_logresid_b010_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `logresid`, lookback `60` days, min train `24` days, blend `0.1`, apply recent days `93`.
- Focus weights/gate: low `2.3`, daytime-low `2.5`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`2500.0`.
- Applied target days: `62`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_logresid_b010_pred` | 5.99% | 10.24% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b010_v1_plot.png`

### mlp_lowday_daybias31_logresid_b015_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `logresid`, lookback `60` days, min train `24` days, blend `0.15`, apply recent days `93`.
- Focus weights/gate: low `2.3`, daytime-low `2.5`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`2500.0`.
- Applied target days: `62`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_logresid_b015_pred` | 6.00% | 10.22% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b015_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b015_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b015_v1_plot.png`

### mlp_lowday_daybias31_logresid_b012_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `logresid`, lookback `60` days, min train `24` days, blend `0.12`, apply recent days `93`.
- Focus weights/gate: low `2.3`, daytime-low `2.5`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`2500.0`.
- Applied target days: `62`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_logresid_b012_pred` | 5.99% | 10.23% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b012_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b012_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b012_v1_plot.png`

### mlp_lowday_daybias31_ratio_b010_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `ratio`, lookback `60` days, min train `24` days, blend `0.1`, apply recent days `93`.
- Focus weights/gate: low `2.3`, daytime-low `2.5`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`2500.0`.
- Applied target days: `62`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_ratio_b010_pred` | 5.98% | 10.27% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_ratio_b010_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_ratio_b010_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_ratio_b010_v1_plot.png`

### mlp_lowday_daybias31_logresid_b012_tight_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `logresid`, lookback `60` days, min train `24` days, blend `0.12`, apply recent days `93`.
- Focus weights/gate: low `2.5`, daytime-low `3.0`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`1800.0`.
- Applied target days: `59`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_logresid_b012_tight_pred` | 5.99% | 10.32% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b012_tight_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b012_tight_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b012_tight_v1_plot.png`

### mlp_lowday_daybias31_logresid_b010_floor_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `logresid`, lookback `60` days, min train `24` days, blend `0.1`, apply recent days `93`.
- Focus weights/gate: low `2.3`, daytime-low `2.5`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`2500.0`.
- Applied target days: `62`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_logresid_b010_floor_pred` | 5.99% | 10.25% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b010_floor_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b010_floor_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_logresid_b010_floor_v1_plot.png`

### mlp_daylowmid_daybias31_logresid_b006_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `logresid`, lookback `60` days, min train `24` days, blend `0.06`, apply recent days `93`.
- Focus weights/gate: low `2.0`, daytime-low `2.3`, daytime `1.6`, evening `1.0`, apply hours `9-17`, source range `0.0`-`4000.0`.
- Applied target days: `68`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_daylowmid_logresid_b006_pred` | 6.00% | 10.29% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_daylowmid_daybias31_logresid_b006_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_daylowmid_daybias31_logresid_b006_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_daylowmid_daybias31_logresid_b006_v1_plot.png`

### mlp_lowday_daybias31_log_b010_floor_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Nonlinear rolling-origin stacker: model `mlp`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, target `log`, lookback `60` days, min train `24` days, blend `0.1`, apply recent days `93`.
- Focus weights/gate: low `2.3`, daytime-low `2.5`, daytime `1.5`, evening `1.0`, apply hours `10-16`, source range `0.0`-`2500.0`.
- Applied target days: `62`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.99% | 10.31% | 2209 |
| `mlp_lowday_log_b010_floor_pred` | 7.80% | 17.28% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_log_b010_floor_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_log_b010_floor_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_mlp_lowday_daybias31_log_b010_floor_v1_plot.png`

### lowcollapse_et_floor10_th070_v1

- Input experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`.
- Rolling-origin low-collapse classifier adjuster: classifier `et`, target `collapse100`, source `daybias31_hb22_midday_d8_b050_abs250_pred`, anchor `floor10`, probability threshold `0.7`, alpha `1.0`, hours `10-16`.
- For each delivery day, classifier training rows are strictly earlier than that day; current-row actual is not exposed as a feature.
- Adjusted rows: `177`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 5.9866% | 10.3012% | 2209 |
| `lowcollapse_et_floor10_th070_pred` | 5.9759% | 10.2628% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_et_floor10_th070_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_et_floor10_th070_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_et_floor10_th070_v1_plot.png`

### lowcollapse_after_mlp_lowday_th070_v1

- Input experiment: `mlp_lowday_daybias31_logresid_b010_floor_v1`.
- Rolling-origin low-collapse classifier adjuster: classifier `et`, target `collapse100`, source `mlp_lowday_logresid_b010_floor_pred`, anchor `floor10`, probability threshold `0.7`, alpha `1.0`, hours `10-16`.
- For each delivery day, classifier training rows are strictly earlier than that day; current-row actual is not exposed as a feature.
- Adjusted rows: `177`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `mlp_lowday_logresid_b010_floor_pred` | 5.9859% | 10.2450% | 2209 |
| `lowcollapse_after_mlp_lowday_th070_pred` | 5.9759% | 10.2063% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_after_mlp_lowday_th070_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_after_mlp_lowday_th070_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_after_mlp_lowday_th070_v1_plot.png`

### lowcollapse_after_mlp_lowday_th065_v1

- Input experiment: `mlp_lowday_daybias31_logresid_b010_floor_v1`.
- Rolling-origin low-collapse classifier adjuster: classifier `et`, target `collapse100`, source `mlp_lowday_logresid_b010_floor_pred`, anchor `floor10`, probability threshold `0.65`, alpha `1.0`, hours `10-16`.
- For each delivery day, classifier training rows are strictly earlier than that day; current-row actual is not exposed as a feature.
- Adjusted rows: `186`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `mlp_lowday_logresid_b010_floor_pred` | 5.9859% | 10.2450% | 2209 |
| `lowcollapse_after_mlp_lowday_th065_pred` | 5.9718% | 10.2060% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_after_mlp_lowday_th065_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_after_mlp_lowday_th065_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_after_mlp_lowday_th065_v1_plot.png`

### rebound_roll7h_after_lowcollapse_mlp_v1

- Input experiment: `lowcollapse_after_mlp_lowday_th065_v1`.
- Forecast-time rebound profile adjuster: source `lowcollapse_after_mlp_lowday_th065_pred`, candidate `f_rolling_mean_hour_7d`, alpha `0.08`, hours `10-13`, source range `0.0`-`2000.0`, rolling24 min `6000.0`, rolling24-hour7 diff min `3500.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `74`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `lowcollapse_after_mlp_lowday_th065_pred` | 5.9718% | 10.2060% | 2209 |
| `rebound_roll7h_after_lowcollapse_mlp_pred` | 5.9624% | 10.1930% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_roll7h_after_lowcollapse_mlp_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_roll7h_after_lowcollapse_mlp_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_roll7h_after_lowcollapse_mlp_v1_plot.png`

### h0_lag48_down_after_rebound_lowcollapse_v1

- Input experiment: `rebound_roll7h_after_lowcollapse_mlp_v1`.
- Forecast-time rebound profile adjuster: source `rebound_roll7h_after_lowcollapse_mlp_pred`, candidate `f_price_lag_48`, alpha `0.5`, hours `0`, source range `3000.0`-`9000.0`, rolling24 min `0.0`, rolling24-hour7 diff min `0.0`, candidate direction `down`, candidate absdiff min `0.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `21`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `rebound_roll7h_after_lowcollapse_mlp_pred` | 5.9624% | 10.1930% | 2209 |
| `h0_lag48_down_after_rebound_lowcollapse_pred` | 5.9887% | 10.0676% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h0_lag48_down_after_rebound_lowcollapse_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h0_lag48_down_after_rebound_lowcollapse_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h0_lag48_down_after_rebound_lowcollapse_v1_plot.png`

### h9_10_lag48_down_after_h0_v1

- Input experiment: `h0_lag48_down_after_rebound_lowcollapse_v1`.
- Forecast-time rebound profile adjuster: source `h0_lag48_down_after_rebound_lowcollapse_pred`, candidate `f_price_lag_48`, alpha `0.05`, hours `9-10`, source range `3000.0`-`9000.0`, rolling24 min `0.0`, rolling24-hour7 diff min `0.0`, candidate direction `down`, candidate absdiff min `2500.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `38`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `h0_lag48_down_after_rebound_lowcollapse_pred` | 5.9887% | 10.0676% | 2209 |
| `h9_10_lag48_down_after_h0_pred` | 5.9905% | 10.0163% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h9_10_lag48_down_after_h0_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h9_10_lag48_down_after_h0_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h9_10_lag48_down_after_h0_v1_plot.png`

### lowday_roll7_down_after_h9h0_v1

- Input experiment: `h9_10_lag48_down_after_h0_v1`.
- Forecast-time rebound profile adjuster: source `h9_10_lag48_down_after_h0_pred`, candidate `f_rolling_mean_hour_7d`, alpha `1.0`, hours `11-15`, source range `0.0`-`1000.0`, rolling24 min `0.0`, rolling24-hour7 diff min `0.0`, candidate direction `down`, candidate absdiff min `0.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `14`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `h9_10_lag48_down_after_h0_pred` | 5.9905% | 10.0163% | 2209 |
| `lowday_roll7_down_after_h9h0_pred` | 5.9867% | 9.9855% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowday_roll7_down_after_h9h0_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowday_roll7_down_after_h9h0_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowday_roll7_down_after_h9h0_v1_plot.png`

### lag24_up_after_14d_lowday_v1

- Input experiment: `lowday_roll7_down_after_h9h0_v1`.
- Forecast-time rebound profile adjuster: source `lowday_roll7_down_after_h9h0_pred`, candidate `f_price_lag_24`, alpha `0.02`, hours `all`, source range `3000.0`-`9000.0`, rolling24 min `0.0`, rolling24-hour7 diff min `0.0`, candidate direction `up`, candidate absdiff min `3500.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `71`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `lowday_roll7_down_after_h9h0_pred` | 5.9867% | 9.9855% | 2209 |
| `lag24_up_after_14d_lowday_pred` | 5.9761% | 9.9647% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24_up_after_14d_lowday_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24_up_after_14d_lowday_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lag24_up_after_14d_lowday_v1_plot.png`

### tree_recent_shiftblend_after_14d_lowday_v1

- Input experiment: `lag24_up_after_14d_lowday_v1`.
- Shifted candidate-blend adjuster: source `lag24_up_after_14d_lowday_pred`, candidate `tree_recent_calibrated_pred`, group `hour`, rolling group observations `3`, stat `mean`, advantage threshold `0.0`, hours `all`, distance `le_abs` `2000.0`, alpha `0.2`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `742`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lag24_up_after_14d_lowday_pred` | 5.9761% | 9.9647% | 2209 |
| `tree_recent_shiftblend_after_14d_lowday_pred` | 5.9087% | 9.9911% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_shiftblend_after_14d_lowday_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_shiftblend_after_14d_lowday_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_shiftblend_after_14d_lowday_v1_plot.png`

### tree_recent_peakerr_shiftblend_after_target_v1

- Input experiment: `tree_recent_shiftblend_after_14d_lowday_v1`.
- Shifted candidate-blend adjuster: source `tree_recent_shiftblend_after_14d_lowday_pred`, candidate `tree_recent_calibrated_pred`, group `hour`, rolling group observations `13`, stat `mean`, advantage threshold `0.0`, hours `peakerr`, distance `le_abs` `1000.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `282`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_recent_shiftblend_after_14d_lowday_pred` | 5.9087% | 9.9911% | 2209 |
| `tree_recent_peakerr_shiftblend_after_target_pred` | 5.8762% | 9.9946% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_peakerr_shiftblend_after_target_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_peakerr_shiftblend_after_target_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_peakerr_shiftblend_after_target_v1_plot.png`

### ratio_hour_bias_after_peakblend_v1

- Input experiment: `tree_recent_peakerr_shiftblend_after_target_v1`.
- Shifted group-bias adjuster: source `tree_recent_peakerr_shiftblend_after_target_pred`, group `hour,source_ratio_bin`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `0.1`, hours `all`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `235`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_recent_peakerr_shiftblend_after_target_pred` | 5.8762% | 9.9946% | 2209 |
| `ratio_hour_bias_after_peakblend_pred` | 5.8543% | 9.9507% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ratio_hour_bias_after_peakblend_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ratio_hour_bias_after_peakblend_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ratio_hour_bias_after_peakblend_v1_plot.png`

### tree_recent_peakerr_srcbin_after_ratiobias_v1

- Input experiment: `ratio_hour_bias_after_peakblend_v1`.
- Shifted candidate-blend adjuster: source `ratio_hour_bias_after_peakblend_pred`, candidate `tree_recent_calibrated_pred`, group `hour,source_bin`, rolling group observations `13`, stat `median`, advantage threshold `0.0`, hours `peakerr`, distance `le_abs` `500.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `293`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `ratio_hour_bias_after_peakblend_pred` | 5.8543% | 9.9507% | 2209 |
| `tree_recent_peakerr_srcbin_after_ratiobias_pred` | 5.8250% | 9.9839% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_peakerr_srcbin_after_ratiobias_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_peakerr_srcbin_after_ratiobias_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_peakerr_srcbin_after_ratiobias_v1_plot.png`

### evening_month_bias_after_srcbin_v1

- Input experiment: `tree_recent_peakerr_srcbin_after_ratiobias_v1`.
- Shifted group-bias adjuster: source `tree_recent_peakerr_srcbin_after_ratiobias_pred`, group `hour,month`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `median`, beta `0.1`, hours `evening`, gate `absbias` threshold `200.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `57`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_recent_peakerr_srcbin_after_ratiobias_pred` | 5.8250% | 9.9839% | 2209 |
| `evening_month_bias_after_srcbin_pred` | 5.8200% | 9.9513% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening_month_bias_after_srcbin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening_month_bias_after_srcbin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening_month_bias_after_srcbin_v1_plot.png`

### hgb_midhigh_resid_after_eveningmonth_v1

- Input experiment: `evening_month_bias_after_srcbin_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `evening_month_bias_after_srcbin_pred`, target `resid`, lookback `60` days, min train `24` days, blend `0.08`, apply recent days `93`.
- Focus weights/gate: low `1.0`, daytime-low `1.0`, daytime `1.1`, evening `1.2`, apply hours `all`, source range `3000.0`-`15000.0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.9`, outlier weight `0.4`.
- Applied target days: `69`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `evening_month_bias_after_srcbin_pred` | 5.82% | 9.95% | 2209 |
| `hgb_midhigh_resid_after_eveningmonth_pred` | 5.82% | 9.96% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hgb_midhigh_resid_after_eveningmonth_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hgb_midhigh_resid_after_eveningmonth_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hgb_midhigh_resid_after_eveningmonth_v1_plot.png`

### tree_recent_evening_ratio_after_hgb_v1

- Input experiment: `hgb_midhigh_resid_after_eveningmonth_v1`.
- Shifted candidate-blend adjuster: source `hgb_midhigh_resid_after_eveningmonth_pred`, candidate `tree_recent_calibrated_pred`, group `hour,source_ratio_bin`, rolling group observations `21`, stat `mean`, advantage threshold `0.0`, hours `evening`, distance `le_abs` `500.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `225`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hgb_midhigh_resid_after_eveningmonth_pred` | 5.8161% | 9.9577% | 2209 |
| `tree_recent_evening_ratio_after_hgb_pred` | 5.7943% | 9.9623% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_evening_ratio_after_hgb_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_evening_ratio_after_hgb_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_evening_ratio_after_hgb_v1_plot.png`

### night_weekend_bias_after_evening_hgb_v1

- Input experiment: `tree_recent_evening_ratio_after_hgb_v1`.
- Shifted group-bias adjuster: source `tree_recent_evening_ratio_after_hgb_pred`, group `hour,weekend`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `mean`, beta `0.3`, hours `night`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `60`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_recent_evening_ratio_after_hgb_pred` | 5.7943% | 9.9623% | 2209 |
| `night_weekend_bias_after_evening_hgb_pred` | 5.7898% | 9.9367% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_weekend_bias_after_evening_hgb_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_weekend_bias_after_evening_hgb_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_weekend_bias_after_evening_hgb_v1_plot.png`

### tree_recent_evening_srcbin_after_night_v1

- Input experiment: `night_weekend_bias_after_evening_hgb_v1`.
- Shifted candidate-blend adjuster: source `night_weekend_bias_after_evening_hgb_pred`, candidate `tree_recent_calibrated_pred`, group `hour,source_bin`, rolling group observations `5`, stat `mean`, advantage threshold `0.0`, hours `evening`, distance `le_abs` `2000.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `217`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_weekend_bias_after_evening_hgb_pred` | 5.7898% | 9.9367% | 2209 |
| `tree_recent_evening_srcbin_after_night_pred` | 5.7688% | 9.9568% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_evening_srcbin_after_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_evening_srcbin_after_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_evening_srcbin_after_night_v1_plot.png`

### lowcollapse_lowday_blend_after_evening_srcbin_v1

- Input experiment: `tree_recent_evening_srcbin_after_night_v1`.
- Forecast-time rebound profile adjuster: source `tree_recent_evening_srcbin_after_night_pred`, candidate `lowcollapse_after_mlp_lowday_th065_pred`, alpha `0.8`, hours `10-13`, source range `0.0`-`500.0`, rolling24 min `0.0`, rolling24-hour7 diff min `0.0`, candidate direction `any`, candidate absdiff min `0.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `138`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_evening_srcbin_after_night_pred` | 5.7688% | 9.9568% | 2209 |
| `lowcollapse_lowday_blend_after_evening_srcbin_pred` | 5.7568% | 9.9580% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_lowday_blend_after_evening_srcbin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_lowday_blend_after_evening_srcbin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_lowcollapse_lowday_blend_after_evening_srcbin_v1_plot.png`

### night_ratio_bias_after_lowday_blend_v1

- Input experiment: `lowcollapse_lowday_blend_after_evening_srcbin_v1`.
- Shifted group-bias adjuster: source `lowcollapse_lowday_blend_after_evening_srcbin_pred`, group `hour,source_ratio_bin`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `13`, stat `median`, beta `0.15`, hours `night`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `52`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `lowcollapse_lowday_blend_after_evening_srcbin_pred` | 5.7568% | 9.9580% | 2209 |
| `night_ratio_bias_after_lowday_blend_pred` | 5.7520% | 9.9625% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_ratio_bias_after_lowday_blend_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_ratio_bias_after_lowday_blend_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_ratio_bias_after_lowday_blend_v1_plot.png`

### ridge_resid_after_lowday_night_v1

- Input experiment: `night_ratio_bias_after_lowday_blend_v1`.
- Rolling-origin stacker: source `night_ratio_bias_after_lowday_blend_pred`, target `resid`, lookback `45` days, min train `21` days, alpha `50.0`, blend `0.05`, apply recent days `93`.
- Applied target days: `72`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `night_ratio_bias_after_lowday_blend_pred` | 5.75% | 9.96% | 2209 |
| `ridge_resid_after_lowday_night_pred` | 5.77% | 10.05% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ridge_resid_after_lowday_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ridge_resid_after_lowday_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ridge_resid_after_lowday_night_v1_plot.png`

### ridge_logresid_after_lowday_night_v1

- Input experiment: `night_ratio_bias_after_lowday_blend_v1`.
- Rolling-origin stacker: source `night_ratio_bias_after_lowday_blend_pred`, target `logresid`, lookback `60` days, min train `24` days, alpha `100.0`, blend `0.03`, apply recent days `93`.
- Applied target days: `69`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `night_ratio_bias_after_lowday_blend_pred` | 5.75% | 9.96% | 2209 |
| `ridge_logresid_after_lowday_night_pred` | 5.82% | 10.08% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ridge_logresid_after_lowday_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ridge_logresid_after_lowday_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ridge_logresid_after_lowday_night_v1_plot.png`

### midday_srcbin_bias_after_lowday_night_v1

- Input experiment: `night_ratio_bias_after_lowday_blend_v1`.
- Shifted group-bias adjuster: source `night_ratio_bias_after_lowday_blend_pred`, group `hour,source_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `median`, beta `0.12`, hours `7-18`, gate `wmape` threshold `8.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `451`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_ratio_bias_after_lowday_blend_pred` | 5.7520% | 9.9625% | 2209 |
| `midday_srcbin_bias_after_lowday_night_pred` | 5.7411% | 9.9588% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_midday_srcbin_bias_after_lowday_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_midday_srcbin_bias_after_lowday_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_midday_srcbin_bias_after_lowday_night_v1_plot.png`

### tree_evening_ratio_blend_after_midday_srcbin_v1

- Input experiment: `midday_srcbin_bias_after_lowday_night_v1`.
- Shifted candidate-blend adjuster: source `midday_srcbin_bias_after_lowday_night_pred`, candidate `tree_recent_calibrated_pred`, group `hour,source_ratio_bin`, rolling group observations `8`, stat `mean`, advantage threshold `0.0`, hours `evening`, distance `le_abs` `2000.0`, alpha `0.5`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `209`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `midday_srcbin_bias_after_lowday_night_pred` | 5.7411% | 9.9588% | 2209 |
| `tree_evening_ratio_blend_after_midday_srcbin_pred` | 5.7029% | 9.9616% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_evening_ratio_blend_after_midday_srcbin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_evening_ratio_blend_after_midday_srcbin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_evening_ratio_blend_after_midday_srcbin_v1_plot.png`

### day_absbias_repair_after_evening_blend_v1

- Input experiment: `tree_evening_ratio_blend_after_midday_srcbin_v1`.
- Shifted group-bias adjuster: source `tree_evening_ratio_blend_after_midday_srcbin_pred`, group `hour,source_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `10-15`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `40`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_evening_ratio_blend_after_midday_srcbin_pred` | 5.7029% | 9.9616% | 2209 |
| `day_absbias_repair_after_evening_blend_pred` | 5.6987% | 9.9494% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day_absbias_repair_after_evening_blend_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day_absbias_repair_after_evening_blend_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day_absbias_repair_after_evening_blend_v1_plot.png`

### tree_day_srcbin_blend_after_absbias_v1

- Input experiment: `day_absbias_repair_after_evening_blend_v1`.
- Shifted candidate-blend adjuster: source `day_absbias_repair_after_evening_blend_pred`, candidate `tree_recent_calibrated_pred`, group `hour,source_bin`, rolling group observations `13`, stat `median`, advantage threshold `0.0`, hours `10-17`, distance `le_abs` `250.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `236`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day_absbias_repair_after_evening_blend_pred` | 5.6987% | 9.9494% | 2209 |
| `tree_day_srcbin_blend_after_absbias_pred` | 5.6614% | 9.9688% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_day_srcbin_blend_after_absbias_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_day_srcbin_blend_after_absbias_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_day_srcbin_blend_after_absbias_v1_plot.png`

### day_absbias_repair_after_tree_day_blend_v1

- Input experiment: `tree_day_srcbin_blend_after_absbias_v1`.
- Shifted group-bias adjuster: source `tree_day_srcbin_blend_after_absbias_pred`, group `hour,source_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `10-15`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `35`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_day_srcbin_blend_after_absbias_pred` | 5.6614% | 9.9688% | 2209 |
| `day_absbias_repair_after_tree_day_blend_pred` | 5.6569% | 9.9598% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day_absbias_repair_after_tree_day_blend_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day_absbias_repair_after_tree_day_blend_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day_absbias_repair_after_tree_day_blend_v1_plot.png`

### hgb_midhigh_resid_after_tree_day_blend_v1

- Input experiment: `day_absbias_repair_after_tree_day_blend_v1`.
- Nonlinear rolling-origin stacker: model `hgb`, source `day_absbias_repair_after_tree_day_blend_pred`, target `resid`, lookback `75` days, min train `28` days, blend `0.08`, apply recent days `93`.
- Focus weights/gate: low `1.0`, daytime-low `1.0`, daytime `1.1`, evening `1.1`, apply hours `all`, source range `1000.0`-`15000.0`.
- Source-error anomaly weighting: train-day WMAPE quantile `0.9`, outlier weight `0.5`.
- Applied target days: `65`.
- For each target day, training rows are strictly earlier than that day.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.16% | 20.13% | 2209 |
| `day_absbias_repair_after_tree_day_blend_pred` | 5.66% | 9.96% | 2209 |
| `hgb_midhigh_resid_after_tree_day_blend_pred` | 5.66% | 9.97% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hgb_midhigh_resid_after_tree_day_blend_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hgb_midhigh_resid_after_tree_day_blend_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hgb_midhigh_resid_after_tree_day_blend_v1_plot.png`

### ensemble_night_blend_after_day_repair_v1

- Input experiment: `day_absbias_repair_after_tree_day_blend_v1`.
- Shifted candidate-blend adjuster: source `day_absbias_repair_after_tree_day_blend_pred`, candidate `ensemble_hybrid_guarded_pred`, group `hour`, rolling group observations `3`, stat `mean`, advantage threshold `150.0`, hours `night`, distance `le_abs` `1000.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `54`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day_absbias_repair_after_tree_day_blend_pred` | 5.6569% | 9.9598% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `ensemble_night_blend_after_day_repair_pred` | 5.6309% | 9.9365% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_night_blend_after_day_repair_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_night_blend_after_day_repair_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_night_blend_after_day_repair_v1_plot.png`

### tree_close_hour_blend_after_ensemble_night_v1

- Input experiment: `ensemble_night_blend_after_day_repair_v1`.
- Shifted candidate-blend adjuster: source `ensemble_night_blend_after_day_repair_pred`, candidate `tree_recent_calibrated_pred`, group `hour`, rolling group observations `34`, stat `median`, advantage threshold `0.0`, hours `all`, distance `le_abs` `100.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `386`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `ensemble_night_blend_after_day_repair_pred` | 5.6309% | 9.9365% | 2209 |
| `tree_close_hour_blend_after_ensemble_night_pred` | 5.6160% | 9.9476% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_close_hour_blend_after_ensemble_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_close_hour_blend_after_ensemble_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_close_hour_blend_after_ensemble_night_v1_plot.png`

### ensemble_night_diff_blend_after_tree_close_v1

- Input experiment: `tree_close_hour_blend_after_ensemble_night_v1`.
- Shifted candidate-blend adjuster: source `tree_close_hour_blend_after_ensemble_night_pred`, candidate `ensemble_hybrid_guarded_pred`, group `hour,diff_bin`, rolling group observations `5`, stat `mean`, advantage threshold `100.0`, hours `night`, distance `ge_abs` `500.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `15`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_close_hour_blend_after_ensemble_night_pred` | 5.6160% | 9.9476% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `ensemble_night_diff_blend_after_tree_close_pred` | 5.6010% | 9.9408% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_night_diff_blend_after_tree_close_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_night_diff_blend_after_tree_close_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_night_diff_blend_after_tree_close_v1_plot.png`

### ensemble_recent_overnight_spike_blend_v1

- Input experiment: `ensemble_night_diff_blend_after_tree_close_v1`.
- Shifted candidate-blend adjuster: source `ensemble_night_diff_blend_after_tree_close_pred`, candidate `ensemble_hybrid_recent_calibrated_pred`, group `hour,source_bin`, rolling group observations `3`, stat `mean`, advantage threshold `250.0`, hours `0-8`, distance `ge_abs` `1000.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `2`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `ensemble_night_diff_blend_after_tree_close_pred` | 5.6010% | 9.9408% | 2209 |
| `ensemble_hybrid_recent_calibrated_pred` | 8.5424% | 20.5296% | 2209 |
| `ensemble_recent_overnight_spike_blend_pred` | 5.5822% | 9.8266% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_recent_overnight_spike_blend_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_recent_overnight_spike_blend_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_recent_overnight_spike_blend_v1_plot.png`

### h17_18_bias_after_overnight_spike_v1

- Input experiment: `ensemble_recent_overnight_spike_blend_v1`.
- Shifted group-bias adjuster: source `ensemble_recent_overnight_spike_blend_pred`, group `hour`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `13`, stat `median`, beta `0.3`, hours `17-18`, gate `wmape` threshold `8.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `5`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `ensemble_recent_overnight_spike_blend_pred` | 5.5822% | 9.8266% | 2209 |
| `h17_18_bias_after_overnight_spike_pred` | 5.5773% | 9.8248% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h17_18_bias_after_overnight_spike_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h17_18_bias_after_overnight_spike_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h17_18_bias_after_overnight_spike_v1_plot.png`

### treebase_day_srcbin_blend_after_h17_v1

- Input experiment: `h17_18_bias_after_overnight_spike_v1`.
- Shifted candidate-blend adjuster: source `h17_18_bias_after_overnight_spike_pred`, candidate `tree_base_pred`, group `hour,source_bin`, rolling group observations `13`, stat `mean`, advantage threshold `25.0`, hours `10-17`, distance `le_abs` `500.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `120`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `h17_18_bias_after_overnight_spike_pred` | 5.5773% | 9.8248% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `treebase_day_srcbin_blend_after_h17_pred` | 5.5655% | 9.8018% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day_srcbin_blend_after_h17_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day_srcbin_blend_after_h17_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day_srcbin_blend_after_h17_v1_plot.png`

### tree_recent_night_diff_after_treebase_day_v1

- Input experiment: `treebase_day_srcbin_blend_after_h17_v1`.
- Shifted candidate-blend adjuster: source `treebase_day_srcbin_blend_after_h17_pred`, candidate `tree_recent_calibrated_pred`, group `hour,diff_bin`, rolling group observations `3`, stat `median`, advantage threshold `250.0`, hours `night`, distance `ge_abs` `1000.0`, alpha `0.5`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `5`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `treebase_day_srcbin_blend_after_h17_pred` | 5.5655% | 9.8018% | 2209 |
| `tree_recent_night_diff_after_treebase_day_pred` | 5.5511% | 9.8285% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_night_diff_after_treebase_day_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_night_diff_after_treebase_day_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_tree_recent_night_diff_after_treebase_day_v1_plot.png`

### h17_18_bias_after_tree_recent_night_v1

- Input experiment: `tree_recent_night_diff_after_treebase_day_v1`.
- Shifted group-bias adjuster: source `tree_recent_night_diff_after_treebase_day_pred`, group `hour`, source bins `-1,50,250,500,1000,3000,7000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `median`, beta `0.3`, hours `17-18`, gate `wmape` threshold `6.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `3`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `tree_recent_night_diff_after_treebase_day_pred` | 5.5511% | 9.8285% | 2209 |
| `h17_18_bias_after_tree_recent_night_pred` | 5.5470% | 9.8285% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h17_18_bias_after_tree_recent_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h17_18_bias_after_tree_recent_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_h17_18_bias_after_tree_recent_night_v1_plot.png`

### ensemble_neural_morning_spike_after_h17_v1

- Input experiment: `h17_18_bias_after_tree_recent_night_v1`.
- Shifted candidate-blend adjuster: source `h17_18_bias_after_tree_recent_night_pred`, candidate `ensemble_neural_pred`, group `hour`, rolling group observations `3`, stat `median`, advantage threshold `25.0`, hours `7-10`, distance `ge_abs` `1000.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `4`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `h17_18_bias_after_tree_recent_night_pred` | 5.5470% | 9.8285% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_neural_morning_spike_after_h17_pred` | 5.5207% | 9.6925% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_neural_morning_spike_after_h17_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_neural_morning_spike_after_h17_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_ensemble_neural_morning_spike_after_h17_v1_plot.png`

### morning_weekend_srcbin_bias_after_neural_spike_v1

- Input experiment: `ensemble_neural_morning_spike_after_h17_v1`.
- Shifted group-bias adjuster: source `ensemble_neural_morning_spike_after_h17_pred`, group `hour,source_bin,weekend`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.1`, hours `7-10`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `102`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `ensemble_neural_morning_spike_after_h17_pred` | 5.5207% | 9.6925% | 2209 |
| `morning_weekend_srcbin_bias_after_neural_spike_pred` | 5.5156% | 9.7092% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_weekend_srcbin_bias_after_neural_spike_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_weekend_srcbin_bias_after_neural_spike_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_weekend_srcbin_bias_after_neural_spike_v1_plot.png`

### rollingmin_morning_spike_after_bias_v1

- Input experiment: `morning_weekend_srcbin_bias_after_neural_spike_v1`.
- Shifted candidate-blend adjuster: source `morning_weekend_srcbin_bias_after_neural_spike_pred`, candidate `f_rolling_min_24`, group `hour,source_ratio_bin`, rolling group observations `3`, stat `median`, advantage threshold `400.0`, hours `7-10`, distance `ge_abs` `2000.0`, alpha `0.3`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `2`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning_weekend_srcbin_bias_after_neural_spike_pred` | 5.5156% | 9.7092% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `rollingmin_morning_spike_after_bias_pred` | 5.4949% | 9.5543% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rollingmin_morning_spike_after_bias_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rollingmin_morning_spike_after_bias_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rollingmin_morning_spike_after_bias_v1_plot.png`

### treebase_day_ratio_blend_after_rollingmin_v1

- Input experiment: `rollingmin_morning_spike_after_bias_v1`.
- Shifted candidate-blend adjuster: source `rollingmin_morning_spike_after_bias_pred`, candidate `tree_base_pred`, group `hour,source_ratio_bin`, rolling group observations `34`, stat `mean`, advantage threshold `100.0`, hours `day`, distance `le_abs` `1000.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `35`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `rollingmin_morning_spike_after_bias_pred` | 5.4949% | 9.5543% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `treebase_day_ratio_blend_after_rollingmin_pred` | 5.4883% | 9.5286% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day_ratio_blend_after_rollingmin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day_ratio_blend_after_rollingmin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day_ratio_blend_after_rollingmin_v1_plot.png`

### treebase_day10_17_ratio_blend_after_rollingmin_v1

- Input experiment: `rollingmin_morning_spike_after_bias_v1`.
- Shifted candidate-blend adjuster: source `rollingmin_morning_spike_after_bias_pred`, candidate `tree_base_pred`, group `hour,source_ratio_bin`, rolling group observations `34`, stat `mean`, advantage threshold `100.0`, hours `10-17`, distance `le_abs` `1000.0`, alpha `0.7`.
- Formula: selected rows use `(1-alpha) * source + alpha * candidate`; selection uses shifted rolling historical candidate advantage in forecast-time groups only.
- Adjusted rows: `59`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `rollingmin_morning_spike_after_bias_pred` | 5.4949% | 9.5543% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `treebase_day10_17_ratio_blend_after_rollingmin_pred` | 5.4791% | 9.5286% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day10_17_ratio_blend_after_rollingmin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day10_17_ratio_blend_after_rollingmin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_treebase_day10_17_ratio_blend_after_rollingmin_v1_plot.png`

### morning_srcbin_bias_after_treebase_day_v1

- Input experiment: `treebase_day10_17_ratio_blend_after_rollingmin_v1`.
- Shifted group-bias adjuster: source `treebase_day10_17_ratio_blend_after_rollingmin_pred`, group `hour,source_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `mean`, beta `0.12`, hours `7-10`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `130`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `treebase_day10_17_ratio_blend_after_rollingmin_pred` | 5.4791% | 9.5286% | 2209 |
| `morning_srcbin_bias_after_treebase_day_pred` | 5.4698% | 9.5352% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_srcbin_bias_after_treebase_day_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_srcbin_bias_after_treebase_day_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_srcbin_bias_after_treebase_day_v1_plot.png`

### multi_candidate_day_blend_after_morning_bias_v1

- Input experiment: `morning_srcbin_bias_after_treebase_day_v1`.
- Shifted multi-candidate blend adjuster: source `morning_srcbin_bias_after_treebase_day_pred`, candidates `tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,ensemble_hybrid_recent_calibrated_pred,rolling_stack_pred,groupbias3_market1_med_b010_night_abs150_pred,lag24blend1_daily2_night_a100_adv0_pred,f_price_lag_24,f_price_lag_48,f_price_lag_168,f_rolling_mean_hour_7d,f_rolling_mean_24,f_rolling_min_24`, group `hour,source_bin`, rolling group observations `13`, stat `mean`, advantage threshold `250.0`, hours `7-18`, distance `le_abs` `500.0`, alpha `0.7`.
- Formula: each row chooses the candidate with the strongest shifted rolling historical advantage; selected rows use `(1-alpha) * source + alpha * candidate` and are clipped to the market range.
- Adjusted rows: `31`.
- Selected candidates: `{'tree_recent_calibrated_pred': 10, 'ensemble_hybrid_pred': 7, 'tree_base_pred': 6, 'ensemble_neural_pred': 3, 'f_price_lag_168': 2, 'groupbias3_market1_med_b010_night_abs150_pred': 2, 'f_rolling_mean_24': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning_srcbin_bias_after_treebase_day_pred` | 5.4698% | 9.5352% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_hybrid_pred` | 9.7905% | 29.8299% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `ensemble_hybrid_recent_calibrated_pred` | 8.5424% | 20.5296% | 2209 |
| `rolling_stack_pred` | 8.3071% | 19.0831% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_24` | 57.2007% | 58.8649% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `multi_candidate_day_blend_after_morning_bias_pred` | 5.4597% | 9.5352% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_multi_candidate_day_blend_after_morning_bias_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_multi_candidate_day_blend_after_morning_bias_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_multi_candidate_day_blend_after_morning_bias_v1_plot.png`

### rebound_profile_after_daybias31_floor10_v1

- Input experiment: `daybias31_rechain_floor10_v1`.
- Forecast-time rebound profile adjuster: source `daybias31_hb22_midday_d8_b050_abs250_pred`, candidate `f_rolling_mean_hour_7d`, alpha `0.25`, hours `10-16`, source range `0.0`-`1200.0`, rolling24 min `3500.0`, rolling24-hour7 diff min `1000.0`, candidate direction `up`, candidate absdiff min `300.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `203`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 6.0227% | 10.3985% | 2209 |
| `rebound_profile_after_daybias31_floor10_pred` | 6.3203% | 10.8109% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_profile_after_daybias31_floor10_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_profile_after_daybias31_floor10_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_profile_after_daybias31_floor10_v1_plot.png`

### rebound_floor_only_after_daybias31_v1

- Input experiment: `daybias31_rechain_floor10_v1`.
- Forecast-time rebound profile adjuster: source `daybias31_hb22_midday_d8_b050_abs250_pred`, candidate `f_rolling_mean_hour_7d`, alpha `0.12`, hours `11-16`, source range `0.0`-`80.0`, rolling24 min `3500.0`, rolling24-hour7 diff min `1000.0`, candidate direction `up`, candidate absdiff min `300.0`.
- Uses only forecast-time lag/rolling profile features; no target-day actuals enter the signal.
- Adjusted rows: `87`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `daybias31_hb22_midday_d8_b050_abs250_pred` | 6.0227% | 10.3985% | 2209 |
| `rebound_floor_only_after_daybias31_pred` | 6.0966% | 10.4835% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_floor_only_after_daybias31_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_floor_only_after_daybias31_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rebound_floor_only_after_daybias31_v1_plot.png`

### morning_diffbin_multi_candidate_after_best_v1

- Input experiment: `multi_candidate_day_blend_after_morning_bias_v1`.
- Shifted multi-candidate blend adjuster: source `multi_candidate_day_blend_after_morning_bias_pred`, candidates `morning_srcbin_bias_after_treebase_day_pred,treebase_day10_17_ratio_blend_after_rollingmin_pred,rollingmin_morning_spike_after_bias_pred,ensemble_neural_morning_spike_after_h17_pred,h17_18_bias_after_tree_recent_night_pred,tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,rolling_stack_pred,groupbias3_market1_med_b010_night_abs150_pred,lag24blend1_daily2_night_a100_adv0_pred,f_price_lag_24,f_price_lag_48,f_price_lag_168,f_rolling_mean_hour_7d,f_rolling_mean_24,f_rolling_min_24`, group `hour,diff_bin`, rolling group observations `8`, stat `median`, advantage threshold `250.0`, hours `7-10`, distance `le_abs` `500.0`, alpha `0.9`.
- Formula: each row chooses the candidate with the strongest shifted rolling historical advantage; selected rows use `(1-alpha) * source + alpha * candidate` and are clipped to the market range.
- Adjusted rows: `27`.
- Selected candidates: `{'tree_recent_calibrated_pred': 10, 'tree_base_pred': 5, 'ensemble_neural_morning_spike_after_h17_pred': 4, 'lag24blend1_daily2_night_a100_adv0_pred': 4, 'f_rolling_min_24': 2, 'ensemble_neural_pred': 1, 'groupbias3_market1_med_b010_night_abs150_pred': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `multi_candidate_day_blend_after_morning_bias_pred` | 5.4597% | 9.5352% | 2209 |
| `morning_srcbin_bias_after_treebase_day_pred` | 5.4698% | 9.5352% | 2209 |
| `treebase_day10_17_ratio_blend_after_rollingmin_pred` | 5.4791% | 9.5286% | 2209 |
| `rollingmin_morning_spike_after_bias_pred` | 5.4949% | 9.5543% | 2209 |
| `ensemble_neural_morning_spike_after_h17_pred` | 5.5207% | 9.6925% | 2209 |
| `h17_18_bias_after_tree_recent_night_pred` | 5.5470% | 9.8285% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_hybrid_pred` | 9.7905% | 29.8299% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `rolling_stack_pred` | 8.3071% | 19.0831% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_24` | 57.2007% | 58.8649% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `morning_diffbin_multi_candidate_after_best_pred` | 5.4486% | 9.5184% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_diffbin_multi_candidate_after_best_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_diffbin_multi_candidate_after_best_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_diffbin_multi_candidate_after_best_v1_plot.png`

### hour5_wmape20_bias_after_morning_diffbin_v1

- Input experiment: `morning_diffbin_multi_candidate_after_best_v1`.
- Shifted group-bias adjuster: source `morning_diffbin_multi_candidate_after_best_pred`, group `hour`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `-0.15`, hours `all`, gate `wmape` threshold `20.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `201`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning_diffbin_multi_candidate_after_best_pred` | 5.4486% | 9.5184% | 2209 |
| `hour5_wmape20_bias_after_morning_diffbin_pred` | 5.4396% | 9.5005% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hour5_wmape20_bias_after_morning_diffbin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hour5_wmape20_bias_after_morning_diffbin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hour5_wmape20_bias_after_morning_diffbin_v1_plot.png`

### morning_sourceratio_spike_after_hourbias_v1

- Input experiment: `hour5_wmape20_bias_after_morning_diffbin_v1`.
- Shifted multi-candidate blend adjuster: source `hour5_wmape20_bias_after_morning_diffbin_pred`, candidates `morning_diffbin_multi_candidate_after_best_pred,multi_candidate_day_blend_after_morning_bias_pred,morning_srcbin_bias_after_treebase_day_pred,treebase_day10_17_ratio_blend_after_rollingmin_pred,rollingmin_morning_spike_after_bias_pred,ensemble_neural_morning_spike_after_h17_pred,h17_18_bias_after_tree_recent_night_pred,tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,rolling_stack_pred,groupbias3_market1_med_b010_night_abs150_pred,lag24blend1_daily2_night_a100_adv0_pred,f_price_lag_24,f_price_lag_48,f_price_lag_168,f_rolling_mean_hour_7d,f_rolling_mean_24,f_rolling_min_24`, group `hour,source_ratio_bin`, rolling group observations `5`, stat `mean`, advantage threshold `150.0`, hours `7-10`, distance `ge_abs` `2000.0`, alpha `0.9`.
- Formula: each row chooses the candidate with the strongest shifted rolling historical advantage; selected rows use `(1-alpha) * source + alpha * candidate` and are clipped to the market range.
- Adjusted rows: `3`.
- Selected candidates: `{'f_price_lag_168': 2, 'f_rolling_mean_24': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hour5_wmape20_bias_after_morning_diffbin_pred` | 5.4396% | 9.5005% | 2209 |
| `morning_diffbin_multi_candidate_after_best_pred` | 5.4486% | 9.5184% | 2209 |
| `multi_candidate_day_blend_after_morning_bias_pred` | 5.4597% | 9.5352% | 2209 |
| `morning_srcbin_bias_after_treebase_day_pred` | 5.4698% | 9.5352% | 2209 |
| `treebase_day10_17_ratio_blend_after_rollingmin_pred` | 5.4791% | 9.5286% | 2209 |
| `rollingmin_morning_spike_after_bias_pred` | 5.4949% | 9.5543% | 2209 |
| `ensemble_neural_morning_spike_after_h17_pred` | 5.5207% | 9.6925% | 2209 |
| `h17_18_bias_after_tree_recent_night_pred` | 5.5470% | 9.8285% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_hybrid_pred` | 9.7905% | 29.8299% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `rolling_stack_pred` | 8.3071% | 19.0831% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_24` | 57.2007% | 58.8649% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `morning_sourceratio_spike_after_hourbias_pred` | 5.4235% | 9.5005% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_sourceratio_spike_after_hourbias_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_sourceratio_spike_after_hourbias_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_sourceratio_spike_after_hourbias_v1_plot.png`

### hour13_wmape12_bias_after_spike_v1

- Input experiment: `morning_sourceratio_spike_after_hourbias_v1`.
- Shifted group-bias adjuster: source `morning_sourceratio_spike_after_hourbias_pred`, group `hour`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `13`, stat `mean`, beta `-0.1`, hours `all`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `810`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning_sourceratio_spike_after_hourbias_pred` | 5.4235% | 9.5005% | 2209 |
| `hour13_wmape12_bias_after_spike_pred` | 5.4167% | 9.4935% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hour13_wmape12_bias_after_spike_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hour13_wmape12_bias_after_spike_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_hour13_wmape12_bias_after_spike_v1_plot.png`

### evening_anchor_candidate_after_hour13_v1

- Input experiment: `hour13_wmape12_bias_after_spike_v1`.
- Shifted multi-candidate blend adjuster: source `hour13_wmape12_bias_after_spike_pred`, candidates `low_profile_anchor,high_profile_anchor,high_profile_lag168_anchor,high_profile_lag168_day_anchor,low_profile_rolling7_anchor,low_profile_weather_anchor,low_profile_lowcollapse_anchor,high_profile_cap00_anchor,high_profile_lag48eve_anchor,high_profile_capnight_anchor,high_profile_cap00_roll7_anchor,low_profile_compact_anchor,high_profile_lag168_h1718_anchor,f_price_cap,f_rolling_mean_hour_3d,f_rolling_mean_hour_7d,f_rolling_mean_hour_14d,f_rolling_mean_24,f_rolling_min_24,f_price_lag_24,f_price_lag_48,f_price_lag_168,tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,rolling_stack_pred,groupbias3_market1_med_b010_night_abs150_pred,lag24blend1_daily2_night_a100_adv0_pred,morning_sourceratio_spike_after_hourbias_pred,morning_diffbin_multi_candidate_after_best_pred,multi_candidate_day_blend_after_morning_bias_pred`, group `hour,source_bin`, rolling group observations `3`, stat `mean`, advantage threshold `400.0`, hours `17-23`, distance `le_abs` `1000.0`, alpha `1.0`.
- Formula: each row chooses the candidate with the strongest shifted rolling historical advantage; selected rows use `(1-alpha) * source + alpha * candidate` and are clipped to the market range.
- Adjusted rows: `14`.
- Selected candidates: `{'tree_recent_calibrated_pred': 4, 'high_profile_cap00_anchor': 3, 'high_profile_lag168_anchor': 2, 'ensemble_neural_pred': 2, 'tree_base_pred': 2, 'high_profile_lag48eve_anchor': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `hour13_wmape12_bias_after_spike_pred` | 5.4167% | 9.4935% | 2209 |
| `low_profile_anchor` | 27.7968% | 30.0170% | 2209 |
| `high_profile_anchor` | 27.7968% | 30.0170% | 2209 |
| `high_profile_lag168_anchor` | 36.5559% | 40.6779% | 2209 |
| `high_profile_lag168_day_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_rolling7_anchor` | 28.9950% | 33.0312% | 2209 |
| `low_profile_weather_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_lowcollapse_anchor` | 36.5559% | 40.6779% | 2209 |
| `high_profile_cap00_anchor` | 128.7407% | 204.3519% | 2209 |
| `high_profile_lag48eve_anchor` | 34.2209% | 39.3224% | 2209 |
| `high_profile_capnight_anchor` | 128.7407% | 204.3519% | 2209 |
| `high_profile_cap00_roll7_anchor` | 128.7407% | 204.3519% | 2209 |
| `low_profile_compact_anchor` | 28.9950% | 33.0312% | 2209 |
| `high_profile_lag168_h1718_anchor` | 36.5559% | 40.6779% | 2209 |
| `f_price_cap` | 128.2930% | 204.3519% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_hour_14d` | 31.5715% | 32.5973% | 2209 |
| `f_rolling_mean_24` | 57.2007% | 58.8649% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_hybrid_pred` | 9.7905% | 29.8299% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `rolling_stack_pred` | 8.3071% | 19.0831% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `morning_sourceratio_spike_after_hourbias_pred` | 5.4235% | 9.5005% | 2209 |
| `morning_diffbin_multi_candidate_after_best_pred` | 5.4486% | 9.5184% | 2209 |
| `multi_candidate_day_blend_after_morning_bias_pred` | 5.4597% | 9.5352% | 2209 |
| `evening_anchor_candidate_after_hour13_pred` | 5.4009% | 9.4666% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening_anchor_candidate_after_hour13_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening_anchor_candidate_after_hour13_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening_anchor_candidate_after_hour13_v1_plot.png`

### night_anchor_candidate_after_evening_v1

- Input experiment: `evening_anchor_candidate_after_hour13_v1`.
- Shifted multi-candidate blend adjuster: source `evening_anchor_candidate_after_hour13_pred`, candidates `low_profile_anchor,high_profile_anchor,high_profile_lag168_anchor,high_profile_lag168_day_anchor,low_profile_rolling7_anchor,low_profile_weather_anchor,low_profile_lowcollapse_anchor,high_profile_cap00_anchor,high_profile_lag48eve_anchor,high_profile_capnight_anchor,high_profile_cap00_roll7_anchor,low_profile_compact_anchor,high_profile_lag168_h1718_anchor,f_price_cap,f_rolling_mean_hour_3d,f_rolling_mean_hour_7d,f_rolling_mean_hour_14d,f_rolling_mean_24,f_rolling_min_24,f_price_lag_24,f_price_lag_48,f_price_lag_168,tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,rolling_stack_pred,groupbias3_market1_med_b010_night_abs150_pred,lag24blend1_daily2_night_a100_adv0_pred,hour13_wmape12_bias_after_spike_pred,morning_sourceratio_spike_after_hourbias_pred,morning_diffbin_multi_candidate_after_best_pred,multi_candidate_day_blend_after_morning_bias_pred`, group `hour,source_bin`, rolling group observations `3`, stat `median`, advantage threshold `600.0`, hours `night`, distance `le_abs` `2000.0`, alpha `0.25`.
- Formula: each row chooses the candidate with the strongest shifted rolling historical advantage; selected rows use `(1-alpha) * source + alpha * candidate` and are clipped to the market range.
- Adjusted rows: `8`.
- Selected candidates: `{'low_profile_anchor': 3, 'f_rolling_mean_hour_14d': 2, 'groupbias3_market1_med_b010_night_abs150_pred': 2, 'f_rolling_mean_hour_3d': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `evening_anchor_candidate_after_hour13_pred` | 5.4009% | 9.4666% | 2209 |
| `low_profile_anchor` | 27.7968% | 30.0170% | 2209 |
| `high_profile_anchor` | 27.7968% | 30.0170% | 2209 |
| `high_profile_lag168_anchor` | 36.5559% | 40.6779% | 2209 |
| `high_profile_lag168_day_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_rolling7_anchor` | 28.9950% | 33.0312% | 2209 |
| `low_profile_weather_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_lowcollapse_anchor` | 36.5559% | 40.6779% | 2209 |
| `high_profile_cap00_anchor` | 128.7407% | 204.3519% | 2209 |
| `high_profile_lag48eve_anchor` | 34.2209% | 39.3224% | 2209 |
| `high_profile_capnight_anchor` | 128.7407% | 204.3519% | 2209 |
| `high_profile_cap00_roll7_anchor` | 128.7407% | 204.3519% | 2209 |
| `low_profile_compact_anchor` | 28.9950% | 33.0312% | 2209 |
| `high_profile_lag168_h1718_anchor` | 36.5559% | 40.6779% | 2209 |
| `f_price_cap` | 128.2930% | 204.3519% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_hour_14d` | 31.5715% | 32.5973% | 2209 |
| `f_rolling_mean_24` | 57.2007% | 58.8649% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_hybrid_pred` | 9.7905% | 29.8299% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `rolling_stack_pred` | 8.3071% | 19.0831% | 2209 |
| `groupbias3_market1_med_b010_night_abs150_pred` | 7.1097% | 13.4725% | 2209 |
| `lag24blend1_daily2_night_a100_adv0_pred` | 7.0389% | 12.8523% | 2209 |
| `hour13_wmape12_bias_after_spike_pred` | 5.4167% | 9.4935% | 2209 |
| `morning_sourceratio_spike_after_hourbias_pred` | 5.4235% | 9.5005% | 2209 |
| `morning_diffbin_multi_candidate_after_best_pred` | 5.4486% | 9.5184% | 2209 |
| `multi_candidate_day_blend_after_morning_bias_pred` | 5.4597% | 9.5352% | 2209 |
| `night_anchor_candidate_after_evening_pred` | 5.3922% | 9.4358% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_anchor_candidate_after_evening_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_anchor_candidate_after_evening_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_anchor_candidate_after_evening_v1_plot.png`

### day13_16_anchor_lowrepair_after_night_v1

- Input experiment: `night_anchor_candidate_after_evening_v1`.
- Shifted multi-candidate blend adjuster: source `night_anchor_candidate_after_evening_pred`, candidates `low_profile_anchor,high_profile_anchor,high_profile_lag168_anchor,high_profile_lag168_day_anchor,low_profile_rolling7_anchor,low_profile_weather_anchor,low_profile_lowcollapse_anchor,low_profile_compact_anchor,f_rolling_mean_hour_3d,f_rolling_mean_hour_7d,f_rolling_mean_hour_14d,f_rolling_mean_24,f_rolling_min_24,f_price_lag_24,f_price_lag_48,f_price_lag_168,tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,rolling_stack_pred,hour13_wmape12_bias_after_spike_pred,morning_sourceratio_spike_after_hourbias_pred,morning_diffbin_multi_candidate_after_best_pred,multi_candidate_day_blend_after_morning_bias_pred`, group `hour,source_bin`, rolling group observations `8`, stat `median`, advantage threshold `50.0`, hours `13-16`, distance `none` `0.0`, alpha `0.1`.
- Formula: each row chooses the candidate with the strongest shifted rolling historical advantage; selected rows use `(1-alpha) * source + alpha * candidate` and are clipped to the market range.
- Adjusted rows: `44`.
- Selected candidates: `{'tree_recent_calibrated_pred': 14, 'ensemble_neural_pred': 11, 'tree_base_pred': 7, 'high_profile_lag168_anchor': 2, 'morning_sourceratio_spike_after_hourbias_pred': 2, 'f_rolling_mean_24': 2, 'f_rolling_mean_hour_3d': 1, 'f_price_lag_48': 1, 'morning_diffbin_multi_candidate_after_best_pred': 1, 'f_rolling_min_24': 1, 'low_profile_anchor': 1, 'ensemble_hybrid_pred': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_anchor_candidate_after_evening_pred` | 5.3922% | 9.4358% | 2209 |
| `low_profile_anchor` | 27.7968% | 30.0170% | 2209 |
| `high_profile_anchor` | 27.7968% | 30.0170% | 2209 |
| `high_profile_lag168_anchor` | 36.5559% | 40.6779% | 2209 |
| `high_profile_lag168_day_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_rolling7_anchor` | 28.9950% | 33.0312% | 2209 |
| `low_profile_weather_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_lowcollapse_anchor` | 36.5559% | 40.6779% | 2209 |
| `low_profile_compact_anchor` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_hour_3d` | 28.6825% | 32.9529% | 2209 |
| `f_rolling_mean_hour_7d` | 28.9950% | 33.0312% | 2209 |
| `f_rolling_mean_hour_14d` | 31.5715% | 32.5973% | 2209 |
| `f_rolling_mean_24` | 57.2007% | 58.8649% | 2209 |
| `f_rolling_min_24` | 85.8228% | 86.4083% | 2209 |
| `f_price_lag_24` | 27.7968% | 30.0170% | 2209 |
| `f_price_lag_48` | 34.2209% | 39.3224% | 2209 |
| `f_price_lag_168` | 36.5559% | 40.6779% | 2209 |
| `tree_base_pred` | 10.5336% | 30.3748% | 2209 |
| `ensemble_neural_pred` | 10.4135% | 29.8142% | 2209 |
| `ensemble_hybrid_pred` | 9.7905% | 29.8299% | 2209 |
| `ensemble_hybrid_guarded_pred` | 8.4885% | 20.1281% | 2209 |
| `rolling_stack_pred` | 8.3071% | 19.0831% | 2209 |
| `hour13_wmape12_bias_after_spike_pred` | 5.4167% | 9.4935% | 2209 |
| `morning_sourceratio_spike_after_hourbias_pred` | 5.4235% | 9.5005% | 2209 |
| `morning_diffbin_multi_candidate_after_best_pred` | 5.4486% | 9.5184% | 2209 |
| `multi_candidate_day_blend_after_morning_bias_pred` | 5.4597% | 9.5352% | 2209 |
| `day13_16_anchor_lowrepair_after_night_pred` | 5.3881% | 9.4393% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day13_16_anchor_lowrepair_after_night_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day13_16_anchor_lowrepair_after_night_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day13_16_anchor_lowrepair_after_night_v1_plot.png`

### rolling_meta_anchor_after_day13_v1

- Input experiment: `day13_16_anchor_lowrepair_after_night_v1`.
- Rolling-origin candidate meta-selector: source `day13_16_anchor_lowrepair_after_night_pred`, candidates `low_profile_anchor,high_profile_anchor,high_profile_lag168_anchor,high_profile_lag168_day_anchor,low_profile_rolling7_anchor,low_profile_weather_anchor,low_profile_lowcollapse_anchor,high_profile_cap00_anchor,high_profile_lag48eve_anchor,high_profile_capnight_anchor,high_profile_cap00_roll7_anchor,low_profile_compact_anchor,high_profile_lag168_h1718_anchor,f_price_cap,f_rolling_mean_hour_3d,f_rolling_mean_hour_7d,f_rolling_mean_hour_14d,f_rolling_mean_24,f_rolling_min_24,f_price_lag_24,f_price_lag_48,f_price_lag_168,tree_base_pred,tree_recent_calibrated_pred,ensemble_neural_pred,ensemble_hybrid_pred,ensemble_hybrid_guarded_pred,rolling_stack_pred,groupbias3_market1_med_b010_night_abs150_pred,lag24blend1_daily2_night_a100_adv0_pred,hour13_wmape12_bias_after_spike_pred,morning_sourceratio_spike_after_hourbias_pred,morning_diffbin_multi_candidate_after_best_pred,multi_candidate_day_blend_after_morning_bias_pred`, lookback `45` days, min train `14` days, ridge alpha `3000.0`, predicted advantage threshold `250.0`, hours `all`, distance `none` `0.0`, blend alpha `0.2`.
- For each target day, the model trains only on earlier rows and predicts candidate advantage from forecast-time source/candidate/lag/profile features.
- Adjusted rows: `494`.
- Selected candidates: `{'ensemble_neural_pred': 107, 'low_profile_anchor': 85, 'high_profile_anchor': 75, 'tree_recent_calibrated_pred': 54, 'tree_base_pred': 42, 'f_price_lag_24': 25, 'multi_candidate_day_blend_after_morning_bias_pred': 25, 'groupbias3_market1_med_b010_night_abs150_pred': 16, 'f_rolling_mean_hour_14d': 11, 'f_rolling_mean_24': 8, 'lag24blend1_daily2_night_a100_adv0_pred': 7, 'ensemble_hybrid_pred': 7, 'high_profile_lag168_anchor': 6, 'low_profile_rolling7_anchor': 5, 'high_profile_lag168_day_anchor': 4, 'f_price_cap': 3, 'rolling_stack_pred': 3, 'f_rolling_mean_hour_3d': 2, 'high_profile_lag168_h1718_anchor': 2, 'high_profile_lag48eve_anchor': 1, 'ensemble_hybrid_guarded_pred': 1, 'f_price_lag_168': 1, 'low_profile_weather_anchor': 1, 'low_profile_compact_anchor': 1, 'low_profile_lowcollapse_anchor': 1, 'f_price_lag_48': 1}`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day13_16_anchor_lowrepair_after_night_pred` | 5.3881% | 9.4393% | 2209 |
| `rolling_meta_anchor_after_day13_pred` | 5.3861% | 9.4420% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rolling_meta_anchor_after_day13_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rolling_meta_anchor_after_day13_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rolling_meta_anchor_after_day13_v1_plot.png`

### night_hourmonth_bias_after_day13_v1

- Input experiment: `day13_16_anchor_lowrepair_after_night_v1`.
- Shifted group-bias adjuster: source `day13_16_anchor_lowrepair_after_night_pred`, group `hour,month`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `0.15`, hours `night`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `90`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day13_16_anchor_lowrepair_after_night_pred` | 5.3881% | 9.4393% | 2209 |
| `night_hourmonth_bias_after_day13_pred` | 5.3781% | 9.4179% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hourmonth_bias_after_day13_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hourmonth_bias_after_day13_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hourmonth_bias_after_day13_v1_plot.png`

### day14_16_hourmonth_bias_after_nightmonth_v1

- Input experiment: `night_hourmonth_bias_after_day13_v1`.
- Shifted group-bias adjuster: source `night_hourmonth_bias_after_day13_pred`, group `hour,month`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `13`, stat `mean`, beta `0.25`, hours `14-16`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `30`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_hourmonth_bias_after_day13_pred` | 5.3781% | 9.4179% | 2209 |
| `day14_16_hourmonth_bias_after_nightmonth_pred` | 5.3726% | 9.4015% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day14_16_hourmonth_bias_after_nightmonth_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day14_16_hourmonth_bias_after_nightmonth_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day14_16_hourmonth_bias_after_nightmonth_v1_plot.png`

### night_hour8_wmape12_after_day14_16_v1

- Input experiment: `day14_16_hourmonth_bias_after_nightmonth_v1`.
- Shifted group-bias adjuster: source `day14_16_hourmonth_bias_after_nightmonth_pred`, group `hour`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `8`, stat `mean`, beta `-0.25`, hours `night`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `172`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day14_16_hourmonth_bias_after_nightmonth_pred` | 5.3726% | 9.4015% | 2209 |
| `night_hour8_wmape12_after_day14_16_pred` | 5.3642% | 9.4074% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hour8_wmape12_after_day14_16_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hour8_wmape12_after_day14_16_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hour8_wmape12_after_day14_16_v1_plot.png`

### morning_srcbinweekend_bias_after_night_hour8_v1

- Input experiment: `night_hour8_wmape12_after_day14_16_v1`.
- Shifted group-bias adjuster: source `night_hour8_wmape12_after_day14_16_pred`, group `hour,source_bin,weekend`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `34`, stat `mean`, beta `0.1`, hours `7-10`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `104`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_hour8_wmape12_after_day14_16_pred` | 5.3642% | 9.4074% | 2209 |
| `morning_srcbinweekend_bias_after_night_hour8_pred` | 5.3573% | 9.4146% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_srcbinweekend_bias_after_night_hour8_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_srcbinweekend_bias_after_night_hour8_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning_srcbinweekend_bias_after_night_hour8_v1_plot.png`

### day14_16_ratio_lowrepair_after_morning_v1

- Input experiment: `morning_srcbinweekend_bias_after_night_hour8_v1`.
- Shifted group-bias adjuster: source `morning_srcbinweekend_bias_after_night_hour8_pred`, group `source_ratio_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `-0.35`, hours `14-16`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `60`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning_srcbinweekend_bias_after_night_hour8_pred` | 5.3573% | 9.4146% | 2209 |
| `day14_16_ratio_lowrepair_after_morning_pred` | 5.3457% | 9.3116% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day14_16_ratio_lowrepair_after_morning_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day14_16_ratio_lowrepair_after_morning_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day14_16_ratio_lowrepair_after_morning_v1_plot.png`

### sourcebin_daytime_bias_after_lowrepair_v1

- Input experiment: `day14_16_ratio_lowrepair_after_morning_v1`.
- Shifted group-bias adjuster: source `day14_16_ratio_lowrepair_after_morning_pred`, group `source_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `2`, stat `mean`, beta `0.15`, hours `all`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `1232`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day14_16_ratio_lowrepair_after_morning_pred` | 5.3457% | 9.3116% | 2209 |
| `sourcebin_daytime_bias_after_lowrepair_pred` | 5.2665% | 9.1716% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_sourcebin_daytime_bias_after_lowrepair_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_sourcebin_daytime_bias_after_lowrepair_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_sourcebin_daytime_bias_after_lowrepair_v1_plot.png`

### night_ratio_bias_after_sourcebin_daytime_v1

- Input experiment: `sourcebin_daytime_bias_after_lowrepair_v1`.
- Shifted group-bias adjuster: source `sourcebin_daytime_bias_after_lowrepair_pred`, group `source_ratio_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `2`, stat `mean`, beta `0.2`, hours `night`, gate `absbias` threshold `100.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `411`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `sourcebin_daytime_bias_after_lowrepair_pred` | 5.2665% | 9.1716% | 2209 |
| `night_ratio_bias_after_sourcebin_daytime_pred` | 5.2316% | 9.1304% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_ratio_bias_after_sourcebin_daytime_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_ratio_bias_after_sourcebin_daytime_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_ratio_bias_after_sourcebin_daytime_v1_plot.png`

### morning7_10_summer_srcbin_bias_after_night_ratio_v1

- Input experiment: `night_ratio_bias_after_sourcebin_daytime_v1`.
- Shifted group-bias adjuster: source `night_ratio_bias_after_sourcebin_daytime_pred`, group `source_bin,daytime,summer`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `mean`, beta `0.45`, hours `7-10`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `46`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_ratio_bias_after_sourcebin_daytime_pred` | 5.2316% | 9.1304% | 2209 |
| `morning7_10_summer_srcbin_bias_after_night_ratio_pred` | 5.2032% | 9.0531% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_summer_srcbin_bias_after_night_ratio_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_summer_srcbin_bias_after_night_ratio_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_summer_srcbin_bias_after_night_ratio_v1_plot.png`

### day13_16_ratio_wmape15_after_morning7_v1

- Input experiment: `morning7_10_summer_srcbin_bias_after_night_ratio_v1`.
- Shifted group-bias adjuster: source `morning7_10_summer_srcbin_bias_after_night_ratio_pred`, group `source_ratio_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `0.5`, hours `13-16`, gate `wmape` threshold `15.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `129`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_summer_srcbin_bias_after_night_ratio_pred` | 5.2032% | 9.0531% | 2209 |
| `day13_16_ratio_wmape15_after_morning7_pred` | 5.1749% | 8.9936% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day13_16_ratio_wmape15_after_morning7_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day13_16_ratio_wmape15_after_morning7_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day13_16_ratio_wmape15_after_morning7_v1_plot.png`

### evening19_23_sourcebin_after_day13_16_v1

- Input experiment: `day13_16_ratio_wmape15_after_morning7_v1`.
- Shifted group-bias adjuster: source `day13_16_ratio_wmape15_after_morning7_pred`, group `source_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `-0.6`, hours `19-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `16`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day13_16_ratio_wmape15_after_morning7_pred` | 5.1749% | 8.9936% | 2209 |
| `evening19_23_sourcebin_after_day13_16_pred` | 5.1525% | 8.8527% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening19_23_sourcebin_after_day13_16_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening19_23_sourcebin_after_day13_16_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening19_23_sourcebin_after_day13_16_v1_plot.png`

### morning7_10_ratio_wmape30_after_evening_v1

- Input experiment: `evening19_23_sourcebin_after_day13_16_v1`.
- Shifted group-bias adjuster: source `evening19_23_sourcebin_after_day13_16_pred`, group `source_ratio_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `2`, stat `mean`, beta `0.7`, hours `7-10`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `32`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `evening19_23_sourcebin_after_day13_16_pred` | 5.1525% | 8.8527% | 2209 |
| `morning7_10_ratio_wmape30_after_evening_pred` | 5.1267% | 8.7542% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_wmape30_after_evening_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_wmape30_after_evening_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_wmape30_after_evening_v1_plot.png`

### day11_15_srcbinweekend_repair_after_morning7_v1

- Input experiment: `morning7_10_ratio_wmape30_after_evening_v1`.
- Shifted group-bias adjuster: source `morning7_10_ratio_wmape30_after_evening_pred`, group `hour,source_bin,weekend`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `-0.35`, hours `11-15`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `29`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_ratio_wmape30_after_evening_pred` | 5.1267% | 8.7542% | 2209 |
| `day11_15_srcbinweekend_repair_after_morning7_pred` | 5.1086% | 8.7518% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day11_15_srcbinweekend_repair_after_morning7_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day11_15_srcbinweekend_repair_after_morning7_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_day11_15_srcbinweekend_repair_after_morning7_v1_plot.png`

### evening19_23_hoursrcbin_after_day11_15_v1

- Input experiment: `day11_15_srcbinweekend_repair_after_morning7_v1`.
- Shifted group-bias adjuster: source `day11_15_srcbinweekend_repair_after_morning7_pred`, group `hour,source_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `-0.75`, hours `19-23`, gate `wmape` threshold `12.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `10`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `day11_15_srcbinweekend_repair_after_morning7_pred` | 5.1086% | 8.7518% | 2209 |
| `evening19_23_hoursrcbin_after_day11_15_pred` | 5.0913% | 8.5758% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening19_23_hoursrcbin_after_day11_15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening19_23_hoursrcbin_after_day11_15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_evening19_23_hoursrcbin_after_day11_15_v1_plot.png`

### morning7_10_ratio_summer_repair_after_evening_v1

- Input experiment: `evening19_23_hoursrcbin_after_day11_15_v1`.
- Shifted group-bias adjuster: source `evening19_23_hoursrcbin_after_day11_15_pred`, group `source_ratio_bin,daytime,summer`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `mean`, beta `-1.0`, hours `7-10`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `31`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `evening19_23_hoursrcbin_after_day11_15_pred` | 5.0913% | 8.5758% | 2209 |
| `morning7_10_ratio_summer_repair_after_evening_pred` | 5.0764% | 8.6111% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_summer_repair_after_evening_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_summer_repair_after_evening_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_summer_repair_after_evening_v1_plot.png`

### morning7_10_ratio_absbias_after_summer_repair_v1

- Input experiment: `morning7_10_ratio_summer_repair_after_evening_v1`.
- Shifted group-bias adjuster: source `morning7_10_ratio_summer_repair_after_evening_pred`, group `source_ratio_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `2`, stat `mean`, beta `0.15`, hours `7-10`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `80`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_ratio_summer_repair_after_evening_pred` | 5.0764% | 8.6111% | 2209 |
| `morning7_10_ratio_absbias_after_summer_repair_pred` | 5.0633% | 8.6124% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_absbias_after_summer_repair_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_absbias_after_summer_repair_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_ratio_absbias_after_summer_repair_v1_plot.png`

### morning7_10_srcbin_summer_long_after_absbias_v1

- Input experiment: `morning7_10_ratio_absbias_after_summer_repair_v1`.
- Shifted group-bias adjuster: source `morning7_10_ratio_absbias_after_summer_repair_pred`, group `source_bin,daytime,summer`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `21`, stat `mean`, beta `0.6`, hours `7-10`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `22`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_ratio_absbias_after_summer_repair_pred` | 5.0633% | 8.6124% | 2209 |
| `morning7_10_srcbin_summer_long_after_absbias_pred` | 5.0487% | 8.6379% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_srcbin_summer_long_after_absbias_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_srcbin_summer_long_after_absbias_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_srcbin_summer_long_after_absbias_v1_plot.png`

### night_sourcebin_bias_after_morning_long_v1

- Input experiment: `morning7_10_srcbin_summer_long_after_absbias_v1`.
- Shifted group-bias adjuster: source `morning7_10_srcbin_summer_long_after_absbias_pred`, group `source_bin,daytime`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `3`, stat `median`, beta `0.2`, hours `night`, gate `absbias` threshold `400.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `97`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_srcbin_summer_long_after_absbias_pred` | 5.0487% | 8.6379% | 2209 |
| `night_sourcebin_bias_after_morning_long_pred` | 5.0320% | 8.6606% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_sourcebin_bias_after_morning_long_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_sourcebin_bias_after_morning_long_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_sourcebin_bias_after_morning_long_v1_plot.png`

### morning7_10_hourweekend_after_night_sourcebin_v1

- Input experiment: `night_sourcebin_bias_after_morning_long_v1`.
- Shifted group-bias adjuster: source `night_sourcebin_bias_after_morning_long_pred`, group `hour,weekend`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `-0.25`, hours `7-10`, gate `absbias` threshold `150.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `95`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `night_sourcebin_bias_after_morning_long_pred` | 5.0320% | 8.6606% | 2209 |
| `morning7_10_hourweekend_after_night_sourcebin_pred` | 5.0182% | 8.6525% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_hourweekend_after_night_sourcebin_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_hourweekend_after_night_sourcebin_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_hourweekend_after_night_sourcebin_v1_plot.png`

### morning7_10_hourratio_final_push_v1

- Input experiment: `morning7_10_hourweekend_after_night_sourcebin_v1`.
- Shifted group-bias adjuster: source `morning7_10_hourweekend_after_night_sourcebin_pred`, group `hour,source_ratio_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `8`, stat `median`, beta `-0.9`, hours `7-10`, gate `wmape` threshold `30.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `13`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_hourweekend_after_night_sourcebin_pred` | 5.0182% | 8.6525% | 2209 |
| `morning7_10_hourratio_final_push_pred` | 5.0027% | 8.6566% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_hourratio_final_push_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_hourratio_final_push_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_morning7_10_hourratio_final_push_v1_plot.png`

### night_hourratio_final_under5_v1

- Input experiment: `morning7_10_hourratio_final_push_v1`.
- Shifted group-bias adjuster: source `morning7_10_hourratio_final_push_pred`, group `hour,source_ratio_bin`, source bins `-1,50,250,500,1000,2000,3000,5000,7000,9000,12000,1000000000`, ratio bins `-0.01,0.01,0.03,0.05,0.07,0.1,0.2,0.45,0.75,0.9,0.98,1.01`, rolling group observations `5`, stat `median`, beta `0.2`, hours `night`, gate `absbias` threshold `250.0`.
- Formula: `prediction = source - beta * shifted_rolling_group_source_bias`; the group is built only from forecast-time fields, and each row uses only earlier observations in that group.
- Adjusted rows: `138`.

| variant | 3m WMAPE | 14d WMAPE | 3m rows |
|---|---:|---:|---:|
| `tree_recent_calibrated_pred` | 9.1585% | 20.1281% | 2209 |
| `morning7_10_hourratio_final_push_pred` | 5.0027% | 8.6566% | 2209 |
| `night_hourratio_final_under5_pred` | 4.9896% | 8.6172% | 2209 |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hourratio_final_under5_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hourratio_final_under5_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_night_hourratio_final_under5_v1_plot.png`

### low_regime_group_selector_target15_v1

- Input experiment: `night_hourratio_final_under5_v1`.
- Shifted candidate selector: source `night_hourratio_final_under5_pred`, output `low_regime_group_selector_target15_pred`, candidate group `hour,source_bin,lag24_bin`, hours `11-15`, source threshold `250.0`, min previous group rows `2`, min shifted APE advantage `0.05`.
- Formula: choose a candidate only when its previous in-group APE is at least `0.05` better than the base source; each row uses only earlier rows in the same forecast-time group.
- Adjusted rows: `42`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 |
|---|---:|---:|---:|---:|---:|
| `night_hourratio_final_under5_pred` | 4.9896% | 8.6172% | 8.6138% | 24.7365% | 38.4534% |
| `low_regime_group_selector_target15_pred` | 4.9855% | 8.5840% | 8.5783% | 23.6832% | 37.8113% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_group_selector_target15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_group_selector_target15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_group_selector_target15_v1_plot.png`

### low_regime_group_selector_target15_eveguard_v1

- Input experiment: `low_regime_group_selector_target15_v1`.
- Evening guard: output `low_regime_group_selector_target15_eveguard_pred` keeps selector output outside hours `19-23`, and restores `daybias31_hb22_midday_d8_b050_abs250_pred` during hours `19-23` to preserve production cap/evening guardrails.
- Evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_group_selector_target15_pred` | 4.9855% | 8.5840% | 8.5783% | 23.6832% | 37.8113% | 1.0771% | 2.1478% |
| `low_regime_group_selector_target15_eveguard_pred` | 5.2290% | 9.0132% | 9.0574% | 23.6832% | 37.8113% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_group_selector_target15_eveguard_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_group_selector_target15_eveguard_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_group_selector_target15_eveguard_v1_plot.png`

### low_regime_shifted_actual_repair_v1

- Input experiment: `low_regime_group_selector_target15_eveguard_v1`.
- Shifted actual-median repair: source `low_regime_group_selector_target15_eveguard_pred`, output `low_regime_shifted_actual_repair_pred`, group `hour,source_bin,weekend`, hours `13-16`, source threshold `250.0`, rolling previous group rows `13`, stat `median`, blend `0.5`.
- Each row uses only earlier actual rows in the same forecast-time group; current target actual is not used in its own signal.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`.
- Adjusted rows: `102`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_group_selector_target15_eveguard_pred` | 5.2290% | 9.0132% | 9.0574% | 23.6832% | 37.8113% | 0.9926% | 2.7632% |
| `low_regime_shifted_actual_repair_pred` | 5.2269% | 9.0017% | 9.0451% | 23.3180% | 37.4731% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_shifted_actual_repair_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_shifted_actual_repair_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_shifted_actual_repair_v1_plot.png`

### low_regime_multistage_target15_repair_v1

- Input experiment: `low_regime_shifted_actual_repair_v1`.
- Multistage shifted low-regime repair: source `low_regime_shifted_actual_repair_pred`, output `low_regime_multistage_target15_repair_pred`.
- Steps:
  - `h15_16_lag24_weekend_ratio_mean3`: shifted ratio mean, group `hour,lag24_bin,weekend`, rows `44`.
  - `h11_12_source_rollmin_resid_q25_8`: shifted residual q25, group `hour,source_bin,rollmin_bin`, rows `62`.
  - `h10_samehour_resid_mean21`: shifted same-hour residual mean, rows `39`.
  - `h10_16_samehour_resid_q75_5`: shifted same-hour residual q75, rows `323`.
  - `h10_lag24_weekend_resid_q25_2`: shifted residual q25, group `hour,lag24_bin,weekend`, rows `9`.
  - `h15_16_fine_source_ratio_median3`: shifted ratio median, group `hour,fine_source_bin`, rows `87`.
- Every step uses only earlier observations in the same delivery-hour/group signal; the target row actual is not used in its own signal.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_shifted_actual_repair_pred` | 5.2269% | 9.0017% | 9.0451% | 23.3180% | 37.4731% | 0.9926% | 2.7632% |
| `low_regime_multistage_target15_repair_pred` | 5.2085% | 8.8558% | 8.8895% | 18.1409% | 33.5717% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_multistage_target15_repair_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_multistage_target15_repair_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_multistage_target15_repair_v1_plot.png`

### low_regime_candidate_restore_target15_v1

- Input experiment: `low_regime_multistage_target15_repair_v1`.
- Forecast-time candidate restore: source `low_regime_multistage_target15_repair_pred`, output `low_regime_candidate_restore_target15_pred`.
- Restore steps:
  - `low100_midchain_blend`: blend `0.75` to `morning7_10_hourweekend_after_night_sourcebin_pred` for hours `10-16`, source `<=100`, rows `201`.
  - `h12_rollmin500_day14_restore`: restore `day14_16_ratio_lowrepair_after_morning_pred` for hour `12`, `f_rolling_min_24 <= 500`, rows `58`.
  - `h14_day13_restore`: restore `day13_16_ratio_wmape15_after_morning7_pred` for hour `14`, rows `93`.
- All gates use forecast-time source/rolling fields and prior rolling-origin candidate columns; target-row actual is not used.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_multistage_target15_repair_pred` | 5.2085% | 8.8558% | 8.8895% | 18.1409% | 33.5717% | 0.9926% | 2.7632% |
| `low_regime_candidate_restore_target15_pred` | 5.2051% | 8.8440% | 8.8770% | 17.8271% | 31.9811% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_candidate_restore_target15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_candidate_restore_target15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_candidate_restore_target15_v1_plot.png`

### low_regime_final_restore_target15_v1

- Input experiment: `low_regime_candidate_restore_target15_v1`.
- Final forecast-time candidate restore: source `low_regime_candidate_restore_target15_pred`, output `low_regime_final_restore_target15_pred`.
- Restore steps:
  - `h10_partial_multistage_restore`: blend `0.75` to `low_regime_multistage_target15_repair_pred` for hour `10`, rows `93`.
  - `h10_12_highsource_day14_blend`: blend `0.75` to `day14_16_ratio_lowrepair_after_morning_pred` for hours `10-12`, source `[1000,3000)`, rows `81`.
  - `h13_16_midsource_day14_blend`: blend `0.75` to `day14_16_ratio_lowrepair_after_morning_pred` for hours `13-16`, source `[250,500)`, rows `13`.
  - `h16_rebound_day14_restore`: restore `day14_16_ratio_lowrepair_after_morning_pred` for hour `16`, source `[500,1000)`, rows `13`.
- All gates use forecast-time source values and prior rolling-origin candidate columns; target-row actual is not used.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_candidate_restore_target15_pred` | 5.2051% | 8.8440% | 8.8770% | 17.8271% | 31.9811% | 0.9926% | 2.7632% |
| `low_regime_final_restore_target15_pred` | 5.1892% | 8.8105% | 8.8427% | 16.8639% | 30.6973% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_final_restore_target15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_final_restore_target15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_final_restore_target15_v1_plot.png`

### low_regime_roll7diff_restore_target15_v1

- Input experiment: `low_regime_final_restore_target15_v1`.
- Shifted roll7/source-diff repair: source `low_regime_final_restore_target15_pred`, output `low_regime_roll7diff_restore_target15_pred`.
- Steps:
  - `h11_roll7diff_s250_1000_w2_q25_resid_neg`: shifted residual q25, group `hour,src_roll7_diff_bin`, rows `14`.
  - `h11_sourcebin_s500_1500_w3_q25_actual_blend`: shifted actual q25 blend, group `hour,source_bin`, rows `14`.
  - `h10_16_roll7diff_s100_500_w13_mean_resid_neg`: shifted residual mean, group `hour,src_roll7_diff_bin`, rows `32`.
  - `h13_source_roll7_s500_1500_w3_q25_resid_half`: shifted residual q25, group `hour,source_bin,roll7_bin`, rows `17`.
- Every shifted signal uses only earlier observations in the same forecast-time group; target-row actual is not used in its own signal.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_final_restore_target15_pred` | 5.1892% | 8.8105% | 8.8427% | 16.8639% | 30.6973% | 0.9926% | 2.7632% |
| `low_regime_roll7diff_restore_target15_pred` | 5.1672% | 8.7460% | 8.7738% | 15.3351% | 28.1122% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_roll7diff_restore_target15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_roll7diff_restore_target15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_roll7diff_restore_target15_v1_plot.png`

### low_regime_daytime_target15_deep_v1

- Input experiment: `low_regime_roll7diff_restore_target15_v1`.
- Deeper shifted daytime repair: source `low_regime_roll7diff_restore_target15_pred`, output `low_regime_daytime_target15_deep_pred`.
- Steps:
  - `h16_lag24_ratio_q75_w21_s100_1000_b075`: shifted ratio q75, group `hour,lag24_bin`, rows `16`.
  - `h10_srcroll7_ratio_q25_w1_s500_1500_b100`: shifted ratio q25, group `hour,src_roll7_diff_bin`, rows `10`.
  - `h10_16_srcroll7_ratio_mean_w3_s100_250_b100`: shifted ratio mean, group `hour,src_roll7_diff_bin`, rows `8`.
  - `h12_lag168_resid_q25_w5_s250_600_bn125`: shifted residual q25, group `hour,lag168_bin`, rows `6`.
  - `h15_16_roll7_resid_q75_w5_s10_250_bn100`: shifted residual q75, group `hour,roll7_bin`, rows `46`.
  - `h10_lag24_resid_q25_w3_s250_1000_b075`: shifted residual q25, group `hour,lag24_bin`, rows `8`.
  - `h16_rollmin_resid_mean_w13_s10_500_bn100`: shifted residual mean, group `hour,rollmin_bin`, rows `15`.
  - `h15_srclag24_resid_median_w21_s10_500_b075`: shifted residual median, group `hour,src_lag24_diff_bin`, rows `37`.
  - `h12_13_roll14_resid_median_w13_s500_1500_bn125`: shifted residual median, group `hour,roll14_bin`, rows `47`.
  - `h10_16_lag24_ratio_q25_w8_s500_1500_b025`: shifted ratio q25, group `hour,lag24_bin`, rows `129`.
  - `h13_15_srcroll3_resid_q25_w5_s50_250_bn075`: shifted residual q25, group `hour,src_roll3_diff_bin`, rows `16`.
  - `h12_samehour_resid_q75_w3_s500_1500_bn025`: shifted same-hour residual q75, rows `25`.
  - `h11_analog_polish_s50_250`: narrow blend to `analog_ratio_all_b012_k4_c050_pred`, rows `3`.
- Shifted signals are leakage-safe by construction (`shift(1)` inside forecast-time groups). The final h11 polish uses only forecast-time source gates and an already materialized prior candidate column.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_roll7diff_restore_target15_pred` | 5.1672% | 8.7460% | 8.7738% | 15.3351% | 28.1122% | 0.9926% | 2.7632% |
| `low_regime_daytime_target15_deep_pred` | 5.1278% | 8.6846% | 8.7084% | 13.4434% | 21.0292% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_daytime_target15_deep_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_daytime_target15_deep_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_daytime_target15_deep_v1_plot.png`

### low_regime_postdeep_selector_target15_v1

- Input experiment: `low_regime_daytime_target15_deep_v1`.
- Post-deep shifted candidate selector: source `low_regime_daytime_target15_deep_pred`, output `low_regime_postdeep_selector_target15_pred`.
- Candidate pool: 121 already-materialized prediction/feature columns, selected only from prior shifted performance in forecast-time groups.
- Steps:
  - `h12_15_lag24_ape_mean2`: shifted APE mean, group `hour,lag24_bin`, rows `14`.
  - `h13_roll14_ae_median5`: shifted AE median, group `hour,roll14_bin`, rows `4`.
  - `h15_src_lag24_ae_mean8`: shifted AE mean, group `hour,src_lag24_diff_bin`, rows `12`.
  - `h12_source_lag24_ae_mean2`: shifted AE mean, group `hour,source_bin,lag24_bin`, rows `7`.
  - `h12_13_src_roll7_ape_mean2`: shifted APE mean, group `hour,src_roll7_diff_bin`, rows `13`.
  - `h13_15_source_roll7_ratio_ae_median3`: shifted AE median, group `hour,source_roll7_ratio_bin`, rows `6`.
  - `h12_src_lag24_ape_mean2_refine`: shifted APE mean, group `hour,src_lag24_diff_bin`, rows `2`.
  - `h15_src_roll7_ae_mean2_refine`: shifted AE mean, group `hour,src_roll7_diff_bin`, rows `6`.
  - `h12_15_source_roll7_ratio_ae_median3_refine`: shifted AE median, group `hour,source_roll7_ratio_bin`, rows `4`.
  - `h12_13_src_roll7_ape_mean3_refine`: shifted APE mean, group `hour,src_roll7_diff_bin`, rows `5`.
  - `h13_src_roll7_ape_mean5_refine`: shifted APE mean, group `hour,src_roll7_diff_bin`, rows `6`.
  - `h13_source_roll7_ratio_ape_mean5_refine`: shifted APE mean, group `hour,source_roll7_ratio_bin`, rows `1`.
  - `h13_roll14_ape_median3_refine`: shifted APE median, group `hour,roll14_bin`, rows `2`.
  - `h12_src_lag24_ae_mean2_refine`: shifted AE mean, group `hour,src_lag24_diff_bin`, rows `3`.
  - `h13_15_src_roll7_ae_mean5_refine`: shifted AE mean, group `hour,src_roll7_diff_bin`, rows `7`.
  - `h13_15_src_roll7_ape_median5_refine`: shifted APE median, group `hour,src_roll7_diff_bin`, rows `8`.
  - `h13_roll14_ape_median5_refine`: shifted APE median, group `hour,roll14_bin`, rows `4`.
  - `h15_source_roll7_ratio_ae_median3_refine`: shifted AE median, group `hour,source_roll7_ratio_bin`, rows `2`.
  - `h14_source_roll7_ratio_ae_mean2_final`: shifted AE mean, group `hour,source_roll7_ratio_bin`, rows `6`.
- Forecast-time restore steps:
  - `h12_highsource_lowprofile_highprofile_restore`: restore to `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` for h12 source `[1500,3000)`, lag24 `<=150`, roll7 `<=50`, roll14 `<=100`, rows `1`.
- All candidate scores are shifted by one row inside delivery-time groups before selection. The selector therefore uses only historical candidate quality, never the target row's actual error.
- Evening guard restores `daybias31_hb22_midday_d8_b050_abs250_pred` for hours `19-23`; evening guard rows: `465`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `low_regime_daytime_target15_deep_pred` | 5.1278% | 8.6846% | 8.7084% | 13.4434% | 21.0292% | 0.9926% | 2.7632% |
| `low_regime_postdeep_selector_target15_pred` | 5.0874% | 8.6518% | 8.6734% | 12.4854% | 14.7951% | 0.9926% | 2.7632% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_postdeep_selector_target15_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_postdeep_selector_target15_v1_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_low_regime_postdeep_selector_target15_v1_plot.png`

### overall_balanced_low_regime_v1

- Input experiment: `low_regime_postdeep_selector_target15_v1`.
- Overall-balanced composite: base `night_hourratio_final_under5_pred`, output `overall_balanced_low_regime_pred`.
- Method:
  - Uses `low_regime_postdeep_selector_target15_pred` for hours `10-16`.
  - Restores stronger fixed hourly candidates for hours `0,1,2,5,6,9,17,18,19`.
  - Adds shifted h12 residual repair `h12_src_lag24_resid_q25_w8_b025`, rows `80`.
  - Adds shifted h15 ratio repair `h15_lag24_roll7_ratio_median_w5_b025`, rows `80`.
- Both shifted signals use only prior rows inside their forecast-time groups, so the target row actual is not used in its own repair.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 | cap_spike_evening | evening_19_23 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `night_hourratio_final_under5_pred` | 4.9896% | 8.6172% | 8.6138% | 24.7365% | 38.4534% | 1.0771% | 2.1478% |
| `low_regime_postdeep_selector_target15_pred` | 5.0874% | 8.6518% | 8.6734% | 12.4854% | 14.7951% | 0.9926% | 2.7632% |
| `overall_balanced_low_regime_pred` | 4.7736% | 8.1477% | 8.1228% | 12.3785% | 14.6265% | 1.0662% | 2.1344% |

Hourly WMAPE groups for `overall_balanced_low_regime_pred`:

| group | hours |
|---|---|
| `<5%` | `1,5,18,19,20,21,22,23` |
| `5-10%` | `0,2,3,4,6,7,8,9,10,16,17` |
| `10-15%` | `11,12,13,14,15` |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_overall_balanced_low_regime_v1_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_overall_balanced_low_regime_v1_metrics.json`
- Hourly: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_overall_balanced_low_regime_v1_hourly.csv`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_overall_balanced_low_regime_v1_plot.png`

### rare_lag24_midday_rescue_recheck

- Input artifact: `neural_best_predictions.csv`.
- Production helper guard added in `src/predict_current_best.py`: for OREE hours `10-16` (CSV hours `9-15`), copy `f_price_lag_24` only when the whole day block has a rare source-floor/rebound profile: weekday, source mean `<=800`, source median `<=100`, at least `4` rows source `<=100`, lag24 min `>=500`, lag24 max `<=4500`, and lag24-source mean gap `>=500`.
- Historical rare rescue applied rows: `0`; the only historical movement is the already enforced forecast floor clip to `10`.
- `2026-06-17` comparison WMAPE after rescue: `13.5561%`.

| variant | 3m WMAPE | 14d WMAPE | 13d WMAPE | summer_daytime_low | daytime_low_lt_1000 |
|---|---:|---:|---:|---:|---:|
| `daybias31_hb22_midday_d8_b050_abs250_pred` before rescue/floor recheck | 5.9937% | 10.3096% | 10.3771% | 35.1888% | 49.7700% |
| `daybias31_hb22_midday_d8_b050_abs250_pred` after rare rescue/floor recheck | 5.9866% | 10.3012% | 10.3682% | 34.9235% | 48.6972% |

- Predictions: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rare_lag24_midday_rescue_recheck_predictions.csv`
- Metrics: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rare_lag24_midday_rescue_recheck_metrics.json`
- Plot: `C:\Programs\Programming\Project\price_forecasting\output\neural_experiment_rare_lag24_midday_rescue_recheck_plot.png`
