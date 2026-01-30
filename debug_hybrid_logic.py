import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

import config # Load environment variables
from utils.key_manager import key_rotator

def test_hybrid_logic():
    print("--- 1. Testing Imports ---")
    try:
        from news_agent import NewsAgent
        import librarian
        from utils.key_manager import key_rotator
        print("[OK] Imports Successful")
    except Exception as e:
        print(f"[FAIL] Import Failed: {e}")
        return

    print("\n--- 2. Testing Key Manager ---")
    
    # DEBUG ENV VARS
    ant_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"   [DEBUG] Raw Env 'ANTHROPIC_API_KEY': '{ant_key if ant_key else 'NONE'}'")
    
    try:
        claude = key_rotator.get_anthropic()
        if claude:
            print("[OK] Claude Client Found")
        else:
            print("[FAIL] Claude Client Missing (Key check failed?)")
            # We proceed to see if NewsAgent fails
    except Exception as e:
        print(f"[FAIL] Key Manager Error: {e}")

    print("\n--- 3. Testing News Agent ---")
    try:
        agent = NewsAgent()
        print("   NewsAgent Initialized.")
        print("   Fetching Market Vibe (This implies network calls)...")
        vibe = agent.get_market_vibe()
        print(f"[OK] Market Vibe: {vibe}")
    except Exception as e:
        print(f"[FAIL] News Agent Failed: {e}")
        
    print("\n--- 4. Testing Claude Forecast Judge ---")
    if claude:
        try:
             # Simulation Data
            stdev = 0.015
            drift = 0.002
            change_pct = 4.5
            news_vibe = {'score': -5, 'reason': 'War rumors'}
            
            prompt = (
                f"Analyze this Market Forecast.\n"
                f"MATH DATA: Volatility={round(stdev*100,2)}%, Drift={round(drift*100,4)}, Expected Move={round(change_pct,2)}%.\n"
                f"NEWS SENTIMENT: Score={news_vibe.get('score')} ({news_vibe.get('reason')}).\n"
                f"TASK: Verify the Math against the News. If News is extreme (Crash/War), override the Math. Otherwise, support it.\n"
                f"OUTPUT JSON: {{'insight': 'Short Label', 'reasoning': '1-sentence explanation', 'confidence': 0-100}}"
            )
            
            print("   Sending User Message to Claude...")
            msg = claude.messages.create(
                model="claude-3-5-sonnet-20240620", max_tokens=200, system="You are the Oracle Judge. Output JSON only.",
                messages=[{"role": "user", "content": prompt}]
            )
            print(f"[OK] Claude Response: {msg.content[0].text}")
        except Exception as e:
            print(f"[FAIL] Claude API Failed: {e}")

if __name__ == "__main__":
    test_hybrid_logic()
