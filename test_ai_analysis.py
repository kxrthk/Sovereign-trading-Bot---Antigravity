import requests
import json

# 1. Get a trade ID
try:
    res = requests.get("http://localhost:8000/api/user_trades")
    trades = res.json()
    if not trades:
        print("No trades found to test.")
        exit()
    
    trade_id = trades[0]['order_id']
    print(f"Testing Analysis for Trade: {trade_id}")

    # 2. Request Analysis
    res = requests.post("http://localhost:8000/api/analyze_trade", json={"trade_id": trade_id}, timeout=60)
    print(f"Status Code: {res.status_code}")
    print("Response:")
    print(json.dumps(res.json(), indent=2))

except Exception as e:
    print(f"Test Failed: {e}")
