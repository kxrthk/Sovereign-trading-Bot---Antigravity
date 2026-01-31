from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import json
import asyncio
import pandas as pd
import os
import secrets
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import config
from mock_broker import MockDhanClient

# Initialize Broker for Manual Trades
manual_broker = MockDhanClient()

app = FastAPI()

# --- AUTONOMOUS TRADING STARTUP ---
import threading
from auto_trader import run_auto_pilot

@app.on_event("startup")
async def startup_event():
    print("[SYSTEM] INITIALIZING SOVEREIGN PROTOCOL...", flush=True)
    # Start the Auto-Pilot in a separate thread so it doesn't block the API
    bot_thread = threading.Thread(target=run_auto_pilot, daemon=True)
    bot_thread.start()
    print("[SYSTEM] AUTO-PILOT ENGAGED IN BACKGROUND THREAD.", flush=True)

# --- SECURITY CONSTANTS ---
# --- SECURITY CONSTANTS ---
# Use Env Var OR Generate a Random Safe Key (Prevent Hardcoded Defaults)
SECRET_KEY = os.getenv("JWT_SECRET") or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480 # 8 Hours

# --- SECURITY SETUP ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Verify exact user (Simple single-user check)
    if not secrets.compare_digest(token_data.username, config.WEB_USERNAME):
        raise credentials_exception
    return token_data.username

# Endpoint to get Token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Verify Credentials
    is_user_ok = secrets.compare_digest(form_data.username, config.WEB_USERNAME)
    is_pass_ok = secrets.compare_digest(form_data.password, config.WEB_PASSWORD)
    
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Grant Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protect App (Require Default Auth on all API routes except public ones if any)
# Note: Root "/" is usually public to load the React App, then React checks for token.
# So we REMOVE global dependency and add it to API routes or middleware.

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
MEMORY_PATH = "memories/bot_brain.json"
JOURNAL_PATH = "trading_journal.csv"
PAPER_TRADES_PATH = "memories/paper_trades.json"
HISTORY_PATH = "memories/account_history.csv"

# Global Settings State
SETTINGS_PATH = "memories/settings.json"

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                return json.load(f)
        except: pass
    return {
        "risk_per_trade": config.RISK_PER_TRADE,
        "trading_mode": config.TRADING_MODE,
        "telegram_enabled": bool(config.TELEGRAM_BOT_TOKEN)
    }

def save_settings(new_settings):
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(new_settings, f, indent=4)

# Global State initialized from file
current_settings = load_settings()

class SettingsUpdate(BaseModel):
    risk_per_trade: float
    trading_mode: str
    min_confidence: float = 0.60 # Default Balanced
    max_daily_loss: float = 5000.0
    telegram_token: str = ""
    telegram_chat_id: str = ""

class ManualOrder(BaseModel):
    symbol: str
    action: str
    quantity: int
    price: float
    order_type: str
    origin: str = "USER"
    stop_loss: float = None
    target: float = None

@app.post("/api/manual_trade")
def execute_manual_trade(order: ManualOrder, force: bool = False, current_user: str = Depends(get_current_user)):
    print(f"[API] Manual Trade Request: {order}, Force Override: {force}")
    
    # 1. Market Hours Check
    from utils.market_hours import MarketSchedule
    if not MarketSchedule.is_market_open(force_override=force):
        status_msg = MarketSchedule.get_status_message()
        print(f"[API] Trade Rejected: Market is {status_msg}")
        return {
            "status": "error", 
            "message": f"Market Offline: {status_msg}. Use 'Force Execute' if testing."
        }

    try:
        # Forward to Mock Broker
        result = manual_broker.place_order(
            symbol=order.symbol,
            quantity=order.quantity,
            action=order.action,
            price=order.price,
            origin=order.origin,
            stop_loss=order.stop_loss,
            target=order.target
        )
        if result["status"] == "success":
            return {"status": "success", "order_id": result["order_id"]}
        else:
            return {"status": "error", "message": result["message"]}
    except Exception as e:
        print(f"[API ERROR] Manual Trade Failed: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/user_trades")
def get_user_trades(current_user: str = Depends(get_current_user)):
    if not os.path.exists(PAPER_TRADES_PATH):
        return []
    with open(PAPER_TRADES_PATH, 'r') as f:
        trades = json.load(f)
    # Filter for USER trades and reverse (newest first)
    user_trades = [t for t in trades if t.get('origin') == 'USER']
    return user_trades[::-1]

class TradeAnalysisRequest(BaseModel):
    trade_id: str
    strategy: str = "Unknown"
    emotion: str = "Neutral"
    notes: str = ""

