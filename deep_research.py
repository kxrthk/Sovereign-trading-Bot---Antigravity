import json
import time
import feedparser
from duckduckgo_search import DDGS
from google import genai
from dotenv import load_dotenv
import config

from utils.key_manager import key_rotator

class DeepResearchAgent:
    def __init__(self):
        self.model_id = "gemini-2.0-flash" # Updated Model
        self.client = key_rotator.get_client()
        
    def investigate(self, headline, context=""):
        """
        The Core Loop: Headline -> 3 Questions -> Search -> Synthesis
        """
        print(f"\n[DEEP RESEARCH] Investigating: '{headline}'...")
        
        if not self.client:
             # Try refreshing
             self.client = key_rotator.get_client()
        
        if not self.client:
            return "Error: AI Client not initialized."

        # Step 1: Generate Investigative Questions
        planning_prompt = f"""
        You are a Senior Intelligence Analyst.
        HEADLINE: "{headline}"
        CONTEXT: "{context}"
        
        TASK: Generate 3 specific, search-friendly questions to uncover the "ROOT CAUSE" and "IMPACT".
        Do not ask generic questions. Ask "Why", "Who", and "What next".
        
        OUTPUT JSON: ["Question 1", "Question 2", "Question 3"]
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id, 
                contents=planning_prompt,
                config={'response_mime_type': 'application/json'}
            )
            questions = json.loads(response.text)
            print(f"   [PLAN] Strategy: {questions}")
        except Exception as e:
            print(f"   [ERR] Strategizing failed: {e}")
            if "429" in str(e):
                 key_rotator.rotate_key()
                 self.client = key_rotator.get_client()
            return "Analysis Failed."

        # Step 2: The Hunt (Hybrid Search: DuckDuckGo + Google News)
        findings = []
        ddgs = DDGS()
        
        for q in questions:
            print(f"   [HUNT] Searching: {q}...")
            
            # Source A: DuckDuckGo (Web)
            try:
                results = ddgs.text(q, max_results=2)
                if results:
                    summary = results[0]['body']
                    findings.append(f"[Source: DuckDuckGo] Q: {q}\nA: {summary}")
                    print("      -> [DDG] Found Web Intel.")
            except Exception as e:
                print(f"      -> [DDG] Failed: {e}")

            # Source B: Google News (Realtime RSS Search)
            try:
                # Encoded query for URL
                encoded_q = q.replace(" ", "%20")
                g_url = f"https://news.google.com/rss/search?q={encoded_q}&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(g_url)
                if feed.entries:
                    # Get top entry
                    top_story = feed.entries[0]
                    findings.append(f"[Source: Google News] Q: {q}\nA: {top_story.title} - {top_story.link}")
                    print("      -> [Google] Found Fresh News.")
            except Exception as e:
                print(f"      -> [Google] Failed: {e}")

            if not findings:
                 print("      -> [X] Dead End on both engines.")
                
        full_intel = "\n\n".join(findings)
        
        # Step 3: Synthesis (The Report)
        report_prompt = f"""
        You are the Sovereign Intelligence Chief.
        HEADLINE: "{headline}"
        
        FIELD INTEL:
        {full_intel}
        
        TASK: Write a BRIEF Strategic Warning (Max 100 words).
        1. Explain the ROOT CAUSE (Why did this happen?)
        2. Predict the IMMEDIATE IMPACT on India/Global Markets.
        
        FORMAT:
        **ROOT CAUSE**: ...
        **IMPACT**: ...
        """
        
        try:
            final_report = self.client.models.generate_content(
                model=self.model_id,
                contents=report_prompt
            )
            report_text = final_report.text
            print(f"\n[DEEP RESEARCH] 📝 REPORT FILED:\n{report_text}\n")
            return report_text
            
        except Exception as e:
            return f"Synthesis Failed: {e}"

if __name__ == "__main__":
    agent = DeepResearchAgent()
    # Test Run
    agent.investigate("Oil prices spike 5% amid Middle East tensions")
