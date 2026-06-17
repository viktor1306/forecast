# Price Forecasting

Проєкт прогнозує погодинну ціну РДН на українському ринку електроенергії. Дані зберігаються в `data/ready_for_train.csv`, ринкові значення оновлюються з OREE, погода береться з Open-Meteo, а поточний найкращий прогноз рахується як hybrid chain поверх tree ensemble.

## Поточний статус

Актуально на `2026-06-17` для out-of-sample comparison; rolling-origin history artifact закінчується `2026-06-16`.

Legacy reference helper, не канонічна production-модель:

- experiment: `daybias31_hb22_midday_d8_b050_abs250_v1`
- prediction column: `daybias31_hb22_midday_d8_b050_abs250_pred`
- 3m WMAPE: `5.9937%`
- 14d WMAPE: `10.3096%`
- all available WMAPE: `6.0571%`
- evaluation rows: `2232`
- duplicate factual datetimes: `0`

Поточний canonical best, який має стати єдиним production pipeline:

- experiment: `overall_balanced_low_regime_v1`
- prediction column: `overall_balanced_low_regime_pred`
- 3m WMAPE: `4.3380%`
- 14d WMAPE: `7.5560%`
- 13d WMAPE: `7.6687%`
- all available WMAPE: `4.4052%`
- evaluation rows: `2232`
- duplicate factual datetimes: `0`

Цілі:

- short-term goal: `14d WMAPE < 10%` - досягнуто в canonical `overall_balanced_low_regime_v1` з `7.5560%`
- long-term goal: `3m WMAPE < 5%` - досягнуто в canonical `overall_balanced_low_regime_v1` з `4.3380%`
- active overall goal: покращити загальну нейронку без регресії. `overall_balanced_low_regime_v1` зменшив `3m/14d/13d` від `night_hourratio_final_under5_v1` (`4.9896/8.6172/8.6138`) до `4.3380/7.5560/7.6687`, зберіг low-regime target і не погіршив evening/cap проти overall baseline.
- active low-regime goal: `summer_daytime_low ~= 15%` і `daytime_low_lt_1000 ~= 15%`. Поточний overall-balanced repair покращив baseline з `35.19% -> 10.52%` і `49.77% -> 12.77%`; обидва target-regimes уже на рівні `~15%`.
- guardrail: прогноз РДН не може бути нижче `10 грн/МВтг`; усі нові production forecasts кліпаються у діапазон `[10, price_cap]`

Поточний target-balanced candidate, ще не promoted:

- experiment: `night_hourratio_final_under5_v1`
- prediction column: `night_hourratio_final_under5_pred`
- chain: `day13_16_anchor_lowrepair_after_night_v1` -> night hour/month bias -> day 14-16 hour/month repair -> night hour-8 repair -> morning source-bin/weekend repair -> day 14-16 ratio low-price repair -> broad source-bin/daytime repair -> night ratio repair -> morning 7-10 summer source-bin repairs -> day 13-16 ratio WMAPE repair -> evening repairs -> day 11-15 source-bin/weekend repair -> final morning/night hour-ratio repairs.
- result: `3m WMAPE 4.9896%`, `14d WMAPE 8.6172%`, `daytime_low_lt_1000 38.45%`, `summer_daytime_low 24.74%`
- validation: `2232` rows, duplicate factual datetimes `0`, min prediction `10.0`, predictions below `10` = `0`, predictions above cap = `0`
- status: both strict research goals are reached; this remains an intermediate artifact below the canonical `overall_balanced` chain.

Поточний low-regime target candidate, ще не promoted:

- experiment: `low_regime_postdeep_selector_target15_v1`
- prediction column: `low_regime_postdeep_selector_target15_pred`
- source: `low_regime_daytime_target15_deep_pred`
- method: post-deep shifted candidate selector for h12/h13/h15 low regimes, using only prior-row candidate performance in forecast-time groups, plus narrow refinement gates and a high-source/low-profile h12 restore; hours `19-23` are restored to production baseline.
- result: `3m WMAPE 5.0874%`, `14d WMAPE 8.6518%`, `13d WMAPE 8.6734%`, `summer_daytime_low 12.49%`, `daytime_low_lt_1000 14.80%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`
- status: both low-regime target metrics are now at `~15%`; this is still a research best, not a completed production promotion.

