import os
import json
import time
import glob
from google import genai
import config

# --- CORTEX: THE REASONING ENGINE ---
# Purpose: Reads scattered news, synthesizes a "World View", and sets the Global DEFCON Level.

from utils.key_manager import key_rotator

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

class Cortex:
    def __init__(self):
        self.client = key_rotator.get_client()
        self.news_dir = os.path.join("training_raw", "news")
        self.memory_path = os.path.join("memories", "world_view.json")

    def load_recent_news(self, hours=24):
        """
        Scans training_raw/news for files modified in the last N hours.
        """
        now = time.time()
        cutoff = now - (hours * 3600)
        
        news_files = glob.glob(os.path.join(self.news_dir, "*.txt"))
        recent_intel = []
        
        print(f"[CORTEX] Scanning Synapses ({len(news_files)} memories total)...")
        
        for f in news_files:
            if os.path.getmtime(f) > cutoff:
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        # Extract just the headline/summary to save tokens
                        lines = content.split('\n')
                        headline = next((l for l in lines if "HEADLINE:" in l), "Unknown News")
                        sentiment = next((l for l in lines if "SENTIMENT:" in l), "Neutral")
                        recent_intel.append(f"{headline} ({sentiment})")
                except:
                    pass
                    
        return recent_intel

    def synthesize_world_view(self):
        """
        The Main Event. Asks Gemini to judge the world state.
        """
        if not self.client:
            print("[CORTEX] No API Key. Cannot think.")
            return None

        # 1. Gather Intelligence
        recent_news = self.load_recent_news(hours=24)
        
        if not recent_news:
            print("[CORTEX] Mind is blank (No recent news). Assuming Neutrality.")
            # Default Neutral State
            default_view = {
                "sentiment_score": 0,
                "risk_level": "CAUTION", 
                "regime": "UNKNOWN",
                "reasoning": "No sensory input.",
                "timestamp": time.time()
            }
            self._save_memory(default_view)
            return default_view

        print(f"[CORTEX] Synthesizing {len(recent_news)} intel reports...")
        
        # 2. The Thought Process (Prompt)
        prompt = f"""
        You are the CORTEX of a Sovereign Trading Bot.
        
        INPUT DATA (Last 24 Hours of Global Intel):
        {json.dumps(recent_news[:5])}  # Limit to 5 items for Absolute Safety
        
        TASK:
        Analyze this data and output a 'World View' JSON.
        
        REQUIREMENTS:
        1. sentiment_score: -10 (The World is Ending) to +10 (Utopia).
        2. risk_level: "SAFE" (Bull Market), "CAUTION" (Choppy), or "DANGER" (Crash/War).
        3. regime: "TRENDING", "RANGING", or "VOLATILE".
        4. sector_watch: List of sectors to WATCH (e.g. ["Energy", "Tech"]).
        5. avoid: List of things to AVOID (e.g. ["Adani", "Crypto"]).
        6. reasoning: A concise, professional executive summary of WHY.
        
        OUTPUT JSON ONLY. NO MARKDOWN.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            world_view = json.loads(response.text)
            world_view['timestamp'] = time.time()
            
            # Save to Disk
            self._save_memory(world_view)
            safe_print("[CORTEX] World View Updated.")
            safe_print(f"   >>> Sentiment: {world_view.get('sentiment_score')} ({world_view.get('risk_level')})")
            safe_print(f"   >>> Insight: {world_view.get('reasoning')[:100]}...")
            
            return world_view
            
        except Exception as e:
            print(f"[CORTEX] Thought Process Failed: {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                key_rotator.rotate_key()
                self.client = key_rotator.get_client()
                print("[CORTEX] Retrying with new key...")
                # Optional: Recursive retry or fail to next cycle
            return None

    def _save_memory(self, data):
        os.makedirs("memories", exist_ok=True)
        with open(self.memory_path, 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    brain = Cortex()
    brain.synthesize_world_view()
