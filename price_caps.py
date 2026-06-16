from datetime import date, datetime

import numpy as np
import pandas as pd


# RDN/IDM DAM price caps used by the Ukrainian market during this project period.
# The 2026 changes are based on NEURC resolutions:
# - No. 70: all-day 15000 from 17.01.2026, then delivery-day time blocks from 01.04.2026
# - No. 621: all-day 15000 again from delivery day 01.05.2026
ALL_DAY_15000_START_2026 = date(2026, 1, 17)
TIME_BLOCKS_RETURN_2026 = date(2026, 4, 1)
ALL_DAY_15000_RETURN_2026 = date(2026, 5, 1)
EVENING_15000_START_2025 = date(2025, 8, 1)


def _parse_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None

    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    parsed = pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _parse_hour(value):
    if value is None or pd.isna(value):
        return None

    try:
        hour = int(float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return None

    if hour == 24:
        return 23
    if hour < 0:
        return 0
    if hour > 23:
        return hour % 24
    return hour


def _time_block_cap(hour, evening_cap=15000.0):
    hour = _parse_hour(hour)
    if hour is None:
        return np.nan

    if hour in (0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 16):
        return 5600.0
    if hour in (7, 8, 9, 10, 23):
        return 6900.0
    if hour in (17, 18, 19, 20, 21, 22):
        return float(evening_cap)
    return np.nan


def get_price_cap(value_date, hour):
    market_date = _parse_date(value_date)
    hour = _parse_hour(hour)

    if market_date is None or hour is None:
        return np.nan

    if market_date >= ALL_DAY_15000_RETURN_2026:
        return 15000.0
    if market_date >= TIME_BLOCKS_RETURN_2026:
        return _time_block_cap(hour, evening_cap=15000.0)
    if market_date >= ALL_DAY_15000_START_2026:
        return 15000.0
    if market_date >= EVENING_15000_START_2025:
        return _time_block_cap(hour, evening_cap=15000.0)
    return _time_block_cap(hour, evening_cap=9000.0)


def apply_price_caps_to_index(df):
    if "price_cap" not in df.columns:
        df["price_cap"] = np.nan

    if not isinstance(df.index, pd.DatetimeIndex):
        raise TypeError("apply_price_caps_to_index expects a DatetimeIndex")

    df["price_cap"] = [get_price_cap(ts.date(), ts.hour) for ts in df.index]
    return df


def apply_price_caps_to_frame(df, date_col=None, hour_col="hour"):
    if "price_cap" not in df.columns:
        df["price_cap"] = np.nan

    if hour_col not in df.columns:
        return df

    if date_col is None:
        date_col = df.columns[0]

    df["price_cap"] = [
        get_price_cap(row_date, row_hour)
        for row_date, row_hour in zip(df[date_col], df[hour_col])
    ]
    return df
