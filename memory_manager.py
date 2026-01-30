import json
import os
import datetime

import csv

MEMORY_PATH = "./memories/bot_brain.json"
JOURNAL_PATH = "trading_journal.csv"

class MemoryManager:
    def __init__(self, memory_path=MEMORY_PATH, journal_path=JOURNAL_PATH):
        self.memory_path = memory_path
        self.journal_path = journal_path
        self.memory = self.load_memory()

    def load_memory(self):
        """Loads the bot brain from JSON, or initializes if missing."""
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Corrupt memory file at {self.memory_path}. Initializing new brain.")
                return self._initialize_brain()
        else:
            return self._initialize_brain()

    def _initialize_brain(self):
        """Returns the default brain structure."""
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        return {
            "karma_score": 0.0,
            "active_trades": [],
            "past_trades": [],
            "mood": "Conservative", # Default mood
            "system_heartbeat": str(datetime.datetime.now())
        }

    def save_memory(self):
        """Saves the current memory state to JSON."""
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def update_karma(self):
        """Updates Karma Score based on past trade results."""
        past_trades = self.memory.get("past_trades", [])
        if not past_trades:
            self.memory["karma_score"] = 0.0
            return

        wins = sum(1 for t in past_trades if t.get("result") == "WIN")
        losses = len(past_trades) - wins
        # simple score: +1 for win, -1 for loss, normalized or raw?
        # User asked to "check trading_journal.csv for past performance"
        # For simplicity, we calculate win rate and map to score.
        win_rate = (wins / len(past_trades)) * 100
        self.memory["karma_score"] = round(win_rate, 2)
        self._update_mood()
        self.save_memory()

    def update_oracle_confidence(self, confidence):
        """Updates the latest Oracle Confidence score."""
        self.memory["latest_oracle_confidence"] = float(confidence)
        self.save_memory()


    def _update_mood(self):
        """Adjusts mood based on Karma (IQ)."""
        karma = self.memory.get("karma_score", 0)
        # If High Karma (High Win Rate), likely Aggressive.
        # If Low Karma, Conservative.
        if karma > 60:
            self.memory["mood"] = "Aggressive"
        else:
            self.memory["mood"] = "Conservative"

    def authorize_trade(self, symbol):
        """
        Checks trade authorization.
        Mood: Aggressive (allow > 40% win rate), Conservative (allow > 50%).
        """
        past_trades = self.memory.get("past_trades", [])
        if len(past_trades) < 5: 
            return True
            
        win_rate = self.memory.get("karma_score", 0)
        mood = self.memory.get("mood", "Conservative")
        
        threshold = 40.0 if mood == "Aggressive" else 50.0
        
        if win_rate >= threshold:
            return True
            
        print(f"Trade DENIED for {symbol}. Karma: {win_rate}% (Mood: {mood}, Threshold: {threshold}%)")
        return False

    def log_trade(self, trade_data):
        """Logs a new active trade and writes to Journal."""
        trade_entry = {
            "symbol": trade_data.get("symbol"),
            "entry_price": trade_data.get("price"),
            "entry_rsi": trade_data.get("rsi"),
            "oracle_confidence": trade_data.get("oracle_confidence", 0.0),
            "timestamp": str(datetime.datetime.now()),
            "status": "OPEN",
            "mood_at_time": self.memory.get("mood", "Conservative")
        }
        self.memory.setdefault("active_trades", []).append(trade_entry)
        self.save_memory()
        
        # Write to CSV
        self.log_journal_entry(trade_entry, action="BUY")
        print(f"Trade LOGGED: {trade_entry['symbol']} @ {trade_entry['entry_price']} ({trade_entry['mood_at_time']}) Conf: {trade_entry['oracle_confidence']}")

    def log_journal_entry(self, trade_data, action="BUY", result="OPEN"):
        """Appends to trading_journal.csv."""
        try:
            file_exists = os.path.isfile(self.journal_path)
            
            with open(self.journal_path, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # Write Header if new file
                if not file_exists:
                    writer.writerow([
                        'timestamp', 'symbol', 'action', 'price', 
                        'rsi', 'sma', 'result', 'mood_at_time', 'oracle_confidence'
                    ])
                
                # timestamp,symbol,action,price,rsi,sma,result,mood_at_time,oracle_confidence
                writer.writerow([
                    trade_data.get("timestamp"),
                    trade_data.get("symbol"),
                    action,
                    trade_data.get("entry_price"),
                    trade_data.get("entry_rsi"),
                    trade_data.get("sma", 0), # Added SMA placeholder if passed
                    result,
                    trade_data.get("mood_at_time"),
                    trade_data.get("oracle_confidence", 0.0)
                ])
        except Exception as e:
            print(f"Error writing to journal: {e}")

    def resolve_active_trades(self, current_prices):
        """
        Checks active trades against current prices.
        Closes trade if:
        - Profit >= 5% (WIN)
        - Loss >= 2% (LOSS)
        """
        active_trades = self.memory.get("active_trades", [])
        still_active = []
        resolved_count = 0
        
        for trade in active_trades:
            symbol = trade['symbol']
            if symbol not in current_prices:
                still_active.append(trade)
                continue
                
            entry_price = trade['entry_price']
            current_price = current_prices[symbol]
            
            # ROI Calculation
            roi = ((current_price - entry_price) / entry_price) * 100
            
            result = None
            if roi >= 5.0:
                result = "WIN"
            elif roi <= -2.0:
                result = "LOSS"
                
            if result:
                # Close Trade
                trade['exit_price'] = current_price
                trade['exit_timestamp'] = str(datetime.datetime.now())
                trade['result'] = result
                trade['roi'] = round(roi, 2)
                trade['status'] = "CLOSED"
                
                self.memory.setdefault("past_trades", []).append(trade)
                self.log_journal_entry(trade, action="SELL", result=result)
                print(f"Trade CLOSED: {symbol} | Result: {result} | ROI: {trade['roi']}%")
                resolved_count += 1
            else:
                still_active.append(trade)
        
        self.memory["active_trades"] = still_active
        self.save_memory()
        
        if resolved_count > 0:
            self.update_karma()
            print(f"Resolved {resolved_count} trades. New Karma: {self.memory.get('karma_score')}")

    def update_heartbeat(self):
        """Updates the system heartbeat timestamp."""
        self.memory["system_heartbeat"] = str(datetime.datetime.now())
        self.save_memory()
        print(f"System Heartbeat UPDATED: {self.memory['system_heartbeat']}")

if __name__ == "__main__":
    mm = MemoryManager()
    print("Memory:", mm.memory)
    # Test Resolution
    # mm.resolve_active_trades({'TEST.NS': 110}) # Assuming entry was 100
    mm.update_karma() 
    print("Updated Memory:", mm.memory)
