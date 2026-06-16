import argparse
import hashlib
import json
import os
import random
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from lightgbm import LGBMRegressor
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.preprocessing import RobustScaler
from torch.utils.data import DataLoader, Dataset
from xgboost import XGBClassifier, XGBRegressor

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from daily_profile_calibrator import apply_daily_profile_calibration
from evaluate_long_term_v1 import align_features, expected_feature_names, repair_legacy_extra_trees
from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts, wmape
from recent_calibrator import (
    apply_day_regime_selector,
    apply_high_price_specialist,
    apply_low_price_specialist,
    apply_recent_hourly_ridge_calibration,
)
from train_model_v1 import enforce_limits, generate_features, load_data


MARKET_RAW_COLUMNS = {
    "rdn_supply",
    "rdn_demand",
    "vdr_supply",
    "vdr_demand",
    "garpok_volume",
}


@dataclass
class ExperimentConfig:
    history_len: int = 168
    horizon: int = 24
    eval_months: int = 3
    val_days: int = 45
    batch_size: int = 16
    epochs: int = 80
    patience: int = 14
    hidden_dim: int = 96
    dropout: float = 0.18
    lr: float = 7e-4
    weight_decay: float = 1e-4
    seed: int = 42
    blend_grid_step: float = 0.025
    daytime_weight: float = 1.35
    evening_weight: float = 1.35
    low_price_weight: float = 1.45
    high_price_weight: float = 1.45
    low_bce_weight: float = 0.05
    high_bce_weight: float = 0.05


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def add_pre_feature_flags(df):
    df = df.copy()
    for col in MARKET_RAW_COLUMNS:
        if col in df.columns:
            df[f"{col}_missing"] = df[col].isna().astype(int)
    return df


def add_neural_engineered_features(df):
    df = df.copy()
    if "winddir" in df.columns:
        wind_rad = np.deg2rad(pd.to_numeric(df["winddir"], errors="coerce").fillna(0.0))
        df["winddir_sin"] = np.sin(wind_rad)
        df["winddir_cos"] = np.cos(wind_rad)

    solar = pd.to_numeric(df.get("solarradiation", 0.0), errors="coerce").fillna(0.0)
    cloud = pd.to_numeric(df.get("cloudcover", 0.0), errors="coerce").fillna(0.0).clip(0.0, 100.0)
    wind = pd.to_numeric(df.get("windspeed", 0.0), errors="coerce").fillna(0.0)
    windgust = pd.to_numeric(df.get("windgust", 0.0), errors="coerce").fillna(0.0)

    df["wind_cloud_interaction"] = wind * (cloud / 100.0)
    df["wind_clear_interaction"] = wind * (1.0 - cloud / 100.0)
    df["windgust_hour_interaction"] = windgust * df["hour"]
    df["renewable_pressure_index"] = solar * (1.0 - cloud / 100.0) + wind * 40.0
    df["is_daytime_low_hour"] = df["hour"].between(10, 16).astype(int)
    df["is_evening_cap_hour"] = df["hour"].between(19, 23).astype(int)
    return df.replace([np.inf, -np.inf], np.nan).ffill().fillna(0.0)


def prepare_dataframe():
    df = load_data()
    df = enforce_limits(df)
    df = add_pre_feature_flags(df)
    df = generate_features(df)
    df = add_neural_engineered_features(df)
    df = df.dropna(subset=["rdn_price"]).sort_index()
    return df


def tree_feature_candidates():
    common_features = [
        "hour_sin", "hour_cos", "day_sin", "day_cos", "month_sin", "month_cos",
        "day_of_year_sin", "day_of_year_cos", "week_sin", "week_cos",
        "is_winter", "is_spring", "is_summer", "is_autumn", "is_heating_season",
        "is_dst_period", "is_dst_transition_day", "days_to_dst_change",
        "cap_regime_all_day_15000", "post_aug_2025_cap_change", "post_jan_2026_cap_change",
        "post_apr_2026_cap_change", "price_cap_norm",
        "is_off_day", "price_cap", "feelslike", "windspeed", "solarradiation",
        "heating_degree", "cooling_degree", "temp_hour_interaction", "temp_summer_interaction",
        "solar_hour_interaction", "solar_summer_interaction",
        "price_lag_24", "price_lag_48", "price_lag_168", "price_lag_336",
        "ratio_lag_24", "ratio_lag_48", "ratio_lag_168",
        "price_lag_167", "price_lag_169",
        "diff_24_48", "diff_168_336",
        "rolling_mean_24", "rolling_std_24", "rolling_max_24", "rolling_min_24",
        "rolling_mean_hour_3d", "rolling_mean_hour_7d", "rolling_mean_hour_14d",
        "ratio_mean_hour_3d", "ratio_mean_hour_7d", "ratio_mean_hour_14d",
        "hour_month_interaction", "price_volatility_24", "demand_supply_ratio_lag_24",
        "demand_ramp_std_24", "supply_ramp_std_24",
        "rolling_mean_168", "rolling_std_168",
        "price_ema_24", "price_ema_168",
        "is_attack", "days_since_attack", "system_balance_lag_24", "demand_x_price_lag_168",
        "dew", "humidity", "precip", "snow", "windgust", "winddir",
        "sealevelpressure", "cloudcover", "visibility", "uvindex",
    ]
    return common_features + [
        "supply_lag_24", "supply_lag_168",
        "demand_ramp", "supply_ramp",
        "garpok_lag_24", "vdr_supply_lag_24",
    ]


