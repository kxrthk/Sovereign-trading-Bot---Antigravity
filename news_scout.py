import feedparser
import os
import datetime
import re
from textblob import TextBlob
import config

# TRUER DATA SOURCES (RSS)
try:
    from bank_watcher import BankWatcher
    from social_scout import SocialScout
    SUPER_INTEL_ACTIVE = True
except ImportError:
    SUPER_INTEL_ACTIVE = False

# TRUER DATA SOURCES (RSS)
RSS_FEEDS = {
    # --- GENERAL MARKET NEWS ---
    "MONEYCONTROL": "https://www.moneycontrol.com/rss/latestnews.xml",
    "ECONOMICTIMES": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "CNBC_GLOBAL": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "REUTERS_BIZ": "http://feeds.reuters.com/reuters/businessNews",
    
    # --- INDIAN POLITY & ECONOMY (HOME BASE) ---
    "TOI_INDIA": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "ET_ECONOMY": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
    "THE_HINDU_NAT": "https://www.thehindu.com/news/national/feeder/default.rss",
    "NDTV_TOP": "https://feeds.feedburner.com/ndtvnews-top-stories",
    
    # --- SUPER-INTELLIGENCE MODULES ---
    # --- GEOPOLITICS & GLOBAL MACRO ---
    "ALJAZEERA_BIZ": "https://www.aljazeera.com/xml/rss/all.xml", # Broad global coverage often catching what western media misses
    "BBC_WORLD": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "BBC_BIZ": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "UN_NEWS": "https://news.un.org/feed/subscribe/en/news/all/rss.xml", # Primary source for sanctions/UN resolutions
    
    # --- INVESTOR INTELLIGENCE ---
    "INVESTING_COM": "https://www.investing.com/rss/news.rss",
    "MARKETWATCH": "http://feeds.marketwatch.com/marketwatch/topstories/",
    "YAHOO_FINANCE": "https://finance.yahoo.com/news/rssindex",
    
    # --- TECH & FUTURE ---
    "TECHCRUNCH": "https://techcrunch.com/feed/",
    "WIRED_BIZ": "https://www.wired.com/feed/category/business/latest/rss",
    
    # --- COMMODITIES & RESOURCES ---
    "KITCO_GOLD": "https://www.kitco.com/rss/category/commodities/gold",
    "KITCO_SILVER": "https://www.kitco.com/rss/category/commodities/silver",
    "OILPRICE": "https://oilprice.com/rss/main",
    "MINING_COM": "https://www.mining.com/feed/" # Critical for Lithium/Copper/Rare Earths
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
                
                # Tagging Logic
                tags = []
                title_upper = title.upper()
                summary_upper = summary.upper()
                combined_text = title_upper + " " + summary_upper
                
                if "GOLD" in combined_text or "XAU" in combined_text: tags.append("[GOLD]")
                if "SILVER" in combined_text or "XAG" in combined_text: tags.append("[SILVER]")
                if "COPPER" in combined_text: tags.append("[COPPER]")
                if "LITHIUM" in combined_text or "RARE EARTH" in combined_text: tags.append("[RARE_EARTH]")
                if "ETF" in combined_text: tags.append("[ETF]")
                if "OIL" in combined_text or "CRUDE" in combined_text or "OPEC" in combined_text: tags.append("[OIL]")
                
                # Global Macro Tags
                if "WAR" in combined_text or "CONFLICT" in combined_text or "MILITARY" in combined_text: tags.append("[WAR]")
                if "SANCTION" in combined_text or "EMBARGO" in combined_text: tags.append("[SANCTIONS]")
                if "TRADE DEAL" in combined_text or "TARIFF" in combined_text or "AGREEMENT" in combined_text: tags.append("[TRADE]")
                if "ELECTION" in combined_text or "VOTE" in combined_text: tags.append("[POLITICS]")
                if "AI " in combined_text or "ARTIFICIAL INTELLIGENCE" in combined_text or "CHIP" in combined_text: tags.append("[TECH]")

                # Indian Context Tags (Home Base)
                if "INDIA" in combined_text or "BHARAT" in combined_text or "DELHI" in combined_text: tags.append("[INDIA]")
                if "RBI" in combined_text or "RESERVE BANK" in combined_text or "REPO RATE" in combined_text: tags.append("[RBI]")
                if "NIFTY" in combined_text or "SENSEX" in combined_text or "ADANI" in combined_text or "RELIANCE" in combined_text: tags.append("[MARKET_IN]")
                if "BUDGET" in combined_text or "GST" in combined_text or "FINANCE MINISTER" in combined_text or "SITHARAMAN" in combined_text: tags.append("[POLICY]")

                tag_str = "".join(tags)

                # Save as Knowledge
                # Format: NEWS_{Source}_{Date}_{TitleTrunc}.txt
                safe_title = "".join([c for c in title if c.isalnum() or c==' '])[:30].replace(" ", "_")
                filename = f"NEWS_{source}_{tag_str}_{safe_title}.txt"
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
    # Auto-Index & Compile RAG
    # Auto-Index & Compile RAG
    try:
        import librarian
        
        # SUPER-INTELLIGENCE SCANS (Phase 1 Trigger)
        if SUPER_INTEL_ACTIVE:
            print("\n[SUPER-INTEL] Engaging Specialized Agents...")
            try:
                # 1. Bank Watcher
                hawk = BankWatcher()
                alerts = hawk.scan_central_banks()
                if alerts:
                    # Save Alerts as Urgent News
                    with open(os.path.join(NEWS_DIR, f"BANK_ALERT_{int(time.time())}.txt"), "w") as f:
                        f.write("\n".join(alerts))
                        
                # 2. Social Scout
                scout = SocialScout()
                trends = scout.scan_social_sentiment()
                if trends:
                    # Save Trends
                    with open(os.path.join(NEWS_DIR, f"SOCIAL_SENTIMENT_{int(time.time())}.txt"), "w") as f:
                        f.write("\n".join(trends))
                        
            except Exception as e:
                print(f"   [INTEL ERR] {e}")

        librarian.ingest_daily_briefing()
    except Exception as e:
        print(f"   [LIBRARIAN ERROR] {e}")

if __name__ == "__main__":
    scout_news()
