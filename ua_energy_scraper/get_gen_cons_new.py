import argparse
import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright

LAST_AVAILABLE_DATE = date(2024, 7, 11)
_HOME_URL = "https://ua.energy/"
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _parse_date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError:
        pass
    try:
        d, m, y = text.split(".")
        return date(int(y), int(m), int(d))
    except (ValueError, AttributeError):
        pass
    raise ValueError("Використовуйте формат дати YYYY-MM-DD або DD.MM.YYYY.")


def _fetch_raw(requested_date: date) -> str:
    params = {
        "action": "get_data_oes_only",
        "report_date": requested_date.strftime("%d.%m.%Y"),
        "type": "day",
        "rnd": "0.9018575009491707",
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=_USER_AGENT,
            viewport={"width": 1366, "height": 768},
            locale="uk-UA",
            timezone_id="Europe/Kyiv",
        )
        page = ctx.new_page()
        page.goto(_HOME_URL, wait_until="networkidle", timeout=45_000)
        raw = page.evaluate(
            """async (params) => {
                const response = await fetch('/wp-admin/admin-ajax.php', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: new URLSearchParams(params).toString(),
                });
                return response.text();
            }""",
            params,
        )
        browser.close()
    return raw


def _parse_response(raw: str, requested_date: date) -> pd.DataFrame:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Сервер повернув не-JSON: {raw[:120]!r}") from exc

    if not isinstance(payload, list) or not payload:
        raise ValueError("Сервер повернув порожню або неочікувану відповідь.")

    records = []
    for item in payload:
        hour = str(item.get("hour", "")).strip()
        if len(hour) != 5 or hour[2] != ":":
            continue
        records.append(
            {
                "DateTime": pd.Timestamp(f"{requested_date} {hour}"),
                "aes": pd.to_numeric(item.get("aes"), errors="coerce"),
                "tes": pd.to_numeric(item.get("tes"), errors="coerce"),
                "tec": pd.to_numeric(item.get("tec"), errors="coerce"),
                "vde": pd.to_numeric(item.get("vde"), errors="coerce"),
                "gesgaes": pd.to_numeric(item.get("gesgaes"), errors="coerce"),
                "consumptiongaespump": pd.to_numeric(item.get("consumptiongaespump"), errors="coerce"),
                "consumption": pd.to_numeric(item.get("consumption"), errors="coerce"),
            }
        )

    if not records:
        raise ValueError(f"Немає даних для {requested_date}.")

    return pd.DataFrame.from_records(records).sort_values("DateTime").reset_index(drop=True)


def get_gen_con(dateforecast: str | date) -> pd.DataFrame:
    requested_date = _parse_date(dateforecast) if isinstance(dateforecast, str) else dateforecast
    if requested_date > LAST_AVAILABLE_DATE:
        raise ValueError(f"Дані доступні лише до {LAST_AVAILABLE_DATE} включно.")
    raw = _fetch_raw(requested_date)
    return _parse_response(raw, requested_date)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("date")
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        frame = get_gen_con(args.date)
    except ValueError as exc:
        print(f"Помилка: {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = Path(__file__).resolve().parent / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output_path, index=False)
        print(f"Збережено {len(frame)} рядків у {output_path}")
        return 0

    print(frame.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())