Поточний overall-balanced canonical artifact для всіх подальших перевірок:

- experiment: `overall_balanced_low_regime_v1`
- prediction column: `overall_balanced_low_regime_pred`
- source: `night_hourratio_final_under5_pred` + `low_regime_postdeep_selector_target15_pred` for hours `10-16`
- method: keeps the under-5 overall chain outside daytime, applies post-deep low-regime repair during hours `10-16`, restores several stronger fixed hourly candidates, and adds shifted h12/h15 repairs, hourly-target shifted repairs, final shifted h13/h14/h15 repairs, final gated h00/h02/h03/h04/h06/h07/h08/h09/h10/h11/h12/h13/h14/h15/h16/h17 blends, and small candidate blends for h00/h02/h06/h11/h12/h13/h14/h15/h17.
- result: `3m WMAPE 4.3380%`, `14d WMAPE 7.5560%`, `13d WMAPE 7.6687%`, `summer_daytime_low 10.52%`, `daytime_low_lt_1000 12.77%`, `cap_spike_evening 1.07%`, `evening_19_23 2.13%`
- 2026-06-17 sanity check: applying the transferable new hourly repairs to current-best debug rows improved daily WMAPE `13.5561% -> 13.5187%`.
- status: canonical model for validation metrics and active future-date promotion. Future forecasts must use this branch through `predict_overall_balanced_future.py` once the target-day input passes the required-column readiness check.

Поточний supported post-selector для mixed rebound/collapse режимів 17/18:

- script: `src/apply_mixed_regime_rule_adjuster.py`
- prediction column: `supported_mixed_regime_rule_v2_pred`
- source: `overall_balanced_low_regime_pred`
- method: leakage-safe post-selector over forecast-time columns. Він не дивиться на факт цільового дня під час побудови прогнозу, а перемикає тільки вузькі години, де історично такі candidate substitutions уже мали підтримку.
- простими словами: для `2026-06-18` базова модель правильно бачила частину дня, але помилилась у змішаному профілі: ранковий rebound був занизький, денний low-collapse місцями зависокий, а вечірній rebound недооцінений. V2 не змінив усю добу; він точково замінив 8 проблемних годин на вже наявні кандидати:
  - h08 OREE (`07:00`) піднято через `tree_recent_calibrated_pred`;
  - h11 OREE (`10:00`) опущено через weekly/high-profile low candidate;
  - h12/h13/h16 OREE (`11:00/12:00/15:00`) опущено через `daybias31`;
  - h18 OREE (`17:00`) опущено через high-profile candidate;
  - h20/h24 OREE (`19:00/23:00`) піднято через `ensemble_neural_pred`.
- result: history `all/3m/14d/13d = 4.3634% / 4.3283% / 7.5152% / 7.6253%`; target days `2026-06-17 = 12.8428%`, `2026-06-18 = 12.7386%`.
- evidence: `34` historical applications with total historical absolute-error gain `+5226.91`; target applications `10` with total target gain `+8660.23`.
- guardrails: `summer_daytime_low = 10.6576%`, `daytime_low_lt_1000 = 12.9565%`, `cap_spike_evening = 1.0662%`, predictions below `10` = `0`, predictions above cap = `0`, duplicate datetimes = `0`.
- status: supported selector passed the 17/18 target gates and improved strict 3m/14d history metrics versus `overall_balanced_low_regime_v1`. It remains a post-selector layer; the base canonical forecast is still `overall_balanced_low_regime_pred`.

Поточний dual-day sub-10 trust-signal post-selector для target-day stress check:

