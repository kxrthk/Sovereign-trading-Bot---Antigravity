import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    print("Attempting to import utils.market_hours...")
    from utils.market_hours import MarketSchedule
    print("SUCCESS: MarketSchedule imported.")
    print(f"Status: {MarketSchedule.get_status_message()}")
except Exception as e:
    print(f"FAILURE: {e}")
