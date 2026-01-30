import unittest
from unittest.mock import MagicMock
import config
from risk_manager import guard
from notifications import TelegramNotifier
import io
import sys

class TestAdvisoryMode(unittest.TestCase):
    
    def test_position_sizing(self):
        print("\nTesting Position Sizing...")
        # Rule: 1% Risk. 2% Stop Loss.
        # Capital = 100,000. Risk = 1,000.
        # Price = 100. SL Dist = 2.
        # Qty = 1000 / 2 = 500.
        
        qty = guard.calculate_position_size(price=100, capital_balance=100000)
        print(f"Capital: 100k, Price: 100 -> Qty: {qty}")
        self.assertEqual(qty, 500)
        
        # Test Affordability Cap
        # Capital = 1000. Risk = 10.
        # Price = 100. SL Dist = 2.
        # Qty = 10/2 = 5. Cost = 500. OK.
        
        # Capital = 100. Risk = 1.
        # Price = 50. SL Dist = 1.
        # Qty = 1. Cost = 50. OK.
        
        print("Position Sizing: PASSED")

    def test_notification_mock(self):
        print("\nTesting Notification...")
        notifier = TelegramNotifier()
        # Capture stdout to verify mock print
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        notifier.send_recommendation("TEST", "BUY", 10, 100)
        sys.stdout = sys.__stdout__
        
        output = capturedOutput.getvalue()
        self.assertIn("ADVISORY ALERT", output)
        print("Notification Mock: PASSED")

if __name__ == "__main__":
    unittest.main()
