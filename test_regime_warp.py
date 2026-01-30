import json
import os
import sys
from market_regime import get_market_regime

def test_regime_warp():
    print("--- Testing Regime Warp (Scenario Injection) ---")
    
    # 1. Create Lock File
    lock_file = "active_scenario.json"
    scenario_data = {
        "name": "Flash Crash 2008",
        "path": "scenarios/flash_crash_2008.csv"
    }
    
    with open(lock_file, "w") as f:
        json.dump(scenario_data, f)
        
    print("[TEST] Injected 'active_scenario.json'.")
    
    # 2. Run Regime Check
    regime = get_market_regime()
    print(f"[TEST] Result Regime: {regime}")
    
    # 3. Validation
    if regime == "CRASH":
        print("[PASS] System detected simulated CRASH.")
    else:
        print(f"[FAIL] System returned {regime}. Expected CRASH.")
        
    # 4. Cleanup
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print("[TEST] Cleaned up lock file.")

if __name__ == "__main__":
    test_regime_warp()
