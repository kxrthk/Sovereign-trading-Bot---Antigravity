import sys
import os
sys.path.append(os.getcwd())
from oracle import Oracle

def test_oracle():
    print("--- Testing Intraday Oracle ---")
    oracle = Oracle()
    
    # Test 1: Fetch Data
    print("\n1. Fetching 1-Minute Data for RELIANCE.NS...")
    data = oracle.fetch_data("RELIANCE.NS")
    if data.empty:
        print("[FAIL] No data returned.")
    else:
        print(f"[PASS] Got {len(data)} lines. Last: {data.index[-1]}")
        
    # Test 2: Analyze
    print("\n2. Analyzing (Feature Engineering)...")
    analysis = oracle.analyze("RELIANCE.NS")
    print(f"Result: {analysis}")
    
    if analysis['price'] > 0:
        print("[PASS] Price is valid.")
    else:
        print("[FAIL] Invalid price.")
        
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_oracle()
