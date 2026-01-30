from daily_bot import fetch_and_scan
import oracle_interface
from risk_manager import guard
from memory_manager import MemoryManager
from mock_broker import MockDhanClient
import config
import logging
import datetime
import time

# --- CONFIGURATION ---
TRADING_MODE = "PAPER" # Options: "PAPER", "LIVE"

# Setup Broker
if TRADING_MODE == "PAPER":
    broker = MockDhanClient()
    logging.info("SENTINEL: Initialized in PAPER TRADING Mode.")
else:
    # Future: broker = DhanHQ(...) 
    logging.warning("SENTINEL: LIVE MODE NOT IMPLEMENTED. SWITCHING TO PAPER.")
    broker = MockDhanClient()

# Logging Setup
logging.basicConfig(filename='sentinel.log', level=logging.INFO, format='%(asctime)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def run_sentinel():
    """
    Vibe Orchestration Workflow:
    1. Scout (Daily Bot): Finds Candidates (SMA + RSI matches)
    2. Oracle: Predicts Future (Random Forest Model)
    3. Guard: Validates Safety (Oracle Confidence + Risk Rules)
    4. Execution: Logs/Executes Trade
    """
    print(f"\n--- SENTINEL v2.0: VIBE ORCHESTRATION [{TRADING_MODE}] ---")
    mm = MemoryManager()
    
    # --- PHASE 1: SCOUTING ---
    try:
        scout_report = fetch_and_scan() # Returns list of candidates (dicts)
    except Exception as e:
        logging.critical(f"SCOUT FAILURE: {e}")
        return

    if not scout_report:
        logging.info("SCOUT: No candidates found. Mission End.")
        return

    print(f"\nSCOUT REPORT: {len(scout_report)} candidates ready for Oracle analysis.")

    # --- PHASE 2: ORACLE ANALYSIS ---
    for candidate in scout_report:
        symbol = candidate['symbol']
        print(f"\nProcessing {symbol}...")
        
        try:
            # The Scout passes the full DF in 'data' key for the Oracle
            # We must pass the DF to the Oracle
            if 'data' not in candidate:
                logging.error(f"DATA MISSING for {symbol}. Skipping.")
                continue
                
            prediction_prob = oracle_interface.get_oracle_prediction(candidate['data'])
            print(f"ORACLE: Prediction for {symbol}: {prediction_prob:.2f}")
            
            # --- PHASE 3: THE GUARD ---
            decision = guard.validate(prediction_prob, symbol)
            
            if decision == "GO":
                # --- PHASE 4: EXECUTION ---
                # Enrich candidate data for logging
                candidate['oracle_confidence'] = prediction_prob
                price = candidate['price']
                
                # Remove heavy DF before logging/storing logic
                del candidate['data'] 
                
                # Update Oracle Confidence in Memory for Dashboard
                mm.update_oracle_confidence(prediction_prob)
                
                # ADVISORY MODE CHECK
                if config.TRADING_MODE == "ADVISORY":
                    # Calculate Position Size
                    wallet_balance = broker.get_fund_balance()
                    current_price = candidate['price']
                    
                    qty = guard.calculate_position_size(current_price, wallet_balance)
                    stop_loss = round(current_price * 0.98, 2)
                    
                    # Smart Target (Tax-Aware)
                    target_price = guard.get_smart_target(current_price, desired_profit_percent=0.05)
                    
                    from notifications import TelegramNotifier
                    notifier = TelegramNotifier()
                    
                    logging.info(f"ADVISORY: Recommendation generated for {symbol}. Qty: {qty}. Target: {target_price}")
                    print(f"ADVISORY ALERT SENT: Buy {qty} {symbol} @ {current_price} | Tgt: {target_price}")
                    
                    notifier.send_recommendation(symbol, "BUY", qty, current_price, stop_loss, target_price)
                    continue

                # EXECUTE ORDER
                qty = 1 # Simple Logic for now
                order_response = broker.place_order(symbol, qty, "BUY", price)
                
                if order_response['status'] == 'success':
                    mm.log_trade(candidate)
                    logging.info(f"EXECUTION: {symbol} Trade Logged. Confidence: {prediction_prob:.2f}. FUNDS USED: {price}")
                else:
                    logging.error(f"EXECUTION FAILED: {order_response['message']}")
            else:
                logging.info(f"GUARD: {symbol} Denied.")
                
        except Exception as e:
            logging.error(f"ORACLE/GUARD ERROR on {symbol}: {e}")
            # Fail-safe: Continue to next candidate
            continue

    print("\n--- MISSION COMPLETE ---")

if __name__ == "__main__":
    run_sentinel()
