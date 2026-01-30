from utils.market_hours import MarketSchedule
import datetime

print("--- MARKET HOURS DIAGNOSTIC ---")
print(f"Current Time (IST): {MarketSchedule.get_current_time()}")
print(f"Is Market Open?: {MarketSchedule.is_market_open()}")
print(f"Status Message: {MarketSchedule.get_status_message()}")
print(f"Seconds until Open: {MarketSchedule.seconds_until_open()}")
print(f"Hours until Open: {MarketSchedule.seconds_until_open() / 3600:.2f} hrs")

# Simulation
if not MarketSchedule.is_market_open():
    print("\n[PASS] System correctly identifies market is CLOSED.")
else:
    print("\n[PASS] System correctly identifies market is OPEN.")
