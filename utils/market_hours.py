from datetime import datetime, time, timedelta
import pytz

# NSE CONSTANTS (IST)
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)
IST = pytz.timezone('Asia/Kolkata')

class MarketSchedule:
    @staticmethod
    def get_current_time():
        """Returns current time in IST"""
        return datetime.now(IST)

    @staticmethod
    def is_market_open(force_override=False):
        """
        Checks if NSE is currently open for trading.
        Returns: True if Open, False if Closed.
        """
        if force_override:
            return True
            
        now_ist = MarketSchedule.get_current_time()
        
        # 1. Check Weekend (5=Sat, 6=Sun)
        if now_ist.weekday() >= 5:
            return False

        # 2. Check Time (09:15 - 15:30)
        current_time = now_ist.time()
        if MARKET_OPEN <= current_time <= MARKET_CLOSE:
            return True
            
        return False

    @staticmethod
    def get_status_message():
        """Returns a human string: 'OPEN', 'CLOSED (Weekend)', etc."""
        now_ist = MarketSchedule.get_current_time()
        
        if now_ist.weekday() >= 5:
            return "CLOSED (Weekend)"
            
        current_time = now_ist.time()
        if current_time < MARKET_OPEN:
            return "CLOSED (Pre-Market)"
        elif current_time > MARKET_CLOSE:
            return "CLOSED (Post-Market)"
            
        return "OPEN (Live)"

    @staticmethod
    def seconds_until_open():
        """
        Returns seconds to sleep until next market open.
        """
        now_ist = MarketSchedule.get_current_time()
        today_open = datetime.combine(now_ist.date(), MARKET_OPEN).replace(tzinfo=IST)
        
        # If morning (before 9:15), sleep until today 9:15
        if now_ist < today_open:
            return (today_open - now_ist).total_seconds()
            
        # If after 3:30 or weekend, calculate next weekday 9:15
        next_open = today_open + timedelta(days=1)
        while next_open.weekday() >= 5: # Skip Sat/Sun
             next_open += timedelta(days=1)
             
        return (next_open - now_ist).total_seconds()

if __name__ == "__main__":
    # Test
    print(f"Current Time (IST): {MarketSchedule.get_current_time()}")
    print(f"Status: {MarketSchedule.get_status_message()}")
    print(f"Is Open? {MarketSchedule.is_market_open()}")
    print(f"Seconds to Open: {MarketSchedule.seconds_until_open()}")
