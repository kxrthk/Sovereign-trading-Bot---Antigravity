import requests
import time

print("🔍 DIAGNOSTIC: Checking Google Connectivity...")

try:
    # Try to reach Google just ONCE
    response = requests.get("https://www.google.com", timeout=5)
    
    if response.status_code == 200:
        print("✅ SUCCESS: You are NOT banned. The Safety Shield will work perfectly.")
    else:
        print(f"⚠️ BLOCKED: Status Code {response.status_code}")
        print("Suggestion: Wait 2 hours before running the bot.")

except Exception as e:
    print(f"❌ CRITICAL FAIL: {e}")
    print("Your IP is likely still soft-banned. Turn off your router for 5 mins to get a new IP, or wait it out.")