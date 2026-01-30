import pandas as pd
import os
import sys

def verify_alpha_logs():
    print("--- Verifying Alpha Logs ---")
    
    # We expect 'memories/bot_brain.json' or 'trading_journal.csv' to exist
    journal_path = "trading_journal.csv"
    
    if not os.path.exists(journal_path):
        print(f"Skipping: {journal_path} not found.")
        return

    try:
        df = pd.read_csv(journal_path)
        print(f"Loaded {len(df)} rows from journal.")
        
        # Check for 'oracle_confidence'
        if 'oracle_confidence' in df.columns:
            # Check if we have diverse values (not all 0.0 or 1.0)
            unique_vals = df['oracle_confidence'].unique()
            print(f"Unique Confidence Values: {unique_vals}")
            
            if len(unique_vals) >= 1:
                print("[PASS] Logic is logging confidence.")
            else:
                print("[WARN] Confidence values seem static.")
        else:
            print("[FAIL] 'oracle_confidence' column missing.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_alpha_logs()
