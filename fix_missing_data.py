
import os
import sys
from datetime import datetime, timedelta
import pandas as pd

# Add current directory to path to import ForecastingManager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from forecasting_core import ForecastingManager

def is_empty(val):
    return val is None or pd.isna(val) or str(val).strip() == '' or str(val).strip() == 'nan'

def main():
    manager = ForecastingManager()
    file_path = manager.file_path
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Get date from user or arguments
    if len(sys.argv) > 1:
        target_input = sys.argv[1]
        end_input = sys.argv[2] if len(sys.argv) > 2 else None
    else:
        print("\nOptions:")
        print("1. Enter a specific date (DD.MM.YYYY)")
        print("2. Enter a range (DD.MM.YYYY DD.MM.YYYY)")
        print("3. Enter 'auto' to scan for all problematic dates")
        user_in = input("Your choice: ").strip().split()
        target_input = user_in[0] if user_in else ""
        end_input = user_in[1] if len(user_in) > 1 else None

    problematic_market_dates = []
    problematic_weather_dates = []

    if target_input.lower() == 'auto':
        # ... (existing auto logic)
        print(f"Analyzing {file_path}...")
        try:
            df = pd.read_csv(file_path, decimal=',')
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        # Normalize columns
        df.columns = [str(c).strip().lower() for c in df.columns]
        date_col = df.columns[0]
        
        # Group by date
        data_by_date = {}
        for idx, row in df.iterrows():
            d_str = str(row[date_col])
            if d_str not in data_by_date:
                data_by_date[d_str] = []
            data_by_date[d_str].append(row)

        # Sort dates
        sorted_dates = sorted(data_by_date.keys(), key=lambda x: datetime.strptime(x, '%d.%m.%Y') if '.' in x else datetime.max)

        # Check for missing dates in the range
        if sorted_dates:
            first_date = datetime.strptime(sorted_dates[0], '%d.%m.%Y')
            last_date = datetime.strptime(sorted_dates[-1], '%d.%m.%Y')
            today = datetime.now()
            
            curr = first_date
            while curr <= today:
                d_str = curr.strftime('%d.%m.%Y')
                if d_str not in data_by_date:
                    print(f"Date {d_str} is missing entirely. Adding to fix list.")
                    problematic_market_dates.append(d_str)
                    problematic_weather_dates.append(d_str)
                curr += timedelta(days=1)

        for d_str in sorted_dates:
            rows = data_by_date[d_str]
            
            # Check market data
            has_market_issue = False
            for r in rows:
                if is_empty(r.get('rdn_price')) or is_empty(r.get('rdn_supply')):
                    has_market_issue = True
                    break
            if has_market_issue or len(rows) < 24:
                if d_str not in problematic_market_dates:
                    problematic_market_dates.append(d_str)

            # Check weather data
            has_weather_issue = False
            for r in rows:
                if is_empty(r.get('feelslike')) or is_empty(r.get('humidity')):
                    has_weather_issue = True
                    break
            if has_weather_issue:
                if d_str not in problematic_weather_dates:
                    problematic_weather_dates.append(d_str)
    else:
        # Specific date or range mode
        try:
            start_dt = datetime.strptime(target_input, '%d.%m.%Y')
            if end_input:
                end_dt = datetime.strptime(end_input, '%d.%m.%Y')
            else:
                end_dt = start_dt
            
            curr = start_dt
            while curr <= end_dt:
                d_str = curr.strftime('%d.%m.%Y')
                problematic_market_dates.append(d_str)
                problematic_weather_dates.append(d_str)
                curr += timedelta(days=1)
        except ValueError:
            print("Invalid date format. Please use DD.MM.YYYY")
            return

    if not problematic_market_dates and not problematic_weather_dates:
        print("No issues found to fix.")
        return

    print(f"Found {len(problematic_market_dates)} dates to update market data.")
    print(f"Found {len(problematic_weather_dates)} dates to update weather data.")

    # 1. Fix Market Data
    for d_str in problematic_market_dates:
        print(f"\n--- Fixing Market Data for {d_str} ---")
        # Fetch DAM
        dam_data = manager.fetch_oree_data(d_str, 'DAM')
        if dam_data:
            manager.update_csv(dam_data, d_str, 'DAM')
        
        # Fetch IDM
        idm_data = manager.fetch_oree_data(d_str, 'IDM')
        if idm_data:
            manager.update_csv(idm_data, d_str, 'IDM')

    # 2. Fix Weather Data
    if problematic_weather_dates:
        # Find range for weather
        dt_objs = [datetime.strptime(d, '%d.%m.%Y') for d in problematic_weather_dates if '.' in d]
        if dt_objs:
            start_date = min(dt_objs).strftime('%d.%m.%Y')
            end_date = max(dt_objs).strftime('%d.%m.%Y')
            
            print(f"\n--- Fixing Weather Data from {start_date} to {end_date} ---")
            weather_df = manager.fetch_weather_data(start_date, end_date)
            if weather_df is not None:
                manager.update_weather_csv(weather_df)
            else:
                print("Failed to fetch weather data (possibly API limit).")

    print("\nProcessing complete.")

if __name__ == "__main__":
    main()
