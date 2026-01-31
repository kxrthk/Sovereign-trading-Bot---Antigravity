import yfinance as yf
import json

symbol = "RELIANCE.NS"
print(f"Fetching fundamentals for {symbol}...")
ticker = yf.Ticker(symbol)
info = ticker.info

# Extract key/val for the Fundamentalist
keys = ['forwardPE', 'trailingPE', 'marketCap', 'sector', 'industry', 'auditRisk', 'boardRisk', 'returnOnEquity', 'debtToEquity']
filtered = {k: info.get(k, 'N/A') for k in keys}

print(json.dumps(filtered, indent=2))
