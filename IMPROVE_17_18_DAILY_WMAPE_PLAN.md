# План пробиття 13% daily WMAPE на 2026-06-17 і 2026-06-18

Дата аналізу: `2026-06-17`

Ціль: зробити production-valid прогноз, у якому `2026-06-17` і `2026-06-18` мають daily WMAPE `< 13%`, не втративши вже прийнятні історичні метрики `14d` і `3m`.

Цей файл є технічним планом. Код моделей не змінювався.

## Що прочитано

- `README.md`
- `NEURAL_MODEL_IMPROVEMENT_PLAN.md`
- `output/overall_balanced_goal_2026-06-17_18.md`
- `output/overall_balanced_selector_research_2026-06-17_18.md`
- `output/neural_best_summary.md`
- `output/neural_best_metrics.json`
- `output/comparison_2026-06-17_overall_balanced.csv`
- `output/comparison_2026-06-18_overall_balanced.csv`
- `src/build_overall_balanced_composite.py`
- `src/predict_overall_balanced_future.py`
- `src/evaluate_neural_hybrid.py`
- `src/train_neural_hybrid.py`
- `src/predict_neural_hybrid_future.py`
- `src/apply_candidate_blend_adjuster.py`
- `src/apply_multi_candidate_blend_adjuster.py`
- `src/rolling_origin_nonlinear_stacker.py`
- `src/assemble_overall_balanced_input.py`
- `forecasting_core.py`

## Поточна база

Canonical production target зараз:

- experiment: `overall_balanced_low_regime_v1`
- prediction column: `overall_balanced_low_regime_pred`
- all available WMAPE: `4.4052%`
- 3m WMAPE: `4.3380%`
- 14d WMAPE: `7.5560%`
- 13d WMAPE: `7.6687%`
- `summer_daytime_low`: `10.52%`
- `daytime_low_lt_1000`: `12.77%`
- `cap_spike_evening`: `1.07%`
- `evening_19_23`: `2.13%`

Ці метрики дуже сильні. Проблема не в середній історичній якості, а в окремих out-of-sample днях, де режим відрізняється від того, що current selector вважає безпечним.

Поточні daily metrics:

| date | WMAPE | MAE | bias | status |
|---|---:|---:|---:|---|
| `2026-06-17` | `13.1011%` | `1030.54` | `-907.75` | майже ціль, треба зняти лише `0.1011 п.п.` |
| `2026-06-18` | `18.0653%` | `1155.12` | `41.94` | головний провал, треба зняти `5.0653 п.п.` |

У грошах:

| date | actual denominator | current abs error | target abs error for 13% | required reduction |
|---|---:|---:|---:|---:|
| `2026-06-17` | `188786.16` | `24733.07` | `24542.20` | `190.87` |
| `2026-06-18` | `153459.76` | `27722.94` | `19949.77` | `7773.17` |

Висновок: 17-те не є справжньою проблемою, його можна пробити дуже малим покращенням. 18-те потребує суттєво кращого визначення режиму.

## Де саме ламається 17.06

Найбільші абсолютні помилки:

| hour | actual | pred | signed error | APE |
|---:|---:|---:|---:|---:|
| 19 | `14977.67` | `10731.22` | `-4246.45` | `28.35%` |
| 7 | `10500.00` | `6562.67` | `-3937.33` | `37.50%` |
| 8 | `9285.00` | `6346.08` | `-2938.92` | `31.65%` |
| 18 | `8000.00` | `5533.13` | `-2466.87` | `30.84%` |
| 24 | `14967.50` | `13816.46` | `-1151.04` | `7.69%` |
| 6 | `6850.00` | `5700.02` | `-1149.98` | `16.79%` |

Вже наявний static candidate `anomaly_hgb_ratio_b0025_q85w025_pred` дає для 17-го `12.7733%`, тобто сам 17-й технічно можна пробити. Але це не вирішує 18-й день і не є достатнім proof для promotion.

## Де саме ламається 18.06

Найбільші абсолютні помилки:

| hour | actual | pred | signed error | APE |
|---:|---:|---:|---:|---:|
| 8 | `11800.00` | `6832.65` | `-4967.35` | `42.10%` |
| 18 | `3902.00` | `7601.06` | `3699.06` | `94.80%` |
| 21 | `11498.88` | `14013.34` | `2514.46` | `21.87%` |
| 17 | `1050.00` | `3444.83` | `2394.83` | `228.08%` |
| 11 | `1100.00` | `3471.90` | `2371.90` | `215.63%` |
| 24 | `11720.00` | `9530.71` | `-2189.29` | `18.68%` |
| 20 | `12500.00` | `11250.53` | `-1249.47` | `10.00%` |

