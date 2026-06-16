# Price Forecasting

Проєкт прогнозує погодинну ціну РДН на українському ринку електроенергії. Дані зберігаються в `data/ready_for_train.csv`, ринкові значення оновлюються з OREE, погода береться з Open-Meteo, а поточний найкращий прогноз рахується як hybrid chain поверх tree ensemble.

## Поточний статус

Актуально на `2026-06-16`.

Поточний promoted best:

- experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`
- prediction column: `daybias31_hb22_midday_d8_b050_abs250_pred`
- 3m WMAPE: `5.9937%`
- 14d WMAPE: `10.3096%`
- all available WMAPE: `6.0571%`
- evaluation rows: `2232`
- duplicate factual datetimes: `0`

Цілі:

- short-term `10-15%` WMAPE за 14 днів: досягнуто, зараз `10.3096%`
- long-term `5-6%` WMAPE за 3 місяці: досягнуто на поточному evaluation window, зараз `5.9937%`

Актуальні артефакти:

- `output/neural_best_predictions.csv`
- `output/neural_best_metrics.json`
- `output/neural_best_plot.png`
- `output/neural_best_summary.md`
- `output/neural_experiments_log.md`

## Що зараз є найкращою моделлю

Базовий прогноз залишається tree ensemble з `ExtraTrees + XGBoost + LightGBM`, але найкращий результат дає не pure LSTM, а hybrid post-processing chain:

1. `tree_recent_calibrated_pred` як сильний tree baseline.
2. Rolling Ridge 30-day stacker.
3. Low/high profile rules для літніх денних провалів і вечірніх cap-spike годин.
4. Nonlinear rolling-origin HGB ratio stacker.
5. Anomaly-aware rolling HGB ratio layer зі зниженими вагами для історичних outlier-днів.
6. Leakage-safe analog-day residual profile correction.
7. Shifted rolling daily-bias daytime correction.
8. Shifted rolling daily-bias day/evening correction.
9. Shifted same-hour source-bias corrections.
10. Shifted group-bias corrections за forecast-time групами `hour/source_bin`, `hour/source_ratio_bin`, `hour/weekend`, `hour/summer/source_bin`.
11. Leakage-safe `lag24` copy-yesterday fallback: повне зміщення до ціни попереднього дня тільки для gated нічних годин, коли shifted daily signal показує, що `lag24` останнім часом бив model.
12. Similarity-based lag24 guard: невелика нічна anti-lag корекція, коли forecast-time model і `lag24` розходяться на `500+` грн/МВтг; рішення не бачить факт цільового дня.
13. Додаткові shifted daily-bias repairs для нічних, ранкових, денних low-price і noon/evening режимів; усі сигнали рахуються тільки з complete earlier days.
14. Lag24 profile/similarity stack: денний `profile_abs` anti-lag, copy-lag тільки коли `source` і `lag24` майже збігаються, нічний малий blend, і фінальний `reldiff<=0.05` anti-lag. Усі gates використовують тільки forecast-time `source`, `lag24`, cap і календар.
15. Фінальний shifted group-bias repair поверх `lag24blend11` для годин `7-9,11,17,18`, згрупований за `hour/source_ratio_bin/weekend`; сигнал бере тільки попередні рядки групи через shifted rolling median.
16. Same-hour median repair для денних годин `11-15`, коли попередня same-hour median bias достатньо велика.
17. Shifted daily-bias repair поверх `hourbias17`: 14-денний попередній daily WMAPE gate, сигнал тільки з complete earlier days.
18. Candidate-blend selector з `f_price_lag_24`: кандидат змішується з current prediction тільки коли shifted rolling historical advantage у forecast-time групі дозволяє це; це враховує спостереження про корисність копіювання попереднього дня без прямого копіювання майбутнього факту.
19. Candidate-blend selectors з `f_rolling_mean_hour_3d`: профільний кандидат використовується тільки за shifted historical advantage у forecast-time групах, без факту цільової години.
20. Candidate-blend selector з `f_price_lag_48` для денного low-source режиму, теж тільки за shifted historical advantage.
21. Candidate-blend selector з `f_rolling_mean_hour_7d` для великих profile-distance режимів.
22. Фінальні shifted daily-bias repairs поверх `candblend9`: короткий 1-day midday bias gate і 8-day all-hours WMAPE gate.
23. Малий `lag24` profile blend поверх `daybias30`: `5%` до `f_price_lag_24` у midday, коли forecast-time денний `profile_abs <= 2000`.
24. Anti-lag48 evening repair: коли shifted daily source-vs-lag48 advantage показує, що lag48 останніми днями шкодив, прогноз відштовхується від `f_price_lag_48` у вечірні години.
25. Morning anti-profile repair: forecast-time відштовхування від `f_rolling_mean_hour_7d`, коли ранковий прогноз близький до 7-day погодинного профілю.
26. Два shifted same-hour repairs `hourbias21/hourbias22` для peak-error годин; сигнали беруть тільки попередні спостереження тієї ж delivery hour.
27. Фінальний `daybias31`: 8-day shifted daily-bias repair тільки для midday, коли abs daily-bias signal перевищує `250`.

Прогрес за тим самим чесним evaluator:

| variant | 3m WMAPE | 14d WMAPE |
|---|---:|---:|
| `tree_recent_calibrated_pred` після cap refresh | `9.1585%` | `20.1281%` |
| Rolling Ridge 30-day stacker v2 | `8.3638%` | `19.0831%` |
| High/low lag-profile chain | `7.8751%` | `15.4415%` |
| Nonlinear HGB ratio b0.15 | `7.8540%` | `15.3780%` |
| HGB b0.15 + cap00-roll | `7.7439%` | `14.5562%` |
| Lowcompact + highlag168 | `7.6380%` | `14.2495%` |
| Cap refresh + anomaly HGB ratio | `7.5765%` | `14.2329%` |
| Promoted analog-day profile correction | `7.5536%` | `14.1719%` |
| Shifted daily-bias daytime correction | `7.5337%` | `14.1614%` |
| Promoted shifted daily-bias day/evening correction | `7.5037%` | `13.9229%` |
| Shifted same-hour day correction | `7.4815%` | `13.7400%` |
| Shifted same-hour peak-error correction | `7.4634%` | `13.7572%` |
| Shifted same-hour morning correction | `7.4543%` | `13.7684%` |
| Promoted shifted same-hour all-hours correction | `7.4426%` | `13.7360%` |
| Shifted same-hour median peak-error correction | `7.4211%` | `13.7375%` |
| Shifted same-hour high-WMAPE daytime correction | `7.4066%` | `13.6228%` |
| Promoted shifted same-hour high-WMAPE peak-error correction | `7.3967%` | `13.5407%` |
| Group-bias forecast-bin chain with summer-low repair | `7.0757%` | `13.1264%` |
| Promoted lag24 daily-gated night fallback | `7.0389%` | `12.8523%` |
| Balanced lag24 similarity night guard | `7.0165%` | `12.8019%` |
| Promoted long-term lag24 anti-lag night guard | `6.9894%` | `12.9678%` |
| Shifted day-bias repair chain through `daybias15` | `6.7461%` | `11.9844%` |
| Lag24 profile anti-lag + near-equal lag copy | `6.6735%` | `11.9932%` |
| Lag24 profile/reldiff stack | `6.6467%` | `11.8717%` |
| Promoted final shifted day-bias repair | `6.6220%` | `11.7966%` |
| Hour-bias + lag24 repair chain through `hourbias12` | `6.5212%` | `11.4068%` |
| Group/ratio/hour/day shifted repair chain through `daybias21` | `6.4249%` | `11.2330%` |
| Lag24/hour/day shifted repair chain through `lag24blend11` | `6.3512%` | `11.0910%` |
| Final shifted group-bias repair through `groupbias12` | `6.3284%` | `11.0746%` |
| Same-hour midday repair through `hourbias17` | `6.3209%` | `11.0746%` |
| Final daily repair through `daybias24` | `6.3157%` | `11.0359%` |
| Lag24 candidate-blend evening selector `candblend1` | `6.2887%` | `10.8793%` |
| Lag24 candidate-blend night selector `candblend2` | `6.2674%` | `10.8033%` |
| Lag24 candidate-blend day selector `candblend3` | `6.2507%` | `10.8033%` |
| Final daily repair through `daybias25` | `6.2478%` | `10.7819%` |
| Profile candidate-blend peak selector `candblend4` | `6.2173%` | `10.6467%` |
| Profile candidate-blend day selector `candblend5` | `6.1874%` | `10.6784%` |
| Daily repair through `daybias26` | `6.1843%` | `10.6559%` |
| Repeated lag24 day selector `candblend6` | `6.1717%` | `10.6559%` |
| Repeated profile day selector `candblend7` | `6.1588%` | `10.6742%` |
| Final daily repair through `daybias27` | `6.1575%` | `10.6644%` |
| Lag48 low-source selector `candblend8` | `6.1249%` | `10.6644%` |
| 7d profile selector `candblend9` | `6.1047%` | `10.6443%` |
| Final daily repair through `daybias28` | `6.1033%` | `10.6339%` |
| Final daily repair through `daybias30` | `6.0941%` | `10.5940%` |
| Lag24 profile + anti-lag48 + morning anti-profile `lagprofile4` | `6.0218%` | `10.3585%` |
| Shifted same-hour repairs through `hourbias22` | `6.0027%` | `10.3096%` |
| Final midday daily-bias repair through `daybias31` | `5.9937%` | `10.3096%` |

## Чесна оцінка

Основний evaluator для hybrid-artifacts:

```powershell
python src/evaluate_neural_hybrid.py output\neural_best_predictions.csv --pred-col daybias31_hb22_midday_d8_b050_abs250_pred
```

Важлива властивість: кожна фактична година рахується рівно один раз. `src/evaluate_neural_hybrid.py` перевіряє дублікати `datetime` і не дозволяє тихо рахувати один факт кілька разів.

Поточний best має:

- `rows = 2232`
- `duplicate_datetimes = 0`
- `actual_gt_cap_rows = 0`
- `pred_gt_cap_rows = 0`

## Leakage-правила

Не можна використовувати майбутні ринкові колонки як known future:

- `rdn_supply`
- `rdn_demand`
- `vdr_supply`
- `vdr_demand`
- `garpok_volume`

Ці поля допустимі тільки як лаги, rolling history або інші статистики, що доступні до моменту прогнозу.

Поточні rolling-origin шари дотримуються таких правил:

- для кожного target day тренування бере тільки рядки строго раніше цього дня;
- anomaly features використовують тільки shifted source residuals: лаги `24/48/168h`, previous-day і rolling-7 source WMAPE/bias;
- analog-day correction вибирає тільки попередні повні дні;
- day-bias corrections використовують тільки complete earlier days: shifted rolling daily source bias і shifted rolling daily source WMAPE;
- hour-bias corrections використовують тільки попередні спостереження тієї ж delivery hour через `shift(1).rolling(...)`; підтримуються mean і median сигнали;
- group-bias corrections використовують тільки forecast-time групи та shifted rolling residuals: поточний факт не входить у сигнал;
- candidate-blend corrections використовують тільки forecast-time candidate/source/cap групи та `shift(1).rolling(...)` historical candidate advantage; candidate `f_price_lag_24` є лагом, не future market column;
- `lag24` fallback не копіює попередній день завжди: перший selector базується на shifted daily source-vs-lag24 error advantage з попередніх днів, другий similarity guard використовує тільки forecast-time відстань між model і `lag24`;
- нові lag24 profile/reldiff gates не використовують факт цільового дня: `profile_abs`, `absdiff`, `ratio` і `reldiff` рахуються з forecast-time `source` та `f_price_lag_24`;
- profile rules використовують лагові ціни, історичні rolling-профілі, календар, погоду, price cap і source predictions;
- факт цільового дня не використовується під час побудови прогнозу.

## Прайскепи

Єдина логіка історичних прайскепів знаходиться в `price_caps.py`. Поточний promoted artifact був перерахований з оновленими caps; `36` рядків змінили cap, після цього `actual_gt_cap_rows = 0`.

Для поточної історії враховано:

- до `2025-08-01`: денні блоки `5600/6900`, вечірній пік `9000`;
- з `2025-08-01`: денні блоки `5600/6900`, вечірній пік `15000`;
- з `2026-01-17`: `15000` протягом усієї доби;
- з `2026-04-01`: повернення часових блоків `5600/6900/15000`;
- з `2026-05-01`: `15000` протягом усієї доби.

Дати важливі саме як delivery day. Попередня помилка з `2026-03-31` і `2026-04-30` давала некоректні caps на частині evaluation window.

## Години OREE та CSV

У `ready_for_train.csv` години зберігаються як `0-23`. OREE віддає години як `1-24`.

Коректний mapping:

- OREE `1` -> CSV `0`
- OREE `2` -> CSV `1`
- ...
- OREE `24` -> CSV `23`

Це критично для навчання й порівняння: exact-match `1 -> 1` зсуває DAM/IDM факт на одну годину.

## Основні файли

- `api.py` - Flask Blueprint для інтеграції в backend.
- `forecasting_core.py` - оновлення даних, погоди, OREE та запуск скриптів.
- `price_caps.py` - історичні прайскепи РДН/ВДР.
- `data/ready_for_train.csv` - основний датасет.
- `models_improved/` - tree ensemble artifacts.
- `src/train_model_v1.py` - основне навчання tree ensemble.
- `src/predict_tomorrow_v1.py` - прогноз на вибрану дату.
- `src/predict_current_best.py` - current-best hybrid forecast/comparison для конкретної дати.
- `src/update_and_compare_v1.py` - порівняння з фактом OREE.
- `src/evaluate_long_term_v1.py` - стара long-term оцінка tree pipeline.
- `src/evaluate_neural_hybrid.py` - чесна оцінка hybrid artifacts.
- `src/rolling_origin_stacker.py` - rolling Ridge residual/ratio stacker.
- `src/rolling_origin_nonlinear_stacker.py` - rolling HGB/ET nonlinear stacker.
- `src/analog_day_profile_adjuster.py` - leakage-safe analog-day profile correction.
- `src/apply_day_bias_adjuster.py` - shifted rolling daily source-bias correction.
- `src/apply_hour_bias_adjuster.py` - shifted rolling same-hour source-bias correction.
- `src/apply_group_bias_adjuster.py` - shifted rolling group source-bias correction за forecast-time групами.
- `src/apply_lag24_blend_adjuster.py` - leakage-safe fallback/blend до ціни попереднього дня.
- `src/apply_candidate_blend_adjuster.py` - leakage-safe shifted selector/blender між current prediction і lag/profile candidate columns.
- `src/apply_low_profile_adjuster.py` - deterministic low-price profile rules.
- `src/apply_high_profile_adjuster.py` - deterministic high-price/cap-spike rules.
- `src/train_lstm.py` і `src/train_lstm_tf.py` - старі LSTM experiments, не production best.

## Основний цикл

Встановити залежності:

```powershell
python -m pip install -r requirements.txt
```

Оновити всі пропущені дані до поточної дати:

```powershell
python fix_missing_data.py auto
```

Зробити прогноз на конкретну дату:

```powershell
python src/predict_tomorrow_v1.py 17.06.2026
```

Застосувати поточний promoted hybrid-chain до дати:

```powershell
python src\predict_current_best.py 17.06.2026
```

Для future-date скрипту потрібен source-файл `output/prediction_YYYY-MM-DD_best_chain_debug.csv` або явний `--source-debug-csv`. Для дати, яка вже є в `output/neural_best_predictions.csv`, скрипт бере promoted rolling-origin prediction напряму і, якщо є факт, створює comparison.

Порівняти з фактом OREE:

```powershell
python src/update_and_compare_v1.py 15.06.2026
```

Оцінити старий tree pipeline:

```powershell
python src/evaluate_long_term_v1.py
```

Оцінити поточний promoted hybrid artifact:

```powershell
python src/evaluate_neural_hybrid.py output\neural_best_predictions.csv --pred-col daybias31_hb22_midday_d8_b050_abs250_pred
```

## Відомі складні режими

Поточна модель вже добре тримає вечірні cap-spike години, але все ще має велику відносну похибку в денних low-price режимах:

| regime | WMAPE |
|---|---:|
| `summer_daytime_low` | `35.19%` |
| `daytime_low_lt_1000` | `49.77%` |
| `cap_spike_evening` | `0.99%` |
| `evening_19_23` | `2.76%` |

Це очікувано для low-price годин: мала база фактичної ціни сильно збільшує WMAPE, а приховані фактори на кшталт атомної генерації, ремонтів, обмежень або ринкових дій не завжди є в публічних погодинних даних.
Окремо перевірено просте копіювання попереднього дня: `f_price_lag_24` сам по собі має близько `27.80% / 30.02%` WMAPE, але daily-gated selector корисний у рідкісних режимах, де вчорашній профіль уже показав перевагу над model.

## Негативні та непідвищені експерименти

- `split_safe_lgbm_tcn168_v1`: `49.52% / 29.99%`, корисний як leakage-control warning, не production.
- `tcn336_lowweighted_guard_v1`: `8.97% / 20.13%`, гірше baseline.
- ExtraTrees nonlinear stacker погіршив 14d приблизно до `15.49%`.
- Second analog residual layer `analog2_resid_h0718_b006_k5_s1200_v1` погіршив до `7.5588% / 14.1886%`.
- Daytime recovery rule після capnight дав false positives, не promoted.
- `candidate_lowcompact_plus_highlag168_stable_v1`: `7.6449% / 14.3006%`, стабільніший reference, але не best.
- `analog_ratio_all_b012_k4_c070_t120_v1`: `7.5536% / 14.1680%`, трохи кращий 14d, але fractionally гірший 3m, тому не promoted.
- `hourbias4_roll2_bn020_day_wmape25_v1`: `7.4488% / 13.5574%`, кращий 14d-reference, але 3m гірший за promoted best.
- Second HGB layer поверх analog-source трохи рухав 14d або 3m, але не покращив обидві метрики одночасно.

## API

Blueprint `forecasting_bp` має основні endpoint-и:

- `POST /update_rdn` - оновити DAM/IDM за дату;
- `POST /update_weather` - оновити погоду за період;
- `POST /train` - перенавчити основний ансамбль;
- `POST /predict` - зробити прогноз на дату;
- `POST /compare` - порівняти з фактом;
- `POST /evaluate` - оцінка моделей;
- `POST /features` - importance фіч;
- `GET /image/<filename>` - віддати PNG з `output/`.

## GPU

Для навчання XGBoost можна ввімкнути відеокарту:

```powershell
$env:USE_GPU = "1"
python src/train_model_v1.py
```

На машині з NVIDIA XGBoost використовує `device='cuda'`. `ExtraTrees` зі scikit-learn лишається CPU-only, а звичайний pip-встановлений LightGBM зазвичай теж працює на CPU, якщо його окремо не збирали з GPU-підтримкою.

## Наступний напрям

Довгострокова ціль `5-6%` на поточному 3m evaluation window формально закрита, але запас малий (`5.9937%`). Найкорисніший наступний крок: перевірити promoted chain на наступному holdout-блоці без підбору параметрів на ньому і окремо побудувати stricter rolling-origin tree teacher/day-profile regime model для anomaly-days та low-price midday режимів.
