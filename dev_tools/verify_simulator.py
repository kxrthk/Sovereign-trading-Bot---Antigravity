import unittest
from mock_broker import MockDhanClient
import tax_engine
import json
import os

class TestTaxSimulator(unittest.TestCase):
    
    def test_broker_deductions(self):
        print("\nTesting Broker Deductions...")
        
        # Reset Brain for Test
        with open("memories/bot_brain.json", 'w') as f:
            json.dump({"wallet_balance": 100000.0}, f)
        
        broker = MockDhanClient()
        initial_balance = broker.get_fund_balance()
        print(f"Initial Balance: {initial_balance}")
        
        # BUY 100 @ 100
        qty = 100
        price = 100
        
        # Calculate Expected Cost
        charges = tax_engine.calculate_taxes(price, 0, qty)['total_charges']
        expected_cost = (qty * price) + charges
        print(f"Expected Charges: {charges:.2f}. Total Cost: {expected_cost:.2f}")
        
        broker.place_order("TEST", qty, "BUY", price)
        
        new_balance = broker.get_fund_balance()
        print(f"New Balance: {new_balance}")
        
        actual_deduction = initial_balance - new_balance
        self.assertAlmostEqual(actual_deduction, expected_cost, delta=0.01)
        print("Deduction Match: PASSED")

if __name__ == "__main__":
    unittest.main()