18-й день має змішаний режим:

- ранковий rebound/spike: h8 фактично `11800`, а модель занизила до `6832`;
- денний collapse: h11-h17 фактично `289-1100`, а модель часто лишається занадто високо;
- вечірній перехід: h18/h21 переоцінені, h20/h24 недооцінені.

Це не одна поправка по bias. Потрібен селектор, який розрізняє різні підрежими всередині одного дня.

## Чому поточні repairs не добивають ціль

`overall_balanced_low_regime_v1` будується так:

1. База: `night_hourratio_final_under5_pred`.
2. Для h10-h16 підставляється `low_regime_postdeep_selector_target15_pred`.
3. Далі йдуть fixed hourly restores, shifted repairs, candidate blends, final shifted repairs і final gated blends.
4. Усі historical corrections використовують тільки shifted history або forecast-time columns.

Це правильно для leakage-control, але є побічний ефект: selector дуже консервативний. Для 18.06 корисні кандидати існують, але shifted same-hour advantage для них часто негативний. Тобто історично схожі заміни частіше шкодили, і production-safe selector їх справедливо відкидає.

Приклади row-wise oracle по вже наявних колонках на 18.06:

| hour | useful candidate | source abs error | candidate abs error | gain |
|---:|---|---:|---:|---:|
| 18 | `f_rolling_mean_hour_14d` | `3699.06` | `280.00` | `3419.06` |
| 8 | `f_price_lag_48` | `4967.35` | `2515.00` | `2452.35` |
| 11 | `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred` | `2371.90` | `50.00` | `2321.90` |
| 21 | `f_rolling_mean_hour_7d` | `2514.46` | `539.68` | `1974.77` |
| 17 | `f_rolling_mean_hour_14d` | `2394.83` | `954.29` | `1440.55` |
| 24 | `ensemble_neural_pred` | `2189.29` | `965.17` | `1224.11` |
| 12 | `lag24blend9_db21_hourall_r3_mean_an005_advn500_pred` | `650.73` | `24.29` | `626.45` |

Oracle WMAPE:

- 17.06 row oracle over available candidates: `7.9562%`
- 18.06 row oracle over available candidates: `4.7124%`

Це важливий факт: у repo вже є достатньо candidate diversity, щоб пройти `<13%`. Не вистачає не кандидата, а leakage-safe механізму довіри до кандидата.

## Що вже пробували і чому цього недостатньо

За `output/overall_balanced_selector_research_2026-06-17_18.md`:

- Static candidate check: жоден static candidate не покращує 17/18 без історичної регресії.
- Focused shifted multi-candidate selector: `0` history-safe configurations; target-heavy варіанти лишають 18-й приблизно `16%+` або ламають history.
- Forecast-time regime rule grid: може опустити 18-й нижче `13%`, але псує 17-й і history.
- Tiny h11/h15 low rescue: 18-й лише до `17.5793%`, історичних застосувань `0`, не production evidence.
- Compact rolling-origin model: `1440` variants, `134` history-safe, `0` досягли обох target days `<13%`.
- Lagged market-structure Ridge: `2880` variants, `222` history-safe, `0` досягли обох target days `<13%`.
- Додавання 17.06 як rolling history для 18.06 дає лише `18.0653% -> 17.8950%`.

Отже, ще одна ручна сітка правил навряд чи достатня. Потрібен сильніший forecast-time signal або нова модель вибору кандидатів.

## Головна гіпотеза

18.06 є не провалом tree/neural price level як такого, а провалом `candidate trust`:

- правильні candidate values часто вже є;
- простий shifted median/mean advantage каже "не довіряти";
- поточні features не відрізняють rare rebound/collapse від звичайного шуму;
- модель одночасно недооцінює ранковий high і переоцінює денний/перехідний low.

Тому найкоротший шлях до `<13%`:

1. Не міняти одразу всю `overall_balanced` модель.
2. Додати над нею leakage-safe `candidate trust ranker`.
3. Навчити ranker не тільки на historical advantage, а на interaction features між source, candidate, лагами, профілями, погодою, lagged market structure і day-level regime.
4. Тільки якщо цього недостатньо, будувати нову day-profile модель.

## Рекомендований шлях 1: Candidate Trust Ranker

### Ідея

Замість поточного правила "кандидат мав позитивний shifted advantage у групі" навчити модель:

```text
P(candidate is safer than source | forecast-time features)
E(abs_error_gain | forecast-time features)
P(catastrophic_harm | forecast-time features)
```

