import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, RobustScaler
import matplotlib.pyplot as plt
import os
import datetime
import warnings

warnings.filterwarnings("ignore")

# ==========================================
# 1. КОНФІГУРАЦІЯ
# ==========================================
CONF = {
    "seq_len": 48,       
    "pred_len": 24,      
    "hidden_dim": 256,   # Широка мережа для всіх фіч
    "layers": 2,
    "batch_size": 32,
    "dropout": 0.3,
    "lr": 0.0007,
    "epochs": 50,
    "patience": 6
}

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 FINAL ALL-FEATURES MODEL running on: {DEVICE}")

# ==========================================
# 2. ПІДГОТОВКА ДАНИХ (АВТОМАТИЧНА)
# ==========================================
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, "ready_for_train.csv"),
        os.path.join(script_dir, "../data/ready_for_train.csv"),
        "ready_for_train.csv"
    ]
    file_path = next((p for p in possible_paths if os.path.exists(p)), None)
    if not file_path: raise FileNotFoundError("❌ ready_for_train.csv не знайдено!")

    print(f"📂 Reading: {file_path}")
    df = pd.read_csv(file_path, decimal=',')
    
    df['datetime'] = pd.to_datetime(df['date_str'], dayfirst=True) + pd.to_timedelta(df['hour'], unit='h')
    df = df.sort_values('datetime').reset_index(drop=True)
    df = df.ffill().bfill()
    
    # --- СТРАТЕГІЯ: Residual ---
    df['price_lag_24'] = df['rdn_price'].shift(24)
    df['target_diff'] = df['rdn_price'] - df['price_lag_24']
    
    # Додаткові лаги
    df['price_lag_48'] = df['rdn_price'].shift(48)
    df['price_lag_168'] = df['rdn_price'].shift(168)
    
    df = df.dropna().reset_index(drop=True)
    return df

df = load_data()

# --- АВТОМАТИЧНИЙ ВИБІР ВСІХ ЧИСЛОВИХ ФІЧ ---
# Виключаємо тільки службові колонки
EXCLUDE_COLS = ['date_str', 'datetime', 'rdn_price', 'target_diff'] 

# Беремо ВСІ числові колонки, які є в файлі
FEATURES = [c for c in df.columns if c not in EXCLUDE_COLS and pd.api.types.is_numeric_dtype(df[c])]

print(f"✅ ВИКОРИСТОВУЄМО ВСІ ФІЧІ ({len(FEATURES)} шт.):")
print(FEATURES) 
# Тепер тут будуть і windspeed, і solarenergy, і supply/demand - все що є.

scaler_x = StandardScaler()
scaler_y = RobustScaler()

test_months = 3
split_idx = len(df) - (30 * 24 * test_months)

train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

scaler_x.fit(train_df[FEATURES])
scaler_y.fit(train_df[['target_diff']])

# ==========================================
# 3. DATASET
# ==========================================
class FullDataset(Dataset):
    def __init__(self, df, seq_len, pred_len):
        self.seq_len = seq_len
        self.pred_len = pred_len
        
        self.X = scaler_x.transform(df[FEATURES])
        self.Y = scaler_y.transform(df[['target_diff']])
        
        self.Base = df['price_lag_24'].values
        self.Real = df['rdn_price'].values
        self.Cap = df['price_cap'].values

    def __len__(self):
        return len(self.X) - self.seq_len - self.pred_len

    def __getitem__(self, idx):
        x_start, x_end = idx, idx + self.seq_len
        y_start, y_end = x_end, x_end + self.pred_len
        
        return {
            'x': torch.tensor(self.X[x_start:x_end], dtype=torch.float32),
            'y': torch.tensor(self.Y[y_start:y_end], dtype=torch.float32),
            'base': self.Base[y_start:y_end],
            'real': self.Real[y_start:y_end],
            'cap': self.Cap[y_start:y_end]
        }

train_dataset = FullDataset(train_df, CONF['seq_len'], CONF['pred_len'])
test_dataset = FullDataset(test_df, CONF['seq_len'], CONF['pred_len'])

train_loader = DataLoader(train_dataset, batch_size=CONF['batch_size'], shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

# ==========================================
# 4. МОДЕЛЬ (Robust LSTM)
# ==========================================
class ResidualModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, layers, dropout):
        super(ResidualModel, self).__init__()
        
        self.lstm = nn.LSTM(input_dim, hidden_dim, layers, batch_first=True, dropout=dropout, bidirectional=True)
        self.norm = nn.LayerNorm(hidden_dim * 2)
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, output_dim)
        )
        
    def forward(self, x):
        out, _ = self.lstm(x)
        last = self.norm(out[:, -1, :])
        return self.fc(last).unsqueeze(-1)

model = ResidualModel(len(FEATURES), CONF['hidden_dim'], CONF['pred_len'], CONF['layers'], CONF['dropout']).to(DEVICE)
optimizer = torch.optim.AdamW(model.parameters(), lr=CONF['lr'], weight_decay=1e-3)
criterion = nn.L1Loss() 