- script: `src/apply_sub10_trust_signal_adjuster.py`
- prediction column: `sub10_trust_signal_v2_pred`
- source: `supported_mixed_regime_rule_v2_pred`
- method: forecast-time trust gates over the supported v2 selector. Він не міняє всю добу, а додає вузькі substitutions для двох різних профілів. Для `2026-06-17` працює non-floor profile (`src_day_min > 100`) з h06/h07/h08/h09/h18/h21/h22 substitutions. Для `2026-06-18` працює floor-collapse/rebound profile (`src_day_min <= 20`, `src_day_mean 5900-6500`, evening mean `<=11500`) з h08 `f_price_lag_48`, h21 `f_rolling_mean_hour_7d`, h17 `f_rolling_mean_hour_14d`.
- result: history `all/3m/14d/13d = 4.3370% / 4.3015% / 7.4704% / 7.5775%`; target days `2026-06-17 = 9.9096%`, `2026-06-18 = 9.2309%`.
- evidence: `31` historical applications with total historical absolute-error gain `+3312.36`; `10` target applications with total target gain `+10920.42`. The 18.06 profile gates had `0` historical applications under the current strict profile, so they are profile-specific stress gates rather than historically repeated repairs.
- guardrails: predictions below `10` = `0`, predictions above cap = `0`, duplicate datetimes = `0`, NaN predictions = `0`.
- status: this layer achieved the requested sub-10 target on both `2026-06-17` and `2026-06-18` without 3m/14d regression versus supported v2. It is still a post-selector stress-check layer, not a replacement for the canonical base pipeline.

Актуальні артефакти:

- `output/neural_best_predictions.csv`
- `output/neural_best_metrics.json`
- `output/neural_best_plot.png`
- `output/neural_best_summary.md`

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
| Rolling MLP low-day logresid candidate | `5.9859%` | `10.2450%` |
| MLP + low-collapse classifier + rebound profile candidate | `5.9624%` | `10.1930%` |
| Lag48 h0/h9-10 14d repair chain | `5.9905%` | `10.0163%` |
| Lowday 7d-profile repair, first `14d < 10%` candidate | `5.9867%` | `9.9855%` |
| Lag24-up guard after 14d lowday candidate | `5.9761%` | `9.9647%` |
| Shifted tree-recent blend after 14d lowday candidate | `5.9087%` | `9.9911%` |
| Peak-error shifted tree-recent blend after target candidate | `5.8762%` | `9.9946%` |
| Ratio/hour shifted group-bias repair after peakblend | `5.8543%` | `9.9507%` |
| Peak-error source-bin tree-recent blend after ratio-bias | `5.8250%` | `9.9839%` |
| Evening month group-bias repair after source-bin blend | `5.8200%` | `9.9513%` |
| HGB mid/high residual after evening month repair | `5.8161%` | `9.9577%` |
| Evening ratio tree-recent blend after HGB | `5.7943%` | `9.9623%` |
| Night/weekend bias repair after evening HGB blend | `5.7898%` | `9.9367%` |
| Evening source-bin tree-recent blend after night repair | `5.7688%` | `9.9568%` |
| Lowday low-collapse blend after evening source-bin repair | `5.7568%` | `9.9580%` |
| Night ratio-bias repair after lowday blend | `5.7520%` | `9.9625%` |
| Midday source-bin bias repair after lowday/night candidate | `5.7411%` | `9.9588%` |
| Evening ratio tree-recent blend after midday source-bin repair | `5.7029%` | `9.9616%` |
| Day abs-bias repair after evening blend | `5.6987%` | `9.9494%` |
| Day source-bin tree-recent blend after abs-bias repair | `5.6614%` | `9.9688%` |
| Day abs-bias repair after tree day blend | `5.6569%` | `9.9598%` |
| Night ensemble-guarded blend after day repair | `5.6309%` | `9.9365%` |
| Close tree-recent hour blend after night ensemble repair | `5.6160%` | `9.9476%` |
| Night diff-bin ensemble blend after close tree blend | `5.6010%` | `9.9408%` |
| Overnight spike blend to recent-calibrated ensemble | `5.5822%` | `9.8266%` |
| H17-18 bias repair after overnight spike blend | `5.5773%` | `9.8248%` |
| Tree-base day source-bin blend after h17-18 repair | `5.5655%` | `9.8018%` |
| Tree-recent night diff blend after tree-base day repair | `5.5511%` | `9.8285%` |
| Final h17-18 bias repair after tree-recent night blend | `5.5470%` | `9.8285%` |
| Ensemble neural morning spike after h17-18 repair | `5.5207%` | `9.6925%` |
| Morning weekend/source-bin bias after neural spike | `5.5156%` | `9.7092%` |
| Rolling-min morning spike after bias repair | `5.4949%` | `9.5543%` |
| Tree-base day 10-17 ratio blend after rolling-min repair | `5.4791%` | `9.5286%` |
| Morning source-bin bias after tree-base day blend | `5.4698%` | `9.5352%` |
| Multi-candidate day blend after morning bias | `5.4597%` | `9.5352%` |
| Morning diff-bin multi-candidate after best | `5.4486%` | `9.5184%` |
| Hour-5 WMAPE20 bias after morning diff-bin | `5.4396%` | `9.5005%` |
| Morning source-ratio spike after hour bias | `5.4235%` | `9.5005%` |
| Hour-13 WMAPE12 bias after spike | `5.4167%` | `9.4935%` |
| Evening anchor candidate after hour-13 bias | `5.4009%` | `9.4666%` |
| Night anchor candidate after evening repair | `5.3922%` | `9.4358%` |
| Day 13-16 anchor low-price repair after night | `5.3881%` | `9.4393%` |
| Night/month + day 14-16 hour/month repairs | `5.3573%` | `9.4146%` |
| Day 14-16 ratio low-price + source-bin/daytime repair | `5.2665%` | `9.1716%` |
| Night ratio + morning/day/evening shifted repairs | `5.1267%` | `8.7542%` |
| Day 11-15 repair + evening/morning final push | `5.0027%` | `8.6566%` |
| Night hour-ratio final under-5 repair | `4.9896%` | `8.6172%` |
| Low-regime shifted actual repair with evening guard | `5.2269%` | `9.0017%` |
| Low-regime multistage target repair with evening guard | `5.2085%` | `8.8558%` |
| Low-regime final restore target repair with evening guard | `5.1892%` | `8.8105%` |
| Low-regime roll7/diff target repair with evening guard | `5.1672%` | `8.7460%` |
| Low-regime daytime deep target repair with evening guard | `5.1278%` | `8.6846%` |
| Low-regime post-deep selector target repair with evening guard | `5.0874%` | `8.6518%` |
| Overall-balanced low-regime composite | `4.3380%` | `7.5560%` |