Для кожного рядка і кожного кандидата формуємо training sample:

```text
source = overall_balanced_low_regime_pred
candidate = one of available candidate columns
label_gain = abs(source - actual) - abs(candidate - actual)
label_good = label_gain > margin
label_bad = label_gain < -bad_margin
```

На inference:

```text
take candidate only if:
  expected_gain > threshold
  P(good) high enough
  P(bad) below safety threshold
  candidate/source distance is plausible
```

### Чому це краще за поточний selector

Поточний selector дивиться на один shifted rolling signal у грубій групі. Ranker може вчити взаємодії:

- source високо, lag48/rolling низько;
- source низько, lag48 високо;
- h8 rebound проти h11-h17 collapse;
- candidate family historically good тільки в певному профілі дня;
- weather/renewable pressure як secondary context;
- lagged market ramps і balance, але без same-day raw leakage.

### Candidate pool

Стартовий пул не треба робити безмежним. Перший ranker має покрити колонки, які вже показали корисність:

- `overall_balanced_low_regime_pred` як no-op source.
- `f_price_lag_24`
- `f_price_lag_48`
- `f_price_lag_168`
- `f_rolling_mean_hour_3d`
- `f_rolling_mean_hour_7d`
- `f_rolling_mean_hour_14d`
- `ensemble_neural_pred`
- `ensemble_hybrid_pred`
- `tree_base_pred`
- `tree_recent_calibrated_pred`
- `daybias31_hb22_midday_d8_b050_abs250_pred`
- `lag24blend9_db21_hourall_r3_mean_an005_advn500_pred`
- `high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred`
- `low_regime_postdeep_selector_target15_pred`
- `sourcebin_daytime_bias_after_lowrepair_pred`
- `hourbias17_gb12_midday_r21_med_bn050_abs250_pred`
- `hourbias22_hb21_peakerr_r8_bn020_wmape40_pred`

Далі пул можна розширити, але перший production-кандидат має бути контрольованим.

### Features для ranker

Forecast-time features:

- hour, day of week, weekend, month, summer;
- price cap і cap regime;
- source price, source ratio to cap;
- candidate price, candidate ratio to cap;
- source-candidate absolute/relative distance;
- candidate family id;
- lag24, lag48, lag168;
- rolling mean hour 3d/7d/14d;
- source minus lag24/48/168;
- candidate minus lag24/48/168;
- source minus rolling profile;
- candidate minus rolling profile;
- day-level profile stats: min/max/mean of source day, h8-h11 slope, h10-h17 average, h18-h21 slope;
- weather: wind, windgust, cloudcover, solarradiation, renewable pressure index;
- regional weather features if available;
- lagged market structure only: `rdn_supply/demand/garpok/vdr` lags `24/48/168/336`, ramps, supply-demand spread, demand/supply ratio.

Forbidden:

- target-day `actual`;
- target-day raw `rdn_supply`, `rdn_demand`, `vdr_supply`, `vdr_demand`, `garpok_volume` for a pre-auction forecast;
- any unshifted same-day market result column.

### Model choices

Start simple and robust:

- `HistGradientBoostingClassifier/Regressor`
- `LightGBM` if installed and stable in the environment
- `CatBoost` only if adding dependency is acceptable

Recommended first version:

- classifier `good/bad/no-op` per candidate;
- regressor for expected gain;
- final score:

```text
score = expected_gain * P(good) - 2.0 * expected_loss * P(bad)
```

Use candidate only if score exceeds a threshold found on rolling validation.

### Validation protocol

Must be rolling-origin:

1. For each target day in the historical evaluation window, train ranker only on rows before that day.
2. Predict candidate scores for that day.
3. Apply selected candidate or blend:

```text
final = (1 - alpha) * source + alpha * candidate
```

4. Tune `alpha` and thresholds only on validation, not on 17/18 directly.

Promotion gates:

- 17.06 daily WMAPE `<13%`;
- 18.06 daily WMAPE `<13%`;
- 3m WMAPE no worse than `4.3380%` by strict target, or max `+0.05 п.п.` if the business accepts controlled regression;
- 14d WMAPE no worse than `7.5560%` by strict target, or max `+0.15 п.п.` if the 17/18 objective is prioritized;
- `summer_daytime_low <= 13%`;
- `daytime_low_lt_1000 <= 15%`;
- `cap_spike_evening <= 2%`;
- no predictions below `10` or above cap;
- duplicate factual datetimes = `0`.

### Нові файли, які варто додати

