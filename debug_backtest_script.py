
import yfinance as yf
import numpy as np
import pandas as pd
import json

def run_debug():
    symbol = "RELIANCE.NS"
    period = "1mo"
    print(f"Fetch {symbol} {period}...")
    
    # 1. Fetch
    df = yf.download(symbol, period=period, interval="1d", auto_adjust=True, progress=False)
    print("Columns:", df.columns)
    print("Head:", df.head())

    # Check for MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        print("Detected MultiIndex! Flattening...")
        # Flatten: If 'Close' is ('Close', 'RELIANCE.NS'), take level 0
        # But commonly it is level 0 is 'Price', level 1 is 'Ticker'? No, usually Level 0 is 'Close'
        # Let's just try to access 'Close'
        try:
             print("df['Close'] type:", type(df['Close']))
        except Exception as e:
             print("Access 'Close' failed:", e)

    # Flatten logic proposal
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    print("Columns after flatten:", df.columns)
    
    # 2. Indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # 3. Strategy
    df['Signal'] = np.where(df['SMA_20'] > df['SMA_50'], 1.0, 0.0)
    df['Position'] = df['Signal'].shift(1)
    
    # 4. Returns
    df['Market_Returns'] = df['Close'].pct_change()
    df['Strategy_Returns'] = df['Market_Returns'] * df['Position']
    
    # 5. Costs
    trades = df['Position'].diff().abs()
    transaction_costs = trades * 0.001 
    df['Strategy_Returns'] = df['Strategy_Returns'] - transaction_costs

    # 6. Equity
    df['Benchmark_Equity'] = (1 + df['Market_Returns']).cumprod() * 100000
    df['Strategy_Equity'] = (1 + df['Strategy_Returns']).cumprod() * 100000
    
    df.fillna(100000, inplace=True)
    
    # 9. Format
    chart_data = []
    for index, row in df.iterrows():
        chart_data.append({
            "date": index.strftime("%Y-%m-%d"),
            "strategy": round(row['Strategy_Equity'], 2),
            "benchmark": round(row['Benchmark_Equity'], 2)
        })
        
    print("Chart Data Sample:", chart_data[:3])

if __name__ == "__main__":
    run_debug()