# ==========================================
# 5. ТРЕНУВАННЯ
# ==========================================
best_val_loss = float('inf')
patience_cnt = 0

print("\n🔥 Training Started...")

for epoch in range(CONF['epochs']):
    model.train()
    train_loss = 0
    for batch in train_loader:
        x, y = batch['x'].to(DEVICE), batch['y'].to(DEVICE)
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        train_loss += loss.item()
        
    model.eval()
    val_loss = 0
    batches = 0
    with torch.no_grad():
        for i, batch in enumerate(test_loader):
            if i > 600: break
            x, y = batch['x'].to(DEVICE), batch['y'].to(DEVICE)
            out = model(x)
            val_loss += criterion(out, y).item()
            batches += 1
            
    avg_train = train_loss / len(train_loader)
    avg_val = val_loss / max(batches, 1)
    
    print(f"Ep {epoch+1} | Train: {avg_train:.4f} | Val: {avg_val:.4f}")

    if avg_val < best_val_loss:
        best_val_loss = avg_val
        torch.save(model.state_dict(), "best_final_all_features.pth")
        patience_cnt = 0
    else:
        patience_cnt += 1
        if patience_cnt >= CONF['patience']:
            print(f"⏹ Early Stopping.")
            break

# ==========================================
# 6. ОЦІНКА & FEATURE IMPORTANCE
# ==========================================
print("\n📊 Calculating Full Metrics...")
model.load_state_dict(torch.load("best_final_all_features.pth", map_location=DEVICE))
model.eval()

preds, trues = [], []

with torch.no_grad():
    for batch in test_loader: # Проходимо по ВСЬОМУ тесту
        x = batch['x'].to(DEVICE)
        
        pred_diff_scaled = model(x).cpu().numpy().flatten()
        pred_diff = scaler_y.inverse_transform(pred_diff_scaled.reshape(-1, 1)).flatten()
        
        base = batch['base'].flatten()
        cap = batch['cap'].flatten()
        real = batch['real'].flatten()
        
        final_pred = base + pred_diff
        final_pred = np.clip(final_pred, 10.0, cap)
        
        preds.extend(final_pred)
        trues.extend(real)

y_p = np.array(preds)
y_t = np.array(trues)

# Метрики
def wmape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100

w_total = wmape(y_t, y_p)
h_14d = 14 * 24
if len(y_t) > h_14d:
    w_14d = wmape(y_t[-h_14d:], y_p[-h_14d:])
else:
    w_14d = w_total

print(f"\n🏆 РЕЗУЛЬТАТИ (ВСІ ФІЧІ):")
print(f"3 Months WMAPE: {w_total:.2f}%")
print(f"14 Days WMAPE:  {w_14d:.2f}%")

# Permutation Importance (Тільки топ 10)
print("\n🕵️ Перевірка впливу фіч (Permutation Importance):")
try:
    test_iter = iter(test_loader)
    batch = next(test_iter)
    x_orig = batch['x'].to(DEVICE)
    y_orig = batch['y'].to(DEVICE)
    
    base_loss = criterion(model(x_orig), y_orig).item()
    
    impacts = []
    # Перевіряємо кожну фічу
    for i, feat_name in enumerate(FEATURES):
        x_perm = x_orig.clone()
        # Перемішуємо значення цієї фічі (ламаємо її)
        idx = torch.randperm(x_perm.shape[1])
        x_perm[:, :, i] = x_perm[:, idx, i] 
        
        with torch.no_grad():
            loss_new = criterion(model(x_perm), y_orig).item()
        
        # Наскільки виросла помилка?
        pct_change = (loss_new - base_loss) / base_loss * 100
        impacts.append((feat_name, pct_change))
    
    impacts.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Feature':<20} | {'Impact':<10}")
    print("-" * 35)
    for name, imp in impacts[:10]: # Топ 10
        print(f"{name:<20} | {imp:.2f}%")

except Exception as e:
    print(f"Помилка аналізу фіч: {e}")


# Графік і збереження
plt.figure(figsize=(18, 10))

plt.subplot(2, 1, 1)
# 3 місяці (останні 2000 точок)
plt.plot(y_t[-2000:], label='Fact', color='black', alpha=0.6)
plt.plot(y_p[-2000:], label='Forecast', color='blue', alpha=0.7)
plt.title(f"3 Months | WMAPE: {w_total:.2f}%")
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
# 14 днів
plt.plot(y_t[-h_14d:], label='Fact', color='black', linewidth=1.5)
plt.plot(y_p[-h_14d:], label='Forecast', color='red', linestyle='--', linewidth=1.5)
plt.title(f"14 Days | WMAPE: {w_14d:.2f}%")
plt.legend()
plt.grid(True, alpha=0.3)

ts = datetime.datetime.now().strftime("%m-%d_%H-%M")
# НАЗВА ФАЙЛУ ЯК ТИ ПРОСИВ
fname = f"Final_AllFeats_WMAPE{w_14d:.1f}_3M{w_total:.1f}_{ts}.png"
script_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(script_dir, fname)
plt.savefig(save_path)
print(f"✅ Saved Graph: {save_path}")