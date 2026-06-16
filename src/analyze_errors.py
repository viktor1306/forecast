import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_errors():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../output/improved_predictions.csv')
    
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    df['Error'] = np.abs(df['Actual'] - df['Predicted'])
    df['APE'] = df['Error'] / df['Actual'] * 100
    
    print(f"📊 Total WMAPE: {df['Error'].sum() / df['Actual'].sum() * 100:.2f}%")
    
    # 1. Error by Hour
    df['Hour'] = df.index.hour
    hourly_wmape = df.groupby('Hour').apply(lambda x: x['Error'].sum() / x['Actual'].sum() * 100)
    
    print("\n🕒 WMAPE by Hour:")
    print(hourly_wmape.sort_values(ascending=False).head(5))
    
    # 2. Error by Price Cap Proximity
    # Assuming we can get price caps. If not in CSV, we infer or skip.
    # The CSV has 'Actual' and 'Predicted'. Let's check if it has 'Price_Cap' or we can infer it.
    # The previous script didn't save Price_Cap in improved_predictions.csv, only Actual/Predicted.
    # But we can guess "At Cap" if Actual is close to standard caps (e.g. 5600, 6900, 7200 etc)
    
    # Let's just look at High vs Low prices
    df['Price_Bin'] = pd.qcut(df['Actual'], q=5)
    bin_wmape = df.groupby('Price_Bin', observed=False).apply(lambda x: x['Error'].sum() / x['Actual'].sum() * 100)
    
    print("\n💰 WMAPE by Price Level:")
    print(bin_wmape)

if __name__ == "__main__":
    analyze_errors()
