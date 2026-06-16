import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import ExtraTreesRegressor
from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor
import joblib
import os
import sys
import warnings
import json
import optuna
import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from price_caps import apply_price_caps_to_index
from prediction_limits import clip_price_forecast

# === НАЛАШТУВАННЯ ===
warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
TEST_DAYS = 14
TUNE_HYPERPARAMS = True # Включіть для автоматичного пошуку кращих параметрів (це займе час)
OPTUNA_TRIALS = 20        # Кількість спроб для кожної моделі
USE_GPU = os.getenv("USE_GPU", "0").lower() in ("1", "true", "yes", "on")

# Відключення логів Optuna для чистоти консолі
optuna.logging.set_verbosity(optuna.logging.WARNING)

def xgb_runtime_params():
    if USE_GPU:
        return {'tree_method': 'hist', 'device': 'cuda'}
    return {'tree_method': 'hist'}

def last_sunday(year, month):
    day = pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)
    while day.weekday() != 6:
        day -= pd.Timedelta(days=1)
    return day.date()

# ==========================================
# 1. ЗАВАНТАЖЕННЯ ТА ПІДГОТОВКА ДАНИХ
# ==========================================
def load_data():
    print("Step 1: Loading file...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(script_dir, "../data/ready_for_train.csv")

    if not os.path.exists(file_name):
        print(f"Error: File {file_name} not found!")
        exit()

    df = pd.read_csv(file_name, decimal=',')

    if df.columns[0] == 'Unnamed: 0':
        df.rename(columns={'Unnamed: 0': 'date_str'}, inplace=True)
    else:
        df.rename(columns={df.columns[0]: 'date_str'}, inplace=True)

    df.columns = [str(c).strip().lower() for c in df.columns]

    # Remove unnamed columns (artifacts from CSV saving)
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]
    
    # Robust numeric conversion handling comma decimals
    for col in df.columns:
        if col != 'date_str' and col != 'day_of_week':
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
        min_h = df['hour'].apply(lambda x: x if not pd.isna(x) else 1).astype(int).min()
        max_h = df['hour'].apply(lambda x: x if not pd.isna(x) else 24).astype(int).max()
        offset = 1 if (min_h == 1 and max_h == 24) else 0
        
        # Drop rows where hour is NaN before creating index
        df = df.dropna(subset=['hour'])
        
        df['datetime'] = pd.to_datetime(df['date_str'], dayfirst=True) + pd.to_timedelta(df['hour'] - offset, unit='h')
        df.set_index('datetime', inplace=True)
        df.drop(columns=['date_str'], inplace=True)
    else:
        df.set_index('date_str', inplace=True)
        df.index = pd.to_datetime(df.index, dayfirst=True)

    df = df[df.index.notna()]
    df.index.name = 'Datetime'
    df = df[~df.index.duplicated(keep='first')]
    
    # Fill day_of_week if missing (User Requirement)
    if 'day_of_week' in df.columns:
        # Check if it's empty or all NaNs
        if df['day_of_week'].isna().all() or (df['day_of_week'] == '').all():
            # Map 0=Monday, ... 6=Sunday
            days_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
            df['day_of_week'] = df.index.dayofweek.map(days_map)
            print("   [OK] Restored column 'day_of_week' from date.")

    # Drop rows where target is missing (crucial for evaluation)
    if 'rdn_price' in df.columns:
        before_drop = len(df)
        df = df.dropna(subset=['rdn_price'])
        after_drop = len(df)
        if before_drop != after_drop:
            print(f"   Warning: Deleted {before_drop - after_drop} rows with missing rdn_price.")
    
    print(f"   Data loaded. Shape: {df.shape}")
            
    return df

def enforce_limits(df):
    """Установлює історично правильні прайскепи РДН/ВДР."""
    return apply_price_caps_to_index(df)

