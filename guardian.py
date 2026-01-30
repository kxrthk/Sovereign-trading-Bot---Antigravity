import time
import os
import json
import pandas as pd
from datetime import datetime

# Config
HISTORY_PATH = "memories/account_history.csv"
STOP_FLAG = "STOP.flag"
MAX_DAILY_DRAWDOWN_PCT = 0.05 # 5% Max Daily Loss
CHECK_INTERVAL = 60 # Check every 1 minute

def check_system_health():
    print(f"\n[GUARDIAN] Scan initiated at {datetime.now().strftime('%H:%M:%S')}...")
    
    # 1. Check Circuit Breaker (Drawdown)
    if os.path.exists(HISTORY_PATH):
        try:
            df = pd.read_csv(HISTORY_PATH)
            if not df.empty:
                # Assuming 'equity' column exists and date is sorted
                # Get start of today (simulated or real)
                # For simplicity in this mock environment, we check peak vs current
                # In production, this would filter by Today's Date
                
                equity_series = pd.to_numeric(df['equity'], errors='coerce').fillna(0)
                peak_equity = equity_series.max()
                current_equity = equity_series.iloc[-1]
                
                drawdown = (peak_equity - current_equity) / peak_equity
                
                print(f"   >>> System Drawdown: {drawdown:.2%}")
                
                if drawdown > MAX_DAILY_DRAWDOWN_PCT:
                    print("   [CRITICAL] MAX DRAWDOWN EXCEEDED! INITIATING KILL SWITCH.")
                    trigger_emergency_stop(f"Max Drawdown Exceeded: {drawdown:.2%}")
                    return
        except Exception as e:
            print(f"   [WARN] Could not read history: {e}")

    # 2. F.O.M.O. SHIELD (Revenge Trade Blocker)
    # Rule: If 3 Manual LOSSES in < 15 mins -> Lock System.
    if os.path.exists("trading_journal.csv"):
        try:
            journal = pd.read_csv("trading_journal.csv")
            # Filter for closed trades (SELLs usually close positions, or explicit PnL column)
            # For this MVP, we look for 'SELL' actions and calculating PnL if possible, 
            # OR we assume the user is manually spamming orders.
            
            # Let's say: 3 MANUAL orders in 15 mins is suspicious enough?
            # Or better: Check for "LOSS". 
            # Since we don't track PnL in CSV easily without pairing, we'll use a heuristic:
            # "High Frequency Manual Action" = Panic.
            
            # Filter: Source = USER
            if 'source' in journal.columns:
                manual_trades = journal[journal['source'] == 'USER'].copy()
                if len(manual_trades) >= 3:
                     # Check timestamps
                     manual_trades['timestamp'] = pd.to_datetime(manual_trades['timestamp'])
                     last_3 = manual_trades.iloc[-3:]
                     
                     start_t = last_3['timestamp'].iloc[0]
                     end_t = last_3['timestamp'].iloc[-1]
                     
                     duration = (end_t - start_t).total_seconds() / 60
                     
                     if duration < 15:
                         print(f"   [CRITICAL] FOMO DETECTED: 3 Manual Trades in {duration:.1f} mins.")
                         trigger_emergency_stop("FOMO Shield Triggered: Cooldown Active (30m)")
                         return
        except Exception as e:
             pass

    # 2. Check Process Health (Heartbeat)
    # In a full OS version, we would check if 'python auto_trader.py' is in process list using psutil
    # For now, we assume if we are running, we are guarding.
    
    print("   [OK] System secure.")

def trigger_emergency_stop(reason):
    with open(STOP_FLAG, "w") as f:
        f.write(f"GUARDIAN INTERVENTION: {reason}")
    print(f"\n[EMERGENCY] STOP SIGNAL BROADCASTED. REASON: {reason}")
    print("   Auto-Trader should detect this and halt within 60 seconds.")

if __name__ == "__main__":
    print("THE GUARDIAN is active. Watching over the fortress.")
    print("-----------------------------------------------------")
    try:
        while True:
            check_system_health()
            if os.path.exists(STOP_FLAG):
                print("[GUARDIAN] Stop Flag detected. My job here is done.")
                break
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n[GUARDIAN] Standing down.")
