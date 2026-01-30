import yfinance as yf
import pandas as pd
import os
import datetime

# Configuration
SYMBOL = "RELIANCE.NS"
START_DATE = "2015-01-01"
END_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = "memories/history"
OUTPUT_FILE = f"{OUTPUT_DIR}/{SYMBOL}_{START_DATE}_{END_DATE}.csv"

def fetch_history():
    print(f"\n[DATA LAKE] Initializing sequence for {SYMBOL}...")
    print(f"[DATA LAKE] Target Range: {START_DATE} to {END_DATE}")
    
    # Ensure directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # Fetch Data
        print("[NETWORK] Connecting to Yahoo Finance API...")
        data = yf.download(SYMBOL, start=START_DATE, end=END_DATE, progress=False)
        
        if data.empty:
            print("[ERROR] No data received. Check internet or symbol.")
            return

        # Basic Processing
        # Yahoo Finance returns MultiIndex columns in newer versions, flatten them
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        # Reset Index to make Date a column
        data.reset_index(inplace=True)
        
        # Save to CSV
        data.to_csv(OUTPUT_FILE, index=False)
        
        print(f"[SUCCESS] Harvested {len(data)} trading days.")
        print(f"[STORAGE] Saved to: {OUTPUT_FILE}")
        
        # Preview
        print("\nData Sample:")
        print(data.tail(3))
        
    except Exception as e:
        print(f"[CRITICAL] Data Fetch Failed: {e}")

if __name__ == "__main__":
    fetch_history()