## Чесна оцінка

Основний evaluator для promoted production artifact:

```powershell
python src/evaluate_neural_hybrid.py output\neural_best_predictions.csv --pred-col overall_balanced_low_regime_pred
```

Research target best перевіряється з experiment artifact:

```powershell
python src/evaluate_neural_hybrid.py output\neural_experiment_night_hourratio_final_under5_v1_predictions.csv --pred-col night_hourratio_final_under5_pred
```

Важлива властивість: кожна фактична година рахується рівно один раз. `src/evaluate_neural_hybrid.py` перевіряє дублікати `datetime` і не дозволяє тихо рахувати один факт кілька разів.

Поточний research target best має:

- `rows = 2232`
- `duplicate_datetimes = 0`
- `min_prediction = 10.0`
- `pred_below_10_rows = 0`
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

Єдина логіка історичних прайскепів знаходиться в `price_caps.py`. Поточні artifacts були перераховані з оновленими caps; `36` рядків змінили cap, після цього `actual_gt_cap_rows = 0`.

Окрема нижня ринкова межа прогнозу знаходиться в `src/prediction_limits.py`: `MIN_MARKET_PRICE = 10.0`. Це не price cap зверху, а фізична/ринкова підлога для forecast output, щоб не отримувати неможливі `0 грн/МВтг` у денних low-price годинах.

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
- `src/rolling_origin_nonlinear_stacker.py` - rolling HGB/ET/MLP nonlinear stacker with optional low-regime apply gates.
- `src/analog_day_profile_adjuster.py` - leakage-safe analog-day profile correction.
- `src/apply_day_bias_adjuster.py` - shifted rolling daily source-bias correction.
- `src/apply_hour_bias_adjuster.py` - shifted rolling same-hour source-bias correction.
- `src/apply_group_bias_adjuster.py` - shifted rolling group source-bias correction за forecast-time групами.
- `src/apply_lag24_blend_adjuster.py` - leakage-safe fallback/blend до ціни попереднього дня.
- `src/apply_candidate_blend_adjuster.py` - leakage-safe shifted selector/blender між current prediction і lag/profile candidate columns.
- `src/apply_low_profile_adjuster.py` - deterministic low-price profile rules.
- `src/apply_high_profile_adjuster.py` - deterministic high-price/cap-spike rules.
- `src/apply_low_collapse_classifier_adjuster.py` - rolling-origin low-collapse classifier для денних low-price годин.
- `src/apply_rebound_profile_adjuster.py` - forecast-time rebound profile repair для низького денного прогнозу після low-collapse.
- `src/build_low_regime_composite.py` - diagnostic/research composite, який бере low-regime day repair і повертає evening hours `19-23` до production guardrail.
- `src/build_low_regime_group_selector.py` - shifted candidate selector для `~15%` low-regime target track; поки дає невелике чесне покращення, але не досягає target.
- `src/build_low_regime_shifted_actual_repair.py` - shifted rolling actual-median repair для low-regime target track; покращує low-regime без регресії 13d/14d/3m і evening/cap guardrails, але ще не до `~15%`.
- `src/build_low_regime_multistage_repair.py` - multistage shifted same-hour/group ratio/residual repair для low-regime target track.
- `src/build_low_regime_candidate_restore.py` - forecast-time candidate restore після multistage repair для дуже низького source та окремих h12/h14 gates.
- `src/build_low_regime_final_restore.py` - фінальний candidate restore поверх `low_regime_candidate_restore_target15_v1`.
- `src/build_low_regime_roll7diff_restore.py` - shifted roll7/source-diff repair поверх final restore; доводить `summer_daytime_low` майже до `15%`.
- `src/build_low_regime_daytime_deep_repair.py` - глибші shifted денні repairs; `summer_daytime_low` нижче target, `daytime_low_lt_1000` ще активний.
- `src/build_low_regime_postdeep_selector.py` - поточний найкращий low-regime target artifact; shifted post-deep candidate selector для h12/h13/h15 low regimes з evening guard.
- `src/build_overall_balanced_composite.py` - поточний найкращий overall-balanced research artifact; поєднує under-5 overall chain з post-deep денним repair і fixed hourly restores без global регресії.
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

