import unittest
import tax_engine

class TestNewTaxEngine(unittest.TestCase):
    
    def test_calculate_taxes(self):
        print("\nTesting New Tax Calculation...")
        # Buy 100 @ 100, Sell 100 @ 110
        # Turnover: Buy 10000, Sell 11000
        # STT: 0.1% of 21000 = 21
        # Stamp: 0.015% of 10000 = 1.5
        # Exch: 0.00345% of 21000 = 0.7245
        # SEBI: 0.0001% of 21000 = 0.021
        # GST: 18% of (0.7455) = 0.13419
        # DP: 12.50 * 1.18 = 14.75
        # Total Charges = 21 + 1.5 + 0.7245 + 0.021 + 0.13419 + 14.75 = ~38.13
        
        res = tax_engine.calculate_taxes(100, 110, 100)
        total = res['total_charges']
        print(f"Total Charges: {total}")
        self.assertAlmostEqual(total, 38.13, delta=0.05)
        
        # Net Profit
        # Gross = 1000
        # Net Pre Tax = 1000 - 38.13 = 961.87
        # Tax = 20% of 961.87 = 192.37
        # Final = 769.50
        print(f"Final In Hand: {res['final_money_in_hand']}")
        self.assertAlmostEqual(res['final_money_in_hand'], 769.50, delta=1.0)
        print("Tax Calculation: PASSED")

    def test_breakeven(self):
        print("\nTesting Breakeven...")
        # Buy @ 100, Qty 100
        # Breakeven needs to cover ~0.38 per share?
        be = tax_engine.get_breakeven_price(100, 100)
        print(f"Breakeven Price: {be}")
        self.assertGreater(be, 100.30)
        print("Breakeven: PASSED")

if __name__ == "__main__":
    unittest.main()
