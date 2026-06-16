import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from prediction_limits import clip_price_forecast


DAILY_PROFILE_BLEND = 0.69
RIDGE_ALPHA = 20.0


def _daily_feature_matrix(df):
    frame = df.copy()
    frame["date0"] = frame.index.normalize()
    frame["hour0"] = frame.index.hour

    full_dates = frame.groupby("date0")["hour0"].nunique()
    full_dates = full_dates[full_dates == 24].index
    frame = frame[frame["date0"].isin(full_dates)]

    price = frame.pivot_table(index="date0", columns="hour0", values="rdn_price", aggfunc="first").sort_index()
    cap = frame.pivot_table(index="date0", columns="hour0", values="price_cap", aggfunc="first").sort_index()
    ratio = (price / cap.replace(0, np.nan)).clip(0, 1.2)

    weather_cols = [
        col for col in [
            "feelslike", "humidity", "solarradiation", "cloudcover", "uvindex", "precip"
        ]
        if col in frame.columns
    ]
    if weather_cols:
        weather = frame.groupby("date0")[weather_cols].agg(["mean", "max", "min", "sum"])
        weather.columns = ["_".join(col) for col in weather.columns]
    else:
        weather = pd.DataFrame(index=price.index)

    rows = []
    for date in price.index:
        ts = pd.Timestamp(date)
        row = {
            "dow": ts.dayofweek,
            "is_weekend": int(ts.dayofweek >= 5),
            "month": ts.month,
            "day_of_year": ts.dayofyear,
            "dow_sin": np.sin(2 * np.pi * ts.dayofweek / 7),
            "dow_cos": np.cos(2 * np.pi * ts.dayofweek / 7),
            "day_of_year_sin": np.sin(2 * np.pi * ts.dayofyear / 366),
            "day_of_year_cos": np.cos(2 * np.pi * ts.dayofyear / 366),
        }

        if date in weather.index:
            row.update(weather.loc[date].to_dict())

        for lag in (1, 2, 7, 14):
            previous = date - pd.Timedelta(days=lag)
            if previous not in price.index:
                continue
            price_values = price.loc[previous].to_numpy(dtype="float64")
            ratio_values = ratio.loc[previous].to_numpy(dtype="float64")
            for hour in range(24):
                row[f"price_lag_{lag}_h{hour}"] = price_values[hour]
                row[f"ratio_lag_{lag}_h{hour}"] = ratio_values[hour]

        price_history = price.loc[price.index < date]
        ratio_history = ratio.loc[ratio.index < date]
        for window in (3, 7, 14):
            price_window = price_history.tail(window)
            ratio_window = ratio_history.tail(window)
            if price_window.empty:
                continue
            for hour in range(24):
                row[f"price_mean_{window}_h{hour}"] = price_window[hour].mean()
                row[f"price_min_{window}_h{hour}"] = price_window[hour].min()
                row[f"price_q25_{window}_h{hour}"] = price_window[hour].quantile(0.25)
                row[f"ratio_mean_{window}_h{hour}"] = ratio_window[hour].mean()
                row[f"ratio_min_{window}_h{hour}"] = ratio_window[hour].min()
                row[f"ratio_q25_{window}_h{hour}"] = ratio_window[hour].quantile(0.25)

        rows.append(row)

    features = pd.DataFrame(rows, index=price.index)
    features = features.replace([np.inf, -np.inf], np.nan).ffill().bfill().fillna(0)
    return features, price, cap


def apply_daily_profile_calibration(
    df,
    calibrated_predictions,
    target_index,
    blend=DAILY_PROFILE_BLEND,
):
    target_index = pd.DatetimeIndex(target_index)
    if target_index.empty:
        return pd.Series(dtype="float64")

    features, price, cap = _daily_feature_matrix(df)
    if features.empty:
        return pd.Series(calibrated_predictions, index=target_index, dtype="float64").reindex(target_index)

    target_dates = pd.DatetimeIndex(sorted(set(target_index.normalize())))
    available_target_dates = target_dates[target_dates.isin(features.index)]
    if available_target_dates.empty:
        return pd.Series(calibrated_predictions, index=target_index, dtype="float64").reindex(target_index)

    result = pd.Series(calibrated_predictions, index=calibrated_predictions.index, dtype="float64").reindex(target_index)

    for target_date in available_target_dates:
        train_dates = features.index[
            (features.index < target_date)
            & price.notna().all(axis=1)
            & cap.notna().all(axis=1)
        ]
        if len(train_dates) < 120:
            continue

        model = make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
        model.fit(features.loc[train_dates], np.log1p(price.loc[train_dates].to_numpy(dtype="float64")))

        daily_pred = np.expm1(model.predict(features.loc[[target_date]])[0])
        daily_cap = cap.loc[target_date].to_numpy(dtype="float64")
        daily_pred = clip_price_forecast(daily_pred, daily_cap)

        day_index = target_index[target_index.normalize() == target_date]
        if len(day_index) == 0:
            continue
        existing = result.loc[day_index].to_numpy(dtype="float64")
        adjusted = blend * existing + (1.0 - blend) * daily_pred[:len(day_index)]
        result.loc[day_index] = clip_price_forecast(adjusted, daily_cap[:len(day_index)])

    return result