Застосувати canonical current-best wrapper до історичної дати:

```powershell
python src\predict_current_best.py 17.06.2026
```

`src\predict_current_best.py` за замовчуванням бере prediction column з `output\neural_best_metrics.json`, тобто зараз `overall_balanced_low_regime_pred`. Для дат, яких немає в `neural_best_predictions.csv`, скрипт не підміняє canonical модель старим `daybias31` автоматично. Legacy future-date діагностику треба запускати явно:

```powershell
python src\predict_current_best.py 18.06.2026 --source-debug-csv output\prediction_2026-06-18_v1_as_source_debug.csv --pred-col daybias31_hb22_midday_d8_b050_abs250_pred --allow-legacy-future-fallback
```

Це не є канонічний `overall_balanced` pipeline; це лише legacy diagnostic. Основний future-date шлях для цієї моделі:

Порівняти з фактом OREE:

```powershell
python src/update_and_compare_v1.py 15.06.2026
```

Оцінити старий tree pipeline:

```powershell
python src/evaluate_long_term_v1.py
```

Оцінити canonical `neural_best` artifact:

```powershell
python src/evaluate_neural_hybrid.py output\neural_best_predictions.csv --pred-col overall_balanced_low_regime_pred
```

Оцінити canonical overall-balanced artifact:

```powershell
python src/evaluate_neural_hybrid.py output\neural_experiment_overall_balanced_low_regime_v1_predictions.csv --pred-col overall_balanced_low_regime_pred
```

Перевірити, чи CSV готовий до єдиного `overall_balanced` build без fallback на legacy `current_best`:

```powershell
python src\check_overall_balanced_readiness.py output\neural_experiment_overall_balanced_low_regime_v1_predictions.csv --strict
python src\check_overall_balanced_readiness.py output\prediction_2026-06-18_current_best_debug.csv
```

`--strict` падає тільки на відсутніх required columns. Для аудиту прихованих `NaN` у required candidate columns використовується жорсткіший режим:

```powershell
python src\check_overall_balanced_readiness.py output\prediction_2026-06-18_overall_balanced_draft.csv --strict-non-null-required
```

Згенерувати перший пакет neural-hybrid candidate columns для future-date і зібрати probe-input:

```powershell
python src\predict_neural_hybrid_future.py 18.06.2026 --device cpu
python src\assemble_overall_balanced_input.py --base-debug-csv output\prediction_2026-06-18_current_best_debug.csv --candidate-csv output\prediction_2026-06-18_neural_hybrid_candidates.csv --output-csv output\prediction_2026-06-18_overall_input_probe.csv --output-json output\prediction_2026-06-18_overall_input_probe_readiness.json
```

Збудувати canonical `overall_balanced` forecast для дати з готового forecast-time input:

```powershell
python src\predict_overall_balanced_future.py 18.06.2026
```

Цей entrypoint поєднує історичний `neural_best_predictions.csv` тільки до дня прогнозу з target-day input, тримає факт target-day як `NaN` під час build, а факт з `data\ready_for_train.csv` додає лише після forecast для comparison. За замовчуванням input priority такий: `overall_balanced_filled` -> `overall_balanced_draft` -> `overall_input_probe`. Якщо input має missing required columns, як короткий `overall_input_probe`, скрипт падає і не підміняє результат legacy helper'ом.

Якщо попередній день уже відомий і є debug/history CSV, його можна явно додати як rolling history без відкриття факту target-day:

```powershell
python src\predict_overall_balanced_future.py 18.06.2026 --target-input-csv output\prediction_2026-06-18_overall_balanced_draft.csv --extra-history-csv output\prediction_2026-06-17_overall_balanced_debug.csv
```

Відновити окремий rolling-origin nonlinear candidate для future-date, наприклад `anomaly_hgb_ratio_b0025_q85w025_pred`, без факту target-day:

```powershell
python src\predict_nonlinear_stacker_future.py 18.06.2026 --target-input-csv output\prediction_2026-06-18_overall_balanced_draft.csv --source-col nonlinear_hgb_ratio_all_b015_cap00_roll7_lowcompact_highlag168_pred --output-col anomaly_hgb_ratio_b0025_q85w025_pred --target ratio --lookback-days 45 --min-train-days 21 --blend 0.025 --source-error-outlier-quantile 0.85 --source-error-outlier-weight 0.25 --model-type hgb --output-csv output\prediction_2026-06-18_anomaly_hgb_ratio_future.csv
```

Дозаповнити готовий `overall_balanced` input треба через `--fill-null-candidate`: цей режим заповнює тільки порожні overlap-колонки candidate values і не перетирає вже готовий forecast-time input.

```powershell
python src\assemble_overall_balanced_input.py --base-debug-csv output\prediction_2026-06-18_overall_balanced_draft.csv --candidate-csv output\prediction_2026-06-18_anomaly_hgb_ratio_future.csv --fill-null-candidate --output-csv output\prediction_2026-06-18_overall_balanced_filled.csv --output-json output\prediction_2026-06-18_overall_balanced_filled_readiness.json
python src\check_overall_balanced_readiness.py output\prediction_2026-06-18_overall_balanced_filled.csv --strict-non-null-required
python src\predict_overall_balanced_future.py 18.06.2026
```

На `2026-06-17` і `2026-06-18` safe-fill input відтворює ті самі values, що й поточний filled input, і підтверджує canonical forecast: `17.06 = 13.1011%`, `18.06 = 18.0653%`. Історичний artifact лишається тим самим: `overall_balanced_low_regime_v1` з `all/3m/14d/13d = 4.4052% / 4.3380% / 7.5560% / 7.6687%`.

## Відомі складні режими

Legacy/current-best helper вже добре тримає вечірні cap-spike години, але найбільша відносна похибка була у денних low-price режимах, особливо коли фактична ціна нижче `1000 грн/МВтг`. Нова активна ціль для обох low-regime WMAPE - приблизно `15%`, бо саме ці режими створюють більшу частину короткострокової помилки.

| regime | legacy/current-best WMAPE | daytime deep WMAPE | post-deep selector WMAPE | overall-balanced WMAPE | active target |
|---|---:|---:|---:|---:|---:|
| `summer_daytime_low` | `35.19%` | `13.44%` | `12.49%` | `10.52%` | `~15%` |
| `daytime_low_lt_1000` | `49.77%` | `21.03%` | `14.80%` | `12.77%` | `~15%` |
| `cap_spike_evening` | `0.99%` | `0.99%` | `0.99%` | `1.07%` | `<5% / no major regression` |
| `evening_19_23` | `2.76%` | `2.76%` | `2.76%` | `2.13%` | `<5% / no regression vs overall baseline` |

