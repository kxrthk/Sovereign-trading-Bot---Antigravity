import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
# import dhanhq # Uncomment when using Real API
import joblib
import os
import config

class Oracle:
    def __init__(self):
        self.watchlist = ["RELIANCE.NS"]
        self.model_path = "memories/models/reliance_rf_v1.joblib"
        self.model = self._load_brain()
        self.data_source = getattr(config, 'DATA_SOURCE', 'YFINANCE') # Default to YFinance
        
        if self.data_source == 'DHAN':
            print("[ORACLE] Connecting to Dhan HQ API...")
            # self.dhan = dhanhq(config.DHAN_CLIENT_ID, config.DHAN_ACCESS_TOKEN)

    def fetch_data(self, symbol):
        if self.data_source == 'DHAN':
             # Real API Call Stub
             # return self.dhan.get_historical_data(...)
             print("[ORACLE] Dhan API not yet configured. Fallback to YFinance.")
             pass 
        
        # Default: YFinance (Intraday Real-Time)
        # 1m data is only available for last 7 days. We fetch 5 days to be safe.
        data = yf.download(symbol, period="5d", interval="1m", progress=False)
        return data

    def _load_brain(self):
        if os.path.exists(self.model_path):
            try:
                print(f"[ORACLE] Loading AI Brain from {self.model_path}...")
                return joblib.load(self.model_path)
            except Exception as e:
                print(f"[ORACLE] Brain Damage: {e}. Reverting to Lizard Brain (Rules).")
                return None
        else:
            print("[ORACLE] No Brain found. Using basic instinct.")
            return None

    def analyze(self, symbol):
        """
        Fetches live data and asks the AI for a prediction.
        """
        try:
            # 1. Fetch Live Data (Need enough for SMA-200)
            data = self.fetch_data(symbol)
            
            if data.empty:
                return {"signal": "HOLD", "confidence": 0.0, "reason": "No Data", "price": 0.0}
            
            # Flatten MultiIndex if present
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            price = data['Close'].iloc[-1]
            
            # 2. Feature Engineering (Must match brain_factory.py EXACTLY)
            # RSI
            data['RSI'] = ta.rsi(data['Close'], length=14)
            
            # MACD (Trend Momentum)
            macd = ta.macd(data['Close'])
            data = pd.concat([data, macd], axis=1) # Append MACD columns
            
            # ATR (Volatility)
            data['ATR'] = ta.atr(data['High'], data['Low'], data['Close'], length=14)

            # SMAs (Intraday Trends)
            # Note: SMA_200 on 1m chart = 200 minutes (3.3 hours). Good for intraday trend.
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['SMA_200'] = data['Close'].rolling(window=200).mean()
            data['Trend_Signal'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
            
            # Volatility
            data['Returns'] = data['Close'].pct_change()
            data['Volatility'] = data['Returns'].rolling(window=20).std()
            
            # Drop NaNs
            data.dropna(inplace=True)
            
            if data.empty:
                 return {"signal": "HOLD", "confidence": 0.0, "reason": "Not enough data for features", "price": price}

            # 3. AI Inference (Random Forest)
            if self.model:
                last_row = data.iloc[[-1]] 
                features = ['RSI', 'Trend_Signal', 'Volatility', 'SMA_50', 'SMA_200']
                
                if not all(col in last_row.columns for col in features):
                     return {"signal": "HOLD", "confidence": 0.0, "reason": "Feature Mismatch", "price": price}

                X_live = last_row[features]
                prediction = self.model.predict(X_live)[0]
                probabilities = self.model.predict_proba(X_live)[0]
                confidence = float(probabilities[1] if prediction == 1 else probabilities[0])
                
                # --- V50 UPGRADE: THE SCHOLAR CHECK ---
                # We ask the LLM to validate the Random Forest's decision using the PDFs
                
                scholar_signal = "HOLD"
                scholar_reason = "Scholar Sleeping"
                
                try:
                    import librarian
                    import model_factory
                    from market_regime import get_market_regime

                     # --- DYNAMIC KNOWLEDGE SWITCHING (The Context Switch) ---
                    current_regime = get_market_regime()
                    
                    # --- CORTEX INTEGRATION (The World View) ---
                    world_view_path = os.path.join("memories", "world_view.json")
                    world_view = {}
                    if os.path.exists(world_view_path):
                        try:
                            with open(world_view_path, 'r') as f:
                                world_view = json.load(f)
                        except: pass
                    
                    # CORTEX OVERRIDE: If DANGER, we halt immediately.
                    if world_view.get("risk_level") == "DANGER":
                         print(f"[ORACLE] 🛑 CORTEX OVERRIDE: World Risk is DANGER. Halting.")
                         return {"signal": "HOLD", "confidence": 0.0, "reason": f"Cortex Halt: {world_view.get('reasoning')}", "price": price}

                    # We store 'last_regime' in self to track state
                    if not hasattr(self, 'last_regime'): self.last_regime = None
                    
                    if current_regime != self.last_regime or not hasattr(self, 'textbooks'):
                         print(f"[ORACLE] Market Shift Detected: {self.last_regime} -> {current_regime}")
                         print(f"[ORACLE] Switching Knowledge Context to '{current_regime}' Mode...")
                         self.textbooks = librarian.get_knowledge_base(regime=current_regime)
                         self.last_regime = current_regime
                    
                    if not hasattr(self, 'llm'):
                        self.llm = model_factory.get_functional_model()
                    
                    if self.textbooks:
                         rsi_val = last_row['RSI'].iloc[0]
                         vol_val = last_row['Volatility'].iloc[0]
                         
                         prompt = (
                             f"Global Context (The Cortex): Sentiment {world_view.get('sentiment_score', 0)}/10. "
                             f"Insight: {world_view.get('reasoning', 'No Data')}. "
                             f"Market Data: Price {price}, RSI {rsi_val:.2f}, Volatility {vol_val:.4f}. "
                             f"The Random Forest Model predicts: {'BUY' if prediction == 1 else 'WAIT'} with {confidence:.2f} confidence. "
                         )

                         # --- RL INJECTION: READ PAST MISTAKES ---
                         # The Bot reads its own diary to avoid repeating errors.
                         journal_path = "trading_journal.csv"
                         history_context = ""
                         if os.path.exists(journal_path):
                             try:
                                 # Read last 5 lines roughly
                                 with open(journal_path, "r") as f:
                                     lines = f.readlines()[-5:]
                                 history_context = "\nMy Recent Trades:\n" + "".join(lines)
                             except:
                                 pass
                         
                         prompt += (
                             f"\n{history_context}\n"
                             f"INSTRUCTION: You are a Reinforcement Learning Agent. "
                             f"1. Look at the attached research papers for strategy. "
                             f"2. Look at 'My Recent Trades' above. If I lost money recently on similar conditions, say NO. "
                             f"3. If I am winning, reinforce the strategy. "
                             f"Answer YES or NO and explain why based on my history."
                         )
                         
                         # Quick check (High priority)
                         response = self.llm.generate_content(self.textbooks + [prompt])
                         scholar_reason = response.text[:100] + "..." # Keep it short for logs
                         
                         # If Scholar says NO, we downgrade signal
                         if "NO" in response.text.upper():
                             return {
                                 "signal": "HOLD", 
                                 "confidence": 0.0, 
                                 "reason": f"Scholar Vetoed: {scholar_reason}", 
                                 "price": price
                             }
                         else:
                             scholar_signal = "CONFIRMED"

                except Exception as e:
                    print(f"[ORACLE] Scholar Check Failed: {e}")

                # Final Decision
                if prediction == 1 and scholar_signal == "CONFIRMED":
                    return {
                        "signal": "BUY", 
                        "confidence": confidence, 
                        "reason": f"AI + Scholar Agreed. {scholar_reason}", 
                        "price": price
                    }
                else:
                    return {
                        "signal": "HOLD", 
                        "confidence": confidence, 
                        "reason": f"RF says Wait. {scholar_reason}", 
                        "price": price
                    }
                    
            else:
                # FALLBACK (Lizard Brain)
                return {"signal": "HOLD", "confidence": 0.0, "reason": "No Brain Loaded", "price": price}

        except Exception as e:
            print(f"[ORACLE] Error: {e}")
            return {"signal": "HOLD", "confidence": 0.0, "reason": "Error", "price": 0.0}

if __name__ == "__main__":
    oracle = Oracle()
    print("Testing Oracle Brain...")
    analysis = oracle.analyze("RELIANCE.NS")
    print(analysis)
