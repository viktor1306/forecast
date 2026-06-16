import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import os
import sys

# Add current directory to path to import from train_model_v1
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from train_model_v1 import load_data, generate_features, enforce_limits

def get_feature_importance():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, "../models_improved")
    
    # Define features (must match training)
    common_features = [
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'is_off_day', 'price_cap', 'feelslike', 'windspeed', 'solar_radiation',
        'price_lag_24', 'price_lag_48', 'price_lag_168', 'price_lag_336',
        'price_lag_167', 'price_lag_169',
        'diff_24_48', 'diff_168_336',
        'rolling_mean_24', 'rolling_std_24', 'rolling_max_24', 'rolling_min_24',
        'rolling_mean_168', 'rolling_std_168',
        'rolling_mean_3d', 'rolling_mean_7d',
        'is_attack', 'system_balance_lag_24', 'demand_x_price_lag_168'
    ]
    
    features = common_features + [
        'supply_lag_24', 'supply_lag_168', 
        'demand_ramp', 'supply_ramp',
        'garpok_lag_24', 'vdr_supply_lag_24'
    ]
    
    # Load data to check which features actually exist
    print("Loading data to verify features...")
    df = load_data()
    df = enforce_limits(df)
    df = generate_features(df)
    
    # Filter features that actually exist in the dataframe
    features = [f for f in features if f in df.columns]
    print(f"Features used ({len(features)}): {features}")

    # Store importances
    importances = pd.DataFrame(index=features)
    
    print("\nCollecting feature importance from XGBoost models...")
    
    xgb_importances = []
    
    for h in range(24):
        model_path = os.path.join(models_dir, f"xgb_hour_{h}.json")
        if not os.path.exists(model_path):
            print(f"Warning: Model for hour {h} not found at {model_path}")
            continue
            
        model = xgb.XGBRegressor()
        model.load_model(model_path)
        
        # Get importance
        imp = model.feature_importances_
        xgb_importances.append(imp)
        
    if xgb_importances:
        avg_xgb_imp = np.mean(xgb_importances, axis=0)
        importances['XGBoost'] = avg_xgb_imp
    
    # Plotting
    if 'XGBoost' in importances.columns:
        # Sort by importance
        importances = importances.sort_values(by='XGBoost', ascending=True)
        
        plt.figure(figsize=(12, 10))
        importances['XGBoost'].plot(kind='barh', color='skyblue')
        plt.title('Average Feature Importance (XGBoost) across 24 hours')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        
        output_plot = os.path.join(script_dir, "../output/feature_importance.png")
        plt.savefig(output_plot)
        print(f"\nFeature importance plot saved to: {output_plot}")
        
        # Print top 10
        print("\nTop 10 Features:")
        print(importances['XGBoost'].sort_values(ascending=False).head(10))
    else:
        print("No XGBoost models found or failed to extract importance.")

if __name__ == "__main__":
    get_feature_importance()