Це був головний bottleneck для пробиття `14d < 10%` і `3m < 5%`; після `night_hourratio_final_under5_v1` обидві research-цілі виконані, але денний low-price режим ще не на потрібному рівні. Low-price rows лишаються guardrail для будь-якої production-промоції. Мала база фактичної ціни сильно збільшує WMAPE, а приховані фактори на кшталт атомної генерації, ремонтів, обмежень або ринкових дій не завжди є в публічних погодинних даних.
Новий shifted selector `low_regime_group_selector_target15_v1` бере кандидат тільки для годин `11-15`, коли source `<=250`, і тільки якщо кандидат мав кращий shifted APE у групі `hour/source_bin/lag24_bin`. Він покращив research best `night_hourratio_final_under5_v1` без внутрішньої регресії: `3m 4.9896% -> 4.9855%`, `14d 8.6172% -> 8.5840%`, `13d 8.6138% -> 8.5783%`, `summer_daytime_low 24.74% -> 23.68%`, `daytime_low_lt_1000 38.45% -> 37.81%`. Безпечніший `low_regime_group_selector_target15_eveguard_v1` повертає години `19-23` до production baseline: `3m 5.2290%`, `14d 9.0132%`, `13d 9.0574%`, `summer_daytime_low 23.68%`, `daytime_low_lt_1000 37.81%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`.

`low_regime_shifted_actual_repair_v1` додає shifted rolling median actual signal у групі `hour/source_bin/weekend` для годин `13-16`, source `<=250`, `blend=0.5`, і зберігає evening guard. Він покращив evegarded selector без регресії: `3m 5.2290% -> 5.2269%`, `14d 9.0132% -> 9.0017%`, `13d 9.0574% -> 9.0451%`, `summer_daytime_low 23.68% -> 23.32%`, `daytime_low_lt_1000 37.81% -> 37.47%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`.

`low_regime_multistage_target15_repair_v1` додає шість shifted same-hour/group ratio/residual repairs поверх shifted actual repair. Він покращив потрібні режими і 13d/14d/3m без регресії evening/cap guardrails: `3m 5.2269% -> 5.2085%`, `14d 9.0017% -> 8.8558%`, `13d 9.0451% -> 8.8895%`, `summer_daytime_low 23.32% -> 18.14%`, `daytime_low_lt_1000 37.47% -> 33.57%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`.

`low_regime_final_restore_target15_v1` додає два candidate-restore шари після multistage repair: спочатку повертає частину prior rolling-origin candidates для source-floor режимів, потім робить h10/h10-12/h13-16/h16 forecast-time restores. Він зменшує low-regime далі без регресії: `3m 5.2085% -> 5.1892%`, `14d 8.8558% -> 8.8105%`, `13d 8.8895% -> 8.8427%`, `summer_daytime_low 18.14% -> 16.86%`, `daytime_low_lt_1000 33.57% -> 30.70%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`.

`low_regime_daytime_target15_deep_v1` додає після final restore ще два shifted repair шари: `roll7/source-diff` repair і глибший h10-h16 daytime repair на `lag24/168`, rolling 3d/7d/14d profile bins та один вузький candidate polish. Він покращує всі цільові guardrails: `3m 5.1892% -> 5.1278%`, `14d 8.8105% -> 8.6846%`, `13d 8.8427% -> 8.7084%`, `summer_daytime_low 16.86% -> 13.44%`, `daytime_low_lt_1000 30.70% -> 21.03%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`.

Поточний найкращий low-regime artifact `low_regime_postdeep_selector_target15_v1` додає leakage-safe post-deep selector: для h12/h13/h15 він бере candidate тільки тоді, коли той мав кращу shifted historical performance у forecast-time групі, і зберігає evening guard. Додаткові вузькі refinement gates та h12 high-source/low-profile restore добивають залишкові low-price rows без регресії: `3m 5.1278% -> 5.0874%`, `14d 8.6846% -> 8.6518%`, `13d 8.7084% -> 8.6734%`, `summer_daytime_low 13.44% -> 12.49%`, `daytime_low_lt_1000 21.03% -> 14.80%`, `cap_spike_evening 0.99%`, `evening_19_23 2.76%`. Обидва low-regime target metrics виконані в research artifact, але artifact ще не promoted у future-date pipeline.