@app.post("/api/analyze_trade")
def analyze_trade(request: TradeAnalysisRequest, current_user: str = Depends(get_current_user)):
    # 1. Find Trade
    if not os.path.exists(PAPER_TRADES_PATH):
        return {"error": "No trades found"}
    
    with open(PAPER_TRADES_PATH, 'r') as f:
        trades = json.load(f)
    
    trade = next((t for t in trades if t.get('order_id') == request.trade_id), None)
    if not trade:
        return {"error": "Trade not found"}

    # 2. Extract Data
    entry = float(trade.get('avg_price', 0))
    sl = trade.get('stop_loss')
    target = trade.get('target')
    action = trade.get('action')

    # 3. Analyze with Real AI (The Oracle)
    import librarian
    # 3. Analyze with Real AI (The Oracle)
    import librarian
    import re
    import time
    import model_factory # Updated to use factory
    
    print(f"[AI REVIEW] Analyzing Trade {request.trade_id} with Context: {request.strategy}/{request.emotion}")
    
    try:
        # Load Knowledge Base (The Library)
        kb = librarian.get_knowledge_base()
        
        # Construct Prompt (Beginner Friendly Rectifier)
        prompt = f"""
        You are "The Rectifier", a professional Trading Mentor for a BEGINNER.
        Your job is to catch their mistakes and explain them simply.
        
        USER CONTEXT (Review this CRITICALLY):
        - Strategy Claimed: {request.strategy}
        - Emotional State: {request.emotion}
        - User's Rationale: "{request.notes}"
        
        TRADE DATA:
        - Symbol: {trade.get('symbol')}
        - Action: {action}
        - Entry Price: {entry}
        - Stop Loss: {sl if sl else "NOT SET (Danger!)"}
        - Target: {target if target else "Not Set"}
        - Result: {trade.get('profitability', 'Pending')}
        
        INSTRUCTIONS:
        1. Compare their "Strategy" vs "Reality". (e.g., If they said "Breakout" but bought at the top, say that).
        2. Check their Emotion. (e.g., If "FOMO", warn them about chasing).
        3. Explain Risk:Reward simply (Are they risking ₹1 to make ₹0.50? That's bad).
        4. Give a Score (0-100).
        
        TONE RULES:
        - Speak like a friendly but strict teacher.
        - USE SIMPLE ENGLISH. No complex jargon without explanation.
        - Be direct. "You messed up here because..."
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "score": <int>,
            "feedback": ["Fault 1: ...", "Advice: ..."],
            "risks": ["Risk 1", "Risk 2"],
            "rr_ratio": <float_or_null>
        }}
        """
        
        # 5. Robust Model Selection Loop (Using Factory Validation)
        candidates = model_factory.get_model_name_list()
        
        text = None
        last_error = ""

        # Using functional model directly usually handles selection, but keeping loop for robustness if factory changes
        # Actually better to just ask factory for a working one.
        
        try:
             # This automatically tries candidates
             model = model_factory.get_functional_model(system_instruction="You are a json agent.")
             if model:
                 response = model.generate_content(prompt) # KB passed? wrapper doesn't support list concatenation easily
                 # Wait, new SDK supports list of parts. 
                 # Wrapper signature: generate_content(contents). 
                 # Old SDK allowed list. New SDK allows list.
                 # KB is a list of file objects. 
                 # Wrapper needs to pass that list to contents.
                 
                 # IMPORTANT: librarian.get_knowledge_base() returns file objects.
                 # New SDK Client expects file names (uri) or objects?
                 # client.models.generate_content(contents=[prompt, file_obj]) works? 
                 # Usually needs types.Part or just strings/URIs.
                 # The wrapper passes 'contents' directly to client.models.generate_content
                 
                 # Let's assume the wrapper 'contents' argument handles the list.
                 # But we need to ensure the list items are compatible.
                 # Librarian returns `genai.types.File` (v2) now because we updated it?
                 # No, Librarian returns `client.files.get()`. This returns a File object.
                 # We must verify if `generate_content` accepts File objects in the list.
                 
                 final_content = [prompt]
                 # If KB returns file objects, we might need to convert to something else if SDK demands.
                 # but let's try passing the objects.
                 for k in kb:
                     final_content.append(k)
                     
                 response = model.generate_content(final_content)
                 text = response.text
                 print(f"   [AI] Success.")
             else:
                 raise Exception("Factory returned None")

        except Exception as e:
                error_msg = str(e)
                print(f"   [AI] Failed: {error_msg}")
                last_error = error_msg

        if not text:
             print(f"[CRITICAL FAIL] All models failed. Last Error: {last_error}")
             raise Exception(f"All models failed. Last error: {last_error}")
        
        # Clean JSON (Gemini sometimes adds ```json ... ```)
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text).strip()
        
        data = json.loads(text)
        
        # Validate Structure
        score = data.get("score", 70)
        feedback = data.get("feedback", ["Analysis completed, but feedback format was unexpected."])
        risks = data.get("risks", [])
        rr_value = data.get("rr_ratio")
        
        return {
            "score": score,
            "feedback": feedback,
            "risks": risks,
            "rr_ratio": rr_value
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[AI FAILURE] Oracle Offline: {e}")
        
        # Log to file for debugging
        with open("ai_error.log", "a") as log_file:
            log_file.write(f"\n[{datetime.now()}] ERROR IN ANALYZE_TRADE:\n")
            log_file.write(error_trace)
            log_file.write("-" * 50 + "\n")

        # Fallback to static if AI fails
        return {
            "score": 50,
            "feedback": [
                "The Oracle is temporarily silent (Connection Error).", 
                "Check 'ai_error.log' in bot folder.",
                f"Error: {str(e)[:50]}..."
            ],
            "risks": ["Could not verify risks."],
            "rr_ratio": None
        }

@app.get("/api/performance")
def get_performance():
    """Returns equity curve AND calculated monthly returns."""
    response = {
        "equity_curve": [],
        "monthly_returns": []
    }
    
    if os.path.exists(HISTORY_PATH):
        try:
            df = pd.read_csv(HISTORY_PATH)
            
            # Sanitize Data (Fix for 500 Errors caused by NaN or Strings)
            if 'equity' in df.columns:
                df['equity'] = pd.to_numeric(df['equity'], errors='coerce').fillna(0)
            
            df = df.fillna(0) # Catch all NaNs

            # Equity Curve
            response["equity_curve"] = df.rename(columns={"date": "name", "equity": "value"}).to_dict(orient="records")
            
            # Calculate Monthly Returns (Simple Logic)
            latest_equity = df.iloc[-1]['equity'] if not df.empty else 100000
            start_equity = 100000 # Base
            
            # Authentic Data: Just Jan for now
            total_pnl = float(latest_equity) - float(start_equity)
            
            response["monthly_returns"] = [
                {"name": "Jan", "pnl": total_pnl}
            ]
            
        except Exception as e:
            print(f"Error reading history: {e}")
            # Return empty structure instead of crashing
            response = {"equity_curve": [], "monthly_returns": []}
            
    return response

@app.get("/api/daily-pulse")
def get_daily_pulse():
    """Created by Bot"""
    if not os.path.exists(JOURNAL_PATH): return {"error": "Journal not found"}
    try:
        column_names = ['timestamp', 'order_id', 'symbol', 'action', 'price', 'quantity', 'taxes', 'total_cost', 'origin']
        df = pd.read_csv(JOURNAL_PATH, names=column_names, on_bad_lines='skip', dtype=str, index_col=False)
        if df.empty: return {"error": "No trades"}
        
        bot = len(df[df['origin'] == 'BOT'])
        manual = len(df[df['origin'] == 'MANUAL'])
        grade = "B"
        insight = "Consistent execution."
        if manual > bot: grade, insight = "C", "High manual interference."
        elif bot > 5 and manual == 0: grade, insight = "A+", "Flawless autonomy."
        
        return {
            "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "grade": grade, "insight": insight,
            "stats": {"trades": len(df), "bot": bot, "manual": manual}
        }
    except Exception as e: return {"error": str(e)}

@app.get("/api/alpha_details")
def get_alpha_details():
    if os.path.exists(JOURNAL_PATH):
        try:
            # CSV has no header and mixed formats (Old v1 vs New v2)
            # We define the V2 columns. V1 rows will be misaligned but we can filter them.
            column_names = ['timestamp', 'order_id', 'symbol', 'action', 'price', 'quantity', 'taxes', 'total_cost', 'origin']
            
            # Use on_bad_lines='skip' to avoid crashing on V1 rows if they have different field counts
            # index_col=False prevents pandas from guessing ID column is index
            df = pd.read_csv(JOURNAL_PATH, names=column_names, on_bad_lines='skip', dtype=str, index_col=False)
            
            # --- TRADE RECONSTRUCTION LOGIC ---
            # Goal: Group executed trades into "Round Trips" (Buy + Sell pair) or "Open Positions"
            
            # 1. Sort by Time Ascending to replay history
            if 'timestamp' in df.columns:
                # Ensure it's string (handled by dtype above, but safe to be sure)
                df['timestamp'] = df['timestamp'].astype(str).str.strip()
                
                # Manual parsing is safer for mixed garbage
                def parse_dt(x):
                    try: return pd.to_datetime(x)
                    except: return pd.NaT
                
                df['dt_temp'] = df['timestamp'].apply(parse_dt)
                
                # Filter out rows where timestamp was invalid (likely V1 headers or garbage)
                df = df.dropna(subset=['dt_temp'])
                df = df.sort_values(by='dt_temp', ascending=True)

            trades = []
            open_positions = {} # Key: Symbol, Value: Buy Row Data

            for _, row in df.iterrows():
                # --- FIELD RECOVERY LOGIC (V1 vs V2) ---
                # V2: order_id=ORD-..., symbol=REL, action=BUY, price=100
                # V1: order_id=REL, symbol=BUY, action=100 (Shifted)
                
                real_symbol = str(row.get('symbol')).strip()
                real_action = str(row.get('action')).strip()
                raw_price_col = str(row.get('price', 0))
                
                # Check for Shift (V1 Signature: Symbol field is 'BUY' or 'SELL')
                is_v1_shifted = False
                if real_symbol in ['BUY', 'SELL'] and real_action.replace('.','',1).isdigit():
                    is_v1_shifted = True
                
                if is_v1_shifted:
                    # Remap V1
                    real_action = real_symbol # "BUY"
                    real_symbol = str(row.get('order_id')).strip() # "RELIANCE.NS"
                    try: real_price = float(row.get('action', 0)) # Used action col for price
                    except: real_price = 0.0
                    real_order_id = "V1-LEGACY"
                else:
                    # Standard V2
                    real_order_id = str(row.get('order_id')).strip()
                    try: real_price = float(row.get('price', 0))
                    except: real_price = 0.0

                symbol = real_symbol
                action = real_action
                price = real_price
                order_id = real_order_id
                origin = str(row.get('origin', 'BOT')).strip() # Default to BOT if missing
                if origin == 'nan': origin = 'BOT'

                # Basic sanity check
                if price == 0.0: continue
                
                # Timestamp Parsing
                ts = row.get('timestamp', str(datetime.now()))
                try:
                    dt_obj = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S.%f")
                except:
                    try: dt_obj = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S")
                    except: dt_obj = datetime.now()
                
                date_str = dt_obj.strftime("%d/%m/%Y")
                time_str = dt_obj.strftime("%H:%M:%S")
                # Store sortable dt for final sort
                sortable_dt = dt_obj

                if action == 'BUY':
                    # Start a new Open Position
                    open_positions[symbol] = {
                        "id": order_id,
                        "date": date_str,
                        "time": time_str,
                        "sort_dt": sortable_dt,
                        "orderId": order_id,
                        "symbol": symbol,
                        "entryPrice": price,
                        "exitPrice": "-", # Pending
                        "action": "OPEN",
                        "profitability": "Pending",
                        "rationale": "Alpha Signal (High Confidence)",
                        "origin": origin
                    }
                
                elif action == 'SELL':
                    # Close the position if exists
                    if symbol in open_positions:
                        trade = open_positions.pop(symbol)
                        trade['exitPrice'] = price
                        trade['action'] = "CLOSED"
                        trade['time'] = time_str # Show Close Time
                        trade['date'] = date_str
                        trade['sort_dt'] = sortable_dt # Update to Close Time for sorting "Status Update"
                        
                        # Calculate ROI
                        entry_p = trade['entryPrice']
                        if entry_p > 0:
                            roi_pct = ((price - entry_p) / entry_p) * 100
                            trade['profitability'] = f"{roi_pct:+.2f}%"
                        
                        trades.append(trade)
                    else:
                        trades.append({
                            "id": order_id,
                            "date": date_str,
                            "time": time_str,
                            "sort_dt": sortable_dt,
                            "orderId": order_id,
                            "symbol": symbol,
                            "entryPrice": "-",
                            "exitPrice": price,
                            "action": "ORPHAN SELL",
                            "profitability": "-",
                            "rationale": "Manual/Unknown Close",
                            "origin": origin
                        })

            # Add remaining Open Positions to the list
            for symbol, trade in open_positions.items():
                trades.append(trade)

            # Explicit Sort by Date/Time Descending (Newest First)
            trades.sort(key=lambda x: x.get('sort_dt', datetime.min), reverse=True)
            
            # Remove sort_dt helper before sending JSON (optional, but clean)
            for t in trades:
                t.pop('sort_dt', None)

            return trades
        except Exception as e:
            print(f"Error reading Alpha journal: {e}")
            return []
    return []

@app.get("/api/settings")
def get_settings():
    return current_settings

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate):
    global current_settings
    current_settings.update(settings.dict())
    save_settings(current_settings) # Persist to disk
    print(f"Server: Settings updated to {current_settings}")
    return {"status": "success", "settings": current_settings}

