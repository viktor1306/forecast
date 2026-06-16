import pandas as pd
import os

def mark_anomalous_days_in_csv(data_file, anomalies_file, output_file=None):
    """
    Add anomaly markers to the original training data CSV.
    Matches by date_str and hour if available in both files, otherwise by date_str.
    """
    if not os.path.exists(data_file):
        print(f"Data file not found: {data_file}")
        return

    if not os.path.exists(anomalies_file):
        print(f"Anomalies file not found: {anomalies_file}")
        return

    # Read original data
    df = pd.read_csv(data_file, decimal=',', sep=',')
    df.columns = df.columns.str.strip()

    # Read anomalies
    anomalies_df = pd.read_csv(anomalies_file, decimal=',', sep=',')
    anomalies_df.columns = anomalies_df.columns.str.strip()

    # Propagation of special flags
    special_flags = [col for col in ['is_attack', 'is_holiday'] if col in anomalies_df.columns]

    # Determine if we should mark by hour or by day
    if 'hour' in df.columns and 'hour' in anomalies_df.columns:
        # Mark specific hours
        print("Marking specific hours as anomalous...")
        
        # Create unique keys for matching
        def make_key(d, h):
            return str(d) + "_" + str(int(float(str(h).replace(',', '.'))))

        df['_temp_key'] = df.apply(lambda x: make_key(x['date_str'], x['hour']), axis=1)
        anomalies_df['_temp_key'] = anomalies_df.apply(lambda x: make_key(x['date_str'], x['hour']), axis=1)
        
        # Mark anomalies
        anomalous_keys = set(anomalies_df['_temp_key'].tolist())
        df['is_anomaly'] = df['_temp_key'].isin(anomalous_keys)
        
        # Add special flags (is_attack, is_holiday)
        # We need to map them back to all hours of the day if they are per-day, 
        # but here we can just use the key-based lookup.
        for flag in special_flags:
            flag_map = anomalies_df.set_index('_temp_key')[flag].to_dict()
            df[flag] = df['_temp_key'].map(flag_map).fillna(0).astype(int)
            # If it's a day-level flag but only some hours are "anomalous", 
            # we might want to flag the WHOLE day in the main CSV.
            # However, for is_attack, it usually applies to the whole day.
            if flag == 'is_attack' or flag == 'is_holiday':
                # Force whole day if any hour of that day has the flag
                day_flags = anomalies_df.groupby('date_str')[flag].max().to_dict()
                df[flag] = df['date_str'].map(day_flags).fillna(0).astype(int)

        # Drop temp key
        df = df.drop(columns=['_temp_key'])
        marked_count = df['is_anomaly'].sum()
        print(f"Marked {marked_count} anomalous hours")
    else:
        # Mark entire days
        print("Marking entire days as anomalous...")
        anomalous_dates = set(anomalies_df['date_str'].tolist())
        df['is_anomaly'] = df['date_str'].isin(anomalous_dates)
        print(f"Marked {len(anomalous_dates)} anomalous days")

    # Save updated file
    if output_file is None:
        # Check if we are in main, if so use ready_for_train.csv
        output_file = 'data/ready_for_train.csv'

    df.to_csv(output_file, index=False, decimal=',')
    print(f"Updated file saved to: {output_file}")

    return df

if __name__ == "__main__":
    data_file = 'data/ready_for_train.csv'
    anomalies_file = 'anomalous_hours.csv'

    mark_anomalous_days_in_csv(data_file, anomalies_file)