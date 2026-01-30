import pandas as pd
import json
import os
from datetime import datetime

JOURNAL_PATH = "trading_journal.csv"
BADGES_PATH = "memories/badges.json"

BADGE_DEFINITIONS = {
    "sniper": {
        "name": "The Sniper",
        "desc": "3 Consecutive Wins",
        "icon": "🎯"
    },
    "diamond_hands": {
        "name": "Diamond Hands", 
        "desc": "Held a position for >30 mins and Won",
        "icon": "💎"
    },
    "iron_will": {
        "name": "Iron Will",
        "desc": "No Manual Interventions for 5 Trades",
        "icon": "🛡️"
    }
}

def check_badges():
    print("[TROPHY] Checking for new accolades...")
    unlocked_badges = []
    
    if not os.path.exists(JOURNAL_PATH):
        return []

    try:
        # Load Trades
        df = pd.read_csv(JOURNAL_PATH)
        # We need "Closed" trades to check wins.
        # MVP Logic: Assume "SELL" rows are potentially closing trades or use a simplified heuristic.
        # Better: Use the same logic as dashboard "reconstruct trades".
        
        # For Speed/MVP: 
        # Check "Sniper": Do we have 3 rows with 'profitability' > 0? 
        # Since CSV doesn't store PnL directly (only prices), we need to rely on 'memories/paper_trades.json' if available, OR calculate it.
        # Let's use 'memories/paper_trades.json' for reliable PnL.
        
        paper_path = "memories/paper_trades.json"
        if os.path.exists(paper_path):
            with open(paper_path, 'r') as f:
                trades = json.load(f)
            
            # 1. Check Sniper (3 Wins in a row)
            wins_streak = 0
            for t in trades:
                pnl = t.get('profitability', '0%')
                try:
                    pnl_val = float(pnl.replace('%',''))
                    if pnl_val > 0: wins_streak += 1
                    else: wins_streak = 0
                except: pass
                
                if wins_streak >= 3:
                    unlocked_badges.append("sniper")
                    break
            
            # 2. Check Diamond Hands (One trade > 30m duration)
            for t in trades:
                # Calculate duration ? 
                # If we don't store it, we skip.
                pass

        # 3. Check Iron Will (Source check from CSV)
        if 'source' in df.columns:
            # Get last 5 trades
            last_5 = df.tail(5)
            if len(last_5) >= 5:
                # If ALL are NOT 'USER'
                system_trades = last_5[last_5['source'] != 'USER']
                if len(system_trades) == 5:
                    unlocked_badges.append("iron_will")

        # Compile Result
        results = []
        for bid in set(unlocked_badges):
            b = BADGE_DEFINITIONS.get(bid)
            if b:
                results.append(b)
        
        # Save cache
        with open(BADGES_PATH, "w") as f:
            json.dump(results, f, indent=4)
            
        print(f"[TROPHY] Unlocked: {[b['name'] for b in results]}")
        return results

    except Exception as e:
        print(f"[TROPHY] Error: {e}")
        return []

if __name__ == "__main__":
    check_badges()
