get_gen_cons_legacy.py - ваш код 

get_gen_cons_new.py - мій трохи модифікований, який дає інформацію максимум до 2024-07-11

get_entsoe_actual_generation.py - перевірка живого ENTSO-E Transparency Platform для актуальної генерації України за типами виробництва

## Використання

```bash
# Вивести дані у термінал
python get_gen_cons_new.py 2024-07-10

# Зберегти у CSV
python get_gen_cons_new.py 2024-07-10 --output data/2024-07-10.csv

# Можна також в такому форматі
python get_gen_cons_new.py 10.07.2024 --output data/2024-07-10.csv
```

## Перевірка актуальної генерації через ENTSO-E

Цей шлях доданий як основний для пошуку новіших даних, ніж `ua.energy`:

```bash
# Перевірити вчорашній день у всіх відомих українських ENTSO-E зонах
python get_entsoe_actual_generation.py

# Перевірити конкретну дату, наприклад 2026-06-15
python get_entsoe_actual_generation.py --date 2026-06-15

# Зберегти CSV та JSON-діагностику
python get_entsoe_actual_generation.py --date 2026-06-15 ^
  --output data/entsoe_ua_generation_2026-06-15.csv ^
  --stats-output data/entsoe_ua_generation_2026-06-15.stats.json

# Просканувати дату і кілька попередніх днів, зупинившись на першому дні з числами
python get_entsoe_actual_generation.py --date 2026-06-15 --scan-days 14
```

Скрипт використовує публічний frontend API ENTSO-E:

`https://transparency.entsoe.eu/generation/actual/perType/generation/load`

Перевірені українські коди зон:

| Код | Опис |
|-----|------|
| `BZN\|10Y1001C--00003F` | Ukraine bidding zone |
| `BZN\|10Y1001C--000182` | UA-IPS bidding zone |
| `BZN\|10Y1001A1001A869` | UA-DobTPP bidding zone |
| `CTY\|10Y1001C--00003F` | Ukraine country |
| `SCA\|10Y1001C--00003F` | Ukraine scheduling area |
| `SCA\|10Y1001C--000182` | UA-IPS scheduling area |
| `SCA\|10Y1001A1001A869` | UA-DobTPP scheduling area |

Станом на перевірку 2026-06-16 для дати 2026-06-15 ENTSO-E повертає структуру кривих і 21 тип виробництва, але значення для України позначені як `n/e`, тобто числових точок генерації немає. Це не помилка парсингу: відповідь містить погодинні точки, але без `value`.

Офіційний REST API ENTSO-E для `documentType=A75` вимагає security token. Без токена endpoint повертає `Authentication failed`. Навіть якщо токен отримати, поточна frontend-перевірка показує, що публічні значення actual generation per type для України на платформі можуть бути не заповнені.

Збережені результати перевірки:

| Файл | Зміст |
|------|-------|
| `data/entsoe_ua_generation_2026-06-15.csv` | CSV зі схемою колонок; 0 рядків, бо ENTSO-E не повернув числових значень |
| `data/entsoe_ua_generation_2026-06-15.stats.json` | Діагностика по всіх українських ENTSO-E зонах за 2026-06-15 |
| `data/entsoe_ua_generation_scan_2026-06-01_2026-06-15.stats.json` | Backward scan основної зони `BZN\|10Y1001C--00003F` за 2026-06-01..2026-06-15 |
| `data/razumkov_april_2026_generation_summary.csv` | Найсвіжіший знайдений публічний агрегований зріз генерації: квітень 2026, не погодинний |
| `data/razumkov_march_2026_generation_summary.csv` | Додатковий агрегований зріз генерації: березень 2026, не погодинний |

## Структура вихідних даних

| Колонка              | Опис                                          |
|----------------------|-----------------------------------------------|
| `DateTime`           | Дата та час (погодинно, початок інтервалу)    |
| `aes`                | Атомна генерація, МВт                         |
| `tes`                | Теплова генерація (ТЕС), МВт                  |
| `tec`                | Теплоелектроцентралі (ТЕЦ), МВт               |
| `vde`                | Відновлювана генерація (сонце + вітер), МВт   |
| `gesgaes`            | ГЕС + ГАЕС (генерація), МВт                   |
| `consumptiongaespump`| ГАЕС (насосний режим, від'ємне значення), МВт |
| `consumption`        | Загальне споживання ОЕС України, МВт          |

## Додаткові джерела, які перевірені

| Джерело | Результат |
|---------|-----------|
| Energy Map / Ukrenergo, погодинний баланс ОЕС України | Повне джерело по генерації/споживанню, але публічна версія застаріла; не дає дані за 2026-06-15 |
| Energy Map, імпорт/експорт | Дані оновлюються близько до поточної дати, але це тільки міждержавні перетоки, не виробництво |
| Міністерство енергетики, оперативні зведення | Є свіжі текстові зведення про ситуацію, обмеження, відновлення, але без погодинної генерації за типами |
| Razumkov Centre, Ukraine's Energy Sector in April 2026 | Є агреговані оцінки за квітень 2026: АЕС до 5.5 ГВт, маневрова генерація до 3.5 ГВт, ВДЕ 1.8-2.0 ГВт, загальне виробництво 12 ГВт |
| Electricity Maps | По Україні у live-інтерфейсі немає відкритих числових значень production mix |
| Energy-Charts API | Україна є у списку країн, але endpoint `public_power` не повертає актуальний контент для `ua` |
| UAEA balance | Публічний CSV містить старий місячний баланс, не актуальні добові/погодинні дані |

Прямі запити блокуються Cloudflare. Код спочатку завантажує головну сторінку в "реальному" браузері, а потім виконує запити з токенами від "реального" користувача.
Дані для дат після 2024-07-11 на сайті `ua.energy` недоступні через серйозніший захист або відсутність публічних рядків. ENTSO-E перевірено окремим скриптом вище.

## Що я пробував

| Метод / ендпоінт | Результат |
|-----------------|-----------|
| `get_data_oes`, `get_data_bur`, `get_data_oes_only` для дат після 2024-07-11 | 0 записів — даних немає |
| `get_data` без `nonce` | Повертає тільки структуру колонок, 0 рядків |
| `get_data` з `nonce` / `multipart` / `_nonce` / `security` | WAF блокує або сервер ігнорує |
| Chart page через Playwright (Chromium, Firefox, Chrome channel) | Cloudflare 403 |
| Chart page через nodriver (stealth) | Cloudflare 403 |
| Chart page через реальний Chrome з CDP | Cloudflare 403 |
| Chart page через `?page_id=5591` | Cloudflare 403 |
| JS-навігація / `fetch` зі сторінки | Cloudflare 403 |
| WordPress REST API (`/wp-json/`) | F5 WAF блокує |
| 12 альтернативних AJAX action | Всі повертають `0` |
| `get_data_oes` з `type=consumption` | 92 220 записів, але лише до 2024-07-11 15:00 |
| ENTSO-E Transparency Platform REST API | Потрібен API key; frontend API без ключа повертає `n/e` для України |