# ==========================================
# 2. ГЕНЕРАЦІЯ ФІЧ
# ==========================================
def generate_features(df):
    print("Step 2: Generating features...")
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
        mask = df.index.date >= attack_date
        if mask.any():
            days_diff = (df.loc[mask, 'date'] - attack_date)
            days_int = np.array([d.days for d in days_diff])
            df.loc[mask, 'days_since_attack'] = np.minimum(df.loc[mask, 'days_since_attack'], days_int)
    df['days_since_attack'] = df['days_since_attack'].clip(upper=30)

    # --- Час ---
    df['day_of_week_num'] = df.index.dayofweek
    df['is_weekend'] = df['day_of_week_num'].isin([5, 6]).astype(int)
    df['is_off_day'] = np.maximum(df['is_weekend'], df['is_holiday'])
    
    df['hour'] = df.index.hour
    df['month'] = df.index.month
    df['day_of_year'] = df.index.dayofyear
    iso_week = df.index.isocalendar().week.astype(int)
    
    # Cyclical time features
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week_num'] / 7.0)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week_num'] / 7.0)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12.0)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12.0)
    df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 366.0)
    df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 366.0)
    df['week_sin'] = np.sin(2 * np.pi * iso_week / 53.0)
    df['week_cos'] = np.cos(2 * np.pi * iso_week / 53.0)

    # --- Season and market regime ---
    df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
    df['is_spring'] = df['month'].isin([3, 4, 5]).astype(int)
    df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
    df['is_autumn'] = df['month'].isin([9, 10, 11]).astype(int)
    df['is_heating_season'] = df['month'].isin([10, 11, 12, 1, 2, 3]).astype(int)

    years = range(df.index.year.min(), df.index.year.max() + 1)
    dst_start = {year: last_sunday(year, 3) for year in years}
    dst_end = {year: last_sunday(year, 10) for year in years}
    date_values = pd.Series(df.index.date, index=df.index)
    df['is_dst_period'] = [
        int(dst_start[d.year] <= d < dst_end[d.year])
        for d in date_values
    ]
    transition_dates = set(dst_start.values()) | set(dst_end.values())
    df['is_dst_transition_day'] = date_values.isin(transition_dates).astype(int).values
    df['days_to_dst_change'] = [
        min(abs((d - t).days) for t in transition_dates)
        for d in date_values
    ]
    df['days_to_dst_change'] = pd.Series(df['days_to_dst_change'], index=df.index).clip(upper=14)

    all_day_cap_15000 = (
        ((df.index >= pd.Timestamp('2026-01-17')) & (df.index < pd.Timestamp('2026-03-31'))) |
        (df.index >= pd.Timestamp('2026-04-30'))
    )
    df['cap_regime_all_day_15000'] = all_day_cap_15000.astype(int)
    df['post_aug_2025_cap_change'] = (df.index >= pd.Timestamp('2025-08-01')).astype(int)
    df['post_jan_2026_cap_change'] = (df.index >= pd.Timestamp('2026-01-17')).astype(int)
    df['post_apr_2026_cap_change'] = (df.index >= pd.Timestamp('2026-04-30')).astype(int)
    df['price_cap_norm'] = df['price_cap'] / 15000.0

    if 'feelslike' in df.columns:
        feels = pd.to_numeric(df['feelslike'], errors='coerce')
        df['heating_degree'] = (18.0 - feels).clip(lower=0)
        df['cooling_degree'] = (feels - 22.0).clip(lower=0)
        df['temp_hour_interaction'] = feels * df['hour']
        df['temp_summer_interaction'] = feels * df['is_summer']
    if 'solarradiation' in df.columns:
        solar = pd.to_numeric(df['solarradiation'], errors='coerce')
        df['solar_hour_interaction'] = solar * df['hour']
        df['solar_summer_interaction'] = solar * df['is_summer']

    # --- Target Ratio ---
    # Add target_ratio for training
    if 'target_ratio' not in df.columns:
        df['target_ratio'] = df['rdn_price'] / df['price_cap']
        df['target_ratio'] = df['target_ratio'].clip(0, 1.1)

    # --- Lags ---
    lags = [24, 48, 72, 96, 168, 336] 
    for lag in lags:
        df[f'price_lag_{lag}'] = df[target_col].shift(lag)
        df[f'supply_lag_{lag}'] = df['rdn_supply'].shift(lag)
        df[f'demand_lag_{lag}'] = df['rdn_demand'].shift(lag)
        
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
    
    # --- Нові фічі (Trends & Volatility) ---
    df['diff_24_48'] = df['price_lag_24'] - df['price_lag_48']
    df['diff_168_336'] = df['price_lag_168'] - df['price_lag_336']
    
    # --- Похідні (Lagged to avoid leakage) ---
    df['demand_ramp'] = df['rdn_demand'].shift(24) - df['rdn_demand'].shift(25)
    df['supply_ramp'] = df['rdn_supply'].shift(24) - df['rdn_supply'].shift(25)
    df['system_balance_lag_24'] = df['rdn_supply'].shift(24) - df['rdn_demand'].shift(24)
    
    # Interaction
    df['demand_x_price_lag_168'] = df['rdn_demand'].shift(24) * df['price_lag_168']

    # --- Rolling ---
    df['rolling_mean_24'] = df[target_col].shift(24).rolling(window=24).mean()
    df['rolling_std_24'] = df[target_col].shift(24).rolling(window=24).std()
    df['rolling_max_24'] = df[target_col].shift(24).rolling(window=24).max()
    df['rolling_min_24'] = df[target_col].shift(24).rolling(window=24).min()
    df['rolling_mean_168'] = df[target_col].shift(24).rolling(window=168).mean()
    df['rolling_std_168'] = df[target_col].shift(24).rolling(window=168).std()
    df['price_volatility_24'] = df['rolling_std_24'] / (df['rolling_mean_24'].abs() + 1e-6)
    df['price_ema_24'] = df[target_col].shift(24).ewm(span=24, adjust=False).mean()
    df['price_ema_168'] = df[target_col].shift(24).ewm(span=168, adjust=False).mean()
    df['demand_supply_ratio_lag_24'] = df['rdn_demand'].shift(24) / (df['rdn_supply'].shift(24).abs() + 1e-6)
    df['demand_ramp_std_24'] = df['demand_ramp'].rolling(window=24, min_periods=1).std()
    df['supply_ramp_std_24'] = df['supply_ramp'].rolling(window=24, min_periods=1).std()
    
    # NEW: Rolling mean for the SAME HOUR over last 3 and 7 days
    # This is extremely powerful for catching level shifts in daily cycles.
    df['rolling_mean_hour_3d'] = df.groupby('hour')[target_col].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['rolling_mean_hour_7d'] = df.groupby('hour')[target_col].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    df['rolling_mean_hour_14d'] = df.groupby('hour')[target_col].transform(lambda x: x.shift(1).rolling(14, min_periods=1).mean())
    df['ratio_mean_hour_3d'] = df.groupby('hour')['target_ratio'].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    df['ratio_mean_hour_7d'] = df.groupby('hour')['target_ratio'].transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    df['ratio_mean_hour_14d'] = df.groupby('hour')['target_ratio'].transform(lambda x: x.shift(1).rolling(14, min_periods=1).mean())
    
    # Interaction: Month * Hour (Seasonality of daily profiles)
    df['hour_month_interaction'] = df['hour'] * df['month']
    
    # ... (rest of feature generation)
    for flag_col in ['is_anomaly', 'is_attack', 'is_holiday']:
        if flag_col in df.columns:
            df[flag_col] = pd.to_numeric(df[flag_col], errors='coerce').fillna(0).astype(int)

    weather_zero_fill = ['precip', 'snow', 'snow_depth', 'solarradiation', 'solarenergy', 'uvindex', 'cloudcover']
    for col in weather_zero_fill:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col not in [target_col, 'target_ratio']:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan).ffill().bfill()
    
    # Final check: Drop rows where CRITICAL features are still NaN
    # We don't drop rows with NaN target if we are in prediction mode
    feature_cols = [c for c in df.columns if c not in [target_col, 'target_ratio', 'date', 'is_anomaly']]
    df = df.dropna(subset=feature_cols)
    print(f"   Features generated. Final Shape: {df.shape}")
    return df

