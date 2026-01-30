import feedparser
import os
import datetime
import re
from textblob import TextBlob
import config

# TRUER DATA SOURCES (RSS)
RSS_FEEDS = {
    "MONEYCONTROL": "https://www.moneycontrol.com/rss/latestnews.xml",
    "ECONOMICTIMES": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "CNBC": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "REUTERS_BUSINESS": "http://feeds.reuters.com/reuters/businessNews"
}

NEWS_DIR = os.path.join("training_raw", "news")
if not os.path.exists(NEWS_DIR):
    os.makedirs(NEWS_DIR)

import time

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def cleanup_old_news(retention_days=7):
    """
    Deletes news files older than retention_days.
    SMART RETENTION: Keeps "Future Intelligence" (Outlook/Target/Forecast) for 30 days.
    """
    print(f"[DEEP RESEARCH] [CLEANUP] Scanning for expired intel...")
    now = time.time()
    deleted_count = 0
    
    # Define Future Keywords (Keep these longer)
    future_keywords = ["outlook", "forecast", "upcoming", "target", "expect", "prediction", "estimate", "guidance"]
    long_retention_days = 30
    
    if not os.path.exists(NEWS_DIR): return

    for filename in os.listdir(NEWS_DIR):
        if not filename.endswith(".txt"): continue
        
        filepath = os.path.join(NEWS_DIR, filename)
        try:
            file_age_days = (now - os.path.getmtime(filepath)) / (24 * 3600)
            
            # 1. If file is fresh (< 7 days), keep it.
            if file_age_days < retention_days:
                continue
                
            # 2. If file is essentially ancient (> 30 days), generic delete.
            if file_age_days > long_retention_days:
                os.remove(filepath)
                deleted_count += 1
                continue
                
            # 3. The "Gray Zone" (7 to 30 days) - Check for Intelligence
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
                
            is_strategic = any(k in content for k in future_keywords)
            
            if is_strategic:
                # Keep it! It has future value.
                # print(f"   [KEEP] Strategic Intel ({int(file_age_days)}d): {filename[:20]}...")
                pass
            else:
                # Delete it! Just daily noise.
                os.remove(filepath)
                deleted_count += 1
                print(f"   [DELETE] Expired Noise ({int(file_age_days)}d): {filename[:30]}...")
                
        except Exception as e:
            print(f"   [ERROR] Cleanup failed for {filename}: {e}")

    if deleted_count > 0:
        print(f"[DEEP RESEARCH] [CLEANUP] Purged {deleted_count} old news files.")


def scout_news():
    # 1. Run Cleanup First
    cleanup_old_news()
    
    print(f"[DEEP RESEARCH] Scanning Global & Local News Wires...")
    
    total_articles = 0
    
    for source, url in RSS_FEEDS.items():
        print(f"   -> Tapping Wire: {source}...")
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]: # Top 5 per source
                title = entry.title
                summary = clean_html(entry.get('summary', ''))
                link = entry.link
                published = entry.get('published', str(datetime.datetime.now()))
                
                # Sentiment Analysis
                blob = TextBlob(f"{title} {summary}")
                sentiment = blob.sentiment.polarity
                sentiment_str = "NEUTRAL"
                if sentiment > 0.1: sentiment_str = "POSITIVE"
                elif sentiment < -0.1: sentiment_str = "NEGATIVE"
                
                # Filter Logic: Only interested in "Business/Market" keywords? 
                # For now, we take all "Markets" feeds as relevant.
                
                # Save as Knowledge
                # Format: NEWS_{Source}_{Date}_{TitleTrunc}.txt
                safe_title = "".join([c for c in title if c.isalnum() or c==' '])[:30].replace(" ", "_")
                filename = f"NEWS_{source}_{safe_title}.txt"
                filepath = os.path.join(NEWS_DIR, filename)
                
                # Content for LLM
                content = f"""
                SOURCE: {source}
                DATE: {published}
                SENTIMENT: {sentiment_str} (Score: {sentiment:.2f})
                
                HEADLINE: {title}
                
                SUMMARY:
                {summary}
                
                LINK: {link}
                """
                
                if not os.path.exists(filepath):
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    total_articles += 1
                    print(f"      [NEW] {sentiment_str}: {title[:40]}...")
                    
        except Exception as e:
            print(f"   [ERROR] Failed to tap {source}: {e}")
            
    print(f"\n[DEEP RESEARCH] Indexed {total_articles} new Intel Reports.")
    print("[DEEP RESEARCH] notifying Librarian...")
    
    # Auto-Index
    try:
        import librarian
        librarian.get_knowledge_base() 
    except Exception as e:
        print(f"   [LIBRARIAN ERROR] {e}")

if __name__ == "__main__":
    scout_news()
