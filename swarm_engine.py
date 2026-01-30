import asyncio
import random
import os
import sys
import json
import time
from datetime import datetime
import config
from oracle import Oracle
from risk_manager import RiskManager
from dhan_broker import DhanBroker
from mock_broker import MockDhanClient

# --- CONFIGURATION ---
SCAN_INTERVAL_OPEN = (15, 30)   # Seconds (09:15 - 10:15)
SCAN_INTERVAL_MID  = (60, 120)  # Seconds (10:15 - 14:30)
SCAN_INTERVAL_CLOSE = (15, 30)  # Seconds (14:30 - 15:30)
MARKET_OPEN_TIME = "09:15"
MARKET_CLOSE_TIME = "15:30"

class AsyncWorker:
    """
    The Drone. Monitors ONE asset permanently.
    Non-blocking, low-latency, resilient.
    """
    def __init__(self, symbol, hive_mind, oracle):
        self.symbol = symbol
        self.hive_mind = hive_mind
        self.oracle = oracle
        self.is_active = True
        
    async def patrol(self):
        print(f"[WORKER] {self.symbol} Drone Launched via Asyncio.")
        
        while self.is_active:
            try:
                # 1. Check if we should be sleeping (Market Hours)
                if not self.hive_mind.is_market_open():
                    # Sleep for 15 mins then check again
                    await asyncio.sleep(900)
                    continue

                # 2. Consult Oracle (Async Wrapper)
                # Since Oracle uses blocking YFinance, we wrap it in to_thread
                analysis = await asyncio.to_thread(self.oracle.analyze, self.symbol)
                
                signal = analysis.get('signal', 'HOLD')
                confidence = analysis.get('confidence', 0.0)
                price = analysis.get('price', 0.0)
                
                # 3. Report to Hive Mind if interesting
                if signal != "HOLD":
                    await self.hive_mind.request_action(self.symbol, signal, confidence, price, analysis)
                
                # 4. Smart Sleep (Jittered)
                delay = self.hive_mind.get_dynamic_sleep_time()
                await asyncio.sleep(delay)
                
            except asyncio.CancelledError:
                print(f"[WORKER] {self.symbol} Drone Decommissioned.")
                break
            except Exception as e:
                print(f"[ERR] {self.symbol} Worker Crashed: {e}. Rebooting in 10s...")
                await asyncio.sleep(10)

class HiveMind:
    """
    Agent A. The Central Brain.
    Manages Risk, Regime, and permissions for all Drones.
    """
    def __init__(self):
        self.risk_manager = RiskManager()
        self.lock = asyncio.Lock() # Prevent race conditions on Wallet/Journal
        
        # Select Broker
        if getattr(config, 'DATA_SOURCE', 'YFINANCE') == 'DHAN':
            print("[HIVE] Config: REAL MONEY (Dhan API)")
            self.broker = DhanBroker()
        else:
            print("[HIVE] Config: SIMULATION (Mock Broker)")
            self.broker = MockDhanClient()
            
    def is_market_open(self):
        """Strict Market Hours Enforcement"""
        now = datetime.now().time()
        start = datetime.strptime(MARKET_OPEN_TIME, "%H:%M").time()
        end = datetime.strptime(MARKET_CLOSE_TIME, "%H:%M").time()
        return start <= now <= end

    def get_dynamic_sleep_time(self):
        """Returns scan interval based on time of day + Jitter"""
        now = datetime.now().time()
        open_end = datetime.strptime("10:15", "%H:%M").time()
        mid_end = datetime.strptime("14:30", "%H:%M").time()
        
        jitter = random.uniform(-2, 2) # Human-like randomness
        
        if now < open_end:
            base = random.randint(*SCAN_INTERVAL_OPEN)
        elif now < mid_end:
            base = random.randint(*SCAN_INTERVAL_MID)
        else:
            base = random.randint(*SCAN_INTERVAL_CLOSE)
            
        return max(5, base + jitter)

    async def request_action(self, symbol, signal, confidence, price, analysis):
        """
        Called by Workers when they find an opportunity.
        Processing involves: Risk Check, Portfolio Check, Execution.
        """
        async with self.lock: # Critical Section
            print(f"   >>> [HIVE] Received Request: {signal} {symbol} ({confidence*100:.1f}%)")
            
            # 1. State Check (Kill Switch)
            if os.path.exists("STOP.flag"):
                print("[HIVE] Kill Switch Detected. Request Denied.")
                return

            # 2. Risk Gate
            required_conf = self.risk_manager.get_required_confidence()
            if confidence < required_conf:
                print(f"      [DENY] Confidence {confidence:.2f} < Required {required_conf:.2f}")
                return
            
            if not self.risk_manager.can_trade():
                print(f"      [DENY] Risk Manager blocking trades (Daily Limit/Target hit).")
                return

            # 3. Execution Logic
            quantity = self.risk_manager.get_position_size(price)
            
            # --- PORTFOLIO CHECK (Async) ---
            # We wrap blocking broker calls
            if signal == "SELL":
                # Only sell if we have it
                # For MVP, assume we check RiskManager or Broker. 
                # (Real implementation needs Portfolio Cache in HiveMind to avoid API spam)
                pass # TODO: Implement Portfolio Check
                
            elif signal == "BUY":
                if quantity > 0:
                    print(f"   [EXEC] OPENING POSITION: Buying {quantity} {symbol} @ {price}...")
                    result = await asyncio.to_thread(
                        self.broker.place_order, symbol, quantity, signal, price
                    )
                    
                    if result['status'] == 'success':
                        print(f"      [OK] Order Filled: {result.get('order_id')}")
                        # Update Daily Stats (P&L tracking happens on Sell, but we verify here)
                    else:
                        print(f"      [ERR] Execution Failed: {result['message']}")
                else:
                    print(f"      [SKIP] Position size 0 (Too expensive or Risk limit).")

async def main():
    print(f"\n[{datetime.now()}] [HIVE] SYSTEM INITIALIZING: SWARM PROTOCOL v1.0")
    print("----------------------------------------------------------------")
    
    # 1. Initialize Components
    hive = HiveMind()
    oracle = Oracle() # Shared Oracle (Stateless analysis)
    
    # 2. Create Workers (Drones)
    watchlist = getattr(config, 'WATCHLIST', ['RELIANCE.NS'])
    drones = [AsyncWorker(sym, hive, oracle) for sym in watchlist]
    
    print(f"[HIVE] Deployed {len(drones)} Drones to the Swarm.")
    
    # 3. Launch the Swarm
    # gather() runs them all concurrently
    await asyncio.gather(*(d.patrol() for d in drones))

if __name__ == "__main__":
    try:
        # Windows Asyncio Policy Fix (if needed)
        # if sys.platform == 'win32':
        #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[HIVE] SHUTDOWN SIGNAL RECEIVED. DRONES RETURNING TO BASE.")
