import sys
import os
sys.path.append(os.getcwd())
from oracle import Oracle

def test_context_switch():
    print("--- Testing Oracle Dynamic Context Switching ---")
    oracle = Oracle()
    
    # Force analyze to trigger the regime check
    # We will see print statements if it switches
    print("\n1. Analyzing (Triggering Regime Check)...")
    analysis = oracle.analyze("RELIANCE.NS")
    
    # Check if context was loaded
    if hasattr(oracle, 'last_regime'):
        print(f"[PASS] Oracle identified Regime: {oracle.last_regime}")
    else:
        print("[FAIL] Oracle did not set last_regime.")
        
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_context_switch()
