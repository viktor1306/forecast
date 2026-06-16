import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error
import os

def check_ensemble():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, '../output')
    
    tree_path = os.path.join(output_dir, 'improved_predictions.csv')
    lstm_path = os.path.join(output_dir, 'lstm_predictions.csv')
    
    if not os.path.exists(tree_path) or not os.path.exists(lstm_path):
        print("❌ One of the prediction files is missing.")
        return

    df_tree = pd.read_csv(tree_path, index_col=0, parse_dates=True)
    df_lstm = pd.read_csv(lstm_path, index_col=0, parse_dates=True)
    
    # Rename columns to avoid collision
    df_tree = df_tree.rename(columns={'Predicted': 'Tree_Pred', 'Actual': 'Actual'})
    df_lstm = df_lstm.rename(columns={'Predicted_Price': 'LSTM_Pred', 'Actual_Price': 'Actual_LSTM'})
    
    # Join
    df = df_tree.join(df_lstm, how='inner', lsuffix='_tree', rsuffix='_lstm')
    
    if len(df) == 0:
        print("⚠️ No overlapping dates found.")
        return
        
    y_true = df['Actual']
    p_tree = df['Tree_Pred']
    p_lstm = df['LSTM_Pred']
    
    # Ensemble (Weighted Average)
    # Since Tree is much better (22% vs 30%), give it more weight.
    # Try different weights
    best_wmape = 100
    best_w = 0
    
    print(f"📅 Evaluation Period: {df.index.min()} to {df.index.max()}")
    print(f"📊 Samples: {len(df)}")
    
    # Baseline Metrics
    wmape_tree = np.sum(np.abs(y_true - p_tree)) / np.sum(y_true) * 100
    wmape_lstm = np.sum(np.abs(y_true - p_lstm)) / np.sum(y_true) * 100
    
    print(f"🌲 Tree WMAPE: {wmape_tree:.2f}%")
    print(f"🧠 LSTM WMAPE: {wmape_lstm:.2f}%")
    
    for w in np.linspace(0, 1, 21): # 0.0 to 1.0 step 0.05
        p_ens = w * p_tree + (1 - w) * p_lstm
        wmape = np.sum(np.abs(y_true - p_ens)) / np.sum(y_true) * 100
        
        if wmape < best_wmape:
            best_wmape = wmape
            best_w = w
            
    print("-" * 30)
    print(f"🏆 Best Ensemble WMAPE: {best_wmape:.2f}%")
    print(f"⚖️ Best Weights: Tree={best_w:.2f}, LSTM={1-best_w:.2f}")
    
    # Save ensemble
    df['Ensemble_Pred'] = best_w * p_tree + (1 - best_w) * p_lstm
    df.to_csv(os.path.join(output_dir, 'ensemble_predictions.csv'))

if __name__ == "__main__":
    check_ensemble()