def finite_frame(frame):
    return frame.replace([np.inf, -np.inf], np.nan).ffill().fillna(0.0)


def add_tree_low_probability(df, models_dir, features):
    df = df.copy()
    clf_path = Path(models_dir) / "low_price_classifier.json"
    if not clf_path.exists():
        if "ratio_mean_hour_7d" in df.columns:
            df["prob_low_price"] = (1.0 - df["ratio_mean_hour_7d"].clip(0, 1)).clip(0, 1)
        else:
            df["prob_low_price"] = 0.0
        return df

    clf = XGBClassifier()
    clf.load_model(os.fspath(clf_path))
    clf_features = expected_feature_names(model=clf) or [f for f in features if f in df.columns]
    X = finite_frame(align_features(df, clf_features))
    df["prob_low_price"] = clf.predict_proba(X)[:, 1]
    return df


def predict_tree_ensemble(df, models_dir):
    df = add_tree_low_probability(df, models_dir, tree_feature_candidates())
    xgb_features = tree_feature_candidates() + ["prob_low_price"]
    xgb_features = [f for f in xgb_features if f in df.columns]
    model_features = [f for f in xgb_features if f not in {"hour", "is_anomaly"}]

    weights_path = Path(models_dir) / "ensemble_weights.json"
    ensemble_weights = {}
    if weights_path.exists():
        with open(weights_path, "r", encoding="utf-8") as f:
            ensemble_weights = json.load(f)

    pred_all = pd.Series(index=df.index, dtype="float64")
    fallback = df.get("price_lag_24", df["rdn_price"].shift(24)).fillna(df["rdn_price"].ffill())

    for hour in range(24):
        mask = df["hour"] == hour
        if not mask.any():
            continue
        X_h = finite_frame(df.loc[mask, model_features])
        caps = pd.to_numeric(df.loc[mask, "price_cap"], errors="coerce").to_numpy(dtype="float64")

        ratios = []
        weights = []
        et_path = Path(models_dir) / f"et_hour_{hour}.pkl"
        if et_path.exists():
            model_et = repair_legacy_extra_trees(joblib.load(et_path))
            X_model = align_features(X_h, expected_feature_names(model=model_et))
            ratios.append(np.asarray(model_et.predict(X_model), dtype="float64"))
            weights.append(0.33)

        xgb_path = Path(models_dir) / f"xgb_hour_{hour}.json"
        if xgb_path.exists():
            model_xgb = XGBRegressor()
            model_xgb.load_model(os.fspath(xgb_path))
            X_model = align_features(X_h, expected_feature_names(model=model_xgb))
            ratios.append(np.asarray(model_xgb.predict(X_model), dtype="float64"))
            weights.append(0.33)

        lgbm_path = Path(models_dir) / f"lgbm_hour_{hour}.txt"
        if lgbm_path.exists():
            booster = lgb.Booster(model_file=os.fspath(lgbm_path))
            X_model = align_features(X_h, expected_feature_names(booster=booster))
            ratios.append(np.asarray(booster.predict(X_model), dtype="float64"))
            weights.append(0.34)

        if str(hour) in ensemble_weights and len(ensemble_weights[str(hour)]) == len(weights):
            weights = [float(w) for w in ensemble_weights[str(hour)]]

        if not ratios:
            pred = fallback.loc[X_h.index].to_numpy(dtype="float64")
        else:
            stacked = np.vstack(ratios)
            weight_arr = np.asarray(weights, dtype="float64")
            weight_arr = weight_arr / max(weight_arr.sum(), 1e-9)
            pred = np.average(stacked, axis=0, weights=weight_arr) * caps

        pred = np.where(np.isfinite(pred), pred, fallback.loc[X_h.index].to_numpy(dtype="float64"))
        pred_all.loc[X_h.index] = np.clip(pred, 0.0, caps)

    pred_all = pred_all.where(pred_all.notna(), fallback).clip(lower=0.0)
    return df, pred_all.sort_index()


def add_split_safe_low_probability(df, train_mask, features):
    df = df.copy()
    classifier_features = [f for f in features if f in df.columns and f not in {"hour", "is_anomaly"}]
    if not classifier_features:
        df["prob_low_price"] = 0.0
        return df

    y_train = (df.loc[train_mask, "rdn_price"] < 3000.0).astype(int)
    if y_train.nunique() < 2 or int(train_mask.sum()) < 500:
        if "ratio_mean_hour_7d" in df.columns:
            df["prob_low_price"] = (1.0 - df["ratio_mean_hour_7d"].clip(0, 1)).clip(0, 1)
        else:
            df["prob_low_price"] = 0.0
        return df

    X_train = finite_frame(df.loc[train_mask, classifier_features])
    X_all = finite_frame(df.loc[:, classifier_features])
    classifier = ExtraTreesClassifier(
        n_estimators=350,
        max_depth=10,
        min_samples_leaf=3,
        class_weight="balanced",
        n_jobs=-1,
        random_state=22,
    )
    classifier.fit(X_train, y_train)
    df["prob_low_price"] = classifier.predict_proba(X_all)[:, 1]
    return df


