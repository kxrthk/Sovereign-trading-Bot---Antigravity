import requests
import json

url = "http://localhost:8000/api/analyze_trade"

# Simulate a Trade ID that likely exists (from PAPER_TRADES_PATH) or get a random one?
# We need a valid trade ID. Let's just use a dummy one, the server will error "Trade not found" 
# or we need to read the trade list first.

# 1. Get Trades to find a valid ID
try:
    res = requests.get("http://localhost:8000/api/user_trades")
    trades = res.json()
    if not trades:
        print("[SKIP] No trades found to test.")
        exit(0)
    
    trade_id = trades[0]['order_id']
    print(f"[TEST] using Trade ID: {trade_id}")
    
    payload = {
        "trade_id": trade_id,
        "strategy": "Breakout",
        "emotion": "Confidence",
        "notes": "Testing Debug Logger"
    }
    
    print("[TEST] Sending Analysis Request...")
    res = requests.post(url, json=payload)
    print(f"[TEST] Response Code: {res.status_code}")
    print(f"[TEST] Response Body: {res.text}")

except Exception as e:
    print(f"[TEST ERROR] {e}")
