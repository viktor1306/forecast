import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_absolute_error
import os
import sys
import math

# Додаємо шлях до поточного каталогу
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from train_model_v1 import load_data, enforce_limits, generate_features
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'PriceForecasting', 'src'))
    from train_model_v1 import load_data, enforce_limits, generate_features

# === НАЛАШТУВАННЯ ===
print(f"🚀 TensorFlow Version: {tf.__version__}")
# Налаштування для відтворюваності
tf.random.set_seed(42)
np.random.seed(42)

def add_cyclical_features(df):
    # Cyclical encoding for hour (0-23)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Cyclical encoding for day of week (0-6)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week_num'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week_num'] / 7)
    
    # Cyclical encoding for month (1-12)
    df['month_sin'] = np.sin(2 * np.pi * (df['month'] - 1) / 12)
    df['month_cos'] = np.cos(2 * np.pi * (df['month'] - 1) / 12)
    return df

def create_sequences(X, y, caps=None, seq_len=24):
    Xs, ys, cs = [], [], []
    for i in range(len(X) - seq_len):
        Xs.append(X[i:(i + seq_len)])
        ys.append(y[i + seq_len])
        if caps is not None and len(caps) > 0:
            cs.append(caps[i + seq_len])
    
    if caps is not None and len(caps) > 0:
        return np.array(Xs), np.array(ys), np.array(cs)
    else:
        return np.array(Xs), np.array(ys)

def custom_price_loss(y_true, y_pred, caps):
    # y_true and y_pred are ratios (0-1)
    # caps are the price caps
    # We want to minimize |(y_true * caps) - (y_pred * caps)|
    # But Keras loss functions only take (y_true, y_pred).
    # So we need to pass caps as part of y_true or use a wrapper.
    # Simpler approach: Just train on Price directly but scaled?
    # No, let's stick to standard loss but simplify model first.
    return tf.keras.losses.Huber()(y_true, y_pred)

