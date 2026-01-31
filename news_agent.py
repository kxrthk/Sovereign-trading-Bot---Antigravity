import feedparser

import os
import json
from duckduckgo_search import DDGS
from dotenv import load_dotenv

import config # Use Central Config for Decryption

api_key = config.GEMINI_API_KEY

# Removed deprecated genai.configure. Relying on model_factory/client.

import model_factory
import model_factory
model = model_factory.get_functional_model()

# SUPER-INTELLIGENCE MODULES
try:
    from deep_research import DeepResearchAgent
    from bank_watcher import BankWatcher
except ImportError:
    DeepResearchAgent = None
    BankWatcher = None

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
        [INVESTIGATOR] Multi-Source Cross-Verification
        """
        try:
            print(f"   [SEARCH] TRIGGERED: Verified Truth Search for '{suspicious_headline[:40]}...'")
        except:
             print("   [SEARCH] TRIGGERED: Verified Truth Search...")
        evidence = []
        try:
            # 1. Primary Search
            results = DDGS().text(suspicious_headline, max_results=4)
            if not results: return "No independent verification found."
            
            # 2. Source Analysis
            # STRICT AUTHENTICITY CHECK: Only Renowned Global Outlets
            trusted_domains = [
                'reuters.com', 'bloomberg.com', 'cnbc.com', 'wsj.com', 'ft.com', 
                'mining.com', 'kitco.com', # Industry Gold Standards
                'apnews.com', 'afp.com', 'bbc.com', 'bbc.co.uk', # Global Wires
                'nytimes.com', 'washingtonpost.com', 'economist.com', 
                'aljazeera.com', 'scmp.com', 'nikkei.com' # Global Perspectives
            ]
            verified_count = 0
            
            for r in results:
                source_conf = "UNVERIFIED"
                for d in trusted_domains:
                    if d in r['href']: 
                        source_conf = "TRUSTED_MAJOR"
                        verified_count += 1
                        break
                
                evidence.append(f"- [{source_conf}] {r['title']} ({r['body'][:100]}...)")
            
            summary = "\n".join(evidence)
            if verified_count >= 2:
                summary += "\n\n[CONCLUSION] VERIFIED BY MULTIPLE RENOWNED SOURCES."
            elif verified_count == 1:
                summary += "\n\n[CONCLUSION] PARTIALLY VERIFIED (1 Major Source)."
            else:
                summary += "\n\n[CONCLUSION] UNVERIFIED / POSSIBLE RUMOR. IGNORE."
                
            return summary
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
            f"TASK: Identify ONE headline that represents a 'MACRO SHOCK' or 'STRATEGIC SHIFT'.\n"
            f"FOCUS AREAS:\n"
            f"- GEOPOLITICS: Wars, Sanctions, Elections, Coups.\n"
            f"- TRADE: Deals, Tariffs, Embargoes, Supply Chain.\n"
            f"- INDIA POLICY (HOME): RBI Rates, Union Budget, Elections, GST, Adani/Reliance.\n"
            f"- COMMODITIES: Gold, Silver, Oil, Lithium, Rare Earths.\n"
            f"- TECH: AI Breakthroughs, Chip Bans.\n\n"
            f"STRICT AUTHENTICITY RULE:\n"
            f"Refer to Article I of the Constitution. IGNORE unverified rumors or minor blogs.\n"
            f"Only flag news from Renowned/Tier-1 sources if possible.\n\n"
            f"RULES:\n"
            f"1. If news is standard noise, output 'NONE'.\n"
            f"2. If news is SIGNIFICANT in above areas, output target.\n"
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
            
            # 3. THE FORK (Verification & Deep Research)
            verification_data = "Source: RSS Feed (Trusted)."
            deep_dive_report = ""
            
            if decision.get('needs_verification') is True:
                target = decision.get('target_headline', '')
                if len(target) > 5:
                    print(f"[ALERT] Key Intelligence identified. Verifying...") # Simplified to avoid charmap error
                    evidence = self._verify_truth(target)
                    verification_data = f"CROSS-VERIFICATION DOSSIER for '{target}':\n{evidence}"
                    
                    # TRIGGER DEEP RESEARCH (If verified and serious)
                    if "UNVERIFIED" not in evidence and DeepResearchAgent:
                         print(f"[SHERLOCK] Commissioning Deep Dive on: {target}...")
                         investigator = DeepResearchAgent()
                         deep_dive_report = investigator.investigate(target, context=evidence) 
                         verification_data += f"\n\nDEEP RESEARCH REPORT:\n{deep_dive_report}"
            
            # 4. FINAL JUDGMENT
            final_prompt = (
                f"You are the Sovereign Judge. \n"
                f"CONSTITUTION:\n{self.constitution}\n\n"
                f"HEADLINES:\n{headlines}\n\n"
                f"VERIFICATION DOSSIER:\n{verification_data}\n\n"
                f"TASK: Score Global Market Sentiment (-10 to +10) and Identify Key Trends.\n"
                f"RULES:\n"
                f"1. UNVERIFIED news = Ignore.\n"
                f"2. GEOPOLITICS (War/Peace) = High Impact (+/- 5 points).\n"
                f"3. COMMODITIES (Gold/Oil) = Strategic Impact.\n"
                f"OUTPUT JSON: {{'score': int, 'reason': 'string', 'key_trend': 'string'}}"
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