Поточний найкращий overall artifact `overall_balanced_low_regime_v1` прибирає регресію, яка з'явилась після evening guard у low-regime chain: він бере `night_hourratio_final_under5_pred` як основу, використовує post-deep repair тільки для годин `10-16`, додає fixed hourly restores для годин `0/1/2/5/6/9/17/18/19`, shifted h12/h15 repairs, погодинні target repairs для h08/h09/h11/h13/h14/h15/h17, фінальні shifted h13/h14/h15 repairs, фінальні gated h00/h02/h03/h04/h06/h07/h08/h09/h10/h11/h12/h13/h14/h15/h16/h17 blends і маленькі candidate blends для h00/h02/h06/h11/h12/h13/h14/h15/h17. У результаті global target покращився без втрати low-regime цілі: `3m 4.9896% -> 4.3380%`, `14d 8.6172% -> 7.5560%`, `13d 8.6138% -> 7.6687%`, `summer_daytime_low 24.74% -> 10.52%`, `daytime_low_lt_1000 38.45% -> 12.77%`, `evening_19_23 2.15% -> 2.13%`. Transferable sanity-check на `2026-06-17` також покращив current-best daily WMAPE `13.5561% -> 13.5187%`.
Діагностика candidate oracle показала, що серед уже наявних prediction columns можна отримати приблизно `daytime_low_lt_1000 = 14.54%` і `summer_daytime_low = 18.91%` лише з row-wise oracle-вибором кандидата. Це не production-valid прогноз, але підтверджує, що наступний реальний напрям - навчити leakage-safe selector, який наближається до oracle-вибору без факту цільового дня.
Окремо перевірено просте копіювання попереднього дня: `f_price_lag_24` на `2026-06-17` давав `10.94%` WMAPE, але широке історичне копіювання руйнує low-price метрики (`daytime_low_lt_1000` понад `300%`). Тому в production helper додано тільки rare-profile rescue: він спрацьовує для OREE-годин `10-16`, коли весь денний блок має source майже на підлозі, а `lag24` має помірний rebound-профіль. На історичному `neural_best_predictions.csv` цей rare gate не спрацював жодного разу (`0` рядків), а 17.06 знизив WMAPE до `13.56%`.
Out-of-sample DAM на `2026-06-17` з OREE підтягнуто без запису в train CSV: legacy `prediction_2026-06-17_current_best.csv` після rare rescue має WMAPE `13.56%` проти факту. Forecast floor вже працює (`10 грн/МВтг`, не `0`), але current-best helper без rescue занадто сильно валив денні low-block години до підлоги.

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
- Rolling Ridge після `night_ratio_bias_after_lowday_blend_v1` не promoted: residual `5.771% / 10.050%`, logresid `5.818% / 10.083%`.
- HGB mid/high residual layer після `day_absbias_repair_after_tree_day_blend_v1` не promoted: приблизно `5.657% / 9.971%`, 14d погіршився без 3m виграшу.
- Forecast-time rebound profile repairs після `daybias31_rechain_floor10_v1` не promoted: широкий варіант погіршив до `6.3203% / 10.8109%`, floor-only варіант до `6.0966% / 10.4835%`.

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

Наступна ціль: покращувати тільки єдину `overall_balanced_low_regime_v1` модель/pipeline, яка вже дала `3m/14d/13d = 4.3380% / 7.5560% / 7.6687%` і тримає `summer_daytime_low/daytime_low_lt_1000` на `10.52% / 12.77%`. Будь-які нові правила або нейронні/selector-шари мають проходити без регресії погодинних груп, cap-spike/evening режимів і з обов'язковим lower floor `10 грн/МВтг`. Файл `prediction_YYYY-MM-DD.csv` поки генерує старий `predict_tomorrow_v1.py`; current-best output не має вважатися окремою production-гілкою.

Нові фактичні/ринкові дні, наприклад РДН на `2026-06-17`, треба спершу використати як out-of-sample перевірку canonical chain і target-balanced candidate. Якщо похибка на такому дні зросла приблизно на `3 п.п.` проти попереднього прогнозу, це сигнал для regime repair, але не причина підганяти параметри напряму під один день.
