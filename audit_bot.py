import csv
import json
import os
import time

JOURNAL_PATH = "trading_journal.csv"
MEMORY_PATH = "memories/bot_brain.json"

def audit_books():
    print("\n[AUDIT] STARTING FORENSIC AUDIT...")
    print("--------------------------------")
    
    # 1. Analyze Journal (The Books)
    csv_balance = 100000.0 # Starting Balance
    trade_count = 0
    
    try:
        with open(JOURNAL_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'total_cost' in row:
                    cost = float(row['total_cost'])
                    csv_balance -= cost
                    trade_count += 1
    except FileNotFoundError:
        print("[ERROR] Journal File Missing!")
        return

    # 2. Analyze Wallet (The Truth)
    real_balance = 0.0
    try:
        with open(MEMORY_PATH, 'r') as f:
            data = json.load(f)
            real_balance = data.get("wallet_balance", 0.0)
    except:
        print("[ERROR] Brain/Wallet Missing!")
        return

    # 3. Check Liveness
    last_modified = os.path.getmtime(JOURNAL_PATH)
    seconds_ago = time.time() - last_modified
    liveness = f"{int(seconds_ago)} seconds ago" if seconds_ago < 60 else f"{int(seconds_ago/60)} minutes ago"

    # 4. The Report
    print(f"[REPORT] Trades Audited: {trade_count}")
    print(f"[REPORT] Calculated Balance (CSV): INR {csv_balance:,.2f}")
    print(f"[REPORT] Actual Wallet Balance:    INR {real_balance:,.2f}")
    print("--------------------------------")
    
    # 5. Integrity Checks
    integrity_issues = []
    
    # Check 1: Balance Match
    diff = abs(csv_balance - real_balance)
    if diff >= 1.0:
        integrity_issues.append(f"Financial Discrepancy: INR {diff:,.2f}")

    # Check 2: Duplicate Order IDs
    seen_ids = set()
    duplicates = []
    try:
        with open(JOURNAL_PATH, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                oid = row.get('order_id')
                if oid:
                    if oid in seen_ids:
                        duplicates.append(oid)
                    seen_ids.add(oid)
    except: pass
    
    if duplicates:
        integrity_issues.append(f"Duplicate Order IDs found: {len(duplicates)}")

    # Final Verdict
    if not integrity_issues:
        print("[PASS] INTEGRITY STATUS: AUTHENTIC")
        print("       (The books match the bank, no duplicates)")
    else:
        print("[FAIL] INTEGRITY STATUS: CORRUPTED")
        for issue in integrity_issues:
            print(f"       - {issue}")
        
    print(f"[INFO] Last Ledger Entry: {liveness}")
    print("--------------------------------\n")

if __name__ == "__main__":
    audit_books()
