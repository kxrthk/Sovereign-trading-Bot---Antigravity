import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
import joblib

import pandas_ta_classic as ta

def train_oracle():
    # Load Data
    data_path = 'research/training_data.csv'
    try:
        df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    except FileNotFoundError:
        print(f"Error: {data_path} not found. Please run data_collector.py first.")
        return

    # Pre-Process: Create features
    df['Open_Close'] = df['Open'] - df['Close']
    df['High_Low'] = df['High'] - df['Low']
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    
    # New Features: RSI and Volatility
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['Volatility'] = df['Close'].rolling(window=10).std()
    
    # Lagged Returns
    df['Return'] = df['Close'].pct_change()
    df['Return_Lag1'] = df['Return']
    df['Return_Lag2'] = df['Return'].shift(1)

    # Drop NaN values created by rolling averages and RSI
    df = df.dropna()

    # Features and Target
    features = ['Open_Close', 'High_Low', 'SMA_5', 'SMA_10', 'RSI', 'Volatility', 'Return_Lag1', 'Return_Lag2']
    X = df[features]
    y = df['Target']

    # The Brain: Use RandomForestClassifier
    # Using random_state for reproducibility, min_samples_split to avoid overfitting
    model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

    # Training: Train on all data as requested ("using the last 2 years of data")
    # Usually we split train/test, but instruction implies training on the dataset.
    # "Train the model ... Use precision score (How often is it right ...)"
    # To get a valid precision score, we should test on something. 
    # If we evaluate on training data, it will be inflated.
    # However, "Train ... using the last 2 years" implies using all of it.
    # Let's do a time-series split manually for validation metrics if strict, 
    # OR just train on all and report score (biased). 
    # Given "Validation: Print the 'Precision Score'", imply we need a score.
    # Let's split last 100 days for validation to give a meaningful score, 
    # or just use scikit-learn's score on the whole set if that's what is implied.
    # BUT, the prompt says "Train ... using the last 2 years". 
    # I will split the data to give a REAL precision score, otherwise it's 1.0.
    # Actually, standard practice for "training a model to be saved" is to verify on a holdout, 
    # then maybe retrain on all? Or just save the one trained on train set?
    # I'll stick to a simple Train/Test split (e.g., last 20% test) to print a valid score,
    # and save that model. Or train on all and print training error?
    # Prompt: "Train the model ... using the last 2 years of data"
    # Prompt: "Validation: Print the 'Precision Score'"
    # I will train on the first ~80% and validate on the last ~20% to give a *real* score.
    
    split = int(len(df) * 0.8)
    train = df.iloc[:split]
    test = df.iloc[split:]
    
    model.fit(train[features], train['Target'])
    
    preds = model.predict(test[features])
    precision = precision_score(test['Target'], preds)
    
    print(f"Precision Score: {precision:.4f}")

    # Re-train on FULL data for the final 'oracle_v1.pkl' to differ to "using last 2 years"
    # or just save the verified one? 
    # Usually you want the best model. 
    # Let's save the one we validated so the score matches the model.
    # Wait, if I want to use it for tomorrow, I should train on all available data.
    # Let's Retrain on ALL data before saving.
    model.fit(X, y)
    
    output_path = 'research/oracle_v1.pkl'
    joblib.dump(model, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train_oracle()
