import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor
import joblib
import warnings
import os
import sys
import shutil
from datetime import datetime, timedelta
import matplotlib.ticker as ticker

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from train_model_v1 import generate_features, enforce_limits
from daily_profile_calibrator import apply_daily_profile_calibration
from prediction_limits import MIN_MARKET_PRICE, clip_price_forecast, clip_price_series
from recent_calibrator import (
    apply_day_regime_selector,
    apply_high_price_specialist,
    apply_low_price_specialist,
    apply_recent_hourly_ridge_calibration,
)

# === НАЛАШТУВАННЯ ===
warnings.filterwarnings('ignore')
sns.set_style("whitegrid")

def load_and_prepare_data(file_name="../data/ready_for_train.csv"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)

    print(f"⏳ Завантаження даних з {file_path}...")
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не знайдено!")
        return None

    df = pd.read_csv(file_path, decimal=',')

    if df.columns[0] == 'Unnamed: 0':
        df.rename(columns={'Unnamed: 0': 'date_str'}, inplace=True)
    else:
        df.rename(columns={df.columns[0]: 'date_str'}, inplace=True)

    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]

    for col in df.columns:
        if col != 'date_str' and col != 'day_of_week':
            if df[col].dtype == 'object':
                try: df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                except: pass
            try: df[col] = pd.to_numeric(df[col], errors='coerce')
            except: pass

    if 'hour' in df.columns:
        df = df.dropna(subset=['hour'])
        offset = 1 if (df['hour'].min() == 1 and df['hour'].max() == 24) else 0
        df['datetime'] = pd.to_datetime(df['date_str'], dayfirst=True) + pd.to_timedelta(df['hour'] - offset, unit='h')
        df.set_index('datetime', inplace=True)
        df.drop(columns=['date_str'], inplace=True)
    else:
        df.set_index('date_str', inplace=True)
        df.index = pd.to_datetime(df.index, dayfirst=True)

    df = df[df.index.notna()].sort_index()
    df = df[~df.index.duplicated(keep='first')]
    
    # Fill day_of_week if missing
    if 'day_of_week' in df.columns and (df['day_of_week'].isna().all() or (df['day_of_week'] == '').all()):
        days_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        df['day_of_week'] = df.index.dayofweek.map(days_map)
    
    df = enforce_limits(df)
    return df

def build_fallback_predictions(df_hist, target_index, caps):
    """Fallback forecast based on the most recent comparable hours."""
    if 'rdn_price' not in df_hist.columns or df_hist.empty:
        return pd.Series(np.nan, index=target_index, dtype='float64')

    hist_prices = df_hist['rdn_price']
    last_known_price = hist_prices.dropna().iloc[-1] if hist_prices.notna().any() else 0.0
    fallback = pd.Series(index=target_index, dtype='float64')

    for ts in target_index:
        candidates = []
        for lag in (24, 48, 168):
            lag_val = hist_prices.get(ts - timedelta(hours=lag))
            if pd.notna(lag_val):
                candidates.append(float(lag_val))

        fallback.loc[ts] = float(np.mean(candidates)) if candidates else float(last_known_price)

    if caps is not None:
        caps_series = pd.Series(caps, index=target_index, dtype='float64')
        fallback = clip_price_series(fallback, caps_series)
    else:
        fallback = clip_price_series(fallback)

    return fallback

def clean_prediction_inputs(df_full):
    """Fill exogenous gaps without leaking the target into future rows."""
    for flag_col in ['is_anomaly', 'is_attack', 'is_holiday']:
        if flag_col in df_full.columns:
            df_full[flag_col] = pd.to_numeric(df_full[flag_col], errors='coerce').fillna(0)

    weather_zero_fill = ['precip', 'snow', 'snow_depth', 'solarradiation', 'solarenergy', 'uvindex', 'cloudcover']
    for col in weather_zero_fill:
        if col in df_full.columns:
            df_full[col] = df_full[col].fillna(0)

    fill_exclude = {'price_cap', 'rdn_price'}
    fill_cols = [c for c in df_full.columns if c not in fill_exclude]
    if fill_cols:
        df_full[fill_cols] = df_full[fill_cols].replace([np.inf, -np.inf], np.nan)
        df_full[fill_cols] = df_full[fill_cols].ffill().bfill()

    return df_full