def train_split_safe_tree_predictions(df, train_end_ts, model_types):
    """Train a tree teacher only on rows before train_end_ts and predict all rows.

    This is slower than loading models_improved, but it avoids using tree models that
    have already seen validation/test targets in historical backtests.
    """
    train_end_ts = pd.Timestamp(train_end_ts)
    train_mask = (df.index < train_end_ts) & df["rdn_price"].notna()
    if train_mask.sum() < 1000:
        raise ValueError(f"Not enough rows before split-safe tree cutoff {train_end_ts}: {train_mask.sum()}")

    df = add_split_safe_low_probability(df, train_mask, tree_feature_candidates())
    feature_names = list(dict.fromkeys(tree_feature_candidates() + ["prob_low_price"]))
    feature_names = [f for f in feature_names if f in df.columns and f not in {"hour", "is_anomaly"}]
    X_all = finite_frame(df.loc[:, feature_names])
    y_all = df["target_ratio"].astype("float64")
    caps_all = pd.to_numeric(df["price_cap"], errors="coerce").astype("float64")
    fallback = df.get("price_lag_24", df["rdn_price"].shift(24)).fillna(df["rdn_price"].ffill())
    predictions = pd.Series(index=df.index, dtype="float64")

    model_types = [m.strip().lower() for m in model_types if m.strip()]
    if not model_types:
        raise ValueError("At least one split-safe tree model type is required.")

    for hour in range(24):
        hour_mask = df["hour"] == hour
        train_hour = train_mask & hour_mask
        if train_hour.sum() < 30:
            predictions.loc[hour_mask] = fallback.loc[hour_mask]
            continue

        X_train = X_all.loc[train_hour]
        y_train = y_all.loc[train_hour]
        X_pred = X_all.loc[hour_mask]
        hour_ratios = []

        dates_h = df.index[train_hour]
        time_weights = np.linspace(0.35, 1.0, len(X_train))
        recent_start = train_end_ts - pd.Timedelta(days=90)
        time_weights[dates_h >= recent_start] *= 1.35

        if "et" in model_types:
            et = ExtraTreesRegressor(
                n_estimators=700,
                max_depth=32,
                min_samples_leaf=2,
                bootstrap=True,
                n_jobs=-1,
                random_state=42 + hour,
            )
            et.fit(X_train, y_train, sample_weight=time_weights)
            hour_ratios.append(np.asarray(et.predict(X_pred), dtype="float64"))

        if "lgbm" in model_types:
            lgbm_model = LGBMRegressor(
                n_estimators=900,
                learning_rate=0.025,
                num_leaves=45,
                max_depth=9,
                min_child_samples=12,
                subsample=0.85,
                colsample_bytree=0.85,
                objective="mae",
                verbosity=-1,
                n_jobs=-1,
                random_state=52 + hour,
            )
            lgbm_model.fit(X_train, y_train, sample_weight=time_weights)
            hour_ratios.append(np.asarray(lgbm_model.predict(X_pred), dtype="float64"))

        if "xgb" in model_types:
            xgb_model = XGBRegressor(
                n_estimators=900,
                learning_rate=0.025,
                max_depth=5,
                subsample=0.85,
                colsample_bytree=0.85,
                objective="reg:absoluteerror",
                tree_method="hist",
                n_jobs=-1,
                random_state=62 + hour,
            )
            xgb_model.fit(X_train, y_train, sample_weight=time_weights)
            hour_ratios.append(np.asarray(xgb_model.predict(X_pred), dtype="float64"))

        if not hour_ratios:
            hour_pred = fallback.loc[hour_mask].to_numpy(dtype="float64")
        else:
            ratio = np.nanmean(np.vstack(hour_ratios), axis=0)
            hour_caps = caps_all.loc[hour_mask].to_numpy(dtype="float64")
            hour_pred = ratio * hour_caps
            hour_pred = np.where(np.isfinite(hour_pred), hour_pred, fallback.loc[hour_mask].to_numpy(dtype="float64"))
            hour_pred = np.clip(hour_pred, 0.0, hour_caps)

        predictions.loc[hour_mask] = hour_pred
        print(f"split-safe tree h={hour:02d} train={int(train_hour.sum())}", flush=True)

    predictions = predictions.where(predictions.notna(), fallback).clip(lower=0.0)
    return df, predictions.sort_index()


def lag_number_is_safe(col_name):
    for match in re.finditer(r"_lag_(\d+)", col_name):
        if int(match.group(1)) < 24:
            return False
    return True


def select_model_features(df):
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "is_anomaly"]
    market_missing_flags = {f"{col}_missing" for col in MARKET_RAW_COLUMNS}
    future_exclude = set(MARKET_RAW_COLUMNS) | market_missing_flags | {"rdn_price", "target_ratio"}

    future_features = []
    for col in numeric_cols:
        if col in future_exclude:
            continue
        if not lag_number_is_safe(col):
            continue
        future_features.append(col)

    preferred_history = list(dict.fromkeys(
        ["rdn_price", "target_ratio", *MARKET_RAW_COLUMNS, *future_features]
    ))
    history_features = [c for c in preferred_history if c in numeric_cols]

    leakage_columns = sorted(set(future_features).intersection(future_exclude))
    unsafe_lags = [c for c in future_features if not lag_number_is_safe(c)]
    if leakage_columns or unsafe_lags:
        raise ValueError(
            f"Unsafe future features detected: raw={leakage_columns}, lags={unsafe_lags}"
        )

    return history_features, future_features


