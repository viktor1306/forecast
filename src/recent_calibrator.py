import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


LOOKBACK_DAYS = 90
MIN_HOUR_SAMPLES = 20
RIDGE_ALPHA = 30.0
LOW_PRICE_THRESHOLD = 500.0
LOW_PRICE_PROB_THRESHOLD = 0.15
LOW_PRICE_BLEND_STRENGTH = 0.50
LOW_PRICE_BASELINE_COLUMN = "price_q25_hour_14d"
HIGH_PRICE_THRESHOLD = 14000.0
HIGH_PRICE_PROB_THRESHOLD = 0.15


def _build_calibrator_frame(df, base_predictions):
    frame = df.copy()
    base = pd.Series(base_predictions, index=base_predictions.index, dtype="float64")
    frame["base_pred"] = base.reindex(frame.index)
    frame["base_ratio"] = frame["base_pred"] / frame["price_cap"].replace(0, np.nan)
    frame["actual_ratio"] = frame["rdn_price"] / frame["price_cap"].replace(0, np.nan)
    frame["base_minus_min3"] = frame["base_pred"] - frame.groupby("hour")["rdn_price"].transform(
        lambda s: s.shift(1).rolling(3, min_periods=1).min()
    )

    frame["is_workday"] = (frame.index.dayofweek < 5).astype(int)
    frame["is_friday"] = (frame.index.dayofweek == 4).astype(int)
    frame["is_saturday"] = (frame.index.dayofweek == 5).astype(int)
    frame["is_sunday"] = (frame.index.dayofweek == 6).astype(int)
    for day_num in range(7):
        frame[f"dow_{day_num}"] = (frame.index.dayofweek == day_num).astype(int)

    for window in (2, 3, 5, 7, 14):
        grouped_price = frame.groupby("hour")["rdn_price"]
        grouped_ratio = frame.groupby("hour")["actual_ratio"]
        frame[f"low_share_hour_{window}d"] = grouped_price.transform(
            lambda s: (s.shift(1) < 1000).rolling(window, min_periods=1).mean()
        )
        frame[f"price_min_hour_{window}d"] = grouped_price.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).min()
        )
        frame[f"price_q25_hour_{window}d"] = grouped_price.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).quantile(0.25)
        )
        frame[f"price_median_hour_{window}d"] = grouped_price.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).median()
        )
        frame[f"price_mean_hour_{window}d"] = grouped_price.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).mean()
        )
        frame[f"ratio_median_hour_{window}d"] = grouped_ratio.transform(
            lambda s: s.shift(1).rolling(window, min_periods=1).median()
        )

    previous_day = frame.groupby(frame.index.normalize())["rdn_price"].agg(
        prev_day_min="min",
        prev_day_mean="mean",
    )
    previous_day.index = previous_day.index + pd.Timedelta(days=1)
    frame = frame.join(previous_day, on=frame.index.normalize())

    return frame


def _feature_columns(frame):
    base_features = [
        "base_pred", "base_ratio",
        "hour", "hour_sin", "hour_cos", "day_sin", "day_cos",
        "day_of_year_sin", "day_of_year_cos", "week_sin", "week_cos",
        "is_weekend", "is_off_day", "is_workday", "is_friday", "is_saturday", "is_sunday",
        "month", "is_summer", "cap_regime_all_day_15000",
        "feelslike", "humidity", "dew", "windspeed", "windgust", "winddir",
        "solarradiation", "solarenergy", "cloudcover", "visibility", "uvindex", "precip",
        "price_lag_24", "price_lag_48", "price_lag_168",
        "ratio_lag_24", "ratio_lag_48", "ratio_lag_168",
        "rolling_mean_hour_3d", "rolling_mean_hour_7d", "rolling_mean_hour_14d",
        "ratio_mean_hour_3d", "ratio_mean_hour_7d", "ratio_mean_hour_14d",
        "price_ema_24", "price_ema_168",
        "supply_lag_24", "demand_lag_24", "demand_ramp", "supply_ramp",
        "system_balance_lag_24", "garpok_lag_24", "vdr_supply_lag_24",
        "prob_low_price", "prev_day_min", "prev_day_mean",
    ]
    base_features.extend([f"dow_{day_num}" for day_num in range(7)])
    for prefix in (
        "low_share_hour",
        "price_min_hour",
        "price_median_hour",
        "ratio_median_hour",
    ):
        base_features.extend([f"{prefix}_{window}d" for window in (2, 3, 5, 7, 14)])

    return [name for name in base_features if name in frame.columns]


