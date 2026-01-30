import unittest
from mock_broker import MockDhanClient
import json
import os

class TestPaperTrading(unittest.TestCase):
    
    def test_mock_broker(self):
        print("\nTesting Mock Broker...")
        broker = MockDhanClient()
        
        # 1. Check Initial Balance (Should be >= 0)
        balance = broker.get_fund_balance()
        print(f"Initial Balance: {balance}")
        self.assertGreaterEqual(balance, 0)
        
        # 2. Place Order
        response = broker.place_order("TEST.NS", 1, "BUY", 1000)
        
        if response['status'] == 'success':
            print("Order Placed Successfully.")
            new_balance = broker.get_fund_balance()
            self.assertEqual(new_balance, balance - 1000)
        else:
            print("Order Failed (Likely Insufficient Funds).")
            
        print("Mock Broker: PASSED")

if __name__ == "__main__":
    unittest.main()
