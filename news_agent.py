import feedparser
import google.generativeai as genai
import os
import json
from duckduckgo_search import DDGS
from dotenv import load_dotenv

import config # Use Central Config for Decryption

api_key = config.GEMINI_API_KEY

if not api_key:
    # Use fallback
    pass

if api_key:
    genai.configure(api_key=api_key)

import model_factory
model = model_factory.get_functional_model()

class NewsAgent:
    def __init__(self):
        self.feeds = {
            "INDIA_ECONOMY": "https://economictimes.indiatimes.com/rssfeeds/1286551815.cms",
            "GLOBAL": "https://www.investing.com/rss/market_overview.rss",
            "TECH": "https://feeds.feedburner.com/TechCrunch/"
        }
        # Load the Constitution
        self.constitution_path = os.path.join("training_raw", "news_rules.txt")
        try:
            if os.path.exists(self.constitution_path):
                with open(self.constitution_path, "r") as f:
                    self.constitution = f.read()
            else:
                self.constitution = "Analyze headlines for market impact."
        except:
            self.constitution = "Analyze headlines for market impact."

    def _fetch_headlines(self):
        digest = []
        for cat, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                # Strict Limit: Only top 3 headlines per source to reduce noise
                for entry in feed.entries[:3]:
                    digest.append(f"[{cat}] {entry.title}")
            except: pass
        return "\n".join(digest)

    def _verify_truth(self, suspicious_headline):
        """
        [INVESTIGATOR] Only runs when triggered
        """
        print(f"   [SEARCH] TRIGGERED: Verifying '{suspicious_headline[:40]}...'")
        try:
            results = DDGS().text(suspicious_headline, max_results=3)
            if not results: return "No independent verification found."
            
            # Combine snippets
            evidence = "\n".join([f"- {r['title']} ({r['body'][:100]}...)" for r in results])
            return evidence
        except Exception as e:
            return f"Search Error: {e}"

    def get_market_vibe(self):
        if not api_key:
             return {"score": 0, "status": "NO_KEY", "reason": "API Key Missing"}

        # 1. READ RAW FEED
        headlines = self._fetch_headlines()
        if not headlines: return {"score": 0, "status": "NO_DATA"}

        # --- CLAUDE PATH ---
        from utils.key_manager import key_rotator
        claude = key_rotator.get_anthropic()
        
        gatekeeper_prompt = (
            f"CONSTITUTION:\n{self.constitution}\n\n"
            f"NEWS FEED:\n{headlines}\n\n"
            f"TASK: select the ONE headline that is 'Suspicious', 'Extreme', or 'Rumor-based' and requires fact-checking.\n"
            f"RULES:\n"
            f"1. If news is standard (earnings, mild fluctuation), output 'NONE'.\n"
            f"2. If news is EXTREME (Crash, War, Ban, Fraud), output that headline.\n"
            f"OUTPUT JSON: {{'needs_verification': boolean, 'target_headline': 'string'}}"
        )

        try:
            # 2. THE GATEKEEPER
            if claude:
                msg = claude.messages.create(
                    model="claude-3-5-sonnet-20240620", max_tokens=200, system="You are a JSON Agent.",
                    messages=[{"role": "user", "content": gatekeeper_prompt}]
                )
                resp_text = msg.content[0].text
            else:
                resp = model.generate_content(gatekeeper_prompt)
                resp_text = resp.text
                
            clean_json = resp_text.replace("```json","").replace("```","").strip()
            decision = json.loads(clean_json)
            
            # 3. THE FORK
            verification_data = "Source: RSS Feed (Trusted)."
            if decision.get('needs_verification') is True:
                target = decision.get('target_headline', '')
                if len(target) > 5:
                    print(f"[ALERT] Suspicious news detected. Investigating...")
                    evidence = self._verify_truth(target)
                    verification_data = f"FACT CHECK for '{target}':\n{evidence}"
            
            # 4. FINAL JUDGMENT
            final_prompt = (
                f"You are the Sovereign Judge. \n"
                f"CONSTITUTION:\n{self.constitution}\n\n"
                f"HEADLINES:\n{headlines}\n\n"
                f"VERIFICATION CONTEXT:\n{verification_data}\n\n"
                f"TASK: Score the Market Sentiment (-10 to +10).\n"
                f"RULE: If Verification Context says the news is FAKE or OLD, ignore it.\n"
                f"OUTPUT JSON: {{'score': int, 'reason': 'string'}}"
            )
            
            if claude:
                msg = claude.messages.create(
                    model="claude-3-5-sonnet-20240620", max_tokens=300, system="You are a JSON Agent.",
                    messages=[{"role": "user", "content": final_prompt}]
                )
                final_resp_text = msg.content[0].text
            else:
                final_resp = model.generate_content(final_prompt)
                final_resp_text = final_resp.text
                
            final_clean_json = final_resp_text.replace("```json","").replace("```","").strip()
            return json.loads(final_clean_json)

        except Exception as e:
            print(f"[ERROR] {e}")
            return {"score": 0, "reason": "Error"}

if __name__ == "__main__":
    agent = NewsAgent()
    print("Fetching Market Vibe...")
    print(agent.get_market_vibe())
