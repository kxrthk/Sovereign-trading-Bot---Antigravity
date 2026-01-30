import unittest
from unittest.mock import MagicMock, patch
from legal_compliance import ComplianceOfficer
from broker_adapter import get_broker_adapter
import pandas as pd

class TestComplianceAPI(unittest.TestCase):
    
    def test_kill_switch(self):
        print("\nTesting Compliance Kill Switch...")
        # 0, 1, 2 trades should be fine
        self.assertTrue(ComplianceOfficer.check_daily_limits(0))
        self.assertTrue(ComplianceOfficer.check_daily_limits(2))
        
        # 3 trades = Limit Reached (Still safe? No, usually check BEFORE adding. If count is 3, means we HAVE 3. Can we add 4th?
        # Logic in risk_manager: "if not check_daily_limits(len(todays_trades))"
        # If len is 3, check(3) returns FALSE? Let's check logic:
        # if count >= 3 return False. Yes.
        
        self.assertFalse(ComplianceOfficer.check_daily_limits(3))
        print("Kill Switch: PASSED")

    def test_broker_adapter(self):
        print("\nTesting Broker Adapter...")
        adapter = get_broker_adapter("research")
        # Fetch data for a reliable symbol
        df = adapter.fetch_data("RELIANCE.NS", period="5d")
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        if hasattr(df.columns, 'droplevel'): # Check cleaning
            # Should be single level
             self.assertIn('Close', df.columns)
             
        print("Broker Adapter (YFinance): PASSED")

if __name__ == "__main__":
    unittest.main()
