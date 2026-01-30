import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import os
import glob

# Config
HISTORY_DIR = "memories/history"
MODEL_DIR = "memories/models"
MODEL_PATH = f"{MODEL_DIR}/reliance_rf_v1.joblib"

# Technical Indicator Functions (Manual Calculation to avoid strict dependency on pandas_ta if not present)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def build_features(df):
    """
    The Gym: Calculates clues for the AI.
    """
    df = df.copy()
    
    # 1. Trend Indicators
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['Trend_Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0) # Golden Cross status
    
    # 2. Momentum
    df['RSI'] = calculate_rsi(df['Close'], 14)
    
    # 3. Volatility (Risk)
    df['Returns'] = df['Close'].pct_change()
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    
    # 4. Target Variable (The Answer Key)
    # Did price go up > 1% in next 5 days?
    df['Future_Close'] = df['Close'].shift(-5)
    df['Target_Return'] = (df['Future_Close'] - df['Close']) / df['Close']
    df['Target'] = (df['Target_Return'] > 0.01).astype(int) # 1 = Buy, 0 = Hold/Wait
    
    # Clean up NaNs from rolling windows
    df.dropna(inplace=True)
    return df

def train_brain():
    print("\n[BRAIN FACTORY] initializing training sequence...")
    
    # 1. Load Data (The Food)
    files = glob.glob(f"{HISTORY_DIR}/*.csv")
    if not files:
        print("[ERROR] No history files found. Run data_collector.py first.")
        return

    latest_file = max(files, key=os.path.getctime)
    print(f"[INPUT] Loading {latest_file}...")
    df = pd.read_csv(latest_file)
    
    # 2. Engineer Features (The Gym)
    print("[GYM] Calculating RSI, SMA, and Volatility...")
    df_processed = build_features(df)
    
    # 3. Time Travel Split
    # Train: 2015 to 2023
    # Test: 2024 onwards
    
    # Add Year column for filtering (Assuming Date is YYYY-MM-DD or similar)
    df_processed['Date'] = pd.to_datetime(df_processed['Date'])
    
    train_data = df_processed[df_processed['Date'].dt.year <= 2023]
    test_data = df_processed[df_processed['Date'].dt.year >= 2024]
    
    print(f"[SPLIT] Training Samples: {len(train_data)} | Testing Samples: {len(test_data)}")
    
    # Define Inputs (X) and Answer (y)
    features = ['RSI', 'Trend_Signal', 'Volatility', 'SMA_50', 'SMA_200']
    X_train = train_data[features]
    y_train = train_data['Target']
    
    X_test = test_data[features]
    y_test = test_data['Target']
    
    # 4. Train Model (The Learning)
    print(f"[TRAINING] Growing Random Forest (100 Trees)... using features: {features}")
    model = RandomForestClassifier(n_estimators=100, min_samples_split=10, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate (The Exam)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print("-" * 40)
    print(f"RESULTS (2024-Present Unseen Data)")
    print("-" * 40)
    print(f"Accuracy: {accuracy:.2%}")
    print("\nDetailed Report:")
    print(classification_report(y_test, predictions))
    
    # 6. Save Brain
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n[PERSISTENCE] Brain saved to {MODEL_PATH}")
    print("[COMPLETE] AI is ready for inference.")

if __name__ == "__main__":
    train_brain()