def _low_specialist_feature_columns(frame):
    features = _feature_columns(frame)
    extra_features = ["cal_pred", "base_minus_min3"]
    for prefix in ("price_q25_hour", "price_mean_hour"):
        extra_features.extend([f"{prefix}_{window}d" for window in (2, 3, 5, 7, 14)])

    return list(dict.fromkeys(features + [name for name in extra_features if name in frame.columns]))


def apply_recent_hourly_ridge_calibration(
    df,
    base_predictions,
    target_index,
    lookback_days=LOOKBACK_DAYS,
    min_hour_samples=MIN_HOUR_SAMPLES,
):
    target_index = pd.DatetimeIndex(target_index)
    if target_index.empty:
        return pd.Series(dtype="float64")

    frame = _build_calibrator_frame(df, base_predictions)
    features = _feature_columns(frame)
    if not features:
        return pd.Series(base_predictions, index=target_index, dtype="float64")

    frame[features] = frame[features].replace([np.inf, -np.inf], np.nan).ffill().fillna(0)

    target_start = target_index.min()
    train_start = target_start - pd.Timedelta(days=lookback_days)
    train_mask = (
        (frame.index >= train_start)
        & (frame.index < target_start)
        & frame["rdn_price"].notna()
        & frame["base_pred"].notna()
    )

    calibrated = pd.Series(base_predictions.reindex(target_index), index=target_index, dtype="float64")

    for hour in range(24):
        train_hour = train_mask & (frame["hour"] == hour)
        target_hour = target_index[(target_index.hour == hour) & target_index.isin(frame.index)]
        if len(target_hour) == 0 or train_hour.sum() < min_hour_samples:
            continue

        model = make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
        model.fit(frame.loc[train_hour, features], frame.loc[train_hour, "rdn_price"])

        raw_pred = model.predict(frame.loc[target_hour, features])
        caps = pd.to_numeric(frame.loc[target_hour, "price_cap"], errors="coerce").to_numpy(dtype="float64")
        calibrated.loc[target_hour] = np.clip(raw_pred, 0, caps)

    return calibrated


def apply_low_price_specialist(
    df,
    base_predictions,
    calibrated_predictions,
    target_index,
    threshold=LOW_PRICE_THRESHOLD,
    prob_threshold=LOW_PRICE_PROB_THRESHOLD,
    blend_strength=LOW_PRICE_BLEND_STRENGTH,
    low_baseline_column=LOW_PRICE_BASELINE_COLUMN,
):
    target_index = pd.DatetimeIndex(target_index)
    if target_index.empty:
        return pd.Series(dtype="float64")

    frame = _build_calibrator_frame(df, base_predictions)
    calibrated = pd.Series(calibrated_predictions, index=calibrated_predictions.index, dtype="float64")
    frame["cal_pred"] = frame["base_pred"]
    target_in_frame = target_index[target_index.isin(frame.index)]
    frame.loc[target_in_frame, "cal_pred"] = calibrated.reindex(target_in_frame)

    features = _low_specialist_feature_columns(frame)
    if not features:
        return calibrated.reindex(target_index)

    frame[features] = frame[features].replace([np.inf, -np.inf], np.nan).ffill().fillna(0)

    target_start = target_index.min()
    train_mask = (
        (frame.index < target_start)
        & frame["rdn_price"].notna()
        & frame["base_pred"].notna()
    )
    if train_mask.sum() < 500:
        return calibrated.reindex(target_index)

    y_train = (frame.loc[train_mask, "rdn_price"] < threshold).astype(int)
    if y_train.nunique() < 2:
        return calibrated.reindex(target_index)

    classifier = ExtraTreesClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=4,
        class_weight="balanced",
        n_jobs=-1,
        random_state=22,
    )
    classifier.fit(frame.loc[train_mask, features], y_train)

    result = calibrated.reindex(target_index).copy()
    if target_in_frame.empty:
        return result

    low_prob = pd.Series(
        classifier.predict_proba(frame.loc[target_in_frame, features])[:, 1],
        index=target_in_frame,
        dtype="float64",
    )
    if low_baseline_column not in frame.columns:
        low_baseline_column = "price_min_hour_14d"
    low_baseline = frame.loc[target_in_frame, low_baseline_column].astype("float64")
    caps = frame.loc[target_in_frame, "price_cap"].astype("float64")
    daytime_low_risk = (
        frame.loc[target_in_frame, "hour"].between(9, 17)
        & (low_prob >= prob_threshold)
        & low_baseline.notna()
    )

    if daytime_low_risk.any():
        idx = target_in_frame[daytime_low_risk.to_numpy()]
        adjusted = (
            (1.0 - blend_strength) * result.loc[idx]
            + blend_strength * low_baseline.loc[idx]
        )
        result.loc[idx] = adjusted.clip(lower=0, upper=caps.loc[idx])

    return result