def full_day_dates(df):
    counts = pd.Series(df.index, index=df.index).groupby(df.index.normalize()).count()
    return pd.DatetimeIndex(counts[counts == 24].index).sort_values()


def build_sample_dates(df, config):
    all_days = full_day_dates(df)
    last_ts = df.index.max()
    test_start_ts = last_ts - pd.DateOffset(months=config.eval_months)
    test_start_day = test_start_ts.normalize()
    val_start_day = test_start_day - pd.Timedelta(days=config.val_days)

    usable = []
    for day in all_days:
        hist_idx = pd.date_range(day - pd.Timedelta(hours=config.history_len), periods=config.history_len, freq="h")
        fut_idx = pd.date_range(day, periods=config.horizon, freq="h")
        if hist_idx.isin(df.index).all() and fut_idx.isin(df.index).all():
            usable.append(day)
    usable = pd.DatetimeIndex(usable)

    train_days = usable[usable < val_start_day]
    val_days = usable[(usable >= val_start_day) & (usable < test_start_day)]
    test_days = usable[usable >= test_start_day]

    if len(train_days) < 120 or len(val_days) < 7 or len(test_days) < 7:
        raise ValueError(
            "Not enough day samples after split: "
            f"train={len(train_days)}, val={len(val_days)}, test={len(test_days)}"
        )
    return train_days, val_days, test_days, test_start_ts


def build_arrays(df, days, history_features, future_features, config):
    x_history, x_future, y_price, base_pred, caps, weights = [], [], [], [], [], []
    low_label, high_label, datetimes = [], [], []

    train_last_day = days.max() if len(days) else None
    for day in days:
        hist_idx = pd.date_range(day - pd.Timedelta(hours=config.history_len), periods=config.history_len, freq="h")
        fut_idx = pd.date_range(day, periods=config.horizon, freq="h")

        hist = df.loc[hist_idx, history_features].to_numpy(dtype="float32")
        fut = df.loc[fut_idx, future_features].to_numpy(dtype="float32")
        actual = df.loc[fut_idx, "rdn_price"].to_numpy(dtype="float32")
        base = df.loc[fut_idx, "tree_base_pred"].to_numpy(dtype="float32")
        cap = df.loc[fut_idx, "price_cap"].to_numpy(dtype="float32")

        hour = df.loc[fut_idx, "hour"].to_numpy(dtype="int64")
        sample_weight = np.ones(config.horizon, dtype="float32")
        sample_weight[(hour >= 10) & (hour <= 16)] *= config.daytime_weight
        sample_weight[(hour >= 19) & (hour <= 23)] *= config.evening_weight
        sample_weight[actual < 1000.0] *= config.low_price_weight
        sample_weight[actual > 14000.0] *= config.high_price_weight
        if train_last_day is not None:
            age_days = max((train_last_day - day).days, 0)
            recency = 1.0 + max(0.0, 1.0 - age_days / 90.0) * 0.35
            sample_weight *= recency

        x_history.append(hist)
        x_future.append(fut)
        y_price.append(actual)
        base_pred.append(np.clip(base, 0.0, cap))
        caps.append(cap)
        weights.append(sample_weight)
        low_label.append((actual < 1000.0).astype("float32"))
        high_label.append((actual > 14000.0).astype("float32"))
        datetimes.extend(fut_idx)

    return {
        "x_history": np.asarray(x_history, dtype="float32"),
        "x_future": np.asarray(x_future, dtype="float32"),
        "y_price": np.asarray(y_price, dtype="float32"),
        "base_pred": np.asarray(base_pred, dtype="float32"),
        "caps": np.asarray(caps, dtype="float32"),
        "weights": np.asarray(weights, dtype="float32"),
        "low_label": np.asarray(low_label, dtype="float32"),
        "high_label": np.asarray(high_label, dtype="float32"),
        "datetimes": pd.DatetimeIndex(datetimes),
        "days": days,
    }


def fit_transform_arrays(train, val, test):
    scaler_h = RobustScaler(quantile_range=(5.0, 95.0))
    scaler_f = RobustScaler(quantile_range=(5.0, 95.0))

    n_h = train["x_history"].shape[-1]
    n_f = train["x_future"].shape[-1]
    scaler_h.fit(train["x_history"].reshape(-1, n_h))
    scaler_f.fit(train["x_future"].reshape(-1, n_f))

    for block in (train, val, test):
        block["x_history"] = scaler_h.transform(block["x_history"].reshape(-1, n_h)).reshape(block["x_history"].shape).astype("float32")
        block["x_future"] = scaler_f.transform(block["x_future"].reshape(-1, n_f)).reshape(block["x_future"].shape).astype("float32")
        block["x_history"] = np.nan_to_num(block["x_history"], nan=0.0, posinf=0.0, neginf=0.0)
        block["x_future"] = np.nan_to_num(block["x_future"], nan=0.0, posinf=0.0, neginf=0.0)
    return scaler_h, scaler_f


