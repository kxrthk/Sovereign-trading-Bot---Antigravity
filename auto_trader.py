import time
import requests
import sys
import random

def safety_shield_check():
    """
    The Gatekeeper: Ensures we have a stable internet connection 
    BEFORE allowing the bot to spam the server.
    """
    print("[SAFETY SHIELD] System warming up...")
    print("[CHECKING] Waiting for stable internet connection...")

    while True:
        try:
            # We try to ping Google's reliable public DNS or Home Page
            # We set a strict timeout of 5 seconds so we don't hang forever
            response = requests.get("https://www.google.com", timeout=5)
            
            # If we get a 200 OK, the internet is alive.
            if response.status_code == 200:
                print("[OK] CONNECTION CONFIRMED. Disengaging Safety Shield.")
                print("[LAUNCH] LAUNCHING SOVEREIGN BOT...")
                break # Break the loop and let the code continue
                
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.SSLError):
            # If the internet is down, we catch the error silently.
            # INSTEAD of crashing, we wait patiently.
            wait_time = random.randint(7, 13)
            print(f"⏳ NETWORK DOWN: Sleeping for {wait_time} seconds... (No Requests Sent)")
            time.sleep(wait_time) # Random delay to avoid patterns
            
        except Exception as e:
            # Catch any other weird errors to keep the bot alive
            wait_time = random.randint(7, 13)
            print(f"⚠️ UNEXPECTED ERROR: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

# --- EXECUTE SHIELD BEFORE ANYTHING ELSE ---
if __name__ == "__main__":
    safety_shield_check()
    
    # [YOUR EXISTING BOT CODE STARTS HERE]
    # import oracle
    # import auto_trader
    # auto_trader.run()

from oracle import Oracle
from mock_broker import MockDhanClient
from dhan_broker import DhanBroker
from risk_manager import RiskManager
import config
import time
import datetime
import random
import os
import sys

def run_auto_pilot():
    print("\n[AUTO-PILOT] Engaging Autonomous Trading Systems...")
    print("--------------------------------------------------")
    
    oracle = Oracle()
    
    # Select Broker based on Config
    if getattr(config, 'DATA_SOURCE', 'YFINANCE') == 'DHAN':
        print("[CONFIG] Mode: REAL MONEY (Dhan API)")
        broker = DhanBroker()
    else:
        print("[CONFIG] Mode: SIMULATION (Mock Broker)")
        broker = MockDhanClient()

    risk_manager = RiskManager()
    
    # Watchlist
    watchlist = getattr(config, 'WATCHLIST', ['RELIANCE.NS']) # Fallback
    from market_regime import get_market_regime
    
    print(f"[AUTO-PILOT] Patrol Mode: Monitoring {len(watchlist)} assets: {watchlist}")
    
    try:
        while True:
            # SAFETY CHECK: Master Switch (Pause Logic)
            if os.path.exists("STOP.flag"):
                 print(f"[PAUSED] Master Switch is OFF. Standing by... {datetime.datetime.now().strftime('%H:%M:%S')}", end='\r')
                 time.sleep(5)
                 continue

            # RISK CHECK (Stateful)
            if not risk_manager.can_trade():
                print("[WAIT] Risk Manager Halted Trading.")
                time.sleep(60)
                continue

            # REGIME CHECK (The Weather)
            regime = get_market_regime()
            if regime == "CRASH":
                print("🔴 REGIME ALERT: HIGH VOLATILITY (CRASH MODE). HALTING TRADING.")
                time.sleep(300) # Wait 5 mins
                continue
            
            print(f"\n[SCAN] {datetime.datetime.now().strftime('%H:%M:%S')} - Patrol Started (Regime: {regime})...")
            
            # Smart Recovery: Get Dynamic Confidence
            min_conf = risk_manager.get_required_confidence()
            
            for symbol in watchlist:
                # Double Safety Check inside loop
                if os.path.exists("STOP.flag"): break

                # Dynamic Settings Reload (Fix for "Irregular Functionality")
                try:
                    with open("memories/settings.json", "r") as f:
                        live_settings = json.load(f)
                except: pass

                # 1. Consult the Oracle
                try:
                    analysis = oracle.analyze(symbol)
                    
                    signal = analysis.get('signal', 'HOLD')
                    confidence = analysis.get('confidence', 0.0)
                    price = analysis.get('price', 0.0)
                    reason = analysis.get('reason', 'Analysis Complete')
                    
                    # 2. Decision Gate (Adaptive)
                    if signal != "HOLD" and confidence >= min_conf:
                        print(f"   >>> SIGNAL DETECTED: {signal} {symbol} ({reason})")
                        
                        # Filter: Chop Mode (Low Volatility) -> Only take very high confidence or Skip?
                        # For now, we trust the Oracle, but maybe increase min_conf?
                        if regime == "CHOP" and confidence < 0.85:
                            print(f"      [SKIP] Regime is CHOP. Ignoring weak signal ({confidence}).")
                            continue

                        # 3. Position Sizing (The Risk Check)
                        quantity = risk_manager.get_position_size(price)

                        # --- PERSISTENCE: CHECK PORTFOLIO ---
                        if getattr(config, 'DATA_SOURCE', 'YFINANCE') != 'DHAN':
                            portfolio = broker.get_portfolio(origin="BOT") # ISOLATION: Bot only sees Bot trades
                        else:
                            portfolio = {} # Todo: Real Dhan Portfolio Fetch

                        if signal == "SELL":
                            held_qty = portfolio.get(symbol, 0)
                            if held_qty > 0:
                                print(f"   [EXEC] CLOSING POSITION: Selling {held_qty} {symbol} @ {price:.2f}...")
                                result = broker.place_order(symbol, held_qty, signal, price) # Sell All
                            else:
                                print(f"      [SKIP] SELL Signal ignored. No holdings in {symbol}.")
                                continue # Skip the trade

                        # BUY LOGIC
                        elif signal == "BUY":
                            if quantity > 0:
                                print(f"   [EXEC] OPENING POSITION: Buying {quantity} {symbol} @ {price:.2f}...")
                                result = broker.place_order(symbol, quantity, signal, price)
                            else:
                                print(f"      [SKIP] {symbol} too expensive/risky.")
                                continue

                        # Handle Result
                        if 'result' in locals() and result['status'] == 'success':
                             print(f"      [OK] ORDER FILLED. ID: {result.get('order_id', 'N/A')}")
                             risk_manager.update_pnl(0) 
                        elif 'result' in locals():
                             print(f"      [ERR] ORDER FAILED: {result['message']}")
                            
                    else:
                        pass
                        # Verbose reduction: Don't print every HOLD for 6 stocks
                        # print(f"   [WAIT] {symbol}: {signal} ({confidence:.2f})")
                
                except Exception as e:
                    print(f"   [ERR] Failed to analyze {symbol}: {e}")

                # Tiny pause to be polite to the API (Round Robin Breath)
                time.sleep(1)
            
            # Wait for next Tick
            delay = random.randint(30, 60)
            print(f"[WAIT] Patrol Complete. Cooling down for {delay} seconds...")
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n[AUTO-PILOT] Disengaging systems. Landing safely.")

if __name__ == "__main__":
    run_auto_pilot()
