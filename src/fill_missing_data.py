import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from forecasting_core import ForecastingManager

def main():
    manager = ForecastingManager(base_dir=parent_dir)
    file_path = os.path.join(parent_dir, "data", "ready_for_train.csv")
    
    today_str = datetime.now().strftime("%d.%m.%Y")
    
    # 1. Спробуємо ще раз оновити RDN/VDR на сьогодні
    print(f"📅 Updating prices for today ({today_str})...")
    for m_type in ['DAM', 'IDM']:
        try:
            data = manager.fetch_oree_data(today_str, m_type)
            if data:
                manager.update_csv(data, today_str, m_type)
                print(f"  ✅ {m_type} updated for today.")
        except Exception as e:
            print(f"  ⚠️ Could not update {m_type} for today: {e}")

    # 2. Фінальна чистка та форматування
    print("🧹 Final formatting in progress...")
    try:
        df = pd.read_csv(file_path, decimal=',')
        
        # Переконаємось, що всі дати за 11-15 січня мають заповнені прапорці
        # Використовуємо .astype(int) для уникнення "0,0" при збереженні з decimal=','
        cols_to_fix = {
            'is_anomaly': bool,
            'is_attack': int,
            'is_holiday': int
        }
        
        for col, dtype in cols_to_fix.items():
            if col not in df.columns:
                df[col] = 0 if dtype == int else False
            
            if dtype == int:
                # Спочатку в float, потім fillna, потім int
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            else:
                df[col] = df[col].fillna(False).astype(bool)

        # Перевірка на дублікати (про всяк випадок)
        date_col = df.columns[0]
        df = df.drop_duplicates(subset=[date_col, 'hour'], keep='last')
        
        # Сортування за датою та годиною
        def parse_dt(x):
            try:
                if '.' in str(x): return datetime.strptime(str(x), "%d.%m.%Y")
                return datetime.strptime(str(x), "%Y-%m-%d")
            except: return datetime(1970,1,1)
            
        df['temp_dt'] = df[date_col].apply(parse_dt)
        df = df.sort_values(['temp_dt', 'hour']).drop(columns=['temp_dt'])

        # Збереження
        df.to_csv(file_path, index=False, decimal=',')
        print("✅ CSV formatted and saved.")
        
    except Exception as e:
        print(f"❌ Error during final formatting: {e}")

if __name__ == "__main__":
    main()
