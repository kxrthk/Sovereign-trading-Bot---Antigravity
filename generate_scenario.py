import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_flash_crash():
    """
    Generates a synthetic 1-minute interval dataset representing a massive market crash.
    Drop: -5% in 15 minutes.
    Volatility: Extreme.
    """
    print("generating flash crash scenario...")
    
    # 1. Setup Timeframe (Today, last 2 hours)
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=200)
    timestamps = pd.date_range(start=start_time, end=end_time, freq='1min')
    
    # 2. Start at Nifty 20,000
    price = 20000.0
    data = []
    
    for i, t in enumerate(timestamps):
        # First 100 mins: Calm (Normal Volatility)
        # Last 100 mins: Crash (High Volatility)
        if i < 100:
            volatility = 0.0005 # Calm
            drift = 0.0001 # Slight Drift Up
            spread = 5 # Tight Spreads
        else:
            volatility = np.random.uniform(0.003, 0.008) # Extreme Vol (10x)
            drift = -0.004 # Heavy Dumping
            spread = 30 # Wide Spreads

        change = price * (drift + np.random.normal(0, volatility))
        price += change
        
        # Candles
        open_p = price + np.random.uniform(-spread/5, spread/5)
        close_p = price
        high_p = max(open_p, close_p) + np.random.uniform(0, spread)
        low_p = min(open_p, close_p) - np.random.uniform(0, spread)
        
        data.append({
            "Date": t,
            "Open": open_p,
            "High": high_p,
            "Low": low_p,
            "Close": close_p,
            "Volume": np.random.randint(50000, 500000) # Panic Volume
        })
        
    df = pd.DataFrame(data)
    
    # Save to scenarios folder
    output_path = "scenarios/flash_crash_2008.csv"
    df.to_csv(output_path, index=False)
    print(f"[SCENARIO] Flash Crash data generated at {output_path}")

if __name__ == "__main__":
    generate_flash_crash()
