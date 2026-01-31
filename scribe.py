import os
import json
import time
from datetime import datetime
from google import genai
import config

# Initialize Client
api_key = config.GEMINI_API_KEY
client = None
if api_key:
    if api_key.startswith("ENC:"):
        from crypto_vault import decrypt_secret
        api_key = decrypt_secret(api_key[4:])
    try:
        client = genai.Client(api_key=api_key)
    except: pass

LOGS_DIR = "memories/daily_logs"
NEWS_DIR = "training_raw/news"
TRADES_PATH = "memories/paper_trades.json"

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

class Scribe:
    """
    The Historian. Writes the Daily Captain's Log.
    """
    def generate_daily_log(self, date_str=None):
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        print(f"\n[SCRIBE] 📜 Writing Log for {date_str}...")
        
        # 1. Gather Intelligence
        intel_summary = self._gather_news(date_str)
        trade_summary = self._gather_trades(date_str)
        
        if not client:
            return {"error": "AI Brain Offline"}

        # 2. The Narrative Prompt
        prompt = f"""
        You are the AI Captain of the 'Sovereign Trading Bot'.
        DATE: {date_str}
        
        INTEL REPORT (News & Events):
        {intel_summary}
        
        MISSION LOG (Trades Executed):
        {trade_summary}
        
        TASK: Write a Daily Captain's Log (Max 3 paragraphs).
        
        TONE:
        - Formal but Friendly (like a sci-fi ship captain).
        - Usage "We" (The Crew).
        - Highlight the connection between INTEL and ACTION. (e.g. "Oil news broke, so we went long.")
        - If no trades, explain why (e.g. "The seas were too choppy today, holding steady.")
        
        FORMAT:
        - Start with a "Stardate" or Greeting.
        - Paragraph 1: Market Context (What happened in the world?).
        - Paragraph 2: Tactical Response (What did we buy/sell and why?).
        - Paragraph 3: Outlook for Tomorrow.
        
        OUTPUT JSON: {{ "title": "String", "log": "String", "mood": "String (e.g. Bullish/Cautious)" }}
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            data = json.loads(response.text)
            
            # Save to Disk
            log_entry = {
                "date": date_str,
                "timestamp": datetime.now().isoformat(),
                "title": data.get("title", "Daily Log"),
                "content": data.get("log", "Log generation error."),
                "mood": data.get("mood", "Neutral"),
                "stats": {
                    "news_count": intel_summary.count("ARTICLE"),
                    "trade_count": trade_summary.count("BUY") + trade_summary.count("SELL")
                }
            }
            
            save_path = os.path.join(LOGS_DIR, f"{date_str}.json")
            with open(save_path, "w") as f:
                json.dump(log_entry, f, indent=4)
                
            print(f"   [SCRIBE] Log Saved: {save_path}")
            return log_entry
            
        except Exception as e:
            print(f"   [ERR] Scribing failed: {e}")
            return {"error": str(e)}

    def _gather_news(self, date_str):
        # Scan training_raw/news for files modified today? 
        # Or Just grab top 5 latest.
        # Let's grab files created on 'date_str' ideally, but for now grab active news.
        # Assuming news_scout cleans up or we just take sample.
        report = ""
        if os.path.exists(NEWS_DIR):
            files = os.listdir(NEWS_DIR)
            # Filter? Let's just take top 5 txts
            count = 0
            for f in files:
                if f.endswith(".txt"):
                    try:
                        with open(os.path.join(NEWS_DIR, f), 'r') as file:
                            report += f"ARTICLE: {f}\n{file.read()[:200]}...\n\n"
                            count += 1
                        if count >= 5: break
                    except: pass
        return report if report else "No significant intelligence gathered."

    def _gather_trades(self, date_str):
        report = ""
        if os.path.exists(TRADES_PATH):
            try:
                with open(TRADES_PATH, 'r') as f:
                    trades = json.load(f)
                    
                # Filter for Date
                # Timestamps are likely ISO or various formats.
                # Simple string match for YYYY-MM-DD
                daily_trades = [t for t in trades if date_str in str(t.get('timestamp', ''))]
                
                for t in daily_trades:
                    report += f"{t.get('action')} {t.get('symbol')} @ {t.get('avg_price')} (Origin: {t.get('origin')})\n"
                    
            except: pass
        return report if report else "No trades executed."

if __name__ == "__main__":
    scribe = Scribe()
    scribe.generate_daily_log()