# ==========================================
# 2.5 CLASSIFICATION FEATURE
# ==========================================
def add_classification_feature(df, train_size, features, script_dir):
    print("Training Classifier (Low Price Probability)...")
    threshold = 3000
    df['is_low_price'] = (df['rdn_price'] < threshold).astype(int)
    
    if train_size < len(df):
        split_date = df.index[train_size]
    else:
        split_date = df.index[-1] + pd.Timedelta(hours=1)
        
    X_train = df[df.index < split_date][features]
    y_train = df[df.index < split_date]['is_low_price']
    
    clf = XGBClassifier(
        n_estimators=500, learning_rate=0.05, max_depth=6,
        subsample=0.8, colsample_bytree=0.8, n_jobs=-1,
        random_state=42, eval_metric='logloss',
        **xgb_runtime_params()
    )
    clf.fit(X_train, y_train)
    
    probs = clf.predict_proba(df[features])[:, 1]
    df['prob_low_price'] = probs
    
    models_dir = os.path.join(script_dir, "../models_improved")
    if not os.path.exists(models_dir): os.makedirs(models_dir)
    clf.save_model(os.path.join(models_dir, "low_price_classifier.json"))
    
    print("   Classifier trained. Feature 'prob_low_price' added.")
    return df

# ==========================================
# 3. OPTUNA TUNING
# ==========================================
def tune_model_params(df, train_size, features, target_col, model_type='xgb'):
    """Tunes global hyperparameters for a model type using Optuna"""
    print(f"   🔍 Optuna: Tuning {model_type}...")
    X = df[features].iloc[:train_size]
    y = df[target_col].iloc[:train_size]
    
    if len(X) > 720:
        X = X.iloc[-720:]
        y = y.iloc[-720:]

    def objective(trial):
        if model_type == 'et':
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 200, 1000),
                'max_depth': trial.suggest_int('max_depth', 20, 45),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 8)
            }
            model = ExtraTreesRegressor(**params, n_jobs=-1, random_state=42)
        elif model_type == 'xgb':
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 500, 2000),
                'max_depth': trial.suggest_int('max_depth', 4, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.05),
                'subsample': trial.suggest_float('subsample', 0.6, 0.9),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 0.9)
            }
            model = XGBRegressor(**params, objective='reg:absoluteerror', n_jobs=-1, random_state=42)
            model.set_params(**xgb_runtime_params())
        else: # lgbm
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 500, 2000),
                'max_depth': trial.suggest_int('max_depth', 4, 15),
                'num_leaves': trial.suggest_int('num_leaves', 20, 150),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1)
            }
            model = LGBMRegressor(**params, objective='mae', n_jobs=-1, random_state=42, verbosity=-1)

        split = int(len(X) * 0.8)
        model.fit(X.iloc[:split], y.iloc[:split])
        preds = model.predict(X.iloc[split:])
        return mean_absolute_error(y.iloc[split:], preds)

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=OPTUNA_TRIALS)
    return study.best_params

