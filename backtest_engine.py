import pandas as pd
import numpy as np
import joblib
import pandas_ta as ta
import matplotlib.pyplot as plt
import glob
import os
import io

# Config
HISTORY_DIR = "memories/history"
MODEL_PATH = "memories/models/reliance_rf_v1.joblib"

def calculate_technical_features(df):
    """
    Standard Feature Engineering (Must match brain_factory.py)
    """
    df = df.copy()
    
    # 1. Trend Indicators
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Trend_Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0)
    
    # 2. Momentum
    # Recalculate RSI manually to match brain_factory exactly or use TA lib if consistent
    # Using simple pandas calculation here for consistency with brain_factory
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. Volatility
    df['Returns'] = df['Close'].pct_change()
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    
    df.dropna(inplace=True)
    return df

def run_backtest():
    print("\n[BACKTEST ENGINE] Initializing Simulation...")
    
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print("[ERROR] AI Brain not found.")
        return
    model = joblib.load(MODEL_PATH)
    print(f"[AI] Loaded Brain: {MODEL_PATH}")
    
    # 2. Load Data
    files = glob.glob(f"{HISTORY_DIR}/*.csv")
    if not files: return
    latest_file = max(files, key=os.path.getctime)
    df = pd.read_csv(latest_file)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # 3. Filter for Testing Period (2024 onwards)
    # accurately simulating "Unseen Future"
    df = calculate_technical_features(df)
    test_data = df[df['Date'].dt.year >= 2024].copy()
    
    if test_data.empty:
        print("[ERROR] No data for 2024 verification.")
        return

    print(f"[SIMULATION] Replaying {len(test_data)} trading days from 2024...")
    
    # 4. Generate AI Signals
    features = ['RSI', 'Trend_Signal', 'Volatility', 'SMA_50', 'SMA_200']
    X_test = test_data[features]
    
    test_data['AI_Signal'] = model.predict(X_test)
    
    # 5. Calculate Returns
    # Strategy: If Signal=1 (Buy), we get the next day's return. If 0 (Hold), we get 0.
    test_data['Next_Day_Return'] = test_data['Close'].pct_change().shift(-1)
    
    test_data['Strategy_Return'] = test_data['AI_Signal'] * test_data['Next_Day_Return']
    test_data['Buy_Hold_Return'] = test_data['Next_Day_Return']
    
    # Cumulative Returns
    test_data['Strategy_Equity'] = (1 + test_data['Strategy_Return'].fillna(0)).cumprod()
    test_data['Benchmark_Equity'] = (1 + test_data['Buy_Hold_Return'].fillna(0)).cumprod()
    
    # 6. Report
    final_strategy = test_data['Strategy_Equity'].iloc[-2] # Last valid value
    final_benchmark = test_data['Benchmark_Equity'].iloc[-2]
    
    print("-" * 40)
    print("BACKTEST RESULTS (2024 - PRESENT)")
    print("-" * 40)
    print(f"AI Strategy Return:  {(final_strategy - 1) * 100:.2f}%")
    print(f"Buy & Hold Return:   {(final_benchmark - 1) * 100:.2f}%")
    
    if final_strategy > final_benchmark:
        print("\n[WIN] RESULT: AI OUTPERFORMED THE MARKET")
    else:
        print("\n[LOSS] RESULT: AI UNDERPERFORMED (Needs Retraining)")
        
    print("-" * 40)

if __name__ == "__main__":
    run_backtest()
