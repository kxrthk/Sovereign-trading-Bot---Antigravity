import json
import os
import datetime
import tax_engine
import uuid
import csv

MEMORY_PATH = "memories/bot_brain.json"
PAPER_TRADES_PATH = "memories/paper_trades.json"
JOURNAL_PATH = "trading_journal.csv"
HISTORY_PATH = "memories/account_history.csv"

class MockDhanClient:
    """
    Simulates the DhanHQ API for Paper Trading.
    Manages a virtual wallet and records fake trades.
    """
    def __init__(self):
        self._ensure_memory()
        
    def _ensure_memory(self):
        # 1. Ensure Paper Trades File
        if not os.path.exists(PAPER_TRADES_PATH):
            os.makedirs("memories", exist_ok=True)
            with open(PAPER_TRADES_PATH, 'w') as f:
                json.dump([], f)
                
        # 2. Ensure Bot Brain (Wallet)
        if not os.path.exists(MEMORY_PATH):
            os.makedirs("memories", exist_ok=True)
            with open(MEMORY_PATH, 'w') as f:
                json.dump({"wallet_balance": 100000.0}, f) # Start with 1L
        else:
            # Check if wallet exists, if not init
            with open(MEMORY_PATH, 'r+') as f:
                try:
                    data = json.load(f)
                except:
                    data = {}
                
                if "wallet_balance" not in data:
                    data["wallet_balance"] = 100000.0
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

    def get_fund_balance(self):
        """Returns virtual wallet balance."""
        with open(MEMORY_PATH, 'r') as f:
            data = json.load(f)
        return data.get("wallet_balance", 0.0)

    def get_positions(self):
        """Returns list of open paper trades."""
        with open(PAPER_TRADES_PATH, 'r') as f:
            return json.load(f)

    def get_portfolio(self, origin=None):
        """
        Calculates Net Holdings from Trade History.
        Returns: { 'SYMBOL': quantity, ... }
        """
        portfolio = {}
        if not os.path.exists(PAPER_TRADES_PATH):
            return portfolio
            
        with open(PAPER_TRADES_PATH, 'r') as f:
            trades = json.load(f)
            
        for t in trades:
            # Filter by Origin if specified
            if origin and t.get('origin', 'BOT') != origin:
                continue

            sym = t['symbol']
            qty = t['quantity']
            action = t['action']
            
            if sym not in portfolio: portfolio[sym] = 0
            
            if action == 'BUY':
                portfolio[sym] += qty
            elif action == 'SELL':
                portfolio[sym] -= qty
                
        # Clean up zero positions (Allow negative for Shorts)
        return {k: v for k, v in portfolio.items() if v != 0}

    def place_order(self, symbol, quantity, action, price, origin="BOT", stop_loss=None, target=None):
        """
        Simulates placing an order.
        Updates wallet balance and records trade.
        DEDUCTS TAXES (Realism Mode).
        """
        # Calculate Taxes
        # --- BANKRUPTCY CHECK ---
        current_balance = self.get_fund_balance()
        
        # Load Brain for Scoring
        with open(MEMORY_PATH, 'r+') as f:
            brain = json.load(f)
            # Initialize Score if missing
            if "score" not in brain: brain["score"] = 0
            
            # 1. Punishment (Bankruptcy)
            if current_balance <= 50.0:
                print("[FATAL] WALLET EMPTY (Simulated Bankruptcy). Trading Rejected.")
                brain["score"] -= 1000
                f.seek(0)
                json.dump(brain, f, indent=4)
                f.truncate()
                return {"status": "failure", "message": "BANKRUPT"}

            # 2. Reward (Doubling Capital) - Reward only once per milestone? 
            # For simplicity, we check if we crossed a high water mark, but let's keep it simple.
            starting_cap = 2000.0
            if current_balance >= (starting_cap * 2):
                 # Exponential Reward
                 brain["score"] = max(brain["score"], 10) * 2 # Safety floor 10
                 print(f"[RL REWARD] Capital Doubled! Score Multiplied to {brain['score']}")
                 # Reset threshold? No, let's just multiply.
                 
            f.seek(0)
            json.dump(brain, f, indent=4)
            f.truncate()


        if action == "BUY":
            # Buy Side Taxes (Sell Price=0)
            charges_breakdown = tax_engine.calculate_taxes(price, 0, quantity)
            total_charges = charges_breakdown['total_charges']
            
            stock_cost = quantity * price
            total_cost = stock_cost + total_charges
            
            # Load Memory
            with open(MEMORY_PATH, 'r') as f:
                brain = json.load(f)
            
            balance = brain.get("wallet_balance", 0.0)
            
            if balance >= total_cost:
                balance -= total_cost
                brain["wallet_balance"] = balance
                
                # Generate Digital Receipt (The Proof)
                order_id = f"ORD-{uuid.uuid4().hex[:4].upper()}-{symbol}"
                
                # Record Trade
                trade = {
                    "order_id": order_id,
                    "symbol": symbol,
                    "quantity": quantity,
                    "avg_price": price,
                    "action": "BUY",
                    "timestamp": str(datetime.datetime.now()),
                    "status": "OPEN",
                    "taxes_paid": total_charges,
                    "origin": origin,
                    "stop_loss": stop_loss,
                    "target": target
                }
                
                with open(PAPER_TRADES_PATH, 'r+') as tf:
                    trades = json.load(tf)
                    trades.append(trade)
                    tf.seek(0)
                    json.dump(trades, tf, indent=4)
                
                # Update Wallet
                with open(MEMORY_PATH, 'w') as bf:
                    json.dump(brain, bf, indent=4)

                # Log to Account History (Real-time Equity Curve)
                today_str = datetime.datetime.now().strftime("%b %d")
                hist_exists = os.path.isfile(HISTORY_PATH)
                with open(HISTORY_PATH, 'a', newline='') as hf:
                    writer = csv.writer(hf)
                    if not hist_exists:
                        writer.writerow(['date', 'equity'])
                    writer.writerow([today_str, balance])

                # Log to CSV (Permanent Record)
                file_exists = os.path.isfile(JOURNAL_PATH)
                with open(JOURNAL_PATH, 'a', newline='') as csvfile:
                    fieldnames = ['timestamp', 'order_id', 'symbol', 'action', 'price', 'quantity', 'taxes', 'total_cost', 'origin']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow({
                        'timestamp': trade['timestamp'],
                        'order_id': order_id,
                        'symbol': symbol,
                        'action': 'BUY',
                        'price': price,
                        'quantity': quantity,
                        'taxes': total_charges,
                        'total_cost': total_cost,
                        'origin': origin
                    })
                    
                print(f"MOCK BROKER: Bought {quantity} {symbol} @ {price}. Receipt: {order_id} [{origin}]")
                return {"status": "success", "message": "Paper Order Placed", "order_id": order_id}
            else:
                 print(f"MOCK BROKER: Insufficient Funds ({balance} < {total_cost})")
                 return {"status": "failure", "message": f"Insufficient Funds: Need {total_cost:.2f}, Have {balance:.2f}"}
        elif action == "SELL":
            # --- PORTFOLIO CHECK (The Persistence Fix) ---
            portfolio = self.get_portfolio()
            current_holding = portfolio.get(symbol, 0)
            
            # STRICT RESTRICTION FOR BOT (Long Only for safety)
            # USER IS ALLOWED TO SHORT SELL
            if origin == "BOT":
                if current_holding <= 0:
                     print(f"MOCK BROKER: Rejected SELL of {symbol}. No holdings found.")
                     return {"status": "failure", "message": "NO_HOLDINGS"}
                     
                # Cap quantity to what we own (No Short Selling in Spot for Bot)
                if quantity > current_holding:
                    print(f"MOCK BROKER: Adjusted Sell Quantity from {quantity} to {current_holding} (Max Held)")
                    quantity = current_holding

             # Sell Side Taxes
            charges_breakdown = tax_engine.calculate_taxes(price, price, quantity) # Simplified
            total_charges = charges_breakdown['total_charges']
            
            stock_value = quantity * price
            net_credit = stock_value - total_charges
            
            # Load Memory
            with open(MEMORY_PATH, 'r') as f:
                brain = json.load(f)
            
            balance = brain.get("wallet_balance", 0.0)
            balance += net_credit # Add to wallet
            brain["wallet_balance"] = balance
            
            # Digital Receipt
            order_id = f"ORD-{uuid.uuid4().hex[:4].upper()}-{symbol}"
            
            # Record Trade
            trade = {
                "order_id": order_id,
                "symbol": symbol,
                "quantity": quantity,
                "avg_price": price,
                "action": "SELL",
                "timestamp": str(datetime.datetime.now()),
                "status": "OPEN",
                "taxes_paid": total_charges,
                "origin": origin,
                "stop_loss": stop_loss,
                "target": target
            }
            
            with open(PAPER_TRADES_PATH, 'r+') as tf:
                trades = json.load(tf)
                trades.append(trade)
                tf.seek(0)
                json.dump(trades, tf, indent=4)
            
            # Update Wallet
            with open(MEMORY_PATH, 'w') as bf:
                json.dump(brain, bf, indent=4)

            # Log to Account History
            today_str = datetime.datetime.now().strftime("%b %d")
            hist_exists = os.path.isfile(HISTORY_PATH)
            with open(HISTORY_PATH, 'a', newline='') as hf:
                writer = csv.writer(hf)
                if not hist_exists:
                    writer.writerow(['date', 'equity'])
                writer.writerow([today_str, balance])
                
            # Log to CSV
            file_exists = os.path.isfile(JOURNAL_PATH)
            with open(JOURNAL_PATH, 'a', newline='') as csvfile:
                fieldnames = ['timestamp', 'order_id', 'symbol', 'action', 'price', 'quantity', 'taxes', 'total_cost', 'origin']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if not file_exists:
                     writer.writeheader()
                writer.writerow({
                    'timestamp': trade['timestamp'],
                    'order_id': order_id,
                    'symbol': symbol,
                    'action': 'SELL',
                    'price': price,
                    'quantity': quantity,
                    'taxes': total_charges,
                    'total_cost': -net_credit, # Negative cost = credit
                    'origin': origin
                })
                
            print(f"MOCK BROKER: Sold {quantity} {symbol} @ {price}. Receipt: {order_id} [{origin}]")
            return {"status": "success", "message": "Paper Order Placed", "order_id": order_id}

        return {"status": "failure", "message": "Not Implemented"}
