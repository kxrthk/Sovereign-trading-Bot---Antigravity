from mock_broker import MockDhanClient
import random
import time

def simulate_market_activity():
    client = MockDhanClient()
    
    # Randomly pick a stock and movement
    stocks = [
        ("RELIANCE", 2400.0),
        ("TATASTEEL", 145.0),
        ("INFY", 1420.0),
        ("HDFCBANK", 1650.0),
        ("ADANIENT", 2900.0)
    ]
    
    symbol, base_price = random.choice(stocks)
    # Fluctuate price by +/- 2%
    price = base_price * random.uniform(0.98, 1.02)
    quantity = random.randint(1, 10)
    
    print(f"\n[TRIGGER] TRIGGERING TRADE: BUY {quantity} {symbol} @ {price:.2f}...")
    
    result = client.place_order(symbol, quantity, "BUY", price)
    
    if result['status'] == 'success':
        print(f"[SUCCESS] Trade Executed!")
        print(f"   Receipt: {result.get('order_id', 'N/A')}")
        print(f"   Equity Logged: Check account_history.csv")
    else:
        print(f"[FAILED] {result['message']}")

if __name__ == "__main__":
    simulate_market_activity()
