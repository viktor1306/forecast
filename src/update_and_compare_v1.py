import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import time
import logging
from datetime import datetime, timedelta

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from forecasting_core import ForecastingManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compare_saved_prediction(target_date_str):
    """
    Loads a saved prediction CSV for the given date and compares it with actual data from OREE.
    target_date_str: "DD.MM.YYYY" (as used in the app)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manager = ForecastingManager(base_dir=parent_dir)
    
    # Convert DD.MM.YYYY to YYYY-MM-DD for filename lookup
    try:
        dt = datetime.strptime(target_date_str, "%d.%m.%Y")
        date_iso = dt.strftime("%Y-%m-%d")
    except ValueError:
        print(f"❌ Invalid date format: {target_date_str}")
        return

    # 1. Load Saved Prediction
    pred_file = os.path.join(script_dir, f"../output/prediction_{date_iso}.csv")
    if not os.path.exists(pred_file):
        print(f"❌ Saved prediction file not found: {pred_file}")
        print("⚠️ Please ensure you have run the prediction for this date previously.")
        return
    
    print(f"📂 Loading saved prediction from: {pred_file}")
    df_pred = pd.read_csv(pred_file)
    
    # 2. Fetch Actual Data (Fact)
    print(f"🔍 Fetching actual data for {target_date_str}...")
    data = manager.fetch_oree_data(target_date_str, 'DAM')
    if not data:
        print(f"❌ No actual data found for {target_date_str}")
        return
    
    # Convert actual data to DataFrame. ForecastingManager returns dicts,
    # but older loaders returned tuples, so support both shapes.
    df_fact = pd.DataFrame(data)
    if 'hour' in df_fact.columns and 'price' in df_fact.columns:
        df_fact.rename(columns={'price': 'Actual_Price', 'hour': 'Hour'}, inplace=True)
    elif 0 in df_fact.columns and 1 in df_fact.columns:
        df_fact = df_fact.rename(columns={0: 'Hour', 1: 'Actual_Price'})
    else:
        print(f"❌ Unexpected data format from OREE: {df_fact.columns}")
        return

    # Ensure numeric
    df_fact['Actual_Price'] = pd.to_numeric(df_fact['Actual_Price'])
    df_fact['Hour'] = pd.to_numeric(df_fact['Hour'])

    # Adjust OREE hours from 1-24 to 0-23 to match prediction format
    # This ensures the chart matches the 0-23 prediction view the user is used to.
    # if df_fact['Hour'].min() == 1 and df_fact['Hour'].max() == 24:
    #     print("ℹ️ Adjusting OREE hours from 1-24 to 0-23")
    #     df_fact['Hour'] = df_fact['Hour'] - 1
    
    # Merge
    # df_pred should have 'Hour' and 'Predicted_Price'
    if 'Hour' not in df_pred.columns:
        # Try to recover from index if it was saved with index
        if 'Datetime' in df_pred.columns:
             df_pred['Hour'] = pd.to_datetime(df_pred['Datetime']).dt.hour
        elif df_pred.index.name == 'Datetime':
             df_pred['Hour'] = df_pred.index.hour
        else:
             # Assume 0..23 index if 24 rows
             if len(df_pred) == 24:
                 df_pred['Hour'] = range(24)
    
    # If prediction is 0-23, but we want to align with 1-24 Fact
    # Check if we need to shift.
    # If min is 0, we shift to 1-24.
    if df_pred['Hour'].min() == 0:
        print("ℹ️ Adjusting Prediction hours from 0-23 to 1-24 (Shift +1)")
        df_pred['Hour'] = df_pred['Hour'] + 1

    if 'Predicted_Price' not in df_pred.columns:
        print("❌ 'Predicted_Price' column missing in saved prediction.")
        return

    # Use outer join to keep all hours (0-24)
    df_merge = pd.merge(df_pred, df_fact[['Hour', 'Actual_Price']], on='Hour', how='outer')
    df_merge = df_merge.sort_values('Hour')
    
    if df_merge.empty:
        print("❌ Error merging prediction and fact data.")
        return

    df_merge['Abs_Error'] = (df_merge['Actual_Price'] - df_merge['Predicted_Price']).abs()
    df_merge['APE_pct'] = np.where(
        df_merge['Actual_Price'].abs() > 1e-9,
        df_merge['Abs_Error'] / df_merge['Actual_Price'].abs() * 100,
        np.nan,
    )

    output_csv = os.path.join(script_dir, f"../output/comparison_{date_iso}.csv")
    df_merge.to_csv(output_csv, index=False)

    # 3. Plot
    plt.figure(figsize=(15, 7))
    # Plot with markers, handling NaNs automatically
    plt.plot(df_merge['Hour'], df_merge['Actual_Price'], 'b-o', label='Факт (OREE)', linewidth=2)
    plt.plot(df_merge['Hour'], df_merge['Predicted_Price'], 'r--x', label='Прогноз (Збережений)', linewidth=2)
    
    plt.title(f"Прогноз vs Факт за {target_date_str}", fontsize=16)
    plt.xlabel("Година", fontsize=12)
    plt.ylabel("Ціна (грн/МВт·год)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)
    # Show ticks for all hours present
    all_hours = df_merge['Hour'].unique()
    plt.xticks(np.arange(min(all_hours), max(all_hours)+1, 1))
    
    # Set Y ticks
    max_val = max(df_merge['Actual_Price'].max(), df_merge['Predicted_Price'].max())
    if pd.isna(max_val): max_val = 10000 # Fallback
    plt.yticks(np.arange(0, max_val + 500, 500))
    
    output_path = os.path.join(script_dir, f"../output/comparison_{date_iso}.png")
    plt.savefig(output_path)
    print(f"📊 Графік порівняння збережено: {output_path}")
    print(f"📄 CSV порівняння збережено: {output_csv}")
    
    # Save generic for GUI
    fixed_output_path = os.path.join(script_dir, "../output/comparison_latest.png")
    plt.savefig(fixed_output_path)
    
    # Metrics (calculate only on overlapping data)
    df_metrics = df_merge.dropna()
    if not df_metrics.empty:
        mae = np.mean(np.abs(df_metrics['Actual_Price'] - df_metrics['Predicted_Price']))
        wmape = np.sum(np.abs(df_metrics['Actual_Price'] - df_metrics['Predicted_Price'])) / np.sum(df_metrics['Actual_Price']) * 100
        print(f"Середня помилка (грн): {mae:.2f}")
        print(f"Середня помилка (%): {wmape:.2f}%")
    else:
        print("⚠️ Недостатньо даних для розрахунку метрик (немає перетину годин).")

def main():
    # Determine target date
    target_date_str = None
    if len(sys.argv) > 1:
        target_date_str = sys.argv[1]
    
    if not target_date_str:
        # Default to today if not provided
        today = datetime.now()
        target_date_str = today.strftime("%d.%m.%Y")
    
    print(f"🔍 Порівняння для дати: {target_date_str}")
    
    manager = ForecastingManager(base_dir=parent_dir)
    data = manager.fetch_oree_data(target_date_str, 'DAM')
    if data:
        print(f"✅ Дані знайдено за {target_date_str}!")
        # Update main CSV just in case (optional but good)
        manager.update_csv(data, target_date_str, 'DAM')
        
        # Compare
        compare_saved_prediction(target_date_str)
    else:
        print(f"❌ Даних за {target_date_str} ще немає на OREE.")

if __name__ == "__main__":
    main()
