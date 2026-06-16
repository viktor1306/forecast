import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import joblib
import os
import sys
import warnings
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from price_caps import apply_price_caps_to_index

# === НАЛАШТУВАННЯ ===
warnings.filterwarnings('ignore')
sns.set_style("whitegrid")

# МАЄ СПІВПАДАТИ З train_lstm.py
SEQUENCE_LENGTH = 48
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"🚀 Evaluation running on: {DEVICE}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    torch.cuda.empty_cache()

# ==========================================
# 0. DATASET CLASS (Identical to train_lstm.py)
# ==========================================
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y, hours, dw, sequence_length, noise=0.0):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        self.hours = torch.tensor(hours, dtype=torch.long)
        self.dw = torch.tensor(dw, dtype=torch.long)
        self.sequence_length = sequence_length
        self.noise = noise

    def __len__(self):
        return len(self.X) - self.sequence_length

    def __getitem__(self, i):
        x_sample = self.X[i:i+self.sequence_length]
        if self.noise > 0:
            x_sample = x_sample + torch.randn_like(x_sample) * self.noise
        return (x_sample, self.hours[i+self.sequence_length], self.dw[i+self.sequence_length]), self.y[i+self.sequence_length]

# ==========================================
# 1. КЛАС LSTM (Архітектура V2)
# ==========================================
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=48):
        super().__init__()
        self.rnn = nn.GRU(input_size, hidden_size, 1, batch_first=True, bidirectional=True)
        self.hour_emb = nn.Embedding(24, 12)
        self.dw_emb = nn.Embedding(7, 4)
        combined_size = (hidden_size * 2) + 12 + 4 + input_size
        self.fc = nn.Sequential(
            nn.Linear(combined_size, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(64, 1)
        )

    def forward(self, x_tuple):
        x_seq, hour, dw = x_tuple
        out, _ = self.rnn(x_seq)
        deep_feat = out[:, -1, :] 
        h_e = self.hour_emb(hour)
        dw_e = self.dw_emb(dw)
        wide_feat = x_seq[:, -1, :]
        combined = torch.cat([deep_feat, h_e, dw_e, wide_feat], dim=1)
        return self.fc(combined)

# ==========================================
# 2. ЗАВАНТАЖЕННЯ ДАНИХ
# ==========================================
def load_data():
    print("⏳ Крок 1: Завантаження даних...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(script_dir, "../data/ready_for_train.csv")

    if not os.path.exists(file_name):
        print(f"❌ Файл {file_name} не знайдено!")
        exit()

    df = pd.read_csv(file_name, decimal=',')
    
    if df.columns[0] == 'Unnamed: 0': df.rename(columns={'Unnamed: 0': 'date_str'}, inplace=True)
    else: df.rename(columns={df.columns[0]: 'date_str'}, inplace=True)
    df.columns = [str(c).strip().lower() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]

    for col in df.columns:
        if col not in ['date_str', 'day_of_week']:
            if df[col].dtype == 'object':
                try: df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                except: pass
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'hour' in df.columns:
        df = df.dropna(subset=['hour'])
        min_h = df['hour'].min()
        offset = 0 if min_h == 0 else 1
        df['datetime'] = pd.to_datetime(df['date_str'], dayfirst=True) + pd.to_timedelta(df['hour'] - offset, unit='h')
        df.set_index('datetime', inplace=True)
        df.drop(columns=['date_str'], inplace=True)
    else:
        df.set_index('date_str', inplace=True)
        df.index = pd.to_datetime(df.index, dayfirst=True)

    df = df[df.index.notna()]
    df = df[~df.index.duplicated(keep='first')]
    if 'rdn_price' in df.columns: df = df.dropna(subset=['rdn_price'])
    
    return df

def enforce_limits(df):
    return apply_price_caps_to_index(df)

def generate_features(df):
    print("⏳ Крок 2: Генерація фіч (V18)...")
    df['hour'] = df.index.hour
    df['day_num'] = df.index.dayofweek
    df['month'] = df.index.month
    
    if 'target_ratio' not in df.columns:
        df['target_ratio'] = (df['rdn_price'] / df['price_cap']).clip(0, 1.2)

    df['hour_mean_7d'] = df.groupby('hour')['target_ratio'].transform(lambda x: x.shift(1).rolling(window=7).mean())
    df['hour_std_14d'] = df.groupby('hour')['target_ratio'].transform(lambda x: x.shift(1).rolling(window=14).std())

    # Lags
    df['ratio_lag_24'] = df['target_ratio'].shift(24)
    df['ratio_lag_48'] = df['target_ratio'].shift(48)
    df['ratio_lag_168'] = df['target_ratio'].shift(168)
    
    # Interaction (Safe check for temp/feelslike)
    temp_col = 'temp' if 'temp' in df.columns else 'feelslike'
    if temp_col in df.columns and 'solarradiation' in df.columns:
        df['sun_temp'] = df['solarradiation'] * df[temp_col]
    else:
        df['sun_temp'] = 0

    attack_dates_str = ["10.01.2026", "09.01.2026", "04.01.2026", "03.01.2026", "02.01.2026", "31.12.2025", "24.12.2025"]
    attack_dates = pd.to_datetime(attack_dates_str, dayfirst=True).date
    df['is_attack'] = [1 if d in attack_dates else 0 for d in df.index.date]
    
    holidays_str = ["07.01.2026", "01.01.2026", "31.12.2025", "24.12.2025", "01.10.2025", "24.08.2025"]
    holiday_dates = pd.to_datetime(holidays_str, dayfirst=True).date
    df['is_holiday'] = [1 if d in holiday_dates else 0 for d in df.index.date]

    df = df.interpolate(method='linear', limit_direction='both').ffill().bfill().fillna(0)
    return df

# ==========================================
# 3. ПРОГНОЗУВАННЯ
# ==========================================
def get_lstm_predictions(df, script_dir):
    print("🧠 Прогнозування (LSTM V2)...")
    models_dir = os.path.join(script_dir, "../models_lstm_torch")
    model_path = os.path.join(models_dir, "best_lstm.pth")
    
    if not os.path.exists(model_path):
        print(f"❌ Модель не знайдена: {model_path}")
        return None

    # Load Scalers
    try:
        scaler_X = joblib.load(os.path.join(models_dir, "scaler_X.pkl"))
        scaler_y = joblib.load(os.path.join(models_dir, "scaler_y.pkl"))
    except:
        print("❌ Помилка завантаження скейлерів!")
        return None

    # Визначаємо фічі (V5)
    if hasattr(scaler_X, 'feature_names_in_'):
        features = list(scaler_X.feature_names_in_)
        print(f"   Фічі моделі: {features}")
    else:
        features = [
            'price_cap', 'ratio_lag_24', 'ratio_lag_48', 'ratio_lag_168',
            'hour_mean_7d', 'hour_std_14d', 'is_attack', 'is_holiday',
            'temp', 'feelslike', 'humidity', 'solarradiation', 'sun_temp'
        ]
    
    # Видаляємо дублікати з назв фіч, якщо вони є (для уникнення TypeError в pandas)
    seen = set()
    features = [x for x in features if not (x in seen or seen.add(x))]
        
    missing = [f for f in features if f not in df.columns]
    if missing:
        print(f"   ⚠️ Відсутні фічі (заповнюємо 0): {missing}")
        for m in missing: df[m] = 0
    
    # Prep Data
    # Вибираємо тільки ті стовпці, що є у списку features
    X_data = df.loc[:, ~df.columns.duplicated()][features].copy()
    for col in X_data.columns: 
        X_data[col] = pd.to_numeric(X_data[col], errors='coerce')
    
    X_data = X_data.replace([np.inf, -np.inf], np.nan).fillna(0)
    
    # Scale
    X_scaled = scaler_X.transform(X_data)
    
    # Sliding Window
    def sliding_window(arr, window):
        shape = (arr.shape[0] - window, window, arr.shape[1])
        strides = (arr.strides[0], arr.strides[0], arr.strides[1])
        return np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)
    
    if len(X_scaled) <= SEQUENCE_LENGTH:
        print("❌ Недостатньо даних.")
        return None
    
    X_seq = sliding_window(X_scaled, SEQUENCE_LENGTH)
    
    # Model Load
    model = LSTMModel(input_size=len(features)).to(DEVICE)
    try:
        model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    except Exception as e:
        print(f"❌ Помилка архітектури моделі: {e}")
        print("Переконайся, що SEQUENCE_LENGTH та параметри класу LSTMModel співпадають з файлом навчання.")
        return None

    # PREDICT
    model.eval()
    Preds_list = []
    
    h_vals = df['hour'].values
    dw_vals = df['day_num'].values if 'day_num' in df.columns else df['day_of_week'].values
    y_dummy = np.zeros(len(X_scaled)) 

    dataset = TimeSeriesDataset(X_scaled, y_dummy, h_vals, dw_vals, SEQUENCE_LENGTH, noise=0.0)
    loader = DataLoader(dataset, batch_size=64, shuffle=False)
    
    print(f"   Базовий прохід по {len(dataset)} семплах...")
    with torch.no_grad():
        for (X_batch, h_batch, dw_batch), _ in loader:
            X_batch, h_batch, dw_batch = X_batch.to(DEVICE), h_batch.to(DEVICE), dw_batch.to(DEVICE)
            preds = model((X_batch, h_batch, dw_batch))
            Preds_list.append(preds.cpu().numpy())
    
    if not Preds_list:
        print("❌ Помилка: Немає прогнозів.")
        return None
        
    Preds = np.concatenate(Preds_list, axis=0)
    
    # 5. Inverse Transform (Residual -> Ratio)
    Residual_Preds = scaler_y.inverse_transform(Preds).flatten()
    Hour_Mean = df['hour_mean_7d'].values[SEQUENCE_LENGTH:]
    
    Preds_orig = Residual_Preds + Hour_Mean
    Actual_orig = df['target_ratio'].values[SEQUENCE_LENGTH:]
    
    # Reconstruct Prices
    valid_indices = df.index[SEQUENCE_LENGTH:]
    Price_Cap = df.loc[valid_indices, 'price_cap'].values
    Final_Preds = (Preds_orig * Price_Cap).clip(0, Price_Cap * 1.2)
    Final_Actual = (Actual_orig * Price_Cap)
    
    return pd.Series(Final_Preds, index=valid_indices)

# ==========================================
# 4. MAIN
# ==========================================
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    df = load_data()
    df = enforce_limits(df)
    df = generate_features(df)
    
    lstm_pred = get_lstm_predictions(df, script_dir)
    
    if lstm_pred is None: return

    # Sync
    common_idx = df.index.intersection(lstm_pred.index)
    y_true = df.loc[common_idx, 'rdn_price']
    y_pred = lstm_pred.loc[common_idx]

    def calculate_wmape(y_true, y_pred):
        return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100

    # Periods calculation (matching long_term_v1 logic)
    # 3 Months
    eval_months = 3
    last_3m_date = df.index[-1] - pd.DateOffset(months=eval_months)
    y_3m = y_true[y_true.index >= last_3m_date]
    p_3m = y_pred[y_pred.index >= last_3m_date]
    
    wmape_3m = calculate_wmape(y_3m, p_3m) if len(y_3m) > 0 else 0
    
    # 14 Days
    last_14d_date = df.index[-1] - pd.DateOffset(days=14)
    y_14d = y_true[y_true.index >= last_14d_date]
    p_14d = y_pred[y_pred.index >= last_14d_date]
    
    wmape_14d = calculate_wmape(y_14d, p_14d) if len(y_14d) > 0 else 0
    
    print("\n" + "="*50)
    print("📊 LSTM V3 RESULTS")
    print("="*50)
    print(f"3 Months WMAPE: {wmape_3m:.2f}%")
    print(f"14 Days  WMAPE: {wmape_14d:.2f}%")
    print("="*50)

    # Plot
    plt.figure(figsize=(16, 10))
    
    plt.subplot(2, 1, 1)
    plt.plot(y_3m.index, y_3m, label='Fact', color='black', alpha=0.6, linewidth=1)
    plt.plot(p_3m.index, p_3m, label='LSTM V2 Forecast', color='#3498db', alpha=0.8, linewidth=1)
    plt.title(f'3 Months (WMAPE: {wmape_3m:.2f}%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    plt.plot(y_14d.index, y_14d, label='Fact', color='black', linewidth=1.5)
    plt.plot(p_14d.index, p_14d, label='LSTM V2 Forecast', color='#e74c3c', linewidth=1.5, linestyle='--')
    plt.title(f'14 Days Zoom (WMAPE: {wmape_14d:.2f}%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_path = os.path.join(script_dir, "../output/lstm_v2_evaluation.png")
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
        
    plt.savefig(output_path)
    print(f"✅ Graph Saved: {output_path}")

if __name__ == "__main__":
    main()
