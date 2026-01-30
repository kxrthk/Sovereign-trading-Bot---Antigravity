import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import sentinel_main

class TestVibeOrchestration(unittest.TestCase):
    
    @patch('sentinel_main.fetch_and_scan')
    @patch('sentinel_main.oracle_interface.get_oracle_prediction')
    @patch('sentinel_main.guard.validate')
    @patch('sentinel_main.MemoryManager')
    def test_full_workflow(self, mock_mm, mock_validate, mock_oracle, mock_scout):
        # 1. Setup Scout Mock
        mock_df = pd.DataFrame({'Close': [100]*200})
        scout_data = [{
            'symbol': 'TEST.NS',
            'price': 100,
            'rsi': 45,
            'timestamp': 'now',
            'data': mock_df
        }]
        mock_scout.return_value = scout_data
        
        # 2. Setup Oracle Mock
        mock_oracle.return_value = 0.88 # High confidence
        
        # 3. Setup Guard Mock
        mock_validate.return_value = "GO"
        
        # 4. Run Sentinel
        sentinel_main.run_sentinel()
        
        # 5. Assertions
        mock_scout.assert_called_once()
        mock_oracle.assert_called_once()
        mock_validate.assert_called_with(0.88, 'TEST.NS')
        mock_mm.return_value.log_trade.assert_called_once()
        
        print("\nTest 1 (Success Flow): PASSED")
        
    @patch('sentinel_main.fetch_and_scan')
    @patch('sentinel_main.oracle_interface.get_oracle_prediction')
    @patch('sentinel_main.guard.validate')
    @patch('sentinel_main.MemoryManager')
    def test_guard_blocking(self, mock_mm, mock_validate, mock_oracle, mock_scout):
        # 1. Setup Scout Mock
        mock_df = pd.DataFrame({'Close': [100]*200})
        scout_data = [{
            'symbol': 'RISKY.NS',
            'price': 100,
            'rsi': 45,
            'timestamp': 'now',
            'data': mock_df
        }]
        mock_scout.return_value = scout_data
        
        # 2. Setup Oracle Mock (Low Confidence)
        mock_oracle.return_value = 0.40 
        
        # 3. Setup Guard Mock (Blocks it)
        mock_validate.return_value = "NO_GO"
        
        # 4. Run Sentinel
        sentinel_main.run_sentinel()
        
        # 5. Assertions
        mock_validate.assert_called_with(0.40, 'RISKY.NS')
        mock_mm.return_value.log_trade.assert_not_called()
        
        print("Test 2 (Guard Block): PASSED")

if __name__ == "__main__":
    unittest.main()
