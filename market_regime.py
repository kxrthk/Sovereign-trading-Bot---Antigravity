import pandas as pd
import numpy as np
import os
import yfinance as yf
import time
import json # Added for Scenario Lock

# Cache path for NIFTY data
NIFTY_DATA_PATH = "memories/history/nifty_intraday.csv"

def _calculate_regime_from_df(df_input):
    """Refactored logic to calculate regime from any DF (Real or Sim)."""
    # Create explicit copy to avoid SettingWithCopyWarning
    df = df_input.copy()
    
    # Ensure columns exist
    req_cols = ['High', 'Low', 'Close']
    for c in req_cols:
        if c not in df.columns: return "UNKNOWN"
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    df = df.dropna(subset=req_cols)
    
    # ATR Analysis
    df['High_Low'] = df['High'] - df['Low']
    df['ATR'] = df['High_Low'].rolling(window=14).mean()
    
    # Normalize ATR by Price to get Percentage Volatility
    df['Vol_Pct'] = (df['ATR'] / df['Close']) * 100

    if df.empty: return "UNKNOWN"
    
    current_vol = df['Vol_Pct'].iloc[-1]
    avg_vol = df['Vol_Pct'].mean()
    
    if pd.isna(current_vol): return "UNKNOWN"

    print(f"[REGIME] Volatility: {current_vol:.2f}% (Avg: {avg_vol:.2f}%)")

    # CRASH LOGIC: Volatility spike AND Price Drop
    # (Simple logic for now: Just Volatility > 1.5x)
    if current_vol > (avg_vol * 1.5):
        return "CRASH" # High Panic (>1.5x normal)
    elif current_vol < (avg_vol * 0.7):
        return "CHOP" # Low Action
    else:
        return "TREND" # Goldilocks

def get_market_regime():
    """
    Analyzes NIFTY 50 Volatility to determine the 'Weather'.
    Returns: 'TREND' (Safe), 'CHOP' (Low Vol), 'CRASH' (High Vol)
    """
    try:
        # --- REGIME WARP (Scenario Injection) ---
        scenario_lock = "active_scenario.json"
        
        # 1. Check if a Simulation is Active
        if os.path.exists(scenario_lock):
             try:
                 with open(scenario_lock, 'r') as f:
                     scenario_config = json.load(f)
                     
                 scenario_path = scenario_config.get("path")
                 if scenario_path and os.path.exists(scenario_path):
                     # [FIX] Removed Unicode Emoji for Windows Compatibility
                     print(f"[REGIME] [!] SIMULATION ACTIVE: Warping Reality to {scenario_config.get('name')}...")
                     df = pd.read_csv(scenario_path)
                     # Ensure Date parsing
                     df['Date'] = pd.to_datetime(df['Date'])
                     df.set_index('Date', inplace=True)
                     
                     return _calculate_regime_from_df(df)
             except Exception as e:
                 print(f"[REGIME] Simulation Error: {e}. Reverting to Reality.")
                 pass

        # 2. Reality (Live Data)
        # Fetch/Load Data
        is_stale = False
        if os.path.exists(NIFTY_DATA_PATH):
            file_age = time.time() - os.path.getmtime(NIFTY_DATA_PATH)
            if file_age > 86400: # 24 Hours
                is_stale = True

        
        if not os.path.exists(NIFTY_DATA_PATH) or is_stale:
             print("[REGIME] Refreshing NIFTY Data...")
             # Force clean download (Intraday 1m for Flash Crash Detection)
             df = yf.download("^NSEI", period="5d", interval="1m", progress=False, auto_adjust=True)
             
             # Create dir if missing
             if not os.path.exists("memories/history"):
                os.makedirs("memories/history")
             
             df.to_csv(NIFTY_DATA_PATH)
        else:
             df = pd.read_csv(NIFTY_DATA_PATH)

        # Flatten MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure we have required columns
        req_cols = ['High', 'Low', 'Close']
        if not set(req_cols).issubset(df.columns):
             df = pd.read_csv(NIFTY_DATA_PATH, header=1) 
             if not set(req_cols).issubset(df.columns):
                 df = yf.download("^NSEI", period="1y", interval="1d", progress=False, auto_adjust=True)
                 if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

        return _calculate_regime_from_df(df)

    except Exception as e:
        print(f"Regime Error: {e}")
        return "UNKNOWN"

if __name__ == "__main__":
    status = get_market_regime()
    print(f"CURRENT REGIME: {status}")
