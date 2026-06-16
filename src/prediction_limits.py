import numpy as np
import pandas as pd


MIN_MARKET_PRICE = 10.0


def clip_price_forecast(values, caps=None, min_price=MIN_MARKET_PRICE):
    """Clip forecast prices to the valid DAM market range."""
    arr = np.asarray(values, dtype="float64")
    lower = float(min_price)
    if caps is None:
        return np.clip(arr, lower, None)

    cap_arr = np.asarray(caps, dtype="float64")
    valid_caps = np.isfinite(cap_arr)
    upper = np.where(valid_caps, np.maximum(cap_arr, lower), np.inf)
    return np.clip(arr, lower, upper)


def clip_price_series(values, caps=None, min_price=MIN_MARKET_PRICE):
    clipped = clip_price_forecast(values, caps=caps, min_price=min_price)
    index = getattr(values, "index", None)
    return pd.Series(clipped, index=index, dtype="float64")
