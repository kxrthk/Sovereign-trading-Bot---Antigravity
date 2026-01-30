import pandas as pd
import json
import os
from datetime import datetime

JOURNAL_PATH = "trading_journal.csv"
REPORT_PATH = "daily_report.json"

def generate_daily_report():
    print("[DEBRIEF] Generating Daily Pulse Report...")
    
    # 1. Load Data
    if not os.path.exists(JOURNAL_PATH):
        return {"grade": "N/A", "message": "No trades recorded today."}
        
    try:
        df = pd.read_csv(JOURNAL_PATH)
        # Filter for Today (simulation: assume all fits for now or filter by date)
        # df['timestamp'] = pd.to_datetime(df['timestamp'])
        # today = datetime.now().date()
        # today_trades = df[df['timestamp'].dt.date == today]
        today_trades = df # For MVP, analyze all
        
        if today_trades.empty:
             return {"grade": "N/A", "message": "No trades today. Market was quiet."}

        # 2. Analyze Performance
        total_trades = len(today_trades)
        
        # Calculate Win Rate (Heuristic: BUYs followed by SELLs?)
        # For MVP, we check "Discipline": Ratio of Bot vs User trades
        # If 'source' column exists
        if 'source' in today_trades.columns:
            manual_trades = len(today_trades[today_trades['source'] == 'USER'])
            bot_trades = len(today_trades[today_trades['source'] != 'USER'])
        else:
            manual_trades = 0
            bot_trades = total_trades

        discipline_score = 100
        if total_trades > 0:
            discipline_score = 100 - ((manual_trades / total_trades) * 100)
            
        # 3. Assign Grade
        grade = "C"
        insight = "Average day."
        
        if discipline_score >= 90:
            grade = "A+"
            insight = "Textbook Discipline! You let the Alpha Algorithms do the heavy lifting."
        elif discipline_score >= 70:
            grade = "B"
            insight = "Good, but you intervened manually a few times. Trust the Council."
        elif discipline_score >= 50:
            grade = "C"
            insight = "You are overruling the bot too much. Let the system breathe."
        else:
            grade = "D"
            insight = "Cowboy Mode detected. High manual interference puts the edge at risk."
            
        # 4. Save
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "grade": grade,
            "insight": insight,
            "stats": {
                "trades": total_trades,
                "manual": manual_trades,
                "bot": bot_trades
            }
        }
        
        with open(REPORT_PATH, "w") as f:
            json.dump(report, f, indent=4)
            
        print(f"[DEBRIEF] Report Generated: Grade {grade}")
        return report

    except Exception as e:
        print(f"[DEBRIEF] Error: {e}")
        return {"grade": "ERR", "message": str(e)}

if __name__ == "__main__":
    generate_daily_report()
