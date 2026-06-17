# Overall-balanced target for 2026-06-17 and 2026-06-18

## Нова ціль

Фінальна модель для production має бути `overall_balanced_low_regime_v1`, бо це найкраща уніфікована гілка:

| model | all WMAPE | 3m WMAPE | 14d WMAPE | 13d WMAPE |
|---|---:|---:|---:|---:|
| `overall_balanced_low_regime_v1` | 4.4052% | 4.3380% | 7.5560% | 7.6687% |
| legacy `current_best` | 6.0571% | 5.9937% | 10.3096% | 10.3771% |

Практична умова для 17/18: daily WMAPE на `2026-06-17` і `2026-06-18` має бути `<13%`, при цьому історичні `14d` і `3m` не мають погіршитись.

## Що вже зроблено

- Для `2026-06-17` добудовано neural future candidates через `src/predict_neural_hybrid_future.py`.
- `src/assemble_overall_balanced_input.py` отримав feature aliases, щоб debug-файли з різних forecast helpers однаково давали `f_price_lag_*`, `f_rolling_mean_hour_*`, weather aliases.
- `2026-06-17` і `2026-06-18` тепер мають однаковий readiness state для `overall_balanced`: `40/62`, missing `22`.
- `output/neural_best_predictions.csv`, `output/neural_best_metrics.json` і `output/neural_best_plot.png` переприв'язано до canonical `overall_balanced_low_regime_v1`, щоб `neural_best` більше не означав старий `daybias31`.
- `src/predict_current_best.py` тепер бере prediction column з `output/neural_best_metrics.json`; для дат поза `neural_best_predictions.csv` він не робить silent fallback на legacy `daybias31`. Старий future-date chain доступний тільки явно через `--pred-col daybias31_hb22_midday_d8_b050_abs250_pred --allow-legacy-future-fallback`.
- Основний evaluator перевірено на `output/neural_best_predictions.csv --pred-col overall_balanced_low_regime_pred`: `3m=4.34%`, `14d=7.56%`.
- Додано `src/predict_overall_balanced_future.py`: canonical future-date entrypoint, який приймає готовий forecast-time input, перевіряє missing required columns, будує `overall_balanced_low_regime_pred` через `build_overall_balanced`, і додає факт тільки після forecast для comparison.
- `src/check_overall_balanced_readiness.py` тепер показує `null_required` warnings і має `--strict-non-null-required` для аудиту прихованих NaN у required candidate columns.
- Додано `src/predict_nonlinear_stacker_future.py`, щоб відтворювати окремі rolling-origin nonlinear candidates для future-date без факту target-day. Через нього заповнено `anomaly_hgb_ratio_b0025_q85w025_pred` для 17.06/18.06.

## Поточний readiness

| date | input probe | readiness | status |
|---|---|---:|---|
| 2026-06-17 | `output/prediction_2026-06-17_overall_input_probe.csv` | 40/62 | not ready |
| 2026-06-18 | `output/prediction_2026-06-18_overall_input_probe.csv` | 40/62 | not ready |

Missing columns are the real blocker for using the `4.338 / 7.556` model on future dates. The important missing target columns include `night_hourratio_final_under5_pred`, `low_regime_postdeep_selector_target15_pred`, `day14_16_ratio_lowrepair_after_morning_pred`, `morning7_10_hourratio_final_push_pred`, and related chain columns.

## Proxy selector check

I tested whether a shorter learned selector over available forecast-time columns could satisfy the new `<13%` daily target without waiting for the full `overall_balanced` chain.

| probe | rows checked | objective rows | best 17 WMAPE | best 18 WMAPE | 14d impact |
|---|---:|---:|---:|---:|---:|
| regular future candidate-meta grid | 125 | 0 | 13.50%+ | 16.85%+ | mixed |
| aggressive candidate-meta grid | 80 | 0 | 13.60% | 16.69% | +0.1106 pp |

The aggressive selector still did not get close to `18 < 13%`, and its best daily result already worsened `14d`. So it should not be promoted.

## 17/18 draft check after canonical switch

The expanded draft files pass `build_overall_balanced` readiness, but they are still not good enough for promotion:

| date | artifact | daily WMAPE | target |
|---|---|---:|---:|
| 2026-06-17 | `output/comparison_2026-06-17_overall_balanced.csv` | `13.1011%` | `<13%` |
| 2026-06-18 | `output/comparison_2026-06-18_overall_balanced.csv` | `18.0653%` | `<13%` |

Largest remaining 18.06 errors are daytime low/rebound hours: h10-h16 are too high while h07 is too low. This confirms the next step is not to promote the draft, but to rebuild the missing leakage-safe chain columns and then learn a unified selector that handles morning spike / daytime collapse without date-specific rules.

Non-null readiness caveat: expanded drafts have all `62/62` required columns, but `anomaly_hgb_ratio_b0025_q85w025_pred` is `NaN` for all target rows. The matching final h11 anomaly gate has `0` matching rows on both 17.06 and 18.06, so current forecasts do not change, but the hidden-null warning is now visible and `--strict-non-null-required` catches it.

Follow-up fix: rebuilt that anomaly candidate with the original rolling-origin HGB parameters and assembled filled drafts. `output/prediction_2026-06-17_overall_balanced_filled.csv` and `output/prediction_2026-06-18_overall_balanced_filled.csv` now pass `--strict-non-null-required`. Metrics are unchanged because the anomaly gate is inactive: `17.06 = 13.1011%`, `18.06 = 18.0653%`; with 17.06 as extra history, `18.06 = 17.8950%`.