def tune_ensemble_weights_optuna(y_true, p_et, p_xgb, p_lgbm):
    """Finds best weights for ensemble using Optuna"""
    def objective(trial):
        w_et = trial.suggest_float('w_et', 0, 1)
        w_xgb = trial.suggest_float('w_xgb', 0, 1)
        w_lgbm = trial.suggest_float('w_lgbm', 0, 1)
        
        tw = w_et + w_xgb + w_lgbm + 1e-6
        pred = (p_et * w_et + p_xgb * w_xgb + p_lgbm * w_lgbm) / tw
        return np.sum(np.abs(y_true - pred)) / (np.sum(y_true) + 1e-6)

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=50)
    
    b = study.best_params
    tw = b['w_et'] + b['w_xgb'] + b['w_lgbm'] + 1e-6
    return (b['w_et']/tw, b['w_xgb']/tw, b['w_lgbm']/tw)

def main():
    df = load_data()
    df = enforce_limits(df)
    df = generate_features(df)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
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
    
    xgb_features = common_features + [
        'supply_lag_24', 'supply_lag_168', 
        'demand_ramp', 'supply_ramp',
        'garpok_lag_24', 'vdr_supply_lag_24'
    ]
    
    # Filter features that actually exist
    xgb_features = [f for f in xgb_features if f in df.columns]

    # Explicitly remove 'is_anomaly' if it got in there
    if 'is_anomaly' in xgb_features:
        xgb_features.remove('is_anomaly')
    
    # Split
    hours_in_test = TEST_DAYS * 24
    if len(df) <= hours_in_test:
        train_size = len(df)
    else:
        train_size = len(df) - hours_in_test
    
    # 0. Train Classifier
    add_classification_feature(df, train_size, xgb_features, script_dir)
    xgb_features_reg = xgb_features + ['prob_low_price']
    
    # --- Optuna Global Tuning ---
    best_params = {'et': {}, 'xgb': {}, 'lgbm': {}}
    if TUNE_HYPERPARAMS:
        best_params['et'] = tune_model_params(df, train_size, xgb_features_reg, 'target_ratio', model_type='et')
        best_params['xgb'] = tune_model_params(df, train_size, xgb_features_reg, 'target_ratio', model_type='xgb')
        best_params['lgbm'] = tune_model_params(df, train_size, xgb_features_reg, 'target_ratio', model_type='lgbm')

    # 1-3. Train Ensemble Components
    print("\n   TRAINING ENSEMBLE COMPONENTS...")
    pred_et = train_ensemble_component(df, train_size, xgb_features_reg, 'target_ratio', script_dir, model_type='et', tuned_params=best_params['et'])
    pred_xgb = train_ensemble_component(df, train_size, xgb_features_reg, 'target_ratio', script_dir, model_type='xgb', tuned_params=best_params['xgb'])
    pred_lgbm = train_ensemble_component(df, train_size, xgb_features_reg, 'target_ratio', script_dir, model_type='lgbm', tuned_params=best_params['lgbm'])

    # 4. Hourly Weighted Ensemble
    y_test = df['rdn_price'].iloc[train_size:]
    if len(y_test) > 0:
        common_idx = pred_et.index.intersection(pred_xgb.index).intersection(pred_lgbm.index).intersection(y_test.index)
        if len(common_idx) > 0:
            p_et = pred_et.loc[common_idx]
            p_xgb = pred_xgb.loc[common_idx]
            p_lgbm = pred_lgbm.loc[common_idx]
            y_true = y_test.loc[common_idx]
            
            hourly_weights = {}
            for h in range(24):
                mask_h = (common_idx.hour == h)
                if mask_h.any():
                    hourly_weights[h] = tune_ensemble_weights_optuna(y_true[mask_h], p_et[mask_h], p_xgb[mask_h], p_lgbm[mask_h])
            
            weights_path = os.path.join(script_dir, "../models_improved/ensemble_weights.json")
            with open(weights_path, 'w') as f:
                json.dump({str(k): v for k, v in hourly_weights.items()}, f)
            print(f"✅ Ensemble weights saved.")

    # ==========================================
    # FINAL: INTEGRATED EVALUATION
    # ==========================================
    print("\n🚀 Starting Integrated Evaluation...")
    try:
        from evaluate_long_term_v1 import evaluate_models
        
        # Unique Hash for the run
        import hashlib
        import time
        run_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        
        # Initial run to get metrics
        w_14d, w_3m = evaluate_models(custom_output_name=f"temp_eval.png")
        
        # Rename with metrics
        final_img_name = f"v1_14d_{w_14d:.2f}_3m_{w_3m:.2f}_{run_id}.png"
        old_path = os.path.join(script_dir, "../output/temp_eval.png")
        new_path = os.path.join(script_dir, "../output", final_img_name)
        
        if os.path.exists(old_path):
            if os.path.exists(new_path): os.remove(new_path)
            os.rename(old_path, new_path)
            # Also keep a "latest" copy
            import shutil
            shutil.copy2(new_path, os.path.join(script_dir, "../output/evaluation_latest.png"))
            print(f"✅ Evaluation complete! Report saved as: {final_img_name}")
            print(f"✅ Summary: 14 Days WMAPE: {w_14d:.2f}%, 3 Months WMAPE: {w_3m:.2f}%")
        
    except Exception as e:
        print(f"❌ Error during integrated evaluation: {e}")

