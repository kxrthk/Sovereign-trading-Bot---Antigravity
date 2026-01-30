import random
import time
from datetime import datetime
import pandas as pd
import numpy as np

class Shard:
    """
    A Ghost Bot running a specific strategy personality.
    It trades virtually (Paper Trading) to prove its worth.
    """
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality # Dict of strategy params
        self.virtual_balance = 100000.0 # Starting Simulation Cash
        self.virtual_pnl = 0.0
        self.win_rate = 0.0
        self.trades = []
        self.is_active = True
        
    def evaluate_signal(self, oracle_analysis):
        """
        Decides to Buy/Sell based on personality traits.
        """
        confidence = oracle_analysis.get('confidence', 0.0)
        signal = oracle_analysis.get('signal', 'HOLD')
        rsi = oracle_analysis.get('rsi', 50)
        
        # 1. The Sniper (High Precision, Low Volume)
        if self.name == "Sniper":
            if confidence > 0.85: return signal
            return "HOLD"
            
        # 2. The Ape (High Risk, High Volume)
        elif self.name == "Ape":
            if confidence > 0.60: return signal
            # FOMO Logic: Buy if RSI is high (Momentum)
            if rsi > 70 and signal == "BUY": return "BUY"
            return "HOLD"
            
        # 3. The Contrarian (Bottom Fisher)
        elif self.name == "Contrarian":
            # Buy when others Sell (Low RSI)
            if rsi < 30 and signal == "HOLD": return "BUY" 
            if rsi > 70 and signal == "HOLD": return "SELL"
            # Invert the Oracle?
            if signal == "BUY" and confidence < 0.7: return "SELL" 
            return "HOLD"
            
        # 4. The Trend Follower (Standard)
        elif self.name == "Trend":
            trend_signal = oracle_analysis.get('trend_signal', 0) # SMA 50 > 200
            if trend_signal == 1 and signal == "BUY": return "BUY"
            if trend_signal == 0 and signal == "SELL": return "SELL"
            return "HOLD"

        return "HOLD"

    def update_performance(self, pnl):
        self.virtual_balance += pnl
        self.virtual_pnl += pnl
        self.trades.append(pnl)
        
        # Recalculate Win Rate (Last 20 trades)
        recent = self.trades[-20:]
        wins = sum(1 for x in recent if x > 0)
        if len(recent) > 0:
            self.win_rate = (wins / len(recent)) * 100
        else:
            self.win_rate = 0.0

class Council:
    """
    The Queen. Manages the Shards and routes Real Capital.
    """
    def __init__(self):
        self.shards = [
            Shard("Sniper", {"risk": "low"}),
            Shard("Ape", {"risk": "degen"}),
            Shard("Contrarian", {"risk": "high"}),
            Shard("Trend", {"risk": "medium"}),
            Shard("Theta", {"risk": "options"}) # Future placeholder
        ]
        self.active_shard = self.shards[0] # Default to Sniper
        print(f"[COUNCIL] Assembled {len(self.shards)} Shards.")

    def get_market_verdict(self, oracle_analysis):
        """
        Polls all Shards. Returns the consensus or the decision of the Best Shard.
        """
        # 1. Simulate Shard Decisions
        votes = {}
        print("\n[COUNCIL] Calling the Banners (Voting):")
        
        for shard in self.shards:
            vote = shard.evaluate_signal(oracle_analysis)
            votes[shard.name] = vote
            print(f"   - {shard.name} ({shard.win_rate:.1f}% WR): {vote}")
            
        # 2. Evolutionary Selection (Survival of the Fittest)
        # Sort shards by Win Rate
        ranked_shards = sorted(self.shards, key=lambda x: x.win_rate, reverse=True)
        best_shard = ranked_shards[0]
        
        # 3. Regime Override? 
        # If Best Shard is "Ape" but regime is "CRASH", we might veto.
        # For now, we trust the evolution.
        
        if self.active_shard != best_shard:
            print(f"[COUNCIL] CROWN TRANSFER: {self.active_shard.name} -> {best_shard.name}")
            self.active_shard = best_shard
            
        final_decision = votes[best_shard.name]
        print(f"[COUNCIL] Ruling: Following {best_shard.name} -> {final_decision}")
        
        return final_decision

    def report_outcome(self, pnl, oracle_analysis):
        """
        Back-propagate the result to update Shards' virtual P&L.
        """
        # We simulate what EACH shard would have made
        for shard in self.shards:
            # Re-evaluate what they WOULD have done
            vote = shard.evaluate_signal(oracle_analysis)
            
            # Simple simulation: 
            # If vote matched the market direction (pnl > 0), they win.
            # If vote opposed, they lose.
            if vote == "BUY":
                shard.update_performance(pnl)
            elif vote == "SELL":
                shard.update_performance(-pnl) # Short PnL logic
            else:
                shard.update_performance(0) # HOLD = 0 PnL

if __name__ == "__main__":
    # Test
    c = Council()
    mock_analysis = {'signal': 'BUY', 'confidence': 0.65, 'rsi': 80, 'trend_signal': 1}
    c.get_market_verdict(mock_analysis)