def apply_high_price_specialist(
    df,
    base_predictions,
    calibrated_predictions,
    target_index,
    threshold=HIGH_PRICE_THRESHOLD,
    prob_threshold=HIGH_PRICE_PROB_THRESHOLD,
):
    target_index = pd.DatetimeIndex(target_index)
    if target_index.empty:
        return pd.Series(dtype="float64")

    frame = _build_calibrator_frame(df, base_predictions)
    calibrated = pd.Series(calibrated_predictions, index=calibrated_predictions.index, dtype="float64")
    frame["cal_pred"] = frame["base_pred"]
    target_in_frame = target_index[target_index.isin(frame.index)]
    frame.loc[target_in_frame, "cal_pred"] = calibrated.reindex(target_in_frame)
    frame["final_pred"] = frame["cal_pred"]
    frame["base_gap"] = frame["base_pred"] - frame["final_pred"]

    features = _low_specialist_feature_columns(frame)
    features = list(dict.fromkeys(features + ["final_pred", "base_gap"]))
    features = [feature for feature in features if feature in frame.columns]
    if not features:
        return calibrated.reindex(target_index)

    frame[features] = frame[features].replace([np.inf, -np.inf], np.nan).ffill().fillna(0)

    target_start = target_index.min()
    train_mask = (
        (frame.index < target_start)
        & frame["rdn_price"].notna()
        & frame["base_pred"].notna()
    )
    if train_mask.sum() < 500:
        return calibrated.reindex(target_index)

    y_train = (frame.loc[train_mask, "rdn_price"] > threshold).astype(int)
    if y_train.nunique() < 2:
        return calibrated.reindex(target_index)

    classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=4,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=33,
    )
    classifier.fit(frame.loc[train_mask, features], y_train)

    result = calibrated.reindex(target_index).copy()
    if target_in_frame.empty:
        return result

    high_prob = pd.Series(
        classifier.predict_proba(frame.loc[target_in_frame, features])[:, 1],
        index=target_in_frame,
        dtype="float64",
    )
    base_series = pd.Series(base_predictions, index=base_predictions.index, dtype="float64").reindex(target_in_frame)
    peak_hours = frame.loc[target_in_frame, "hour"].isin([0, 1, 2, 3, 21, 22, 23])
    high_risk = (
        peak_hours
        & (high_prob >= prob_threshold)
        & (base_series > result.reindex(target_in_frame))
    )

    if high_risk.any():
        idx = target_in_frame[high_risk.to_numpy()]
        caps = frame.loc[idx, "price_cap"].astype("float64")
        result.loc[idx] = base_series.loc[idx].clip(lower=0, upper=caps)

    return result