class DayDataset(Dataset):
    def __init__(self, arrays):
        self.arrays = arrays

    def __len__(self):
        return len(self.arrays["days"])

    def __getitem__(self, idx):
        return {
            "x_history": torch.tensor(self.arrays["x_history"][idx], dtype=torch.float32),
            "x_future": torch.tensor(self.arrays["x_future"][idx], dtype=torch.float32),
            "y_price": torch.tensor(self.arrays["y_price"][idx], dtype=torch.float32),
            "base_pred": torch.tensor(self.arrays["base_pred"][idx], dtype=torch.float32),
            "caps": torch.tensor(self.arrays["caps"][idx], dtype=torch.float32),
            "weights": torch.tensor(self.arrays["weights"][idx], dtype=torch.float32),
            "low_label": torch.tensor(self.arrays["low_label"][idx], dtype=torch.float32),
            "high_label": torch.tensor(self.arrays["high_label"][idx], dtype=torch.float32),
        }


class TCNBlock(nn.Module):
    def __init__(self, channels, dilation, dropout):
        super().__init__()
        padding = dilation
        self.conv1 = nn.Conv1d(channels, channels, kernel_size=3, padding=padding, dilation=dilation)
        self.conv2 = nn.Conv1d(channels, channels, kernel_size=3, padding=padding, dilation=dilation)
        self.norm1 = nn.BatchNorm1d(channels)
        self.norm2 = nn.BatchNorm1d(channels)
        self.dropout = nn.Dropout(dropout)

    def _trim(self, x, target_len):
        if x.shape[-1] > target_len:
            return x[..., -target_len:]
        return x

    def forward(self, x):
        target_len = x.shape[-1]
        out = self.conv1(x)
        out = self._trim(out, target_len)
        out = self.dropout(F.gelu(self.norm1(out)))
        out = self.conv2(out)
        out = self._trim(out, target_len)
        out = self.dropout(F.gelu(self.norm2(out)))
        return x + out


