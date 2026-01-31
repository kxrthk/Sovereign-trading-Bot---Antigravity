import requests
import json
import time
from textblob import TextBlob

class SocialScout:
    """
    The Crowd. Monitors Reddit for Retail Sentiment.
    """
    def __init__(self):
        self.subreddits = [
            "IndiaInvestments", 
            "IndianStreetBets", 
            "StockMarketIndia",
            "Economics" # Global Context
        ]
        self.headers = {'User-Agent': 'SovereignBot/1.0'}
        
    def scan_social_sentiment(self):
        print("\n[SOCIAL SCOUT] 📢 Listening to the Crowd...")
        
        intel = []
        
        for sub in self.subreddits:
            print(f"   [SCAN] r/{sub}...", end=" ")
            try:
                # Use standard JSON endpoint (Rate limits apply, but sufficient for low freq)
                url = f"https://www.reddit.com/r/{sub}/hot.json?limit=5"
                resp = requests.get(url, headers=self.headers, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json()
                    posts = data['data']['children']
                    
                    for p in posts:
                        title = p['data']['title']
                        score = p['data']['score']
                        url = p['data']['url']
                        
                        # Sentiment Check
                        blob = TextBlob(title)
                        sentiment = blob.sentiment.polarity
                        
                        # Filter: Only High Engagement or Strong Sentiment
                        if score > 50 and abs(sentiment) > 0.2:
                            sentiment_str = "BULLISH" if sentiment > 0 else "BEARISH"
                            intel.append(f"[r/{sub}] {sentiment_str}: {title} (Score: {score})")
                            
                    print("✅")
                else:
                    print(f"❌ (Status: {resp.status_code})")
                    
            except Exception as e:
                print(f"[ERR] {e}")
                
        return intel

if __name__ == "__main__":
    scout = SocialScout()
    trends = scout.scan_social_sentiment()
    for t in trends:
        print(t)