Safe-fill check: `src/assemble_overall_balanced_input.py` now supports `--fill-null-candidate`, which fills only missing overlap cells from a candidate CSV and does not replace complete base columns. Rebuilding `prediction_2026-06-17_overall_balanced_filled_safe.csv` and `prediction_2026-06-18_overall_balanced_filled_safe.csv` produced `62/62` required columns with `0` required nulls. The safe files have the same values as the existing filled inputs; the only difference is column order around the anomaly candidate columns.

Production default update: `src/predict_overall_balanced_future.py` now prefers `overall_balanced_filled` input before `overall_balanced_draft` and `overall_input_probe`. A default 18.06 run without `--target-input-csv` confirmed it uses `output/prediction_2026-06-18_overall_balanced_filled.csv` and reproduces `18.0653%`; the default rolling-history run reproduces `17.8950%`.

The new entrypoint correctly rejects the short probe input:

```powershell
python src\predict_overall_balanced_future.py 2026-06-18 --target-input-csv output\prediction_2026-06-18_overall_input_probe.csv
```

Result: fails on the same `22` missing required columns instead of producing a misleading fallback forecast.

## Selector research update

Additional selector probes are documented in `output/overall_balanced_selector_research_2026-06-17_18.md`.

Summary:

- Static candidates: no no-regression candidate beats the source on 17/18.
- Focused shifted multi-candidate selector: `0` history-safe configurations in the partial grid; best target-heavy variants still leave `18` around `16%+` and regress history.
- Forecast-time regime rule grid: can push `18` below `13%`, but worsens `17` and history badly, so it is not promotable.
- Tiny h11/h15 legacy low rescue has `0` historical applications and lowers `18` only to `17.5793%`; not enough and not enough evidence for production.
- Compact rolling-origin model probe over source/candidate prices, lags, rolling profiles, weather/solar/wind, calendar and hour features tested `1440` model/hour-mask variants. `134` were history-safe, but `0` reached both 17.06 and 18.06 below `13%`; the best target-heavy 18.06 variant reached `11.4943%` only by worsening history to `all=12.6255%`, `14d=15.8844%` and 17.06 to `16.4046%`.
- Lagged market-structure probe tested `2880` Ridge/hour-mask variants with shifted supply/demand/Garpok/VDR features. `222` were history-safe, but `0` reached both target days below `13%`; best history-safe 18.06 was only `18.0348%`.
- Rolling-history forecast support was added to `src/predict_overall_balanced_future.py` via `--extra-history-csv`. Using 17.06 as known pre-target history for 18.06 improves `18.0653% -> 17.8950%`, but this is still too small for the target.
- Main useful candidates for 18.06 have negative shifted same-hour historical advantage, so a leakage-safe selector correctly refuses them.

This means the next real improvement needs a stronger forecast-time signal, likely from market structure features (`rdn_supply`, `rdn_demand`, `garpok_volume`, ramps/spreads) or a classifier trained on shifted historical candidate trust, not more hardcoded date rules.

## Conclusion

Use `overall_balanced_low_regime_v1` as the final target model, not a current-best-only spike patch. The next implementation step is to rebuild the missing 22 forecast-time columns through the same leakage-safe chain that produced `night_hourratio_final_under5_v1` and `low_regime_postdeep_selector_target15_v1`.

Artifacts:

- `output/overall_balanced_readiness_current_best_debug_2026-06-17.json`
- `output/prediction_2026-06-17_neural_hybrid_candidates.csv`
- `output/prediction_2026-06-17_overall_input_probe.csv`
- `output/prediction_2026-06-17_overall_input_probe_readiness.json`
- `output/prediction_2026-06-18_overall_input_probe.csv`
- `output/prediction_2026-06-18_overall_input_probe_readiness.json`
- `output/prediction_2026-06-17_overall_balanced.csv`
- `output/prediction_2026-06-17_overall_balanced_debug.csv`
- `output/comparison_2026-06-17_overall_balanced.csv`
- `output/prediction_2026-06-18_overall_balanced.csv`
- `output/prediction_2026-06-18_overall_balanced_debug.csv`
- `output/comparison_2026-06-18_overall_balanced.csv`
- `output/prediction_2026-06-17_anomaly_hgb_ratio_future.csv`
- `output/prediction_2026-06-18_anomaly_hgb_ratio_future.csv`
- `output/prediction_2026-06-17_overall_balanced_filled.csv`
- `output/prediction_2026-06-18_overall_balanced_filled.csv`
- `output/overall_balanced_filled_probe/comparison_2026-06-17_overall_balanced.csv`
- `output/overall_balanced_filled_probe/comparison_2026-06-18_overall_balanced.csv`
- `output/overall_balanced_filled_rolling_history_probe/comparison_2026-06-18_overall_balanced.csv`
- `output/overall_balanced_default_input_probe/comparison_2026-06-18_overall_balanced.csv`
- `output/overall_balanced_default_input_rolling_probe/comparison_2026-06-18_overall_balanced.csv`
- `output/overall_balanced_selector_research_2026-06-17_18.md`
- `output/overall_balanced_multicandidate_selector_focused_grid_17_18.csv`
- `output/overall_balanced_regime_rule_grid_17_18.csv`
- `output/overall_balanced_compact_walkforward_grid_17_18.csv`
- `output/overall_balanced_market_lag_ridge_grid_17_18.csv`
- `output/overall_balanced_rolling_history_probe/comparison_2026-06-18_overall_balanced.csv`
- `output/future_candidate_meta_17_18_grid.csv`
- `output/future_candidate_meta_17_18_aggressive_grid.csv`