class NeuralResidualDayModel(nn.Module):
    def __init__(self, history_dim, future_dim, hidden_dim=96, dropout=0.18, horizon=24):
        super().__init__()
        self.horizon = horizon
        self.input_proj = nn.Conv1d(history_dim, hidden_dim, kernel_size=1)
        self.blocks = nn.Sequential(
            TCNBlock(hidden_dim, 1, dropout),
            TCNBlock(hidden_dim, 2, dropout),
            TCNBlock(hidden_dim, 4, dropout),
            TCNBlock(hidden_dim, 8, dropout),
            TCNBlock(hidden_dim, 16, dropout),
        )
        self.context_norm = nn.LayerNorm(hidden_dim * 2)
        self.future_mlp = nn.Sequential(
            nn.Linear(future_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.residual_head = nn.Linear(hidden_dim, 1)
        self.ratio_head = nn.Linear(hidden_dim, 1)
        self.low_head = nn.Linear(hidden_dim, 1)
        self.high_head = nn.Linear(hidden_dim, 1)

    def forward(self, x_history, x_future):
        hist = x_history.transpose(1, 2)
        enc = self.blocks(self.input_proj(hist))
        last = enc[:, :, -1]
        pooled = enc.mean(dim=-1)
        context = self.context_norm(torch.cat([last, pooled], dim=1))
        context = context.unsqueeze(1).expand(-1, self.horizon, -1)

        fut = self.future_mlp(x_future)
        decoded = self.decoder(torch.cat([context, fut], dim=-1))
        return {
            "residual_log": self.residual_head(decoded).squeeze(-1),
            "ratio": torch.sigmoid(self.ratio_head(decoded).squeeze(-1)) * 1.15,
            "low_logit": self.low_head(decoded).squeeze(-1),
            "high_logit": self.high_head(decoded).squeeze(-1),
        }


def hybrid_loss(outputs, batch, config):
    y = batch["y_price"]
    base = batch["base_pred"].clamp(min=0.0)
    caps = batch["caps"].clamp(min=1.0)
    weights = batch["weights"]

    pred_log = torch.log1p(base) + outputs["residual_log"]
    cap_log = torch.log1p(caps)
    pred_log = torch.minimum(pred_log, cap_log + 0.05)
    pred_price = torch.expm1(pred_log).clamp(min=0.0)
    pred_price = torch.minimum(pred_price, caps)

    price_loss = F.smooth_l1_loss((pred_price - y) / 1000.0, torch.zeros_like(y), reduction="none")
    log_loss = F.smooth_l1_loss(pred_log, torch.log1p(y.clamp(min=0.0)), reduction="none")
    ratio_target = (y / caps).clamp(0.0, 1.15)
    ratio_loss = F.smooth_l1_loss(outputs["ratio"], ratio_target, reduction="none")
    wmape_like = (torch.abs(pred_price - y) * weights).sum() / ((y.abs() * weights).sum() + 1.0)
    low_loss = F.binary_cross_entropy_with_logits(outputs["low_logit"], batch["low_label"], reduction="none")
    high_loss = F.binary_cross_entropy_with_logits(outputs["high_logit"], batch["high_label"], reduction="none")

    weighted = lambda value: (value * weights).sum() / (weights.sum() + 1e-6)
    return (
        0.52 * weighted(price_loss)
        + 0.22 * weighted(log_loss)
        + 0.10 * wmape_like
        + 0.06 * weighted(ratio_loss)
        + config.low_bce_weight * weighted(low_loss)
        + config.high_bce_weight * weighted(high_loss)
    )


def move_batch(batch, device):
    return {k: v.to(device) for k, v in batch.items()}


def train_model(train_arrays, val_arrays, history_dim, future_dim, config, device):
    train_loader = DataLoader(DayDataset(train_arrays), batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(DayDataset(val_arrays), batch_size=config.batch_size, shuffle=False)

    model = NeuralResidualDayModel(
        history_dim=history_dim,
        future_dim=future_dim,
        hidden_dim=config.hidden_dim,
        dropout=config.dropout,
        horizon=config.horizon,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.6, patience=5)

    best_state = None
    best_val = float("inf")
    stale = 0
    history = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        train_losses = []
        for batch in train_loader:
            batch = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            loss = hybrid_loss(model(batch["x_history"], batch["x_future"]), batch, config)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_losses.append(float(loss.detach().cpu()))

        model.eval()
        val_losses = []
        with torch.no_grad():
            for batch in val_loader:
                batch = move_batch(batch, device)
                loss = hybrid_loss(model(batch["x_history"], batch["x_future"]), batch, config)
                val_losses.append(float(loss.detach().cpu()))

        train_loss = float(np.mean(train_losses))
        val_loss = float(np.mean(val_losses))
        scheduler.step(val_loss)
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
        print(f"epoch={epoch:03d} train={train_loss:.5f} val={val_loss:.5f}")

        if val_loss < best_val - 1e-5:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= config.patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return model, history


def predict_arrays(model, arrays, device, batch_size):
    loader = DataLoader(DayDataset(arrays), batch_size=batch_size, shuffle=False)
    residuals, ratios, low_probs, high_probs = [], [], [], []
    model.eval()
    with torch.no_grad():
        for batch in loader:
            batch = move_batch(batch, device)
            out = model(batch["x_history"], batch["x_future"])
            residuals.append(out["residual_log"].cpu().numpy())
            ratios.append(out["ratio"].cpu().numpy())
            low_probs.append(torch.sigmoid(out["low_logit"]).cpu().numpy())
            high_probs.append(torch.sigmoid(out["high_logit"]).cpu().numpy())

    residuals = np.concatenate(residuals, axis=0)
    ratios = np.concatenate(ratios, axis=0)
    low_probs = np.concatenate(low_probs, axis=0)
    high_probs = np.concatenate(high_probs, axis=0)

    base = arrays["base_pred"]
    caps = arrays["caps"]
    pred = np.expm1(np.log1p(np.clip(base, 0.0, None)) + residuals)
    pred = np.clip(pred, 0.0, caps)

    flat = pd.DataFrame({
        "datetime": arrays["datetimes"],
        "actual": arrays["y_price"].reshape(-1),
        "price_cap": caps.reshape(-1),
        "tree_base_pred": base.reshape(-1),
        "neural_pred": pred.reshape(-1),
        "neural_ratio": ratios.reshape(-1),
        "low_prob": low_probs.reshape(-1),
        "high_prob": high_probs.reshape(-1),
    })
    return flat.sort_values("datetime").reset_index(drop=True)


def tune_blend_weights(val_predictions, config):
    grid = np.arange(0.0, 1.0 + config.blend_grid_step / 2.0, config.blend_grid_step)
    global_scores = []
    for weight_tree in grid:
        pred = weight_tree * val_predictions["tree_base_pred"] + (1.0 - weight_tree) * val_predictions["neural_pred"]
        global_scores.append((wmape(val_predictions["actual"], pred), float(weight_tree)))
    global_weight = min(global_scores, key=lambda x: x[0])[1]

    hourly_weights = {}
    for hour, group in val_predictions.groupby(pd.to_datetime(val_predictions["datetime"]).dt.hour):
        if len(group) < 12:
            hourly_weights[int(hour)] = global_weight
            continue
        scores = []
        for weight_tree in grid:
            pred = weight_tree * group["tree_base_pred"] + (1.0 - weight_tree) * group["neural_pred"]
            scores.append((wmape(group["actual"], pred), float(weight_tree)))
        hourly_weights[int(hour)] = min(scores, key=lambda x: x[0])[1]
    return {"global_tree_weight": global_weight, "hourly_tree_weight": hourly_weights}


def apply_blend(predictions, blend):
    frame = predictions.copy()
    hours = pd.to_datetime(frame["datetime"]).dt.hour
    weights = np.array([
        blend["hourly_tree_weight"].get(int(hour), blend["global_tree_weight"])
        for hour in hours
    ], dtype="float64")
    frame["hybrid_pred"] = weights * frame["tree_base_pred"] + (1.0 - weights) * frame["neural_pred"]
    frame["hybrid_pred"] = frame["hybrid_pred"].clip(lower=0.0, upper=frame["price_cap"])
    return frame


def apply_recent_calibration(df, base_predictions, target_index):
    target_index = pd.DatetimeIndex(target_index)
    if target_index.empty:
        return pd.Series(dtype="float64")
    ridge = apply_recent_hourly_ridge_calibration(df, base_predictions, target_index)
    low = apply_low_price_specialist(df, base_predictions, ridge, target_index)
    daily = apply_daily_profile_calibration(df, low, target_index)
    high = apply_high_price_specialist(df, base_predictions, daily, target_index)
    final = apply_day_regime_selector(df, base_predictions, ridge, low, high, target_index)
    return final.reindex(target_index)


def add_calibrated_variants(df, predictions):
    frame = predictions.copy()
    dt_index = pd.DatetimeIndex(pd.to_datetime(frame["datetime"]))
    last_ts = dt_index.max()
    last_14_start = last_ts - pd.Timedelta(days=14)
    last_14_index = dt_index[dt_index >= last_14_start]

    tree_all = df["tree_base_pred"].copy()
    tree_cal = apply_recent_calibration(df, tree_all, last_14_index)
    frame["tree_recent_calibrated_pred"] = frame["tree_base_pred"]
    if not tree_cal.empty:
        tree_map = tree_cal.to_dict()
        mask = frame["datetime"].isin(tree_map.keys())
        frame.loc[mask, "tree_recent_calibrated_pred"] = frame.loc[mask, "datetime"].map(tree_map)

    hybrid_all = df["tree_base_pred"].copy()
    hybrid_series = pd.Series(frame["hybrid_pred"].to_numpy(dtype="float64"), index=dt_index)
    hybrid_all.loc[hybrid_series.index] = hybrid_series
    hybrid_cal = apply_recent_calibration(df, hybrid_all, last_14_index)
    frame["hybrid_recent_calibrated_pred"] = frame["hybrid_pred"]
    if not hybrid_cal.empty:
        hybrid_map = hybrid_cal.to_dict()
        mask = frame["datetime"].isin(hybrid_map.keys())
        frame.loc[mask, "hybrid_recent_calibrated_pred"] = frame.loc[mask, "datetime"].map(hybrid_map)

    for col in ["tree_recent_calibrated_pred", "hybrid_recent_calibrated_pred"]:
        frame[col] = frame[col].clip(lower=0.0, upper=frame["price_cap"])

    frame["hybrid_guarded_pred"] = frame["hybrid_recent_calibrated_pred"]
    guarded_mask = frame["datetime"].isin(last_14_index)
    frame.loc[guarded_mask, "hybrid_guarded_pred"] = frame.loc[
        guarded_mask, "tree_recent_calibrated_pred"
    ]
    frame["hybrid_guarded_pred"] = frame["hybrid_guarded_pred"].clip(lower=0.0, upper=frame["price_cap"])
    return frame


def metrics_by_variant(predictions, columns):
    return {col: calculate_metrics(predictions, pred_col=col) for col in columns if col in predictions.columns}


def append_experiment_log(output_dir, experiment_id, config, artifacts, split_info, feature_info, variant_metrics):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    rows = []
    for name, metrics in variant_metrics.items():
        rows.append(
            f"| `{name}` | {metrics['last_3m']['wmape']:.2f}% | "
            f"{metrics['last_14d']['wmape']:.2f}% | {metrics['last_3m']['n']} |"
        )

    text = [
        f"\n### {experiment_id}",
        "",
        f"- Split: train days `{split_info['train_days']}`, val days `{split_info['val_days']}`, test days `{split_info['test_days']}`.",
        f"- Test starts from day `{split_info['test_start_day']}`; evaluator uses one row per factual hour.",
        f"- Tree teacher source: `{split_info.get('tree_source', 'current')}`.",
        f"- History features `{feature_info['history_count']}`, future features `{feature_info['future_count']}`.",
        "- Anti-leakage: future raw market columns are excluded; future lag columns with lag < 24 are rejected; scalers fit on train only.",
        f"- Model: TCN residual-log hybrid, hidden `{config.hidden_dim}`, history `{config.history_len}`, dropout `{config.dropout}`.",
        f"- Weights: daytime `{config.daytime_weight}`, evening `{config.evening_weight}`, low-price `{config.low_price_weight}`, high-price `{config.high_price_weight}`, low BCE `{config.low_bce_weight}`, high BCE `{config.high_bce_weight}`.",
        "",
        "| variant | 3m WMAPE | 14d WMAPE | 3m rows |",
        "|---|---:|---:|---:|",
        *rows,
        "",
        f"- Predictions: `{artifacts['predictions_csv']}`",
        f"- Metrics: `{artifacts['metrics_json']}`",
        f"- Plot: `{artifacts['plot_png']}`",
    ]
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n".join(text) + "\n")
    return os.fspath(log_path)


def make_experiment_id(config):
    payload = json.dumps(asdict(config), sort_keys=True)
    return hashlib.md5(payload.encode("utf-8")).hexdigest()[:8]


def main():
    parser = argparse.ArgumentParser(description="Train leakage-aware neural residual day model over tree ensemble.")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--history-len", type=int, default=168)
    parser.add_argument("--val-days", type=int, default=45)
    parser.add_argument("--hidden-dim", type=int, default=96)
    parser.add_argument("--dropout", type=float, default=0.18)
    parser.add_argument("--lr", type=float, default=7e-4)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--models-dir", default=os.path.join(ROOT_DIR, "models_improved"))
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--experiment-id", default=None)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--tree-source", choices=["current", "split-safe"], default="current")
    parser.add_argument("--split-tree-models", default="et,lgbm")
    parser.add_argument("--daytime-weight", type=float, default=1.35)
    parser.add_argument("--evening-weight", type=float, default=1.35)
    parser.add_argument("--low-price-weight", type=float, default=1.45)
    parser.add_argument("--high-price-weight", type=float, default=1.45)
    parser.add_argument("--low-bce-weight", type=float, default=0.05)
    parser.add_argument("--high-bce-weight", type=float, default=0.05)
    args = parser.parse_args()

    config = ExperimentConfig(
        history_len=args.history_len,
        epochs=args.epochs,
        val_days=args.val_days,
        hidden_dim=args.hidden_dim,
        dropout=args.dropout,
        lr=args.lr,
        batch_size=args.batch_size,
        seed=args.seed,
        daytime_weight=args.daytime_weight,
        evening_weight=args.evening_weight,
        low_price_weight=args.low_price_weight,
        high_price_weight=args.high_price_weight,
        low_bce_weight=args.low_bce_weight,
        high_bce_weight=args.high_bce_weight,
    )
    seed_everything(config.seed)
    experiment_id = args.experiment_id or make_experiment_id(config)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"experiment_id={experiment_id}")
    print(f"device={args.device}")
    df = prepare_dataframe()
    train_days, val_days, test_days, test_start_ts = build_sample_dates(df, config)
    print(f"split train={len(train_days)} val={len(val_days)} test={len(test_days)} test_start={test_start_ts}")
    if args.tree_source == "split-safe":
        tree_train_end = val_days.min()
        tree_models = [model.strip() for model in args.split_tree_models.split(",") if model.strip()]
        print(f"tree_source=split-safe train_end={tree_train_end} models={tree_models}")
        df, tree_base_pred = train_split_safe_tree_predictions(df, tree_train_end, tree_models)
    else:
        print("tree_source=current models_improved")
        df, tree_base_pred = predict_tree_ensemble(df, args.models_dir)
    df["tree_base_pred"] = tree_base_pred
    df["tree_base_ratio"] = (df["tree_base_pred"] / df["price_cap"].replace(0, np.nan)).clip(0, 1.2)

    history_features, future_features = select_model_features(df)
    print(f"features history={len(history_features)} future={len(future_features)}")

    train_arrays = build_arrays(df, train_days, history_features, future_features, config)
    val_arrays = build_arrays(df, val_days, history_features, future_features, config)
    test_arrays = build_arrays(df, test_days, history_features, future_features, config)
    scaler_h, scaler_f = fit_transform_arrays(train_arrays, val_arrays, test_arrays)

    device = torch.device(args.device)
    model, train_history = train_model(
        train_arrays,
        val_arrays,
        history_dim=len(history_features),
        future_dim=len(future_features),
        config=config,
        device=device,
    )

    val_predictions = apply_blend(
        predict_arrays(model, val_arrays, device, config.batch_size),
        {"global_tree_weight": 1.0, "hourly_tree_weight": {h: 1.0 for h in range(24)}},
    )
    blend = tune_blend_weights(val_predictions, config)
    print(f"blend global_tree_weight={blend['global_tree_weight']:.3f}")

    test_predictions = predict_arrays(model, test_arrays, device, config.batch_size)
    test_predictions = apply_blend(test_predictions, blend)
    test_predictions = add_calibrated_variants(df, test_predictions)

    variant_cols = [
        "tree_base_pred",
        "tree_recent_calibrated_pred",
        "neural_pred",
        "hybrid_pred",
        "hybrid_recent_calibrated_pred",
        "hybrid_guarded_pred",
    ]
    variant_metrics = metrics_by_variant(test_predictions, variant_cols)
    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.2f}% "
            f"14d={metrics['last_14d']['wmape']:.2f}%"
        )

    primary_col = "hybrid_guarded_pred"
    artifacts = save_evaluation_artifacts(
        test_predictions,
        experiment_id=experiment_id,
        output_dir=output_dir,
        pred_col=primary_col,
    )
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_payload = json.load(f)
    metrics_payload["variant_metrics"] = variant_metrics
    metrics_payload["blend"] = blend
    metrics_payload["split"] = {
        "train_days": int(len(train_days)),
        "val_days": int(len(val_days)),
        "test_days": int(len(test_days)),
        "test_start_ts": str(test_start_ts),
        "tree_source": args.tree_source,
    }
    if args.tree_source == "split-safe":
        metrics_payload["split"]["tree_train_end"] = str(val_days.min())
        metrics_payload["split"]["split_tree_models"] = args.split_tree_models
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)

    model_path = output_dir / f"neural_experiment_{experiment_id}_model.pt"
    torch.save(
        {
            "model_state": model.state_dict(),
            "config": asdict(config),
            "history_features": history_features,
            "future_features": future_features,
            "blend": blend,
            "train_history": train_history,
        },
        model_path,
    )
    scaler_path = output_dir / f"neural_experiment_{experiment_id}_scalers.joblib"
    joblib.dump({"history": scaler_h, "future": scaler_f}, scaler_path)

    log_path = append_experiment_log(
        output_dir=output_dir,
        experiment_id=experiment_id,
        config=config,
        artifacts=artifacts,
        split_info={
            "train_days": int(len(train_days)),
            "val_days": int(len(val_days)),
            "test_days": int(len(test_days)),
            "test_start_day": str(test_days.min().date()),
            "tree_source": args.tree_source,
        },
        feature_info={
            "history_count": len(history_features),
            "future_count": len(future_features),
        },
        variant_metrics=variant_metrics,
    )
    print(f"saved model={model_path}")
    print(f"saved scalers={scaler_path}")
    print(f"updated log={log_path}")


if __name__ == "__main__":
    main()
