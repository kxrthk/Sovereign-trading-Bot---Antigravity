import oracle_interface
import pandas as pd
import numpy as np
import daily_bot

def test_oracle():
    print("Testing Oracle Interface...")
    # Create dummy data
    dates = pd.date_range(start='2024-01-01', periods=20, freq='D')
    df = pd.DataFrame({
        'Open': np.random.rand(20) * 100,
        'High': np.random.rand(20) * 100 + 10,
        'Low': np.random.rand(20) * 100 - 10,
        'Close': np.random.rand(20) * 100
    }, index=dates)
    
    prob = oracle_interface.get_oracle_prediction(df)
    print(f"Oracle Probability for dummy data: {prob}")
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0
    print("Oracle Interface Test Passed.")

def test_daily_bot_import():
    print("Testing Daily Bot properties...")
    # Just check if function exists and runs
    try:
        daily_bot.analyze_stock('RELIANCE.NS') 
        print("daily_bot.analyze_stock ran successfully (returned Result or None)")
    except Exception as e:
        print(f"daily_bot.analyze_stock failed: {e}")

if __name__ == "__main__":
    test_oracle()
    test_daily_bot_import()