- `src/build_candidate_trust_ranker.py`
- `src/predict_candidate_trust_future.py`
- `src/evaluate_target_days.py`
- `output/candidate_trust_ranker_17_18_grid.csv`
- `output/candidate_trust_ranker_17_18_summary.md`

## Рекомендований шлях 2: Day-Level Regime Classifier

Ranker стане сильнішим, якщо перед ним буде класифікатор режиму всього дня.

Потрібні класи:

- `normal_day`
- `morning_rebound_spike`
- `daytime_low_collapse`
- `low_to_evening_rebound`
- `evening_overcap_risk`
- `mixed_rebound_collapse`

Для 18.06 це особливо важливо, бо день має і ранковий high, і денний low. Hour-only rules погано бачать таку комбінацію.

Day-level features:

- source day min/max/mean;
- source h7-h9 peak;
- source h10-h17 mean;
- source h17-h21 ramp;
- lag24/48/168 day profiles;
- rolling 3d/7d/14d day profiles;
- profile distances:
  - source vs lag24;
  - source vs lag48;
  - source vs lag168;
  - source vs rolling7;
- forecast weather day aggregates;
- lagged market day aggregates;
- candidate disagreement stats: std/min/max across candidate pool by hour and day block.

Labels can be derived from historical actual profile:

- morning rebound if h7-h9 actual much above h10-h16 actual;
- daytime collapse if min h10-h17 `<1000`;
- evening overcap if h19-h23 actual `>12000`;
- mixed if both morning high and daytime collapse happen.

Usage:

- regime probabilities become features for `Candidate Trust Ranker`;
- regime probabilities can also gate candidate pool, for example allow `f_price_lag_48` at h8 only when `morning_rebound_spike` probability is high.

## Рекомендований шлях 3: Day-Profile Residual Model

Якщо ranker не проб'є 18-й день, треба робити нову модель не погодинною, а добовою.

Ідея: один sample = один delivery day, output = 24 residuals.

Input:

- last `14-28` day profiles of actual price;
- last `14-28` day profiles of source/model errors;
- lag24/48/168 profiles;
- rolling 3d/7d/14d profiles;
- weather profiles for target day;
- lagged market profiles;
- current candidate profiles.

Target:

```text
y[h] = log1p(actual[h]) - log1p(overall_balanced_low_regime_pred[h])
```

Models to try in order:

1. `MultiOutputRegressor(LightGBM/Ridge/ExtraTrees)` over engineered day-profile features.
2. Small MLP over full 24-hour feature matrix.
3. TCN/GRU day-profile residual model with history `336-672h`.
4. Mixture of experts: low-day expert, rebound expert, evening expert.

Why day-profile model matters:

- 18.06 cannot be fixed hour-by-hour independently;
- h8, h11-h17, h18, h21, h24 errors are correlated by day shape;
- current code already has TCN residual model, but its production role is candidate generation, not final regime selection.

Acceptance:

- do not promote neural-alone;
- use it as one more candidate in the trust ranker first;
- only replace `overall_balanced` if it beats it on 3m/14d and both target days.

## Рекомендований шлях 4: Data Upgrade

If ranker + day-profile model still cannot pass `<13%`, the missing variable is likely fundamental system state, not model architecture.

### OREE market structure

`data/ready_for_train.csv` already contains:

- `rdn_supply`
- `rdn_demand`
- `vdr_supply`
- `vdr_demand`
- `garpok_volume`

But same-day raw values are not valid for a pre-auction forecast because they are published with or after the market result. They can be used only as:

- lagged features;
- rolling historical features;
- post-auction diagnostic mode.

If the product definition allows post-auction diagnostics, same-day OREE rows can likely reduce 18.06 materially. If the product is pre-auction forecasting, do not use them unshifted.

### ENTSO-E and generation data

Repo already has `ua_energy_scraper/` and generation-related artifacts. Next data work:

- add load/generation/renewables features if available before forecast time;
- separate solar/wind generation pressure instead of relying only on weather proxy;
- add nuclear/hydro/thermal availability or outage proxies if obtainable;
- add import/export or cross-border flow signals if available.

Priority features:

- day-ahead load forecast;
- solar generation forecast;
- wind generation forecast;
- actual generation lag24/48/168 by type;
- renewable share lag/profile;
- residual load = load - wind - solar.

This is the most plausible way to distinguish 18.06-like "morning high plus daytime collapse" days before prices are known.

### Regional weather

`forecasting_core.py` already averages regional weather. For electricity price, average can hide extremes. Add per-region features:

- Kyiv center;
- Lviv west;
- Odesa south;
- Chernihiv north;
- Donetsk east;
- min/max/std across regions;
- solar/wind weighted index by region.

