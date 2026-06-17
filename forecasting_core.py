import os
import sys
import math
import logging
import requests
import pandas as pd
import numpy as np
import subprocess
from datetime import datetime, timedelta
from io import StringIO
from bs4 import BeautifulSoup
import urllib3
from price_caps import apply_price_caps_to_frame, get_price_cap

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REGIONAL_WEATHER_LOCATIONS = [
    {"name": "kyiv_center", "latitude": 50.45, "longitude": 30.52},
    {"name": "lviv_west", "latitude": 49.84, "longitude": 24.03},
    {"name": "odesa_south", "latitude": 46.48, "longitude": 30.73},
    {"name": "chernihiv_north", "latitude": 51.50, "longitude": 31.29},
    {"name": "donetsk_east", "latitude": 48.02, "longitude": 37.80},
]


class ForecastingManager:
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = base_dir
            
        self.data_dir = os.path.join(self.base_dir, "data")
        self.src_dir = os.path.join(self.base_dir, "src")
        self.models_dir = os.path.join(self.base_dir, "models_improved")
        self.output_dir = os.path.join(self.base_dir, "output")
        self.file_path = os.path.join(self.data_dir, "ready_for_train.csv")
        
        # Ensure directories exist
        for d in [self.data_dir, self.output_dir]:
            os.makedirs(d, exist_ok=True)

    def log(self, message):
        # This can be replaced with a proper logging system or callback
        print(f"[ForecastingManager] {message}")
        return message

    def fetch_oree_data(self, target_date_str, market_type='DAM'):
        """
        Fetch hourly data from OREE for a specific date (DD.MM.YYYY).
        market_type: 'DAM' (RDN) or 'IDM' (VDR)
        Returns a list of dicts or None if no data.
        """
        base_url = "https://www.oree.com.ua"
        
        # Determine endpoints based on market type
        if market_type == 'IDM':
            init_url = f"{base_url}/index.php/PXS/get_pxs_res_idm"
            referer = f"{base_url}/index.php/control/results_mo/IDM"
        else: # DAM
            init_url = f"{base_url}/index.php/PXS/get_pxs_res"
            referer = f"{base_url}/index.php/control/results_mo/DAM"

        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": base_url,
            "Referer": referer
        })
        
        self.log(f"Requesting data ({market_type}) for {target_date_str}...")
        
        try:
            # Step 1: Get session ID
            resp = session.post(init_url, data={"day": target_date_str}, verify=False)
            
            if resp.status_code != 200:
                self.log(f"HTTP Error {resp.status_code} during initialization")
                return None

            soup = BeautifulSoup(resp.text, 'html.parser')
            link_input = soup.find('input', class_='hdata_link')
            
            if not link_input:
                self.log("Data identifier (hdata_link) not found. Data might be missing.")
                return None
                
            param = link_input.get('value')
            
            # Step 2: Get table data
            h_url = f"{base_url}/index.php/PXS/get_pxs_hdata/{param}"
            resp_h = session.post(h_url, verify=False)
            
            if resp_h.status_code != 200:
                self.log(f"HTTP Error {resp_h.status_code} getting table")
                return None
                
            try:
                html_content = resp_h.json().get('html', '')
            except:
                html_content = resp_h.text
                
            if not html_content:
                self.log("Empty response received")
                return None
                
            # Step 3: Parse table
            soup_h = BeautifulSoup(html_content, 'html.parser')
            rows = soup_h.find_all('tr')
            
            results = []
            for row in rows:
                cols = row.find_all('td')
                # Expected: [№, Hour, Price, Supply, Demand, ...]
                if len(cols) >= 5:
                    try:
                        h_txt = cols[1].get_text(strip=True)
                        if not h_txt.isdigit():
                            continue
                            
                        h = int(h_txt)
                        p = float(cols[2].get_text(strip=True).replace(' ', '').replace(',', '.'))
                        s = float(cols[3].get_text(strip=True).replace(' ', '').replace(',', '.'))
                        d = float(cols[4].get_text(strip=True).replace(' ', '').replace(',', '.'))
                        
                        # Try to get Garpok volume (usually index 5 or 8 depending on table)
                        g = 0.0
                        if market_type == 'DAM' and len(cols) >= 6:
                            try:
                                g_txt = cols[5].get_text(strip=True).replace(' ', '').replace(',', '.')
                                g = float(g_txt)
                            except:
                                g = 0.0
                        
                        results.append({'hour': h, 'price': p, 'supply': s, 'demand': d, 'garpok': g})
                    except ValueError:
                        continue
            
            if results:
                self.log(f"Successfully parsed {len(results)} rows")
                return results
            else:
                self.log("No data found after parsing")
                return None

        except Exception as e:
            self.log(f"Error: {e}")
            return None

    def update_csv(self, data_list, target_date_str, market_type='DAM'):
        """Update ready_for_train.csv with fetched data"""
        if not os.path.exists(self.file_path):
            self.log(f"File {self.file_path} not found")
            return False
        
        try:
            df = pd.read_csv(self.file_path, decimal=',')
            
            # Normalize columns
            df.columns = [str(c).strip().lower() for c in df.columns]

            # Remove unnamed columns if any exist
            df = df.loc[:, ~df.columns.str.contains('^unnamed')]
            
            # Identify date column
            date_col = df.columns[0] # Assuming first column is date
            
            updated = False
            
            # Create a map of OREE hour -> data. OREE publishes hours as 1..24,
            # while this CSV stores hours as 0..23. Existing-row updates must
            # respect the CSV convention, otherwise every hour after 0 is shifted.
            data_map = {item['hour']: item for item in data_list}
            hour_numeric = pd.to_numeric(df.get('hour', pd.Series(dtype=float)).astype(str).str.replace(',', '.'), errors='coerce')
            zero_based_hours = hour_numeric.min() == 0 and hour_numeric.max() == 23
            
            # Iterate and update
            for idx, row in df.iterrows():
                row_date = str(row[date_col])
                try:
                    # Try to parse row date
                    if '.' in row_date:
                        d = datetime.strptime(row_date, "%d.%m.%Y")
                    else:
                        d = datetime.strptime(row_date, "%Y-%m-%d")
                    
                    target_d = datetime.strptime(target_date_str, "%d.%m.%Y")
                    
                    if d.date() == target_d.date():
                        # Match!
                        h_val = row['hour']
                        try:
                            h = int(float(str(h_val).replace(',', '.')))
                        except:
                            h = int(h_val)
                        
                        oree_hour = h + 1 if zero_based_hours else h
                        if oree_hour in data_map:
                            item = data_map[oree_hour]
                            if market_type == 'DAM':
                                df.at[idx, 'rdn_price'] = item['price']
                                df.at[idx, 'rdn_supply'] = item['supply']
                                df.at[idx, 'rdn_demand'] = item['demand']
                                if 'garpok' in item:
                                    df.at[idx, 'garpok_volume'] = item['garpok']
                            elif market_type == 'IDM':
                                df.at[idx, 'vdr_supply'] = item['supply']
                                df.at[idx, 'vdr_demand'] = item['demand']
                            updated = True
                        elif h in data_map:
                            item = data_map[h]
                            if market_type == 'DAM':
                                df.at[idx, 'rdn_price'] = item['price']
                                df.at[idx, 'rdn_supply'] = item['supply']
                                df.at[idx, 'rdn_demand'] = item['demand']
                                if 'garpok' in item:
                                    df.at[idx, 'garpok_volume'] = item['garpok']
                            elif market_type == 'IDM':
                                df.at[idx, 'vdr_supply'] = item['supply']
                                df.at[idx, 'vdr_demand'] = item['demand']
                            updated = True
                except:
                    continue
            
            if not updated:
                self.log(f"Date {target_date_str} not found in CSV. Adding new rows...")
                
                # Create new rows for 0-23 hours
                new_rows = []
                target_date = datetime.strptime(target_date_str, "%d.%m.%Y")
                day_of_week = target_date.weekday() # 0=Monday
                month = target_date.month
                
                columns = df.columns.tolist()
                
                for h in range(24):
                    # Map 0-23 to OREE 1-24
                    oree_h = h + 1
                    item = None
                    
                    if oree_h in data_map:
                        item = data_map[oree_h]
                    elif h in data_map:
                        item = data_map[h]
                    
                    if item is not None:
                        row_dict = {col: None for col in columns}
                        row_dict[date_col] = target_date_str
                        row_dict['hour'] = h
                        
                        if market_type == 'DAM':
                            row_dict['rdn_price'] = item['price']
                            row_dict['rdn_supply'] = item['supply']
                            row_dict['rdn_demand'] = item['demand']
                            if 'garpok' in item:
                                row_dict['garpok_volume'] = item['garpok']
                        elif market_type == 'IDM':
                            row_dict['vdr_supply'] = item['supply']
                            row_dict['vdr_demand'] = item['demand']
                            
                        row_dict['day_of_week'] = day_of_week
                        row_dict['month'] = month
                        
                        row_dict['price_cap'] = get_price_cap(target_date, h)
                        
                        new_rows.append(row_dict)
                
                if new_rows:
                    new_df = pd.DataFrame(new_rows)
                    df = pd.concat([df, new_df], ignore_index=True)
                    self.log(f"Added {len(new_rows)} new rows to {self.file_path}")
                    updated = True
                else:
                    self.log("No data to add.")
                    return False

            if updated:
                apply_price_caps_to_frame(df, date_col=date_col)

                # Only update numeric formatting and sin/cos for the whole DF if absolutely necessary,
                # but let's optimize: only do it for the rows we might have touched or just once.
                # To keep it simple and fast, we'll just ensure the new/updated data is correct.
                
                # Recalculate hour_sin and hour_cos only if they are missing or for the whole DF once
                # (Doing it for the whole DF is fast if we use vectorized operations instead of .apply)
                try:
                    if 'hour' in df.columns:
                        # Vectorized conversion to numeric
                        h_numeric = pd.to_numeric(df['hour'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                        df['hour_sin'] = np.sin(2 * np.pi * h_numeric / 24)
                        df['hour_cos'] = np.cos(2 * np.pi * h_numeric / 24)
                except Exception as e:
                    self.log(f"Warning: Failed to update sin/cos: {e}")

                df.to_csv(self.file_path, index=False, decimal=',')
                self.log(f"Changes saved to {self.file_path}")
                return True
                
            return False
        except Exception as e:
            self.log(f"Error updating CSV: {e}")
            return False

    def fetch_weather_data(self, start_date_str, end_date_str, locations=None):
        """
        Fetch weather data from Open-Meteo API (No limits, no key required).
        Long ranges are split between archive and forecast endpoints because
        the forecast endpoint does not cover older historical dates.
        Weather is averaged across representative Ukrainian regions instead
        of using Kyiv only, because national power prices depend on country-wide
        renewable conditions.
        Returns a pandas DataFrame or None.
        """
        locations = locations or REGIONAL_WEATHER_LOCATIONS
        
        try:
            s_dt = datetime.strptime(start_date_str, "%d.%m.%Y")
            e_dt = datetime.strptime(end_date_str, "%d.%m.%Y")
        except Exception as e:
            self.log(f"Date format error: {e}")
            return None

        def request_chunk(base_url, chunk_start, chunk_end, location):
            s_date = chunk_start.strftime("%Y-%m-%d")
            e_date = chunk_end.strftime("%Y-%m-%d")
            params = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "start_date": s_date,
                "end_date": e_date,
                "hourly": "apparent_temperature,dew_point_2m,relative_humidity_2m,precipitation,precipitation_probability,snowfall,snow_depth,wind_gusts_10m,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover,visibility,shortwave_radiation,uv_index",
                "timezone": "auto"
            }

            self.log(
                "Requesting Open-Meteo weather for "
                f"{location['name']} ({location['latitude']},{location['longitude']}) "
                f"from {s_date} to {e_date}..."
            )
            response = requests.get(base_url, params=params, timeout=30)
            if response.status_code != 200:
                self.log(f"API Error: {response.status_code}, {response.text}")
                return None

            data = response.json()
            if "hourly" not in data:
                self.log("No hourly data in response")
                return None

            frame = pd.DataFrame(data["hourly"])
            frame["_weather_location"] = location["name"]
            return frame

        try:
            today = datetime.now()
            archive_end = today - timedelta(days=2)
            chunks = []

            if s_dt <= archive_end:
                chunks.append((
                    "https://archive-api.open-meteo.com/v1/archive",
                    s_dt,
                    min(e_dt, archive_end)
                ))

            forecast_start = max(s_dt, archive_end + timedelta(days=1))
            if forecast_start <= e_dt:
                chunks.append((
                    "https://api.open-meteo.com/v1/forecast",
                    forecast_start,
                    e_dt
                ))

            frames = []
            for location in locations:
                for base_url, chunk_start, chunk_end in chunks:
                    chunk = request_chunk(base_url, chunk_start, chunk_end, location)
                    if chunk is not None and not chunk.empty:
                        frames.append(chunk)

            if not frames:
                return None

            df_weather = pd.concat(frames, ignore_index=True)

            mapping = {
                "time": "datetime",
                "apparent_temperature": "feelslike",
                "dew_point_2m": "dew",
                "relative_humidity_2m": "humidity",
                "precipitation": "precip",
                "precipitation_probability": "precipprob",
                "snowfall": "snow",
                "snow_depth": "snowdepth",
                "wind_gusts_10m": "windgust",
                "wind_speed_10m": "windspeed",
                "wind_direction_10m": "winddir",
                "pressure_msl": "sealevelpressure",
                "cloud_cover": "cloudcover",
                "visibility": "visibility",
                "shortwave_radiation": "solarradiation",
                "uv_index": "uvindex"
            }
            df_weather = df_weather.rename(columns=mapping)

            df_weather["datetime"] = pd.to_datetime(df_weather["datetime"])
            numeric_cols = [
                col for col in df_weather.columns
                if col not in {"datetime", "_weather_location"}
            ]
            for col in numeric_cols:
                df_weather[col] = pd.to_numeric(df_weather[col], errors="coerce")

            if "winddir" in df_weather.columns:
                wind_rad = np.deg2rad(df_weather["winddir"])
                df_weather["_winddir_sin"] = np.sin(wind_rad)
                df_weather["_winddir_cos"] = np.cos(wind_rad)

            mean_cols = [
                col for col in numeric_cols
                if col != "winddir" and col in df_weather.columns
            ]
            grouped = df_weather.groupby("datetime", as_index=False)[mean_cols].mean()

            if {"_winddir_sin", "_winddir_cos"}.issubset(df_weather.columns):
                wind_group = df_weather.groupby("datetime")[["_winddir_sin", "_winddir_cos"]].mean()
                wind_degrees = np.rad2deg(np.arctan2(wind_group["_winddir_sin"], wind_group["_winddir_cos"]))
                wind_degrees = (wind_degrees + 360.0) % 360.0
                grouped = grouped.merge(
                    wind_degrees.rename("winddir").reset_index(),
                    on="datetime",
                    how="left",
                )

            df_weather = grouped.sort_values("datetime").reset_index(drop=True)

            df_weather['precipprob'] = df_weather['precipprob'].fillna(0.0)
            df_weather['uvindex'] = df_weather['uvindex'].fillna(0.0)
            df_weather['visibility'] = df_weather['visibility'].fillna(15.0) # Default 15km

            if 'solarradiation' in df_weather.columns:
                df_weather['solarenergy'] = df_weather['solarradiation'].fillna(0.0) * 3600 / 1000000

            def get_precip_type(row):
                p = row.get('precip', 0)
                s = row.get('snow', 0)
                if p and p > 0 and s and s > 0: return 3
                if s and s > 0: return 2
                if p and p > 0: return 1
                return 0

            df_weather['preciptype'] = df_weather.apply(get_precip_type, axis=1)

            df_weather['date_formatted'] = pd.to_datetime(df_weather['datetime']).dt.strftime("%d.%m.%Y")
            df_weather['hour_int'] = pd.to_datetime(df_weather['datetime']).dt.hour
            df_weather['weather_source'] = "regional_open_meteo_mean"
            df_weather['weather_locations'] = ",".join(location["name"] for location in locations)

            return df_weather
        except Exception as e:
            self.log(f"Error fetching weather: {e}")
            return None

    def update_weather_csv(self, api_data):
        """Update csv with weather data, adding new rows if needed"""
        if not os.path.exists(self.file_path):
            self.log(f"File {self.file_path} not found")
            return False
            
        column_mapping = {
            'feelslike': 'feelslike',
            'snowdepth': 'snow_depth',
            'windspeed': 'windspeed',
            'cloudcover': 'cloudcover',
            'solarradiation': 'solarradiation',
            'solarenergy': 'solarenergy',
            'dew': 'dew',
            'humidity': 'humidity',
            'precip': 'precip',
            'precipprob': 'precipprob',
            'preciptype': 'preciptype',
            'snow': 'snow',
            'windgust': 'windgust',
            'winddir': 'winddir',
            'sealevelpressure': 'sealevelpressure',
            'visibility': 'visibility',
            'uvindex': 'uvindex'
        }
        
        try:
            df = pd.read_csv(self.file_path, decimal=',')
            # Normalize columns
            df.columns = [str(c).strip().lower() for c in df.columns]

            # Remove unnamed columns if any exist
            df = df.loc[:, ~df.columns.str.contains('^unnamed')]
            
            date_col = df.columns[0]
            
            # Helper to get existing dates
            existing_dates = set()
            for idx, row in df.iterrows():
                row_date = str(row[date_col])
                if '.' in row_date:
                     existing_dates.add(row_date)
                else:
                     try:
                        d_obj = datetime.strptime(row_date, "%Y-%m-%d")
                        existing_dates.add(d_obj.strftime("%d.%m.%Y"))
                     except: pass

            # Create lookup map: (date_str, hour_int) -> row
            api_lookup = {}
            dates_in_api = set()
            
            for _, row in api_data.iterrows():
                d_str = row['date_formatted']
                h = row['hour_int']
                api_lookup[(d_str, h)] = row
                dates_in_api.add(d_str)
                
            updated_count = 0
            
            # 1. Update existing rows
            for idx, row in df.iterrows():
                row_date = str(row[date_col])
                try:
                    # Parse row date
                    if '.' in row_date:
                        d_str = row_date
                    else:
                        d_obj = datetime.strptime(row_date, "%Y-%m-%d")
                        d_str = d_obj.strftime("%d.%m.%Y")
                    
                    # Parse hour
                    h_val = row['hour']
                    try:
                        h = int(float(str(h_val).replace(',', '.')))
                    except:
                        h = int(h_val)
                    
                    # Match
                    if (d_str, h) in api_lookup:
                        api_row = api_lookup[(d_str, h)]
                        for api_col, csv_col in column_mapping.items():
                            if api_col in api_row:
                                val = api_row[api_col]
                                if pd.isna(val):
                                    if api_col in ['snowdepth', 'solarradiation', 'precip', 'snow']:
                                        val = 0.0
                                df.at[idx, csv_col] = val
                        
                        # Fix day_of_week and month if missing
                        d_obj = datetime.strptime(d_str, "%d.%m.%Y")
                        if 'day_of_week' in df.columns:
                            df.at[idx, 'day_of_week'] = d_obj.weekday()
                        if 'month' in df.columns:
                            df.at[idx, 'month'] = d_obj.month

                        updated_count += 1
                except:
                    continue

            # 2. Add missing rows
            new_rows = []
            columns = df.columns.tolist()
            
            for d_str in dates_in_api:
                if d_str not in existing_dates:
                    self.log(f"Adding new rows for date {d_str}...")
                    d_obj = datetime.strptime(d_str, "%d.%m.%Y")
                    day_of_week = d_obj.weekday()
                    month = d_obj.month
                    
                    for h in range(24):
                        row_dict = {col: None for col in columns}
                        row_dict[date_col] = d_str
                        row_dict['hour'] = h
                        row_dict['day_of_week'] = day_of_week
                        row_dict['month'] = month
                        
                        row_dict['price_cap'] = get_price_cap(d_obj, h)
                        
                        # Weather
                        if (d_str, h) in api_lookup:
                            api_row = api_lookup[(d_str, h)]
                            for api_col, csv_col in column_mapping.items():
                                if api_col in api_row:
                                    val = api_row[api_col]
                                    if pd.isna(val):
                                         if api_col in ['snowdepth', 'solarradiation', 'precip', 'snow']:
                                             val = 0.0
                                    row_dict[csv_col] = val
                        
                        new_rows.append(row_dict)
            
            if new_rows:
                new_df = pd.DataFrame(new_rows)
                df = pd.concat([df, new_df], ignore_index=True)
                updated_count += len(new_rows)
                
            if updated_count > 0:
                apply_price_caps_to_frame(df, date_col=date_col)

                # Global cleanup of month and day_of_week
                try:
                    def parse_date(d):
                        try:
                            if '.' in str(d): return datetime.strptime(str(d), "%d.%m.%Y")
                            return datetime.strptime(str(d), "%Y-%m-%d")
                        except: return None
                    
                    dates = df[date_col].apply(parse_date)
                    df['month'] = dates.apply(lambda d: d.month if d else None)
                    df['day_of_week'] = dates.apply(lambda d: d.weekday() if d else None)
                except Exception as e:
                    self.log(f"Warning: Failed to update month/dow: {e}")

                # Recalculate sin/cos for the whole DF (vectorized is fast)
                try:
                    if 'hour' in df.columns:
                        h_numeric = pd.to_numeric(df['hour'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                        df['hour_sin'] = np.sin(2 * np.pi * h_numeric / 24)
                        df['hour_cos'] = np.cos(2 * np.pi * h_numeric / 24)
                except Exception as e:
                    self.log(f"Warning: Failed to update sin/cos: {e}")

                df.to_csv(self.file_path, index=False, decimal=',')
                self.log(f"Updated weather in {updated_count} rows (including new days).")
                return True
            else:
                self.log("No rows found to update weather.")
                return False
                
        except Exception as e:
            self.log(f"Error updating CSV with weather: {e}")
            import traceback
            traceback.print_exc()
            return False

    def ensure_future_caps(self):
        """
        Ensure that price caps for the next 2 days are present in the file.
        """
        if not os.path.exists(self.file_path):
            return

        try:
            df = pd.read_csv(self.file_path, decimal=',')
            df.columns = [str(c).strip().lower() for c in df.columns]
            # Implementation omitted for brevity, assuming it's similar to update_csv logic
            # For now, we can skip this or implement if critical
            pass
        except Exception as e:
            self.log(f"Error ensuring caps: {e}")

    def run_script(self, script_name, args=None):
        """Run a python script from the src directory"""
        script_path = os.path.join(self.src_dir, script_name)
        if not os.path.exists(script_path):
            return False, f"Script not found: {script_name}"
        
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)
            
        self.log(f"Running script: {' '.join(cmd)}")
        
        try:
            # Set environment to force UTF-8
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            result = subprocess.run(
                cmd, 
                cwd=self.src_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env
            )
            
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
                
            if result.returncode == 0:
                return True, output
            else:
                return False, f"Script failed with code {result.returncode}:\n{output}"
        except Exception as e:
            return False, f"Error running script: {e}"
