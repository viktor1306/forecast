# План покращення нейронної моделі

Дата аналізу: 16.06.2026

Мета:

- довгий період: вийти приблизно на `5-6%` WMAPE;
- короткий період: вийти приблизно на `10-15%` WMAPE;
- не погіршити коректність даних після виправлення мапінгу годин OREE `1-24` -> CSV `0-23`.

Цей файл є тільки аналітичним планом. Код моделей і тренування не змінювались.

## Поточний стан

Поточна правильна tree-модель після виправлення годин і retrain:

- `3 місяці`: `9.01%` WMAPE;
- `14 днів`: `20.09%` WMAPE;
- base без short-term калібраторів: `10.45% / 31.33%`;
- прогноз проти факту за `15.06.2026`: `28.58%` WMAPE, MAE `1716.07 грн/МВт·год`.

Старі результати з `result/study.txt`:

- найкращий tree ensemble взимку: `6.54-6.69%` за 3 місяці і `15.45-15.55%` за 14 днів;
- найкраща LSTM у старих експериментах: `14.71%` за 14 днів, але `19.79%` за 3 місяці;
- тобто LSTM вже вміла ловити короткий зимовий профіль, але не була стабільною на довгому періоді.

Висновок: ціль `5-6% / 10-15%` реалістичніше досягати не чистою LSTM, а hybrid-підходом:

- tree ensemble лишається сильним базовим прогнозом;
- нейронка вчиться виправляти residual/ratio помилки tree-моделі;
- окремі голови моделі вчаться low-price і cap-spike режимам.

## Стан даних

Після останнього оновлення:

- рядків у `ready_for_train.csv`: `21575`;
- фактичних `rdn_price`: `21551`;
- майбутніх рядків без факту: `24` на `17.06.2026`;
- останній фактичний час: `16.06.2026 23:00`;
- після `generate_features()` для навчання: `21551` рядок, `137` колонок;
- inf у числових фічах не знайдено.

Пропуски у важливих колонках:

- `rdn_price`: `24`, це майбутній день;
- `rdn_supply`, `rdn_demand`, `garpok_volume`: `24`, це майбутній день;
- `vdr_supply`, `vdr_demand`: `72`, бо IDM/VDR не завжди віддається OREE одразу;
- погода (`feelslike`, `windspeed`, `windgust`, `cloudcover`, `solarradiation`, `uvindex`) заповнена.

Важливий принцип для нейронки: майбутні `rdn_supply`, `rdn_demand`, `vdr_supply`, `vdr_demand`, `garpok_volume` не можна вважати відомими на момент прогнозу. Їх можна використовувати тільки як лаги (`lag_24`, `lag_48`, `lag_168`) або як статистики минулих днів.

## Літній режим

Останні дні показують два різні літні сценарії:

- денний провал: години `10-16` падають до сотень або навіть десятків грн/МВт·год;
- вечірній cap-spike: години `19-23` можуть доходити до `14000-15000`.

За останні 30 фактичних днів кореляція денного середнього з локальним київським вітром не стабільна:

- `wind_day`: приблизно `-0.28`;
- `solar_day`: приблизно `-0.12`;
- `cloud_day`: приблизно `0.12`;
- `min price`: приблизно `0.95`.

Це означає, що локальна погода сама по собі не пояснює режим. Потрібні:

- лаги цінового профілю;
- лаги ринку;
- погодні взаємодії `wind * cloud`, `solar * hour`, `solar * summer`;
- окремий low/high regime head.

## Проблеми існуючих neural-скриптів

### `src/train_lstm.py`

Плюси:

- PyTorch;
- GPU використовується автоматично;
- є multi-horizon вихід на `24` години;
- ціль у вигляді residual від `price_lag_24` є хорошою ідеєю.

Проблеми:

- модель бачить тільки минулі `48` годин, але не отримує відомі майбутні коверіати на наступні `24` години: погоду, календар, прайскепи;
- усі числові колонки беруться автоматично, тому легко випадково змішати чесні лаги і нечесні поточні ринкові значення;
- оцінка concatenates усі overlapping 24-годинні прогнози, через це одна і та сама фактична година може рахуватись багато разів;
- early stopping дивиться на test loader, тобто тест використовується як validation;
- split `30 * 24 * test_months` не збігається з calendar-month логікою `evaluate_long_term_v1.py`;
- немає price-cap regime, DST, day-profile і літніх regime-фіч із `train_model_v1.py`.

### `src/train_lstm_tf.py`

Проблеми:

- scaler_X і scaler_y fit-яться на всьому датасеті до split, це leakage;
- модель фактично MLP із `Flatten`, хоча файл називається LSTM;
- test sequences створюються тільки всередині test частини, без контексту останніх train-годин;
- частина фіч у списку не існує і просто відфільтровується;
- оцінюється лише 14 днів, немає чесного 3-місячного порівняння.

