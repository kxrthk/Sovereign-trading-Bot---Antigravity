import config
import pyotp
import sys
from dhan_broker import DhanBroker

print("--------------------------------------------------")
print("[VERIFICATION] Checking Credentials Logic...")

# 1. Check Config Existence
if not config.DHAN_CLIENT_ID:
    print("[FAIL] Client ID is MISSING.")
else:
    print("[PASS] Client ID is present.")

if not config.DHAN_PASSWORD:
    print("[WARN] Password is MISSING (Auto-Login will fail).")

if not config.DHAN_TOTP_SECRET:
    print("[WARN] TOTP Secret is MISSING (2FA will fail).")

# 2. Test TOTP Generation
if config.DHAN_TOTP_SECRET:
    try:
        print("[TEST] Attempting to generate TOTP...")
        totp = pyotp.TOTP(config.DHAN_TOTP_SECRET).now()
        print(f"[PASS] TOTP Generation Successful! Code: {totp}")
        print("       (If this code matches your App, the secret is correct.)")
    except Exception as e:
        print(f"[FAIL] TOTP Secret Invalid: {e}")
        print("       Ensure you copied the Base32 Secret Key, not the 6-digit code.")

# 3. Test Broker Initialization
print("\n[TEST] Initializing Broker...")
try:
    broker = DhanBroker()
    if broker.dhan:
        print("[PASS] Broker Initialized (Connected equivalent).")
    else:
        print("[INFO] Broker Initialized (Auto-Login Pending/Placeholder verifying flow).")
except Exception as e:
    print(f"[FAIL] Broker Crash: {e}")

print("--------------------------------------------------")
