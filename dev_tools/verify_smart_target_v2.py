import unittest
import tax_engine
from risk_manager import guard

class TestSmartTargetV2(unittest.TestCase):
    
    def test_net_profit_target(self):
        print("\nTesting Net Profit Target...")
        
        capital = 10000.0
        price = 100.0
        qty = int(capital / price) # 100
        desired_net_pct = 0.05 # 5%
        desired_cash = capital * desired_net_pct # 500
        
        print(f"Capital: {capital}, Qty: {qty}. Desired Net: {desired_cash} (5%)")
        
        # Get Target
        target_price = guard.get_smart_target(price, desired_net_pct, qty)
        print(f"Calculated Target Price: {target_price}")
        
        # Verify result with Tax Engine
        res = tax_engine.calculate_taxes(price, target_price, qty)
        actual_net = res['final_money_in_hand']
        print(f"Actual Net at Target: {actual_net}")
        
        # It should be >= desired_cash, within reasonable rounding error (5 paise step)
        self.assertGreaterEqual(actual_net, desired_cash)
        self.assertLess(actual_net, desired_cash + 50) # Shouldn't be TOO high
        
        # Check implied gross gain
        gross_gain_pct = (target_price - price) / price
        print(f"Implied Gross Gain Required: {gross_gain_pct*100:.2f}%")
        
        # Should be > 5% (likely around 6.5% as user suggested)
        self.assertGreater(gross_gain_pct, 0.06)
        
        print("Net Profit Target: PASSED")

if __name__ == "__main__":
    unittest.main()
