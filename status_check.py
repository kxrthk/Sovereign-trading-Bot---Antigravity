import json
import pandas as pd
import os
from datetime import datetime

MEMORY_PATH = "memories/bot_brain.json"
JOURNAL_PATH = "trading_journal.csv"

def show_daily_summary():
    print("="*40)
    print(f"SENTINEL STATUS: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, 'r') as f:
            brain = json.load(f)
        
        karma = brain.get('karma_score', 'N/A')
        mood = brain.get('mood', 'N/A')
        heartbeat = brain.get('system_heartbeat', None)
        
        print(f"Stats | Karma: {karma} | Mood: {mood}")
        print(f"Heartbeat: {heartbeat if heartbeat else 'MISSING'}")
        
        # Check if heartbeat is stale (> 3 days) - Silent Guard
        if heartbeat:
            try:
                hb_time = datetime.strptime(heartbeat, "%Y-%m-%d %H:%M:%S.%f")
                delta = datetime.now() - hb_time
                if delta.days > 3:
                    print(f"WARNING: Heartbeat is STALE ({delta.days} days old)!")
                else:
                    print(f"Status: ONLINE (Last pulse {delta} ago)")
            except ValueError:
                print(f"Heartbeat format error: {heartbeat}")

    else:
        print(f"ERROR: Brain not found at {MEMORY_PATH}")
    
    print("="*40)
    
    # Load the journal to see the work done
    if os.path.exists(JOURNAL_PATH):
        try:
            df = pd.read_csv(JOURNAL_PATH)
            if not df.empty:
                print("LATEST ACTIONS (Last 5):")
                # Adjust columns to match what we actually have: timestamp,symbol,action,price,rsi,sma,result,mood_at_time
                cols_to_show = ['timestamp', 'symbol', 'action', 'rsi', 'mood_at_time']
                # Filter strictly for columns that exist
                existing_cols = [c for c in cols_to_show if c in df.columns]
                print(df[existing_cols].tail(5).to_string(index=False))
            else:
                print("Journal is empty.")
        except Exception as e:
            print(f"Error reading journal: {e}")
    else:
        print(f"Journal not found at {JOURNAL_PATH}")
    print("="*40)

if __name__ == "__main__":
    show_daily_summary()