### `src/evaluate_full_system.py`

Проблеми:

- очікує стару папку `models_lstm_torch`;
- архітектура і scaler-и мають збігатися з попереднім навчанням, але це не гарантовано;
- це радше legacy evaluator, не база для нової neural-моделі.

## Основна гіпотеза

Чиста LSTM не повинна бути головною моделлю. Для цього датасету даних мало: близько `21.5k` погодинних точок, а режимів багато.

Найкращий шанс:

1. Зберегти tree ensemble як teacher/baseline.
2. Нейронку навчати не прогнозувати всю ціну з нуля, а прогнозувати поправку:
   - `actual_price - tree_pred`;
   - або `log1p(actual_price) - log1p(tree_pred)`;
   - або `actual_ratio - tree_ratio`.
3. Додати multi-task heads:
   - regression head для ціни/ratio;
   - classifier head для very-low price (`<500`, `<1000`);
   - classifier head для high/cap price (`>14000`);
   - optional quantile heads `p10/p50/p90`.

Так нейронка фокусується на тому, де tree-модель помиляється: літній день і cap-spike вечір.

## Рекомендована архітектура V1

Назва: `NeuralResidualDayModel`

Вхід:

- encoder history: останні `168` або `336` годин;
- decoder future: наступні `24` години відомих наперед фіч.

Encoder features:

- `target_ratio`, `rdn_price`, `price_cap`;
- `price_lag_24`, `price_lag_48`, `price_lag_168`;
- same-hour rolling: `3d`, `7d`, `14d`;
- lagged market: `supply_lag_*`, `demand_lag_*`, `vdr_supply_lag_*`, `garpok_lag_*`;
- weather history;
- missing flags для VDR/IDM.

Future decoder features:

- `hour_sin`, `hour_cos`;
- `day_sin`, `day_cos`, `week_sin`, `week_cos`;
- `month`, `is_summer`, `is_weekend`, `is_off_day`;
- `price_cap`, `price_cap_norm`, cap-regime flags;
- future weather: `feelslike`, `windspeed`, `windgust`, `winddir_sin/cos`, `cloudcover`, `solarradiation`, `uvindex`, `precip`;
- engineered renewable pressure:
  - `solar_summer_interaction`;
  - `solar_hour_interaction`;
  - `wind_cloud_interaction`;
  - `windgust_hour_interaction`;
  - `renewable_pressure_index = solar * (1 - cloudcover/100) + windspeed * k`.

Backbone:

- почати з TCN/dilated Conv1D, не Transformer;
- hidden `64-128`;
- dropout `0.10-0.25`;
- LayerNorm;
- residual skip від tree/base forecast.

Чому TCN:

- менше параметрів, ніж Transformer;
- добре ловить лаги `24/48/168`;
- швидше тренується на GPU;
- менше ризику overfit на `21k` рядків.

Альтернатива:

- GRU encoder + decoder MLP на future covariates;
- N-BEATS/N-HiTS style day-profile residual;
- MLP/TabNet/FT-Transformer тільки як residual model по engineered features, без sequence.

## Target

Не варто навчати тільки raw price.

Кандидати:

1. `target_ratio = rdn_price / price_cap`
2. `log_price = log1p(rdn_price)`
3. `residual_price = rdn_price - base_tree_pred`
4. `residual_log = log1p(rdn_price) - log1p(base_tree_pred)`
5. `residual_ratio = target_ratio - base_tree_ratio`

Рекомендований старт:

- основний regression target: `residual_log`;
- inference:
  - `pred = expm1(log1p(base_tree_pred) + neural_residual_log)`;
  - clip `0..price_cap`;
- auxiliary target: `target_ratio`;
- classifiers: low/high regimes.

## Loss

Комбінований loss:

```text
loss =
  0.55 * Huber(price_error)
  + 0.20 * Huber(log_price_error)
  + 0.10 * WMAPE-like batch loss
  + 0.075 * BCE(low_price)
  + 0.075 * BCE(high_price)
```

Додаткові ваги:

- `2.0x` для останніх `45-60` днів;
- `1.5x` для годин `10-16`;
- `1.5x` для годин `19-23`;
- `2.0x` для actual `<1000`;
- `2.0x` для actual `>14000`.

Але ці ваги треба включати поступово, бо агресивні recency weights вже раніше псували стабільність.

## Anti-leakage правила

Обов'язково:

- scaler-и fit тільки на train;
- validation не може бути test-періодом;
- final test не використовується для early stopping;
- майбутні `rdn_supply`, `rdn_demand`, `vdr_supply`, `vdr_demand`, `garpok_volume` не використовуються як known future;
- для прогнозу на день D можна використовувати тільки:
  - історію до D-1;
  - погоду на D;
  - календар;
  - прайскепи;
  - лаги, які реально доступні;
