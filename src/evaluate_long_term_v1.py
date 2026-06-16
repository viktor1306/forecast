import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBRegressor
import joblib
import warnings
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from price_caps import apply_price_caps_to_index
from train_model_v1 import generate_features as shared_generate_features
from daily_profile_calibrator import apply_daily_profile_calibration
from recent_calibrator import (
    apply_day_regime_selector,
    apply_high_price_specialist,
    apply_low_price_specialist,
    apply_recent_hourly_ridge_calibration,
)

# === НАЛАШТУВАННЯ ===
warnings.filterwarnings('ignore')
sns.set_style("whitegrid")

# ==========================================
# 1. ЗАВАНТАЖЕННЯ ТА ПІДГОТОВКА ДАНИХ
# ==========================================
def load_data():
    print("⏳ Крок 1: Завантаження файлу...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(script_dir, "../data/ready_for_train.csv")

    if not os.path.exists(file_name):
        print(f"❌ Файл {file_name} не знайдено!")
        exit()

    df = pd.read_csv(file_name, decimal=',')

    if df.columns[0] == 'Unnamed: 0':
        df.rename(columns={'Unnamed: 0': 'date_str'}, inplace=True)
    else:
        df.rename(columns={df.columns[0]: 'date_str'}, inplace=True)

    df.columns = [str(c).strip().lower() for c in df.columns]

    # Robust numeric conversion handling comma decimals
    for col in df.columns:
        if col != 'date_str':
            # If column is object (string), try replacing comma with dot
            if df[col].dtype == 'object':
                try:
                    df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                except:
                    pass
            
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

    if 'hour' in df.columns:
        min_h = df['hour'].min()
        max_h = df['hour'].max()
        offset = 1 if (min_h == 1 and max_h == 24) else 0
        df['datetime'] = pd.to_datetime(df['date_str'], dayfirst=True) + pd.to_timedelta(df['hour'] - offset, unit='h')
        df.set_index('datetime', inplace=True)
        df.drop(columns=['date_str'], inplace=True)
    else:
        df.set_index('date_str', inplace=True)
        df.index = pd.to_datetime(df.index, dayfirst=True)

    df = df[df.index.notna()]
    df.index.name = 'Datetime'
    df = df[~df.index.duplicated(keep='first')]
    
    # Drop rows where target is missing (crucial for evaluation)
    if 'rdn_price' in df.columns:
        before_drop = len(df)
        df = df.dropna(subset=['rdn_price'])
        after_drop = len(df)
        if before_drop != after_drop:
            print(f"   ⚠️ Видалено {before_drop - after_drop} рядків з відсутньою ціною (rdn_price).")
            
    return df

def enforce_limits(df):
    """Установлює історично правильні прайскепи РДН/ВДР."""
    return apply_price_caps_to_index(df)

# ==========================================
# 2. ГЕНЕРАЦІЯ ФІЧ (ідентично до train_improved.py)
# ==========================================
def generate_features(df):
    print("⏳ Крок 2: Генерація розширених фіч...")
    target_col = 'rdn_price'
    
    # --- Свята ---
    holidays_str = [
        "07.01.2026", "01.01.2026", "31.12.2025", "24.12.2025", "01.10.2025", 
        "24.08.2025", "23.08.2025", "01.01.2025", "24.08.2024", "05.05.2024", 
        "07.01.2024", "01.01.2024"
    ]
    holiday_dates = pd.to_datetime(holidays_str, format='%d.%m.%Y').date
    df['date'] = df.index.date
    df['is_holiday'] = df['date'].isin(holiday_dates).astype(int)

    # --- Атаки ---
    attack_dates_str = [
        "10.01.2026", "09.01.2026", "04.01.2026", "03.01.2026", "02.01.2026", 
        "31.12.2025", "27.12.2025", "24.12.2025", "13.12.2025", "21.09.2025", 
        "31.08.2025", "24.08.2025", "24.02.2025", "23.02.2025", "22.02.2025", 
        "11.08.2024", "02.06.2024", "08.01.2024", "06.01.2024", "02.01.2024", "01.01.2024"
    ]
    attack_dates = pd.to_datetime(attack_dates_str, format='%d.%m.%Y').date
    df['is_attack'] = df['date'].isin(attack_dates).astype(int)
    
    # Days since last attack
    df['days_since_attack'] = 999
    for attack_date in attack_dates:
        mask = df['date'] >= attack_date
        if mask.any():
            days_diff = (df.index[mask].date - attack_date)
            # Convert timedelta to days
            days_int = np.array([d.days for d in days_diff])
            df.loc[mask, 'days_since_attack'] = np.minimum(df.loc[mask, 'days_since_attack'], days_int)
    df['days_since_attack'] = df['days_since_attack'].clip(upper=30)

    # --- Час ---
    df['day_of_week_num'] = df.index.dayofweek
    df['is_weekend'] = df['day_of_week_num'].isin([5, 6]).astype(int)
    df['is_off_day'] = np.maximum(df['is_weekend'], df['is_holiday'])
    
    df['hour'] = df.index.hour
    df['month'] = df.index.month
    
    # Cyclical time features
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week_num'] / 7.0)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week_num'] / 7.0)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)

    # --- Target Ratio ---
    if 'target_ratio' not in df.columns:
        df['target_ratio'] = df['rdn_price'] / df['price_cap']
        df['target_ratio'] = df['target_ratio'].clip(0, 1.1)

    # --- Lags ---
    lags = [24, 48, 72, 96, 168, 336] 
    for lag in lags:
        df[f'price_lag_{lag}'] = df[target_col].shift(lag)
        if 'rdn_supply' in df.columns: df[f'supply_lag_{lag}'] = df['rdn_supply'].shift(lag)
        if 'rdn_demand' in df.columns: df[f'demand_lag_{lag}'] = df['rdn_demand'].shift(lag)
        
        # Ratio Lags
        df[f'ratio_lag_{lag}'] = df['target_ratio'].shift(lag)
        
        if 'garpok_volume' in df.columns:
            df[f'garpok_lag_{lag}'] = df['garpok_volume'].shift(lag)
        if 'vdr_supply' in df.columns:
            df[f'vdr_supply_lag_{lag}'] = df['vdr_supply'].shift(lag)
        if 'vdr_demand' in df.columns:
            df[f'vdr_demand_lag_{lag}'] = df['vdr_demand'].shift(lag)

    # --- Сусідні лаги ---
    df['price_lag_23'] = df[target_col].shift(23)
    df['price_lag_25'] = df[target_col].shift(25)
    df['price_lag_167'] = df[target_col].shift(167)
    df['price_lag_169'] = df[target_col].shift(169)
    
    # --- Trends ---
    df['diff_24_48'] = df['price_lag_24'] - df['price_lag_48']
    df['diff_168_336'] = df['price_lag_168'] - df['price_lag_336']
    
    # --- Похідні (Lagged to avoid leakage) ---
    if 'rdn_demand' in df.columns:
        df['demand_ramp'] = df['rdn_demand'].shift(24) - df['rdn_demand'].shift(25)
    if 'rdn_supply' in df.columns:
        df['supply_ramp'] = df['rdn_supply'].shift(24) - df['rdn_supply'].shift(25)
    
    if 'rdn_supply' in df.columns and 'rdn_demand' in df.columns:
        df['system_balance_lag_24'] = df['rdn_supply'].shift(24) - df['rdn_demand'].shift(24)
        df['demand_x_price_lag_168'] = df['rdn_demand'].shift(24) * df['price_lag_168']

    # --- Rolling ---
    df['rolling_mean_24'] = df[target_col].shift(24).rolling(window=24).mean()
    df['rolling_std_24'] = df[target_col].shift(24).rolling(window=24).std()
    df['rolling_max_24'] = df[target_col].shift(24).rolling(window=24).max()
    df['rolling_min_24'] = df[target_col].shift(24).rolling(window=24).min()
    
    # NEW: Rolling mean for the SAME HOUR over last 3, 7, and 14 days
    df['rolling_mean_hour_3d'] = df.groupby('hour')[target_col].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['rolling_mean_hour_7d'] = df.groupby('hour')[target_col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    df['rolling_mean_hour_14d'] = df.groupby('hour')[target_col].transform(lambda x: x.shift(1).rolling(14, min_periods=1).mean())
    
    # Interaction: Month * Hour (Seasonality of daily profiles)
    df['hour_month_interaction'] = df['hour'] * df['month']
    
    # Robust NaN Handling
    if df.isna().any().any():
        for flag_col in ['is_anomaly', 'is_attack', 'is_holiday']:
            if flag_col in df.columns:
                df[flag_col] = pd.to_numeric(df[flag_col], errors='coerce').fillna(0).astype(int)

        weather_cols_zero_fill = ['precip', 'snow', 'snow_depth', 'solarradiation', 'solarenergy', 'uvindex', 'cloudcover']
        
        for col in weather_cols_zero_fill:
            if col in df.columns:
                df[col] = df[col].fillna(0)
                
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
             if col != target_col:
                  df[col] = df[col].interpolate(method='linear', limit_direction='both').fillna(method='ffill').fillna(method='bfill').fillna(0)
                  
    df = df.dropna()
    return df


def repair_legacy_extra_trees(model):
    if hasattr(model, 'estimators_'):
        for estimator in model.estimators_:
            if not hasattr(estimator, 'monotonic_cst'):
                estimator.monotonic_cst = None
    return model


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


# ==========================================
# 3. ОЦІНКА
# ==========================================
def evaluate_models(custom_output_name=None):
    # 1. Завантаження
    df = load_data()
    df = enforce_limits(df)
    df = shared_generate_features(df)
    
    if df.empty:
        print("❌ Помилка: Недостатньо даних для оцінки (після генерації фіч DataFrame порожній).")
        print("Переконайтеся, що у вас є дані хоча б за 15 днів.")
        return 0, 0

    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.getenv("MODELS_DIR_OVERRIDE", os.path.join(script_dir, "../models_improved"))
    
    if not os.path.exists(models_dir):
        print(f"❌ Папка {models_dir} не знайдена! Спочатку запустіть train_improved.py")
        return 0, 0

    # 2. Вибір періоду оцінки (останні 3 місяці або весь доступний період)
    eval_months = 3
    start_date = df.index[-1] - pd.DateOffset(months=eval_months)
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
        'hour_month_interaction',
        'price_volatility_24', 'demand_supply_ratio_lag_24',
        'demand_ramp_std_24', 'supply_ramp_std_24',
        'rolling_mean_168', 'rolling_std_168',
        'price_ema_24', 'price_ema_168',
        'is_attack', 'days_since_attack', 'system_balance_lag_24', 'demand_x_price_lag_168',
        'dew', 'humidity', 'precip', 'snow', 'windgust', 'winddir', 'sealevelpressure', 'cloudcover', 'visibility', 'uvindex'
    ]

    
    xgb_features = common_features + [
        'supply_lag_24', 'supply_lag_168', 
        'demand_ramp', 'supply_ramp',
        'garpok_lag_24', 'vdr_supply_lag_24'
    ]

    import json
    weights_path = os.path.join(models_dir, "ensemble_weights.json")
    ensemble_weights = None
    if os.path.exists(weights_path):
        with open(weights_path, 'r') as f:
            ensemble_weights = json.load(f)
    
    # Load Classifier
    clf_path = os.path.join(models_dir, "low_price_classifier.json")
    if os.path.exists(clf_path):
        from xgboost import XGBClassifier
        clf = XGBClassifier()
        clf.load_model(clf_path)
        clf_features = expected_feature_names(model=clf) or [f for f in xgb_features if f in df.columns]
        probs = clf.predict_proba(align_features(df, clf_features))[:, 1]
        df['prob_low_price'] = probs
        xgb_features.append('prob_low_price')

    xgb_features = [f for f in xgb_features if f in df.columns]
    start_idx = df.index.get_slice_bound(start_date, 'left')
    df_eval = df.iloc[start_idx:]
    
    # Define features dropped inside training
    features_to_drop = ['hour', 'is_anomaly']
    model_features = [f for f in xgb_features if f not in features_to_drop]
    X_eval_cols = list(dict.fromkeys(model_features + ['hour', 'price_cap']))
    X_eval = df[X_eval_cols]
    y_eval = df_eval['rdn_price']
    
    from lightgbm import LGBMRegressor
    import lightgbm as lgb
    
    pred_all = pd.Series(index=X_eval.index, dtype='float64')
    
    for h in range(24):
        mask = (X_eval['hour'] == h)
        if not mask.any(): continue
        X_h = X_eval[mask]
        X_pred = X_h[model_features]
        
        et_path = os.path.join(models_dir, f"et_hour_{h}.pkl")
        if os.path.exists(et_path):
            model_et = repair_legacy_extra_trees(joblib.load(et_path))
            et_pred = model_et.predict(align_features(X_pred, expected_feature_names(model=model_et)))
        else:
            et_pred = None
        
        xgb_path = os.path.join(models_dir, f"xgb_hour_{h}.json")
        if os.path.exists(xgb_path):
            m_xgb = XGBRegressor(); m_xgb.load_model(xgb_path)
            xgb_pred = m_xgb.predict(align_features(X_pred, expected_feature_names(model=m_xgb)))
        else: xgb_pred = None
                
        lgbm_path = os.path.join(models_dir, f"lgbm_hour_{h}.txt")
        if os.path.exists(lgbm_path):
            booster_lgbm = lgb.Booster(model_file=lgbm_path)
            lgbm_pred = booster_lgbm.predict(align_features(X_pred, expected_feature_names(booster=booster_lgbm)))
        else:
            lgbm_pred = None
        
        caps = X_h['price_cap'].values
        w_et, w_xgb, w_lgbm = 0.33, 0.33, 0.34
        if ensemble_weights and str(h) in ensemble_weights:
            weights = ensemble_weights[str(h)]
            if len(weights) == 3: w_et, w_xgb, w_lgbm = weights
        
        combined_ratio = np.zeros(len(X_h))
        sw = 0.0
        if et_pred is not None: combined_ratio += et_pred * w_et; sw += w_et
        if xgb_pred is not None: combined_ratio += xgb_pred * w_xgb; sw += w_xgb
        if lgbm_pred is not None: combined_ratio += lgbm_pred * w_lgbm; sw += w_lgbm
             
        if sw > 0:
            p_price = (combined_ratio / sw) * caps
            p_price = np.clip(p_price, 0, caps)
            pred_all.loc[X_h.index] = p_price

    pred_all = pred_all.dropna().sort_index()
    pred_ensemble = pred_all.loc[pred_all.index.intersection(df_eval.index)]
    y_true = y_eval.loc[pred_ensemble.index]

    base_pred_ensemble = pred_ensemble.copy()
    
    base_wmape_3m = np.sum(np.abs(y_true - base_pred_ensemble)) / np.sum(y_true) * 100
    
    # WMAPE 14 days
    last_14_days = 14 * 24
    base_wmape_14d = 0
    if len(y_true) > last_14_days:
        y_last = y_true.iloc[-last_14_days:]
        p_last = base_pred_ensemble.loc[y_last.index]
        base_wmape_14d = np.sum(np.abs(y_last - p_last)) / np.sum(y_last) * 100

        ridge_last = apply_recent_hourly_ridge_calibration(df, pred_all, y_last.index)
        low_last = apply_low_price_specialist(df, pred_all, ridge_last, y_last.index)
        daily_last = apply_daily_profile_calibration(df, low_last, y_last.index)
        high_last = apply_high_price_specialist(df, pred_all, daily_last, y_last.index)
        calibrated_last = apply_day_regime_selector(
            df,
            pred_all,
            ridge_last,
            low_last,
            high_last,
            y_last.index,
        )
        pred_ensemble.loc[y_last.index] = calibrated_last.loc[y_last.index]

    wmape_3m = np.sum(np.abs(y_true - pred_ensemble)) / np.sum(y_true) * 100

    wmape_14d = 0
    if len(y_true) > last_14_days:
        y_last = y_true.iloc[-last_14_days:]
        p_last = pred_ensemble.loc[y_last.index]
        wmape_14d = np.sum(np.abs(y_last - p_last)) / np.sum(y_last) * 100
    
    print(
        f"📊 LONG TERM: {wmape_3m:.2f}% | 14 DAYS: {wmape_14d:.2f}% "
        f"(base: {base_wmape_3m:.2f}% / {base_wmape_14d:.2f}%)"
    )
    
    # 5. Візуалізація
    plt.figure(figsize=(15, 7))
    plt.subplot(2, 1, 1)
    plt.plot(y_true.index, y_true, label='Fact', color='black', alpha=0.5)
    plt.plot(pred_ensemble.index, pred_ensemble, label='Pred', color='red', alpha=0.7)
    plt.title(f'Evaluation {eval_months} months (WMAPE: {wmape_3m:.2f}%)')
    plt.legend(); plt.grid(True)
    
    plt.subplot(2, 1, 2)
    if len(y_true) > last_14_days:
        y_14 = y_true.iloc[-last_14_days:]
        plt.plot(y_14.index, y_14, color='black', label='Fact')
        plt.plot(y_14.index, pred_ensemble.loc[y_14.index], color='red', label='Pred')
        plt.title(f'Focus: Last 14 Days (WMAPE: {wmape_14d:.2f}%)')
    
    plt.tight_layout()
    img_name = custom_output_name if custom_output_name else "evaluation_improved.png"
    output_png = os.path.join(script_dir, "../output", img_name)
    plt.savefig(output_png)
    plt.close()
    
    return wmape_14d, wmape_3m

if __name__ == "__main__":
    evaluate_models()
