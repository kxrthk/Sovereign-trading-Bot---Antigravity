import pandas as pd
from datetime import datetime
import os
import guardian

def test_fomo_shield():
    print("--- Testing FOMO Shield ---")
    
    # Disable Drawdown Check for this test
    guardian.HISTORY_PATH = "does_not_exist.csv"
    ids = ["ORD-1", "ORD-2", "ORD-3"]
    t = datetime.now()
    
    data = []
    for i in range(3):
        # All 3 trades within same minute
        data.append({
            "timestamp": t,
            "order_id": ids[i],
            "symbol": "RELIANCE.NS",
            "action": "SELL",
            "price": 2400,
            "quantity": 1,
            "taxes": 0,
            "total_cost": 0,
            "source": "USER"
        })
    
    df = pd.DataFrame(data)
    df.to_csv("trading_journal.csv", index=False)
    print("[TEST] Created fake journal with 3 manual trades in < 1 min.")
    
    # 2. Run Guardian Check
    # We mock 'trigger_emergency_stop' to verify call
    original_trigger = guardian.trigger_emergency_stop
    triggered = False
    
    def mock_trigger(reason):
        nonlocal triggered
        triggered = True
        print(f"[PASS] Guardian Triggered: {reason}")
        
    guardian.trigger_emergency_stop = mock_trigger
    
    guardian.check_system_health()
    
    if triggered:
        print("[PASS] FOMO Shield blocked the panic.")
    else:
        print("[FAIL] Guardian did not react.")
        
    # Cleanup
    guardian.trigger_emergency_stop = original_trigger
    # Remove fake csv? No, stick with valid CSV structure for future.

if __name__ == "__main__":
    test_fomo_shield()