def train_lstm_process_tf():
    # 1. Завантаження даних
    print("📥 Завантаження та підготовка даних...")
    df = load_data()
    df = enforce_limits(df)
    df = generate_features(df)
    
    # Додаємо циклічні фічі
    df = add_cyclical_features(df)
    
    # === TARGET TRANSFORMATION ===
    # Прогнозуємо не ціну, а відношення ціни до прайскепу (0.0 - 1.0)
    target_col = 'target_ratio' 
    if 'target_ratio' not in df.columns:
        df['target_ratio'] = df['rdn_price'] / df['price_cap']
        df['target_ratio'] = df['target_ratio'].clip(0, 1.1)

    # Вибираємо розширений набір фіч
    feature_cols = [
        # Time
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
        'is_off_day', 'is_holiday', 'is_weekend',
        
        # Price Caps & Context
        'price_cap', 'is_attack', 'days_since_attack',
        
        # Lags
        'ratio_lag_24', 'ratio_lag_48', 'ratio_lag_168',
        'price_lag_24', 'price_lag_168',
        
        # System State
        'system_balance_lag_24', 'demand_ramp', 'supply_ramp',
        
        # Rolling Stats
        'rolling_mean_24', 'rolling_std_24',
        'rolling_mean_168', 'rolling_std_168',
        'rolling_mean_3d', 'rolling_mean_7d',
        
        # Diffs
        'diff_24_48', 'diff_168_336'
    ]
    
    # Фільтруємо тільки ті, що є в датафреймі
    feature_cols = [c for c in feature_cols if c in df.columns]
    print(f"🧠 Фічі для LSTM ({len(feature_cols)} шт.): {feature_cols}")

    # 2. Масштабування
    scaler_X = StandardScaler()
    scaler_y = MinMaxScaler(feature_range=(0, 1))
    
    data_X = scaler_X.fit_transform(df[feature_cols].fillna(0))
    data_y = scaler_y.fit_transform(df[[target_col]].fillna(0))
    
    # 3. Розділення на Train/Test
    test_days = 14
    test_size = test_days * 24
    train_size = len(df) - test_size
    
    X_train_raw, X_test_raw = data_X[:train_size], data_X[train_size:]
    y_train_raw, y_test_raw = data_y[:train_size], data_y[train_size:]
    
    # Створення послідовностей
    SEQ_LEN = 24 # Повертаємо 24 години
    
    print(f"🔄 Створення часових послідовностей (SEQ_LEN={SEQ_LEN})...")
    X_train, y_train = create_sequences(X_train_raw, y_train_raw, [], SEQ_LEN)[:2] # Ignore caps for now
    X_test, y_test = create_sequences(X_test_raw, y_test_raw, [], SEQ_LEN)[:2]
    
    print(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")
    
    # 4. Ініціалізація моделі (MLP / Dense замість LSTM)
    # Для MLP нам не потрібна часова вісь (SEQ_LEN), якщо ми використовуємо Flatten або просто беремо останній крок
    # Але create_sequences повертає (Batch, SeqLen, Features).
    # Ми можемо використати Flatten() щоб "розгорнути" часовий ряд в один довгий вектор фіч.
    
    model = Sequential([
        tf.keras.layers.Flatten(input_shape=(SEQ_LEN, len(feature_cols))),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.4),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(1, activation='linear') 
    ])
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005) # Менший LR для стабільності
    model.compile(optimizer=optimizer, loss='huber') 
    model.summary()
    
    # 5. Callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5, verbose=1)
    ]
    
    # 6. Навчання
    epochs = 150 # Більше епох, бо є EarlyStopping
    batch_size = 32
    print("\n🔥 Починаємо навчання LSTM (TensorFlow) з покращеннями...")
    
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.15, # Більше даних на валідацію
        callbacks=callbacks,
        verbose=1
    )

    # 7. Оцінка
    print("\n📊 Оцінка моделі...")
    predictions_ratio = model.predict(X_test)
    
    # Повертаємо масштаб ratio
    predictions_ratio_inv = scaler_y.inverse_transform(predictions_ratio)
    actuals_ratio_inv = scaler_y.inverse_transform(y_test)
    
    # === КОНВЕРТАЦІЯ RATIO -> PRICE ===
    # Нам потрібні price_cap для тестового періоду, щоб відновити ціну
    # Індекси тестового набору (з урахуванням зсуву SEQ_LEN)
    test_indices = df.index[train_size + SEQ_LEN:]
    
    # Перевірка розмірності
    if len(test_indices) != len(predictions_ratio_inv):
        print(f"⚠️ Розмірності не співпадають: Indices={len(test_indices)}, Preds={len(predictions_ratio_inv)}")
        # Обрізаємо зайве
        min_len = min(len(test_indices), len(predictions_ratio_inv))
        test_indices = test_indices[:min_len]
        predictions_ratio_inv = predictions_ratio_inv[:min_len]
        actuals_ratio_inv = actuals_ratio_inv[:min_len]

    price_caps_test = df.loc[test_indices, 'price_cap'].values.reshape(-1, 1)
    
    # Відновлюємо ціни
    predictions_price = predictions_ratio_inv * price_caps_test
    actuals_price = actuals_ratio_inv * price_caps_test # Або взяти df['rdn_price']
    
    # Обмеження прайскепами (на всяк випадок)
    predictions_price = np.minimum(predictions_price, price_caps_test)
    
    mae = mean_absolute_error(actuals_price, predictions_price)
    wmape = np.sum(np.abs(actuals_price - predictions_price)) / np.sum(actuals_price) * 100
    
    print("\n" + "="*40)
    print("🤖 РЕЗУЛЬТАТИ ПОКРАЩЕНОЇ LSTM (Target: Ratio)")
    print("="*40)
    print(f"MAE: {mae:.2f}")
    print(f"WMAPE: {wmape:.2f}%")
    
    # Збереження моделі
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models_improved', 'lstm_tf_v2.keras')
    model.save(model_path)
    print(f"💾 Модель збережено в: {model_path}")
    
    # Збереження результатів у CSV для аналізу
    res_df = pd.DataFrame({
        'Datetime': test_indices,
        'Actual_Price': actuals_price.flatten(),
        'Predicted_Price': predictions_price.flatten(),
        'Price_Cap': price_caps_test.flatten()
    })
    res_df.set_index('Datetime', inplace=True)
    res_df.to_csv(os.path.join(os.path.dirname(__file__), '..', 'output', 'lstm_predictions.csv'))
    print("💾 Детальні прогнози збережено в output/lstm_predictions.csv")

if __name__ == "__main__":
    train_lstm_process_tf()
