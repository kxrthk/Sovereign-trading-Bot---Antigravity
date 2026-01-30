import unittest
from risk_manager import guard
import tax_engine

class TestSmartTarget(unittest.TestCase):
    
    def test_smart_target_logic(self):
        print("\nTesting Smart Target...")
        entry_price = 1000.0
        desired_profit = 0.05 # 5% Net
        
        # 1. Breakeven
        # Charges on 1000 buy ~ 1.2 (0.12%) -> Breakeven ~ 1001.2
        breakeven = tax_engine.calculate_breakeven(entry_price)
        print(f"Breakeven for {entry_price}: {breakeven}")
        self.assertGreater(breakeven, entry_price)
        
        # 2. Smart Target
        # Target = Breakeven * 1.05
        # 1001.2 * 1.05 = 1051.26
        target = guard.get_smart_target(entry_price, desired_profit)
        print(f"Smart Target (Net 5%): {target}")
        
        # Gross Target would be 1000 * 1.05 = 1050.
        # Smart Target must be higher to cover tax.
        self.assertGreater(target, entry_price * (1 + desired_profit))
        
        print("Smart Target: PASSED")

if __name__ == "__main__":
    unittest.main()