- кожна фактична година у метриці рахується один раз.

## Протокол оцінки

Потрібен один спільний evaluator для tree і neural.

Мінімальні метрики:

- WMAPE за 3 місяці;
- WMAPE за 14 днів;
- WMAPE by hour;
- WMAPE by price bin:
  - `<500`;
  - `500-1000`;
  - `1000-3000`;
  - `3000-7000`;
  - `7000-12000`;
  - `>12000`;
- WMAPE для low-day режимів;
- WMAPE для cap-spike вечорів.

Файли після кожного експерименту:

- `output/neural_experiment_<id>_predictions.csv`;
- `output/neural_experiment_<id>_metrics.json`;
- `output/neural_experiment_<id>_plot.png`;
- `output/neural_experiments_log.md`.

Головне правило прийняття:

- не приймати модель, яка покращила 14 днів, але зламала 3 місяці;
- не приймати модель, яка покращила 3 місяці, але повністю пропускає літній low/high режим.

## Етапи роботи

### Етап 0. Зафіксувати чесний baseline

Зробити перед neural-роботою:

- перегенерувати current tree predictions у CSV після hour-fix;
- зберегти `actual`, `tree_base`, `calibrated_tree`, `price_cap`, всі regime flags;
- перевірити, що `15.06.2026 hour=23` відповідає OREE Hour 24, тобто `8369`, а не `14977`.

Очікуваний baseline:

- tree calibrated: близько `9.01% / 20.09%`;
- tree base: близько `10.45% / 31.33%`.

### Етап 1. Переписати neural dataset

Створити новий dataset-клас, який повертає:

- `x_history`: `[batch, history_len, history_features]`;
- `x_future`: `[batch, 24, future_features]`;
- `y`: `[batch, 24]`;
- `base_pred`: `[batch, 24]`;
- `price_cap`: `[batch, 24]`;
- `sample_weight`: `[batch, 24]`;
- `low_label`, `high_label`.

Один sample = один target day, а не довільне overlapping hour-window. Це прибирає дублювання годин у метриці.

### Етап 2. Neural residual MLP/TCN

Перший реальний експеримент:

- не чиста LSTM;
- TCN encoder + future decoder MLP;
- target `residual_log`;
- input включає `tree_base` або `calibrated_tree` як teacher feature.

Ціль етапу:

- довгий період нижче `8.5%`;
- короткий нижче `18%`;
- стабільний графік без диких overshoot.

### Етап 3. Regime heads

Додати multi-task класифікацію:

- low-price head: `actual < 500`, `actual < 1000`;
- high-price head: `actual > 14000`;
- day-regime head:
  - normal;
  - low-solar/wind day;
  - rebound day;
  - cap-spike evening.

Ціль етапу:

- короткий період `14-17%`;
- long-term не гірше `7.5-8%`.

### Етап 4. Ensemble neural + tree

Не замінювати tree-модель, а змішувати:

```text
final = w * tree_calibrated + (1 - w) * neural_residual_corrected
```

Де `w` може бути:

- по годинах;
- по regime probability;
- learned stacking через Ridge/LightGBM на validation, але без test leakage.

Ціль етапу:

- довгий період `6-7%`;
- короткий `12-16%`.

### Етап 5. Дотиснути до 5-6 / 10-15

Якщо попередні етапи спрацюють:

- додати quantile heads;
- окремо калібрувати evening cap-spikes;
- окремо калібрувати low daytime;
- додати rolling-origin fine-tuning на останніх `60-90` днях;
- перевірити ансамбль кількох seeds.

Ціль:

- long-term `5-6%`;
- short-term `10-15%`.

## Що не варто робити першим

- Не запускати великий Transformer як основну модель: даних мало, ризик overfit високий.
- Не тренувати pure neural price model з нуля без tree baseline.
- Не використовувати майбутні ринкові колонки як known future.
- Не оптимізувати тільки останні 14 днів: це вже раніше давало красивий short-term і поганий long-term.
- Не оцінювати overlapping multi-horizon predictions без агрегації до одного прогнозу на годину.

## Найімовірніший шлях до цілі

Найкраща стратегія:

1. Tree ensemble дає базовий прогноз.
2. NeuralResidualDayModel прогнозує добову поправку на 24 години.
3. Regime heads визначають low-day і cap-spike.
4. Stacking змішує tree і neural по годинах/режимах.
5. Оцінка тільки через чесний rolling/calendar evaluator.

Очікування:

- neural alone навряд чи одразу дасть `5-6%`;
- hybrid neural + tree має шанс;
- короткий період `10-15%` реалістичний, бо старі LSTM вже доходили до `14.71%`, але треба не втратити long-term;
- long-term `5-6%` потребує не тільки архітектури, а й стабільного feature protocol без leakage та з коректними ринковими лагами.