Do not replace existing averaged weather; add richer features beside it.

## Тактичний варіант для 17.06

17.06 is only `190.87` UAH of total absolute error above target. If the business needs 17.06 alone below 13 quickly:

- test a narrow fallback to `anomaly_hgb_ratio_b0025_q85w025_pred`;
- or add a tiny h21/h22 lag24 evening restore, because `f_price_lag_24` was very close there.

But this should not be promoted as the main fix:

- it does not solve 18.06;
- it can hide the real regime-selection issue;
- it risks a date-specific patch with no historical evidence.

## Конкретна послідовність реалізації

### Phase 0. Lock the evaluator

Create `src/evaluate_target_days.py` that reports:

- historical all/3m/14d/13d metrics;
- daily WMAPE for arbitrary target dates;
- hourly top errors;
- regime metrics;
- cap/floor violations;
- duplicate datetimes.

Required command shape:

```powershell
python src\evaluate_target_days.py --predictions-csv output\candidate.csv --pred-col candidate_pred --target-days 2026-06-17,2026-06-18
```

This prevents optimizing only one CSV manually.

### Phase 1. Build candidate trust dataset

Create a script that expands historical rows into `(row, candidate)` training records:

```powershell
python src\build_candidate_trust_ranker.py --input-csv output\neural_best_predictions.csv --source-col overall_balanced_low_regime_pred --output-dir output
```

Outputs:

- `output/candidate_trust_training_frame.parquet` or `.csv`;
- ranker backtest predictions;
- grid of thresholds and alphas.

First success criterion:

- reduce 18.06 below `16%` without historical regression.

Second success criterion:

- reduce both 17.06 and 18.06 below `13%`.

### Phase 2. Add day-level regime probabilities

Add `src/build_day_regime_classifier.py`.

Train rolling-origin probabilities and add them to:

- historical `neural_best_predictions.csv`;
- future `prediction_YYYY-MM-DD_overall_balanced_filled.csv`.

Then rerun candidate trust ranker with regime features.

### Phase 3. Add day-profile residual candidate

Create a new candidate generator:

- `src/build_day_profile_residual_model.py`
- `src/predict_day_profile_residual_future.py`

Feed its output into candidate trust ranker, not directly into production.

### Phase 4. Fundamental data features

Use `ua_energy_scraper/` and add valid forecast-time or lagged system features.

Important rule:

- if a feature is not available before the forecast moment, it must be shifted or excluded from production mode.

### Phase 5. Integrate into future pipeline

Once a candidate passes:

- add required candidate/trust columns to `overall_balanced_required_columns()`;
- update `assemble_overall_balanced_input.py` aliases if needed;
- update `predict_overall_balanced_future.py` to prefer the new filled input;
- keep `--strict-non-null-required`;
- regenerate 17/18 comparisons.

Verification commands:

```powershell
python src\check_overall_balanced_readiness.py output\prediction_2026-06-18_overall_balanced_filled.csv --strict-non-null-required
python src\predict_overall_balanced_future.py 2026-06-17 --strict-non-null-required
python src\predict_overall_balanced_future.py 2026-06-18 --strict-non-null-required
python src\evaluate_neural_hybrid.py output\neural_best_predictions.csv --pred-col overall_balanced_low_regime_pred
```

## Чого не робити

- Не підбирати thresholds напряму під 17/18 і не називати це production.
- Не використовувати target-day raw `rdn_supply`, `rdn_demand`, `garpok_volume`, `vdr_supply`, `vdr_demand` у pre-auction режимі.
- Не приймати модель, яка покращує тільки 18.06 ціною різкого погіршення `14d/3m`.
- Не замінювати поточну canonical модель на neural-alone, доки вона не б'є `overall_balanced_low_regime_v1`.
- Не додавати широкі lag24/lag48 copy-rules для low-price daytime. Попередні нотатки показують, що такі правила можуть зруйнувати low-price режими.

## Очікуваний результат

Найімовірніший шлях до успіху:

1. `Candidate Trust Ranker` одразу опускає 17.06 нижче `13%` і суттєво зменшує 18.06.
2. `Day-Level Regime Classifier` дає відсутній сигнал для mixed rebound/collapse днів.
3. `Day-Profile Residual Model` додає сильнішого кандидата для h8/h11-h18/h21/h24 патернів.
4. Fundamental generation/load features стають fallback, якщо доступні forecast-time колонки все ще не можуть безпечно розрізнити 18.06.

Ключове: трактувати 18.06 як selector/regime проблему, а не як причину одразу відкидати сильний baseline `overall_balanced_low_regime_v1`.
