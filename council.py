import random
import time
import json
import os
import yfinance as yf
from oracle import Oracle
import config
from google import genai

# --- THE COUNCIL OF EXPERTS (Hybrid: Competitive Shards + Reasoning Judge) ---

class Shard:
    def __init__(self, name, philosophy):
        self.name = name
        self.philosophy = philosophy
        self.win_rate = 0.5 # Starts neutral
        self.trades = [] # Track PnL history
        
    def vote(self, market_data, fundamentals, world_view):
        """ Returns: 'BUY', 'SELL', or 'HOLD' based on philosophy """
        return "HOLD" # Placeholder for specialized logic
        
    def update_performance(self, pnl):
        self.trades.append(pnl)
        # Recalculate Win Rate (Last 10 trades)
        recent = self.trades[-10:]
        wins = sum(1 for x in recent if x > 0)
        total = len(recent)
        if total > 0:
            self.win_rate = wins / total

class Council:
    def __init__(self):
        # 1. The Agents (Shards)
        self.shards = [
            Shard("Sniper", "High Precision, High Confidence Only"),
            Shard("Ape", "High Risk, Momentum Chasing"),
            Shard("Contrarian", "Fade the Trend, Buy fear"),
            Shard("Trend", "Follow the Moving Averages")
        ]
        self.active_shard = self.shards[0] # Default
        
        # 2. To avoid losing the 'Quant', we integrate Oracle as a tool for Shards
        self.oracle = Oracle()
        
        # 3. The Judge (LLM) - Using Key Manager
        from utils.key_manager import key_rotator
        self.key_rotator = key_rotator
        self.client = self.key_rotator.get_client()

    def _get_fundamentals(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "pe_ratio": info.get('forwardPE', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "roe": info.get('returnOnEquity', 'N/A'),
                "recommendation": info.get('recommendationKey', 'none')
            }
        except:
            return {"status": "No Data"}

    def convene(self, symbol):
        """ The Main Entry Point for Auto-Trader """
        print(f"\n[COUNCIL] THE COUNCIL IS CONVENING for {symbol}...")
        
        # 1. Gather Evidence
        q_vote = self.oracle.analyze(symbol)
        f_data = self._get_fundamentals(symbol)
        
        world_view = {}
        try:
            with open(os.path.join("memories", "world_view.json"), "r") as f:
                 world_view = json.load(f)
        except: pass
        
        # 2. Shards Cast Votes (Simulated based on Oracle Data + their Personality)
        votes = {}
        for shard in self.shards:
            # Logic: Map Oracle data to Shard Personality
            vote = "HOLD"
            conf = q_vote.get('confidence', 0)
            signal = q_vote.get('signal', 'HOLD')
            rsi = 50 # Mock if not present, ideally Oracle returns full data
            
            # --- SHARD LOGIC ---
            if shard.name == "Sniper":
                if conf > 0.85: vote = signal
            
            elif shard.name == "Ape":
                # Ape loves Momentum but hates Fear
                if world_view.get('risk_level') != 'DANGER' and conf > 0.6:
                    vote = signal
            
            elif shard.name == "Contrarian":
                # Fades the signal if Sentiment is extreme?
                # For now, simplistic:
                if world_view.get('risk_level') == 'DANGER' and signal == 'BUY':
                    vote = "SELL" # Short the hope
            
            elif shard.name == "Trend":
                if world_view.get('regime') == 'TRENDING':
                    vote = signal
            
            votes[shard.name] = vote
            # print(f"   [{shard.name}] Votes: {vote} (WR: {shard.win_rate:.0%})")

        # 3. The Judge Deliberates
        if not self.client:
            return q_vote # Fallback

        prompt = f"""
        You are the CHIEF INVESTMENT OFFICER.
        
        CASE FILE: {symbol}
        
        EVIDENCE:
        - Technicals (Oracle): {q_vote.get('signal')} ({q_vote.get('confidence'):.2f})
        - Fundamentals: P/E {f_data.get('pe_ratio')}, Rec {f_data.get('recommendation')}
        - Global Macro (Cortex): {world_view.get('risk_level', 'UNKNOWN')} ({world_view.get('reasoning', 'N/A')})
        
        THE COUNCIL VOTES:
        {json.dumps(votes, indent=2)}
        
        TASK:
        Issue a FINAL VERDICT.
        1. Weigh the votes. 'Sniper' (Precision) is usually right. 'Contrarian' is good for hedging.
        2. If Cortex says DANGER, be very hesitant to BUY.
        
        OUTPUT JSON ONLY:
        {{
            "signal": "BUY/SELL/HOLD",
            "confidence": float (0.0 to 1.0),
            "reason": "Short explanation."
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            verdict = json.loads(response.text)
            verdict['price'] = q_vote.get('price')
            
            print(f"   [JUDGE] VERDICT: {verdict.get('signal')} ({verdict.get('confidence'):.2f})")
            print(f"       \"{verdict.get('reason')}\"")
            return verdict
            
        except Exception as e:
            print(f"   [JUDGE ERR] {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                self.key_rotator.rotate_key()
                self.client = self.key_rotator.get_client()
            return q_vote

    # --- Backward Compatibility for Tests ---
    def get_market_verdict(self, analysis):
        # Mocks the old function used by test_council.py
        # returns 'BUY', 'SELL' etc.
        # We just return the active shard's "vote" (simulated)
        return analysis.get('signal', 'HOLD') 

    def report_outcome(self, pnl, analysis):
        # Mocks test function
        pass

if __name__ == "__main__":
    c = Council()
    c.convene("RELIANCE.NS")
