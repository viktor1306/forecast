import pandas as pd
import numpy as np
import os

def repair_dataset(file_path):
    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path, decimal=',')
    
    # 1. Create Datetime Index
    # Handle both 0-23 and 1-24 hour formats
    min_h = df['hour'].min()
    max_h = df['hour'].max()
    offset = 1 if (min_h == 1 and max_h == 24) else 0
    
    df['datetime'] = pd.to_datetime(df['date_str'], dayfirst=True) + pd.to_timedelta(df['hour'] - offset, unit='h')
    df = df.set_index('datetime').sort_index()
    df = df[~df.index.duplicated(keep='first')]
    
    print(f"Original shape: {df.shape}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    
    # 2. Reindex to full hourly range
    full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='H')
    df = df.reindex(full_range)
    print(f"New shape after reindex: {df.shape}")
    
    # 3. Fill time-based columns
    df['hour'] = df.index.hour + offset
    df['date_str'] = df.index.strftime('%d.%m.%Y')
    df['month'] = df.index.month
    df['day_of_week'] = df.index.day_name()
    
    # 4. Interpolate numeric values
    # We interpolate prices and supply/demand to keep the timeline smooth
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Columns that should be 0 if missing (weather/anomalies)
    zero_fill_cols = ['precip', 'snow', 'snow_depth', 'solarradiation', 'solarenergy', 'uvindex', 
                      'is_anomaly', 'is_attack', 'is_holiday']
    for col in zero_fill_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            
    # Everything else - linear interpolation
    for col in numeric_cols:
        if col not in zero_fill_cols:
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
            
    # 5. Save back
    df.to_csv(file_path, index=False, decimal=',')
    print(f"Repaired file saved to {file_path}")

if __name__ == "__main__":
    repair_dataset('data/ready_for_train.csv')