def train_ensemble_component(df, train_size, features, target_col, script_dir, model_type='et', tuned_params=None):
    """Trains a specific model type with enhanced recency weighting"""
    models_dir = os.path.join(script_dir, "../models_improved")
    if not os.path.exists(models_dir): os.makedirs(models_dir)
        
    X = df[features].drop(columns=['hour'], errors='ignore')
    y = df[target_col]
    
    X_train = X.iloc[:train_size]
    y_train = y.iloc[:train_size]
    X_test = X.iloc[train_size:]
    
    pred_all = pd.Series(index=X_test.index, dtype='float64')
    
    for h in range(24):
        mask_train = (df.iloc[:train_size]['hour'] == h)
        if not mask_train.any(): continue
        
        X_train_h = X_train[mask_train]; y_train_h = y_train[mask_train]
        mask_test = (df.iloc[train_size:]['hour'] == h)
        X_test_h = X_test[mask_test]
        
        # --- ENHANCED WEIGHTING ---
        # Very aggressive weight on recent days to catch new market trends
        dates_h = df.index[:train_size][mask_train]
        time_weights = np.linspace(0.1, 1.0, len(X_train_h))
        
        # Multipliers for specific periods
        m_weights = time_weights.copy()
        
        # Last 30 days get 2x boost
        last_30d = df.index[train_size-1] - pd.Timedelta(days=30)
        m_weights[dates_h > last_30d] *= 2.0
        
        # Last 7 days get another 2x boost (total 4x)
        last_7d = df.index[train_size-1] - pd.Timedelta(days=7)
        m_weights[dates_h > last_7d] *= 2.0
        
        # Post-rule change boost
        change_date = pd.Timestamp('2025-08-01')
        m_weights[dates_h >= change_date] *= 2.0

        # Reduce weight for attacks
        is_attack_h = df.iloc[:train_size][mask_train]['is_attack'].values
        m_weights[is_attack_h == 1] *= 0.3

        if model_type == 'et':
            params = {'n_estimators': 3000, 'max_depth': 40, 'min_samples_leaf': 2, 'bootstrap': True, 'n_jobs': -1, 'random_state': 42}
            if tuned_params: params.update(tuned_params)
            model = ExtraTreesRegressor(**params)
        elif model_type == 'xgb':
            params = {'n_estimators': 2000, 'learning_rate': 0.015, 'max_depth': 8, 'subsample': 0.8, 'colsample_bytree': 0.8, 'objective': 'reg:absoluteerror', 'n_jobs': -1, 'random_state': 42}
            if tuned_params: params.update(tuned_params)
            params.update(xgb_runtime_params())
            model = XGBRegressor(**params)
        elif model_type == 'lgbm':
            params = {'n_estimators': 2000, 'learning_rate': 0.02, 'num_leaves': 63, 'max_depth': 10, 'objective': 'mae', 'verbosity': -1, 'n_jobs': -1, 'random_state': 42}
            if tuned_params: params.update(tuned_params)
            model = LGBMRegressor(**params)
            
        model.fit(X_train_h, y_train_h, sample_weight=m_weights)
        
        # Save
        if model_type == 'et': joblib.dump(model, os.path.join(models_dir, f"et_hour_{h}.pkl"))
        elif model_type == 'xgb': model.save_model(os.path.join(models_dir, f"xgb_hour_{h}.json"))
        elif model_type == 'lgbm': model.booster_.save_model(os.path.join(models_dir, f"lgbm_hour_{h}.txt"))
        
        if len(X_test_h) > 0:
            p_price = model.predict(X_test_h) * df.loc[X_test_h.index, 'price_cap'].values
            pred_all.loc[X_test_h.index] = clip_price_forecast(p_price, df.loc[X_test_h.index, 'price_cap'].values)
            
        print(".", end="", flush=True)
        
    return pred_all.sort_index()

if __name__ == "__main__":
    main()