@app.get("/api/status")
def get_status():
    status_data = {}
    latest_confidence = 0.0 # Logic skipped for brevity
    
    # Wallet Balance from Brain
    wallet_balance = 100000.0
    if os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, 'r') as f:
                data = json.load(f)
                wallet_balance = data.get("wallet_balance", 100000.0)
        except: pass

    # Risk Status (The Dialogue Box Data)
    risk_status_msg = "UNKNOWN"
    daily_stats_path = "memories/daily_stats.json"
    if os.path.exists(daily_stats_path):
        try:
             with open(daily_stats_path, 'r') as f:
                 stats = json.load(f)
                 # Map internal status to User Friendly Message
                 s = stats.get("status", "ACTIVE")
                 if s == "ACTIVE":
                     if stats.get("is_cautious_mode", False):
                         risk_status_msg = "CAUTIOUS MODE (Recovering Loss - Sniper Only)"
                     else:
                         risk_status_msg = "TRADING ACTIVE (Hunting for Opportunities)"
                 elif s == "STOP_LOSS":
                     risk_status_msg = "STOPPED (Max Loss Hit - Done for the Day)"
                 elif s == "TARGET_HIT":
                     risk_status_msg = "STOPPED (Profit Target Hit - Bag Secured)"
                 else:
                     risk_status_msg = s
        except: pass

    from utils.market_hours import MarketSchedule
    status_data['market_status'] = MarketSchedule.get_status_message()
    status_data['risk_status'] = risk_status_msg
    status_data['latest_oracle_confidence'] = 0.85
    status_data['trading_mode'] = current_settings['trading_mode']
    status_data['wallet_balance'] = wallet_balance
    status_data['server_timestamp'] = datetime.now().isoformat()
    status_data['bot_message'] = "Market is active. Scanning for opportunities."

    return status_data

