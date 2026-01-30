import json
import os
import math
from datetime import datetime
import config

class RiskManager:
    def __init__(self):
        self.stats_file = "memories/daily_stats.json"
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.stats = self.load_stats()
        
        # Check if it's a new day (Reset Daily P&L, but remember yesterday)
        if self.stats.get("date") != self.today:
            self.start_new_day()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_stats(self):
        # Create folder if missing
        os.makedirs("memories", exist_ok=True)
        with open(self.stats_file, "w") as f:
            json.dump(self.stats, f, indent=4)

    def start_new_day(self):
        """Resets daily counters but activates Cautious Mode if yesterday was a loss."""
        yesterday_pnl = self.stats.get("daily_pnl", 0)
        
        # SMART RECOVERY LOGIC:
        # If we lost money yesterday, we enter "Cautious Mode" today.
        is_cautious = yesterday_pnl < 0
        
        self.stats = {
            "date": self.today,
            "daily_pnl": 0.0,
            "trade_count": 0,
            "is_cautious_mode": is_cautious,  # The "Memory" of pain
            "yesterday_pnl": yesterday_pnl,
            "status": "ACTIVE"  # Options: ACTIVE, STOP_LOSS, TARGET_HIT
        }
        self.save_stats()
        
        if is_cautious:
            print(f"[RISK MANAGER] Recovering from yesterday's loss ({yesterday_pnl}). Cautious Mode ACTIVATED.")

    def update_pnl(self, amount):
        """Called by the Broker after a trade closes to update the Scoreboard."""
        self.stats["daily_pnl"] += amount
        self.stats["trade_count"] += 1
        
        # Check Hard Limits immediately
        if self.stats["daily_pnl"] <= -config.MAX_DAILY_LOSS:
            self.stats["status"] = "STOP_LOSS"
            print(f"[WATCHMAN] Max Daily Loss Hit ({self.stats['daily_pnl']}). Shutting down system.")
            
        elif self.stats["daily_pnl"] >= config.DAILY_PROFIT_TARGET:
            self.stats["status"] = "TARGET_HIT"
            print(f"[STRATEGIST] Profit Target Hit ({self.stats['daily_pnl']}). Bag Secured.")
        
        self.save_stats()

    def can_trade(self):
        """The Gatekeeper Function. Called before every trade."""
        # 1. Check Status Flags
        if self.stats["status"] != "ACTIVE":
            return False
            
        # 2. Redundant Math Check (Double Safety)
        if self.stats["daily_pnl"] <= -config.MAX_DAILY_LOSS:
            return False
        if self.stats["daily_pnl"] >= config.DAILY_PROFIT_TARGET:
            return False
            
        return True

    def get_position_size(self, price):
        """Enforces the 'Max ₹500 per trade' rule."""
        if price <= 0: return 0
        
        # Calculate how many shares we can buy with ₹500
        quantity = math.floor(config.MAX_TRADE_AMOUNT / price)
        
        # If stock is expensive (e.g., ₹2000), result is 0. We don't trade.
        if quantity < 1:
            return 0
            
        return quantity

    def get_required_confidence(self):
        """Returns the AI Confidence % required to take a trade."""
        base_confidence = config.MIN_CONFIDENCE # Usually 0.80
        
        # If we are recovering from a loss, we demand higher perfection
        if self.stats.get("is_cautious_mode", False):
            # Bump requirement by 5% (e.g., 0.80 -> 0.85)
            print("🛡️ CAUTIOUS MODE: Demanding 85% Confidence.")
            return base_confidence + 0.05 
            
        return base_confidence
