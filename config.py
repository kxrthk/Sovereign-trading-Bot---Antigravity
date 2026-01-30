# --- FINANCIAL CONSTITUTION ---
import os
from dotenv import load_dotenv

# --- PERSISTENT SECRETS LOADING ---
# 1. Current Folder
load_dotenv() 
# 2. Parent Folder (If running from a subfolder like release_v35)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
# 3. User Home Directory (The Ultimate Persistence)
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path)
    print(f"[CONFIG] Loaded Secrets from {user_secrets_path}")

# --- DECRYPTION LAYER ---
try:
    from crypto_vault import decrypt_secret
    print("[CONFIG] CrytoVault Imported Successfully.") # DEBUG
    def get_secure(key, default=""):
        val = os.getenv(key, default)
        if val and val.startswith("ENC:"):
            try:
                # Remove ENC: prefix and decrypt
                decrypted = decrypt_secret(val[4:])
                print(f"[CONFIG] Decrypted {key} successfully.") # DEBUG
                return decrypted
            except Exception as e:
                print(f"[CONFIG] CRITICAL ERROR: Failed to decrypt {key}. Error: {e}")
                return val # Fail open (return encrypted string) so we see the error in logs
        return val
except ImportError as e:
    print(f"[CONFIG] WARNING: CryptoVault Import Failed ({e}). Encryption disabled.")
    # Fallback if crypto_vault missing
    def get_secure(key, default=""): return os.getenv(key, default)

TOTAL_CAPITAL = 100000.0     # RL Reset Capital (Standard Paper Account)
MAX_DAILY_LOSS = 99999999.0  # Infinite (RL Autonomy)
DAILY_PROFIT_TARGET = 99999999.0 # Infinite
MAX_TRADE_AMOUNT = 10000.0   # Cap at 10k per trade for risk management

# --- STRATEGY SETTINGS ---
# --- STRATEGY SETTINGS ---
TRADING_MODE = 'PAPER'       # Simulation Mode
MIN_CONFIDENCE = 0.60        # Aggressive Learning Mode (Was 0.80)
MAX_TRADES_PER_DAY = 20      # High Volume for Data Collection

# The Budget Watchlist (Diversified Sectors)
WATCHLIST = [
    'ITC.NS',         # FMCG (Stable)
    'TATASTEEL.NS',   # Metal (Volatile/Fast)
    'BEL.NS',         # Defense (Trending)
    'NTPC.NS',        # Power (Slow & Steady)
    'POWERGRID.NS',   # Energy (Defensive)
    'ASHOKLEY.NS',    # Auto (Cyclical)
    'HDFCBANK.NS',    # Banking (Market Mover)
    'ICICIBANK.NS',   # Banking (Aggressive)
    'SBIN.NS',        # PSU Banking (High Volume)
    'TATAMOTORS.NS',  # Auto (EV Growth)
    'MARUTI.NS'       # Auto (Premium)
]

# --- BROKER CREDENTIALS (KEEP SECRET) ---
DHAN_CLIENT_ID = ""      # Client ID (e.g. "10000xxxxx")
DHAN_ACCESS_TOKEN = ""   # Optional: Paste manually if you don't want auto-login
DHAN_PASSWORD = ""       # Optional: For Auto-Login
DHAN_TOTP_SECRET = ""    # Optional: TOTP Secret (Get this from Dhan 2FA setup)
DATA_SOURCE = "YFINANCE" # Options: "YFINANCE" (Sim), "DHAN" (Real)

# --- DASHBOARD SETTINGS (Restored) ---
RISK_PER_TRADE = 0.02        # Default risk per trade (2%)
TELEGRAM_BOT_TOKEN = ""      # Blank for now

# --- WEB SECURITY ---
# --- WEB SECURITY ---
WEB_USERNAME = os.getenv("WEB_USERNAME", "admin")
# Use Secure Getter to allow Encrypted Passwords
WEB_PASSWORD = get_secure("WEB_PASSWORD", "9392352630sk")

# --- AI BRAIN ---
GEMINI_API_KEY = get_secure("GEMINI_API_KEY", "")