@app.get("/api/health")
def health_check():
    return {"status": "Online"}

@app.get("/api/regime")
def get_regime_status():
    try:
        from market_regime import get_market_regime
        regime = get_market_regime()
        return {"status": "success", "regime": regime}
    except Exception as e:
        return {"status": "error", "regime": "UNKNOWN", "details": str(e)}

@app.post("/api/kill_switch")
def trigger_kill_switch():
    try:
        with open("STOP.flag", "w") as f:
            f.write("TERMINATE")
        print("🚨 API TRIGGERED KILL SWITCH")
        return {"status": "success", "message": "KILL SIGNAL SENT"}
    except Exception as e:
        return {"status": "success", "message": "KILL SIGNAL SENT"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

        return {"status": "success", "message": "KILL SIGNAL SENT"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- BACKTEST LAB ENGINE ---
class BacktestRequest(BaseModel):
    symbol: str
    period: str = "1y"

@app.post("/api/backtest")
def run_backtest(req: BacktestRequest, current_user: str = Depends(get_current_user)):
    try:
        import yfinance as yf
        import numpy as np

        print(f"[BACKTEST] simulating {req.symbol} for {req.period}...")
        
        # 1. Fetch Data (Auto Adjust for Dividends/Splits)
        df = yf.download(req.symbol, period=req.period, interval="1d", auto_adjust=True, progress=False)
        
        if df.empty:
            return {"status": "error", "message": "No data found for symbol"}

        # Fix for MultiIndex Columns (common in new yfinance)
        # e.g. columns are ('Close', 'RELIANCE.NS'), we just want 'Close'
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 2. Indicators (Vectorized)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # 3. Strategy Logic (Golden Cross)
        # Signal: 1 (Long) when SMA20 > SMA50, else 0 (Cash/Neutral)
        df['Signal'] = np.where(df['SMA_20'] > df['SMA_50'], 1.0, 0.0)
        
        # Shift signal by 1 day to avoid lookahead bias (Trade happens NEXT open)
        df['Position'] = df['Signal'].shift(1)
        
        # 4. Returns Calculation
        df['Market_Returns'] = df['Close'].pct_change()
        df['Strategy_Returns'] = df['Market_Returns'] * df['Position']
        
        # 5. Commission & Slippage Simulation (0.1% per trade)
        # Detect Trade Entries/Exits: Diff != 0
        trades = df['Position'].diff().abs()
        transaction_costs = trades * 0.001 
        df['Strategy_Returns'] = df['Strategy_Returns'] - transaction_costs

        # 6. Cumulative Returns (Equity Curve)
        df['Benchmark_Equity'] = (1 + df['Market_Returns']).cumprod() * 100000
        df['Strategy_Equity'] = (1 + df['Strategy_Returns']).cumprod() * 100000
        
        # Fill NaN (Start of period)
        df.fillna(100000, inplace=True)
        
        # 7. Metrics Calculation
        total_return_pct = ((df['Strategy_Equity'].iloc[-1] - 100000) / 100000) * 100
        benchmark_return_pct = ((df['Benchmark_Equity'].iloc[-1] - 100000) / 100000) * 100
        
        # Max Drawdown
        peak = df['Strategy_Equity'].cummax()
        drawdown = (df['Strategy_Equity'] - peak) / peak
        max_drawdown_pct = drawdown.min() * 100
        
        # Win Rate (Daily)
        winning_days = len(df[df['Strategy_Returns'] > 0])
        total_trade_days = len(df[df['Position'] > 0])
        win_rate = (winning_days / total_trade_days * 100) if total_trade_days > 0 else 0

        # Sharpe Ratio (Annualized, assuming 252 trading days)
        # Risk Free Rate assumed 0 for simplicity
        daily_mean = df['Strategy_Returns'].mean()
        daily_std = df['Strategy_Returns'].std()
        sharpe = (daily_mean / daily_std) * np.sqrt(252) if daily_std > 0 else 0

        # 8. AI Insights Generation
        suggestions = []
        if total_return_pct > benchmark_return_pct:
            suggestions.append("✅ Outperformed the Market Benchmark.")
        else:
            suggestions.append("⚠️ Underperformed Buy & Hold. Strategy may be over-trading.")
            
        if max_drawdown_pct < -20:
            suggestions.append("⚠️ High Risk Detected: Max Drawdown exceeds 20%.")
        else:
             suggestions.append("Shield Holding: Drawdown is within acceptable limits.")

        if sharpe > 1.5:
             suggestions.append("Excellent Risk-Adjusted Returns (Sharpe > 1.5).")
        
        if df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
             suggestions.append("Current Trend: BULLISH (Golden Cross Active).")
        else:
             suggestions.append("Current Trend: BEARISH (Death Cross Active).")

        # 9. Format Data for UI (Downsample if needed)
        # Limit points to ~200 for chart performance if necessary, but 1y is fine (~252 pts)
        chart_data = []
        for index, row in df.iterrows():
            chart_data.append({
                "date": index.strftime("%Y-%m-%d"),
                "strategy": round(row['Strategy_Equity'], 2),
                "benchmark": round(row['Benchmark_Equity'], 2)
            })
            
        return {
            "status": "success",
            "data": chart_data,
            "metrics": {
                "roi": round(total_return_pct, 2),
                "final_strategy": round(df['Strategy_Equity'].iloc[-1], 2),
                "final_benchmark": round(df['Benchmark_Equity'].iloc[-1], 2),
                "max_dd": round(max_drawdown_pct, 2),
                "win_rate": round(win_rate, 1),
                "sharpe": round(sharpe, 2)
            },
            "suggestions": suggestions
        }

    except Exception as e:
        print(f"[BACKTEST ERROR] {e}")
        return {"status": "error", "message": str(e)}

# --- DAILY CAPTAIN'S LOG ---
@app.get("/api/logs")
def get_logs():
    """Returns list of daily logs sorted by date"""
    logs = []
    log_dir = "memories/daily_logs"
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(log_dir, f), 'r') as file:
                        logs.append(json.load(file))
                except: pass
    # Sort newest first
    logs.sort(key=lambda x: x.get('date', ''), reverse=True)
    return logs

@app.post("/api/logs/generate")
def generate_log():
    """Triggers the Scribe to write/update today's log"""
    try:
        from scribe import Scribe
        s = Scribe()
        log = s.generate_daily_log()
        return {"status": "success", "log": log}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- ORACLE FORECAST ENGINE (MONTE CARLO) ---
class ForecastRequest(BaseModel):
    symbol: str
    days: int = 30

@app.post("/api/forecast")
def run_forecast(req: ForecastRequest, current_user: str = Depends(get_current_user)):
    try:
        import yfinance as yf
        import numpy as np
        
        print(f"[ORACLE] Forecasting {req.symbol} for {req.days} days...")
        
        # 1. Fetch History (1 Year for Volatility Context)
        df = yf.download(req.symbol, period="1y", interval="1d", auto_adjust=True, progress=False)
        
        if df.empty:
            return {"status": "error", "message": "No data found"}
            
        # Fix MultiIndex if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 2. Derive Stats (Smart Drift)
        # Log Returns = ln(Pt / Pt-1)
        log_returns = np.log(1 + df['Close'].pct_change())
        
        u = log_returns.mean()
        var = log_returns.var()
        drift = u - (0.5 * var)
        stdev = log_returns.std()
        
        # --- SMART DRIFT (Trend Awareness) ---
        # If the trend is strong (SMA20 > SMA50), we nudge the drift slightly 
        # to respect Momentum aka "The Trend is your Friend".
        try:
            sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
            
            # Annualized Nudge: 5% per year approx -> 0.05 / 252 (daily)
            bias = (0.05 / 252) 
            
            if sma_20 > sma_50:
                print(f"[ORACLE] Used Golden Cross Bias (+5%)")
                drift += bias
            elif sma_20 < sma_50:
                print(f"[ORACLE] Used Death Cross Bias (-5%)")
                drift -= bias
        except:
            pass # Fallback to pure random walk
        
        # 3. Monte Carlo Simulation (1000 Iterations)
        iterations = 1000
        days = req.days
        
        # Random Z-scores
        daily_returns = np.exp(drift + stdev * np.random.normal(0, 1, (days, iterations)))
        
        # Price Paths
        last_price = df['Close'].iloc[-1]
        price_paths = np.zeros_like(daily_returns)
        price_paths[0] = last_price * daily_returns[0]
        
        for t in range(1, days):
             price_paths[t] = price_paths[t-1] * daily_returns[t]
             
        # 4. Aggregate Percentiles (P10, P50, P90)
        # Result shape: [days, 3] -> (P10, P50, P90)
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, days+1)]
        forecast_data = []
        
        for t in range(days):
            prices = price_paths[t]
            p10 = np.percentile(prices, 10)
            p50 = np.percentile(prices, 50)
            p90 = np.percentile(prices, 90)
            
            forecast_data.append({
                "date": future_dates[t].strftime("%Y-%m-%d"),
                "p10": round(p10, 2),
                "p50": round(p50, 2),
                "p90": round(p90, 2)
            })
            
        # 5. Prepare Historical Context (Last 60 Days)
        history_data = []
        subset = df.iloc[-60:]
        for index, row in subset.iterrows():
            history_data.append({
                "date": index.strftime("%Y-%m-%d"),
                "price": round(row['Close'], 2)
            })
            
        # 6. Oracle Insight (Hybrid: Math + Neural)
        final_p50 = forecast_data[-1]['p50']
        final_p10 = forecast_data[-1]['p10']
        change_pct = ((final_p50 - last_price) / last_price) * 100
        
        # A. Neural Context (News + Research)
        try:
            from news_agent import NewsAgent
            import librarian
            from utils.key_manager import key_rotator
            
            print("[ORACLE] 🧠 Summoning Neural Context...", flush=True)
            
            # Fetch Context (Fast Check)
            news_vibe = NewsAgent().get_market_vibe() # {'score': X, 'reason': Y}
            # key_knowledge = librarian.get_knowledge_text(tags=['Strategy'])[:1000] # Cap tokens
            
            claude = key_rotator.get_anthropic()
            
            if claude:
                prompt = (
                    f"Analyze this Market Forecast.\n"
                    f"MATH DATA: Volatility={round(stdev*100,2)}%, Drift={round(drift*100,4)}, Expected Move={round(change_pct,2)}%.\n"
                    f"NEWS SENTIMENT: Score={news_vibe.get('score')} ({news_vibe.get('reason')}).\n"
                    f"TASK: Verify the Math against the News. If News is extreme (Crash/War), override the Math. Otherwise, support it.\n"
                    f"OUTPUT JSON: {{'insight': 'Short Label (e.g. Bullish Convergence)', 'reasoning': '1-sentence explanation', 'confidence': 0-100}}"
                )
                
                msg = claude.messages.create(
                    model="claude-3-5-sonnet-20240620", max_tokens=200, system="You are the Oracle Judge. Output JSON only.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # Parse JSON
                import json
                clean = msg.content[0].text.replace("```json","").replace("```","").strip()
                neural_data = json.loads(clean)
                
                insight = neural_data.get('insight', 'Neural Analysis')
                reasoning = neural_data.get('reasoning', 'Analysis complete.')
                confidence = neural_data.get('confidence', 50)
                
                print(f"[ORACLE] 🧠 Neural Verdict: {insight}", flush=True)
                
            else:
                # Fallback to Math
                raise Exception("No Claude Key")
                
        except Exception as e:
            print(f"[ORACLE] ⚠️ Neural Bypass: {e}")
            # Fallback Logic
            insight = "Neutral View."
            if change_pct > 5: insight = "Bullish Outlook (Math Only)."
            elif change_pct < -5: insight = "Bearish Outlook (Math Only)."
            
            vol_desc = "High" if (stdev*100) > 20 else "Low"
            reasoning = f"Based on {round(stdev*100, 1)}% Volatility & {round(drift*100, 2)}% Drift."
            
            spread_pct = (forecast_data[-1]['p90'] - final_p10) / final_p50
            confidence = max(0, min(100, int((1 - spread_pct) * 100)))

        return {
            "status": "success",
            "history": history_data,
            "forecast": forecast_data,
            "metrics": {
                "current_price": round(last_price, 2),
                "expected_price": round(final_p50, 2),
                "worst_case": round(final_p10, 2),
                "volatility": round(stdev * 100, 2),
                "confidence": confidence,
                "insight": insight,
                "reasoning": reasoning
            }
        }

    except Exception as e:
        print(f"[FORECAST ERROR] {e}")
        return {"status": "error", "message": str(e)}

# --- BOT CONTROL ENDPOINTS ---
@app.get("/api/bot/status")
def get_bot_status():
    if os.path.exists("STOP.flag"):
        return {"status": "stopped"}
    return {"status": "running"}

@app.post("/api/bot/start")
def start_bot():
    try:
        if os.path.exists("STOP.flag"):
            os.remove("STOP.flag")
        return {"status": "success", "message": "Bot Started"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/bot/stop")
def stop_bot():
    try:
        with open("STOP.flag", "w") as f:
            f.write("User Requested Stop via Dashboard")
        return {"status": "success", "message": "Bot Stopped"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

app.mount("/assets", StaticFiles(directory="dashboard/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    file_path = f"dashboard/dist/{full_path}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Serve index.html with No-Cache headers to prevent stale UI
    response = FileResponse("dashboard/dist/index.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- VISION CENTER ENDPOINTS ---
from fastapi import UploadFile, File, Form
from vision_agent import VisionAgent
import shutil

# Initialize Vision Agent
vision_bot = VisionAgent()
UPLOAD_DIR = "memories/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class JournalEntry(BaseModel):
    symbol: str
    mode: str
    analysis: str
    image_path: str
    user_notes: str = ""
    timestamp: str = None

@app.post("/api/analyze-chart")
async def analyze_chart(file: UploadFile = File(...), mode: str = Form(...)):
    try:
        # 1. Save File
        file_path = f"{UPLOAD_DIR}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Call Gemini
        print(f"[REQUEST] Analyze {file.filename} in [{mode}] mode")
        analysis = vision_bot.analyze_chart(file_path, mode)
        
        return {
            "status": "success",
            "analysis": analysis,
            "image_path": file_path
        }
    except Exception as e:
        print(f"[VISION ERROR] {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/save-journal")
def save_journal(entry: JournalEntry):
    try:
        journal_file = "memories/trade_journal.json"
        
        # Load Existing
        history = []
        if os.path.exists(journal_file):
            with open(journal_file, "r") as f:
                history = json.load(f)
        
        # Add New
        new_entry = entry.dict()
        new_entry['timestamp'] = datetime.now().isoformat()
        history.insert(0, new_entry) # Add to top
        
        # Save
        with open(journal_file, "w") as f:
            json.dump(history, f, indent=4)
            
        print("[OK] Journal Entry Saved.")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

import socket

@app.get("/api/network-ip")
async def get_network_ip():
    try:
        # Connect to a public DNS to find the most appropriate network interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return {"ip": ip, "url": f"http://{ip}:8000"}
    except Exception:
        try:
             # Fallback: Local Hostname (Works offline usually)
             ip = socket.gethostbyname(socket.gethostname())
             return {"ip": ip, "url": f"http://{ip}:8000"}
        except:
             return {"ip": "127.0.0.1", "url": "/"}

# -------------------------------

# --- GAMIFICATION & REPORTING ---
@app.get("/api/daily-pulse")
async def get_daily_pulse():
    """Returns the Daily Report Card."""
    import daily_debrief
    try:
        return daily_debrief.generate_daily_report()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/trophies")
async def get_trophies():
    """Returns unlocked badges."""
    import trophy_cabinet
    try:
        return trophy_cabinet.check_badges()
    except Exception as e:
        return [{"name": "Error", "icon": "⚠️"}]

# --- VOICE ASSISTANT ---
from voice_assistant import OracleVoice
voice_bot = OracleVoice()

class ChatRequest(BaseModel):
    message: str
    voice: str = "male" # "male" or "female"
    context: str = ""   # e.g. "Viewing HDFC Chart"

@app.post("/api/chat")
async def chat_with_oracle(request: ChatRequest, current_user: str = Depends(get_current_user)):
    """
    1. Processing User Text (Simulated STT)
    2. Asking Gemini (Intelligence)
    3. Generating Speech (TTS)
    """
    try:
        print(f"[VOICE DEBUG] Request Received: '{request.message}' | Voice: {request.voice}")
        
        
        # 0. REFLEX SYSTEM (Save Quota)
        msg_lower = request.message.lower().strip()
        ai_text = None
        
        if "status" in msg_lower or "report" in msg_lower:
             vol_msg = "Market is stable."
             try:
                 from market_regime import get_market_regime
                 regime = get_market_regime()
                 vol_msg = f"Market is in {regime} mode."
             except: pass
             ai_text = f"Systems operational. {vol_msg}"
             
        elif "market" in msg_lower:
             ai_text = "The market is open. I am scanning for opportunities."
             
        elif "hello" in msg_lower or "hi" in msg_lower:
             ai_text = "Greetings. I am ready."
             
        elif "okay" in msg_lower or "ok" in msg_lower:
             ai_text = "Acknowledged."
             
        elif "thanks" in msg_lower:
             ai_text = "You are welcome." 
             
        # reflexes.get(msg_lower) -- Replaced by logic above
        
        if ai_text:
             print(f"[REFLEX] Fast Reply: {ai_text}", flush=True)
        else:
            # 1. AI Logic (Only if not reflex)
            try:
                import google.generativeai as genai
                from utils.key_manager import key_rotator
                
                # Strict Data-Only Prompt
                prompt = f"""
                You are Jarvis. DATA ONLY MODE.
                User: "{request.message}"
                Context: "{request.context}"
                
                INSTRUCTIONS:
                - Answer IMMEDIATELY.
                - NO pleasantries ("Hello", "Here is").
                - NO repetition.
                - Max 15 words.
                """
                
                print(f"[VOICE DEBUG] Asking Neural Engine...", flush=True)
                ai_text = ""
                
                # 1. Try Claude (Primary)
                claude = key_rotator.get_anthropic()
                if claude:
                    try:
                        print(f"[VOICE DEBUG] Using Claude 3.5 Sonnet...", flush=True)
                        msg = claude.messages.create(
                            model="claude-3-5-sonnet-20240620",
                            max_tokens=100,
                            system="You are Oracle. Answer IMMEDIATELY. NO pleasantries. NO repetition. Max 15 words. Tone: Professional, slightly mystical.",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        ai_text = msg.content[0].text
                    except Exception as e:
                        print(f"[VOICE ERROR] Claude Failed: {e}", flush=True)
                
                # 2. Fallback to Gemini (if Claude failed or missing)
                if not ai_text:
                    print(f"[VOICE DEBUG] Falling back to Gemini...", flush=True)
                    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash']
                    
                    success = False
                    for attempt in range(2):
                        if success: break
                        for model_name in models_to_try:
                            try:
                                model = key_rotator.get_model(model_name)
                                resp = await asyncio.to_thread(model.generate_content, prompt)
                                ai_text = resp.text
                                success = True
                                break 
                            except Exception as e:
                                print(f"[VOICE DEBUG] {model_name} Failed: {e}", flush=True)
                                if "429" in str(e): key_rotator.rotate_key()
                        if success: break
                
                if not ai_text:
                    ai_text = "I am currently overloaded. Please add more API Keys."
                
                if not ai_text:
                    ai_text = "I am currently overloaded. Please add more API Keys."

                print(f"[VOICE DEBUG] Gemini Reply: {ai_text}", flush=True)
            except Exception as ai_e:
                print(f"[VOICE DEBUG] AI Failed: {ai_e}", flush=True)
                ai_text = "System critical failure."

        # 2. Generate Audio (Stateless request)
        print(f"[VOICE DEBUG] Generating Audio for: '{ai_text}' as {request.voice}", flush=True)
        audio_path = await voice_bot.generate_speech(ai_text, gender=request.voice)
        
        if not audio_path:
             print("[VOICE DEBUG] TTS Failed (audio_path is None)", flush=True)
             raise Exception("TTS Generation Failed")
             
        full_url = f"{audio_path}"
        print(f"[VOICE DEBUG] Audio Ready: {full_url}", flush=True)
        
        return {
            "status": "success",
            "reply_text": ai_text,
            "audio_url": full_url
        }
    except Exception as e:
        print(f"[VOICE ERROR] Critical: {e}")
        return {"status": "error", "message": str(e)}

# --- FRONTEND INTEGRATION (SINGLE LINK MODE) ---
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check if build exists
FRONTEND_BUILD_DIR = os.path.join(os.getcwd(), "dashboard", "dist")

if os.path.exists(FRONTEND_BUILD_DIR):
    print(f"[SERVER] Mounting Frontend from: {FRONTEND_BUILD_DIR}")
    
    # 1. Mount Assets (JS/CSS)
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_BUILD_DIR, "assets")), name="assets")
    
    # 2. Serve Index (Root)
    @app.get("/")
    async def serve_spa_root():
        return FileResponse(os.path.join(FRONTEND_BUILD_DIR, "index.html"))

    # 3. Catch-All for React Router (e.g. /journal, /settings)
    # Must be LAST to avoid swallowing API routes
    @app.get("/{full_path:path}")
    async def serve_spa_fallback(full_path: str):
        # Allow API calls to pass through (just in case)
        if full_path.startswith("api"):
             raise HTTPException(status_code=404, detail="API Endpoint Not Found")
             
        # Check if file exists in root of dist (e.g. favicon.ico, manifest.json)
        file_path = os.path.join(FRONTEND_BUILD_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Default fallback to index.html for Client-Side Routing
        return FileResponse(os.path.join(FRONTEND_BUILD_DIR, "index.html"))

else:
    print("[SERVER] ⚠️ Frontend Build Not Found. Running in API-Only Mode.")
    print("   -> Run 'npm run build' in /dashboard folder to enabling UI serving.")


if __name__ == "__main__":
    import uvicorn
    import subprocess
    import re
    import time
    
    def force_clear_port(port):
        """Finds the process holding the port and KILLS it."""
        print(f"[STARTUP] Checking for zombie processes on port {port}...")
        try:
            # 1. Find PID
            cmd = f"netstat -ano | findstr :{port}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if "LISTENING" in line:
                        parts = re.split(r'\s+', line.strip())
                        pid = parts[-1] 
                        if pid != "0":
                            print(f"[STARTUP] Found Process {pid} blocking port {port}. TERMINATING...")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            time.sleep(1) # Give OS time to release handle
                            print(f"[STARTUP] Process {pid} Killed. Port {port} is free.")
            else:
                print(f"[STARTUP] Port {port} appears clean.")
                
        except Exception as e:
            print(f"[STARTUP] Warning: Auto-cleanup failed: {e}")

    # --- EXECUTE CLEANUP ---
    force_clear_port(8000)

    print("\n" + "="*50)
    print(" >>> SOVEREIGN TRADING BOT SERVER V2.5 (GEMINI 2.0) <<< ")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
