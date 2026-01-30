
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def run_debug():
    symbol = "GOLDBEES.NS"
    days = 30
    print(f"Testing Oracle for {symbol}...")

    # 1. Fetch
    df = yf.download(symbol, period="1y", interval="1d", auto_adjust=True, progress=False)
    print(f"Data Shape: {df.shape}")
    
    if df.empty:
        print("ERROR: Empty Data")
        return

    # Fix MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    print("Columns:", df.columns)

    # 2. Stats
    log_returns = np.log(1 + df['Close'].pct_change())
    u = log_returns.mean()
    var = log_returns.var()
    drift = u - (0.5 * var)
    stdev = log_returns.std()
    
    print(f"Drift: {drift}, Stdev: {stdev}")

    # 3. Monte Carlo
    iterations = 1000
    daily_returns = np.exp(drift + stdev * np.random.normal(0, 1, (days, iterations)))
    
    last_price = df['Close'].iloc[-1]
    price_paths = np.zeros_like(daily_returns)
    price_paths[0] = last_price * daily_returns[0]
    
    for t in range(1, days):
         price_paths[t] = price_paths[t-1] * daily_returns[t]
         
    final_prices = price_paths[-1]
    print(f"Forecast P50: {np.percentile(final_prices, 50)}")
    print("SUCCESS")

if __name__ == "__main__":
    run_debug()