def expected_feature_names(model=None, booster=None):
    if model is not None and hasattr(model, 'feature_names_in_'):
        return list(model.feature_names_in_)
    if booster is None and model is not None and hasattr(model, 'get_booster'):
        try:
            booster = model.get_booster()
        except Exception:
            booster = None
    if booster is not None:
        if hasattr(booster, 'feature_names') and booster.feature_names:
            return list(booster.feature_names)
        if hasattr(booster, 'feature_name'):
            names = booster.feature_name()
            if names:
                return list(names)
    return None

def align_features(X, expected_names):
    if not expected_names:
        return X

    aligned = X.copy()
    for name in expected_names:
        if name not in aligned.columns:
            aligned[name] = 0.0
    return aligned[expected_names]

def repair_legacy_extra_trees(model):
    # ExtraTrees pickles created with older scikit-learn versions may miss
    # attributes that newer versions expect during prediction.
    if hasattr(model, 'estimators_'):
        for estimator in model.estimators_:
            if not hasattr(estimator, 'monotonic_cst'):
                estimator.monotonic_cst = None
    return model

def predict_tomorrow(target_date_str=None):
    # 1. Завантаження історичних даних
    df_all = load_and_prepare_data()
    if df_all is None:
        return

    if 'rdn_price' not in df_all.columns:
        print("❌ У датасеті відсутня колонка 'rdn_price'.")
        return

    df_hist = df_all.dropna(subset=['rdn_price']).copy()
    if df_hist.empty:
        print("❌ Немає історичних значень 'rdn_price' для побудови прогнозу.")
        return

    # 2. Підготовка "Завтра"
    last_date = df_hist.index[-1]
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, "%d.%m.%Y").date()
            cutoff_date = pd.Timestamp(target_date)
            df_hist = df_hist[df_hist.index < cutoff_date]
            if df_hist.empty:
                print("❌ Помилка: Немає історичних даних до обраної дати!")
                return
            last_date = df_hist.index[-1]
        except ValueError:
            print(f"❌ Невірний формат дати. Використовується наступний день від {last_date.date()}")
            target_date = (last_date + timedelta(days=1)).date()
    else:
        target_date = (last_date + timedelta(days=1)).date()

    future_start = pd.Timestamp(target_date)
    future_index = pd.date_range(start=future_start, periods=24, freq='H')
    print(f"🔮 Прогнозуємо період: {future_index[0]} - {future_index[-1]}")

    # Reuse future rows already present in CSV (weather, caps, etc.)
    df_future = df_all[df_all.index.normalize() == future_start].copy().reindex(future_index)
    df_full = pd.concat([df_hist, df_future], sort=False)
    df_full = df_full[~df_full.index.duplicated(keep='last')].sort_index()
    df_full = clean_prediction_inputs(df_full)
    df_full = enforce_limits(df_full)
    df_full.loc[future_index, 'rdn_price'] = np.nan
    df_full = generate_features(df_full)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "../models_improved")

    # Features (Must match train_model_v1.py)
    common_features = [
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'day_of_year_sin', 'day_of_year_cos', 'week_sin', 'week_cos',
        'is_winter', 'is_spring', 'is_summer', 'is_autumn', 'is_heating_season',
        'is_dst_period', 'is_dst_transition_day', 'days_to_dst_change',
        'cap_regime_all_day_15000', 'post_aug_2025_cap_change', 'post_jan_2026_cap_change',
        'post_apr_2026_cap_change', 'price_cap_norm',
        'is_off_day', 'price_cap', 'feelslike', 'windspeed', 'solarradiation',
        'heating_degree', 'cooling_degree', 'temp_hour_interaction', 'temp_summer_interaction',
        'solar_hour_interaction', 'solar_summer_interaction',
        'price_lag_24', 'price_lag_48', 'price_lag_168', 'price_lag_336',
        'ratio_lag_24', 'ratio_lag_48', 'ratio_lag_168',
        'price_lag_167', 'price_lag_169',
        'diff_24_48', 'diff_168_336',
        'rolling_mean_24', 'rolling_std_24', 'rolling_max_24', 'rolling_min_24',
        'rolling_mean_hour_3d', 'rolling_mean_hour_7d', 'rolling_mean_hour_14d',
        'ratio_mean_hour_3d', 'ratio_mean_hour_7d', 'ratio_mean_hour_14d',
        'hour_month_interaction', 'price_volatility_24', 'demand_supply_ratio_lag_24',
        'demand_ramp_std_24', 'supply_ramp_std_24',
        'rolling_mean_168', 'rolling_std_168',
        'price_ema_24', 'price_ema_168',
        'is_attack', 'days_since_attack', 'system_balance_lag_24', 'demand_x_price_lag_168',
        'dew', 'humidity', 'precip', 'snow', 'windgust', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility', 'uvindex'
    ]
    xgb_features_list = common_features + [
        'supply_lag_24', 'supply_lag_168', 
        'demand_ramp', 'supply_ramp',
        'garpok_lag_24', 'vdr_supply_lag_24'
    ]

    # Load Classifier for prob_low_price
    clf_path = os.path.join(models_dir, "low_price_classifier.json")
    if os.path.exists(clf_path):
        from xgboost import XGBClassifier
        clf = XGBClassifier()
        clf.load_model(clf_path)
        clf_features = expected_feature_names(model=clf) or [f for f in xgb_features_list if f in df_full.columns]
        df_full['prob_low_price'] = clf.predict_proba(align_features(df_full, clf_features))[:, 1]
        xgb_features_list.append('prob_low_price')

    # Load Hourly Weights
    import json
    weights_path = os.path.join(models_dir, "ensemble_weights.json")
    ensemble_weights = None
    if os.path.exists(weights_path):
        with open(weights_path, 'r') as f:
            ensemble_weights = json.load(f)
    
    # Drop features handled in training component
    features_to_drop = ['hour', 'is_anomaly']
    model_features = [f for f in xgb_features_list if f in df_full.columns and f not in features_to_drop]
    
    calibrator_start = future_start - timedelta(days=90)
    historical_scope = df_full.index[(df_full.index >= calibrator_start) & (df_full.index < future_start)]
    prediction_scope_index = historical_scope.union(future_index).sort_values()
    df_predict_scope = df_full.reindex(prediction_scope_index)
    fallback_predictions = build_fallback_predictions(
        df_hist,
        prediction_scope_index,
        df_predict_scope['price_cap'],
    )
    
    print(f"🚀 Застосування Ensemble (ET + XGB + LGBM) на {len(model_features)} ознаках...")
    
    predictions = pd.Series(index=prediction_scope_index, dtype='float64')
    
    for h in range(24):
        mask = (df_predict_scope.index.hour == h)
        if not mask.any():
            continue
        
        X_h = df_predict_scope.loc[mask, model_features].replace([np.inf, -np.inf], np.nan)
        caps = pd.to_numeric(df_predict_scope.loc[mask, 'price_cap'], errors='coerce').to_numpy(dtype='float64')
        fallback_h = fallback_predictions.loc[X_h.index].to_numpy(dtype='float64')

        valid_mask = (~X_h.isna().any(axis=1)).to_numpy() & np.isfinite(caps)
        if not valid_mask.any():
            predictions.loc[X_h.index] = fallback_h
            continue

        X_valid = X_h.loc[valid_mask]
        caps_valid = caps[valid_mask]
        fallback_valid = fallback_h[valid_mask]
        
        # Determine weights
        w_et, w_xgb, w_lgbm = 0.33, 0.33, 0.34
        if ensemble_weights is not None and str(h) in ensemble_weights:
            weights = ensemble_weights[str(h)]
            if len(weights) == 3:
                 w_et, w_xgb, w_lgbm = weights
            elif len(weights) == 2:
                 w_et, w_xgb = weights
                 w_lgbm = 0.0
        
        et_path = os.path.join(models_dir, f"et_hour_{h}.pkl")
        xgb_path = os.path.join(models_dir, f"xgb_hour_{h}.json")
        lgbm_path = os.path.join(models_dir, f"lgbm_hour_{h}.txt")
        
        et_ratio = None
        if os.path.exists(et_path):
            try:
                model_et = joblib.load(et_path)
                model_et = repair_legacy_extra_trees(model_et)
                X_model = align_features(X_valid, expected_feature_names(model=model_et))
                et_ratio = np.asarray(model_et.predict(X_model), dtype='float64')
            except Exception as e: print(f"Error ET h={h}: {e}")
            
        xgb_ratio = None
        if os.path.exists(xgb_path):
            try:
                model_xgb = XGBRegressor()
                model_xgb.load_model(xgb_path)
                X_model = align_features(X_valid, expected_feature_names(model=model_xgb))
                xgb_ratio = np.asarray(model_xgb.predict(X_model), dtype='float64')
            except Exception as e: print(f"Error XGB h={h}: {e}")
            
        lgbm_ratio = None
        if os.path.exists(lgbm_path):
            try:
                import lightgbm as lgb
                booster = lgb.Booster(model_file=lgbm_path)
                X_model = align_features(X_valid, expected_feature_names(booster=booster))
                lgbm_ratio = np.asarray(booster.predict(X_model), dtype='float64')
            except Exception as e: print(f"Error LGBM h={h}: {e}")
            
        combined = np.zeros(len(X_valid), dtype='float64')
        w_sum = np.zeros(len(X_valid), dtype='float64')

        for ratio, weight in ((et_ratio, w_et), (xgb_ratio, w_xgb), (lgbm_ratio, w_lgbm)):
            if ratio is None:
                continue
            finite_ratio = np.isfinite(ratio)
            combined[finite_ratio] += ratio[finite_ratio] * weight
            w_sum[finite_ratio] += weight

        final_valid = np.full(len(X_valid), np.nan, dtype='float64')
        ensemble_mask = w_sum > 0
        final_valid[ensemble_mask] = (combined[ensemble_mask] / w_sum[ensemble_mask]) * caps_valid[ensemble_mask]
        final_valid = np.where(np.isfinite(final_valid), final_valid, fallback_valid)
        final_valid = clip_price_forecast(final_valid, caps_valid)

        hour_predictions = pd.Series(fallback_h, index=X_h.index, dtype='float64')
        hour_predictions.loc[X_valid.index] = final_valid
        predictions.loc[X_h.index] = hour_predictions.values

    predictions = predictions.where(predictions.notna(), fallback_predictions)
    base_predictions = predictions.copy()
    ridge_predictions = apply_recent_hourly_ridge_calibration(df_full, base_predictions, future_index)
    low_predictions = apply_low_price_specialist(
        df_full,
        base_predictions,
        ridge_predictions,
        future_index,
    )
    daily_predictions = apply_daily_profile_calibration(
        df_full,
        low_predictions,
        future_index,
    )
    high_predictions = apply_high_price_specialist(
        df_full,
        base_predictions,
        daily_predictions,
        future_index,
    )
    calibrated_predictions = apply_day_regime_selector(
        df_full,
        base_predictions,
        ridge_predictions,
        low_predictions,
        high_predictions,
        future_index,
    )
    predictions = calibrated_predictions.where(
        calibrated_predictions.notna(),
        base_predictions.reindex(future_index),
    )
    df_predict = df_full.reindex(future_index)
    predictions = clip_price_series(predictions, df_predict['price_cap'])
             
    # 5. Візуалізація
    plt.figure(figsize=(15, 7))
    plt.plot(predictions.index.hour + 1, predictions, label='Ensemble Forecast', color='red', linewidth=2, marker='o')
    plt.plot(predictions.index.hour + 1, df_predict['price_cap'], label='Price Cap', color='green', linestyle='--', alpha=0.5)
    plt.axhline(MIN_MARKET_PRICE, label='Price Floor', color='gray', linestyle=':', alpha=0.5)
    
    plt.title(f"Прогноз цін на {target_date} (Ensemble V1)", fontsize=14)
    plt.xlabel("Година", fontsize=12)
    plt.ylabel("Ціна (грн/МВт·год)", fontsize=12)
    plt.xticks(range(1, 25))
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    output_dir = os.path.join(script_dir, "../output")
    os.makedirs(output_dir, exist_ok=True)

    output_png = os.path.join(output_dir, "prediction_tomorrow.png")
    plt.savefig(output_png)
    shutil.copy2(output_png, os.path.join(output_dir, "prediction_plot_v1.png"))
    print(f"✅ Графік збережено у {output_png}")
    
    print("\n📋 Результат прогнозу:")
    res = pd.DataFrame({
        'Hour': predictions.index.hour + 1,
        'Predicted_Price': predictions.values,
        'Price_Cap': df_predict['price_cap'].values
    })
    date_iso = pd.Timestamp(target_date).strftime("%Y-%m-%d")
    output_csv = os.path.join(output_dir, f"prediction_{date_iso}.csv")
    latest_csv = os.path.join(output_dir, "prediction_latest.csv")
    res.to_csv(output_csv, index=False)
    res.to_csv(latest_csv, index=False)
    print(f"✅ CSV прогнозу збережено у {output_csv}")
    print(res)

if __name__ == "__main__":
    target_date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    predict_tomorrow(target_date_arg)