def apply_day_regime_selector(
    df,
    base_predictions,
    ridge_predictions,
    low_predictions,
    final_predictions,
    target_index,
):
    """Switch whole-day profiles when recent lag signals point to another regime."""
    target_index = pd.DatetimeIndex(target_index)
    if target_index.empty:
        return pd.Series(dtype="float64")

    result = pd.Series(final_predictions, index=final_predictions.index, dtype="float64").reindex(target_index).copy()
    base_series = pd.Series(base_predictions, index=base_predictions.index, dtype="float64").reindex(target_index)
    ridge_series = pd.Series(ridge_predictions, index=ridge_predictions.index, dtype="float64").reindex(target_index)
    low_series = pd.Series(low_predictions, index=low_predictions.index, dtype="float64").reindex(target_index)

    required = {"hour", "prob_low_price", "price_lag_24", "rolling_mean_hour_7d"}
    if not required.issubset(df.columns):
        return result

    frame = df.reindex(target_index)

    for target_date in sorted(set(target_index.normalize())):
        day_index = target_index[target_index.normalize() == target_date]
        if len(day_index) == 0:
            continue

        day_frame = frame.loc[day_index]
        daytime = day_frame["hour"].between(9, 16)
        evening = day_frame["hour"].between(18, 23)
        if not daytime.any():
            continue

        low_prob_day = pd.to_numeric(day_frame.loc[daytime, "prob_low_price"], errors="coerce").mean()
        lag_day = pd.to_numeric(day_frame.loc[daytime, "price_lag_24"], errors="coerce").mean()
        rolling_day = pd.to_numeric(day_frame.loc[daytime, "rolling_mean_hour_7d"], errors="coerce").mean()
        lag_evening = pd.to_numeric(day_frame.loc[evening, "price_lag_24"], errors="coerce").mean()
        dow = pd.Timestamp(target_date).dayofweek

        if not np.isfinite([low_prob_day, lag_day, rolling_day]).all():
            continue

        final_for_day = result.loc[day_index]
        chosen = final_for_day

        base_rebound = (
            (low_prob_day > 0.75 and lag_day > 1000.0 and rolling_day < 2100.0)
            or (
                dow >= 5
                and low_prob_day > 0.85
                and lag_day < 500.0
                and np.isfinite(lag_evening)
                and lag_evening > 7500.0
            )
        )
        ridge_transition = (
            dow == 1
            and lag_day > 3000.0
            and 0.55 < low_prob_day < 0.75
        )
        low_start = (
            dow in (0, 1)
            and low_prob_day < 0.65
            and lag_day < 3000.0
            and rolling_day < 1900.0
        )

        selected_regime = "final"
        if base_rebound:
            selected_regime = "base"
            chosen = base_series.loc[day_index]
            evening_trim = (
                day_frame["hour"].between(19, 21)
                & ((base_series.loc[day_index] - final_for_day) > 700.0)
            )
            if evening_trim.any():
                trimmed = chosen.copy()
                trimmed.loc[day_index[evening_trim.to_numpy()]] = final_for_day.loc[
                    day_index[evening_trim.to_numpy()]
                ]
                chosen = trimmed
        elif ridge_transition:
            selected_regime = "ridge"
            chosen = ridge_series.loc[day_index]
        elif low_start:
            selected_regime = "low"
            chosen = low_series.loc[day_index]

        if "cloudcover" in day_frame.columns:
            sunday_rebound_morning = (
                selected_regime == "final"
                and dow == 6
                and low_prob_day < 0.65
            )
            if sunday_rebound_morning:
                rebound_mask = (
                    day_frame["hour"].between(1, 7)
                    & (pd.to_numeric(day_frame["prob_low_price"], errors="coerce") < 0.05)
                    & (pd.to_numeric(day_frame["cloudcover"], errors="coerce") > 90.0)
                )
                if rebound_mask.any():
                    rebound_index = day_index[rebound_mask.to_numpy()]
                    chosen.loc[rebound_index] = base_series.loc[rebound_index]

            morning_after_low_rebound = selected_regime == "final"
            if morning_after_low_rebound:
                morning_mask = (
                    day_frame["hour"].between(8, 11)
                    & (pd.to_numeric(day_frame["price_lag_24"], errors="coerce") < 2000.0)
                    & (pd.to_numeric(day_frame["rolling_mean_hour_7d"], errors="coerce") > 1200.0)
                    & (pd.to_numeric(day_frame["prob_low_price"], errors="coerce") < 0.70)
                    & (pd.to_numeric(day_frame["cloudcover"], errors="coerce") < 90.0)
                )
                if morning_mask.any():
                    morning_index = day_index[morning_mask.to_numpy()]
                    chosen.loc[morning_index] = base_series.loc[morning_index]

        if {"cloudcover", "windspeed"}.issubset(day_frame.columns):
            windy_low_morning = selected_regime == "low" and dow == 1
            if windy_low_morning:
                windy_mask = (
                    day_frame["hour"].between(1, 5)
                    & (pd.to_numeric(day_frame["prob_low_price"], errors="coerce") < 0.05)
                    & (pd.to_numeric(day_frame["cloudcover"], errors="coerce") > 90.0)
                    & (pd.to_numeric(day_frame["windspeed"], errors="coerce") > 14.0)
                )
                if windy_mask.any():
                    windy_index = day_index[windy_mask.to_numpy()]
                    chosen.loc[windy_index] = base_series.loc[windy_index]

        chosen = chosen.where(chosen.notna(), result.loc[day_index])
        if "price_cap" in frame.columns:
            caps = pd.to_numeric(frame.loc[day_index, "price_cap"], errors="coerce")
            chosen = chosen.clip(lower=0).where(caps.isna(), chosen.clip(lower=0, upper=caps))
        else:
            chosen = chosen.clip(lower=0)
        result.loc[day_index] = chosen

    return result
