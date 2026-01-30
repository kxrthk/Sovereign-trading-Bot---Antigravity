import requests
import time
import subprocess
import sys
import os

SERVER_URL = "http://localhost:8000/api/status"

def test_auth():
    print("Locked & Loaded: Testing Security protocols...")
    
    # 1. Test No Auth
    try:
        print("1. Attempting Unauthorized Access...")
        response = requests.get(SERVER_URL, timeout=5)
        if response.status_code == 401:
            print("   [PASS] Access Denied (401) as expected.")
        else:
            print(f"   [FAIL] Unexpected Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Connection Error: {e}")
        return False

    # 2. Test Incorrect Auth
    try:
        print("2. Attempting Brute Force (Wrong Password)...")
        response = requests.get(SERVER_URL, auth=("admin", "wrongpass"), timeout=5)
        if response.status_code == 401:
            print("   [PASS] Access Denied (401) as expected.")
        else:
            print(f"   [FAIL] Unexpected Status Code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Connection Error: {e}")
        return False

    # 3. Test Correct Auth
    try:
        print("3. Attempting Authorized Access (admin:sovereign)...")
        response = requests.get(SERVER_URL, auth=("admin", "sovereign"), timeout=5)
        if response.status_code == 200:
            print("   [PASS] Access Granted (200). Payload received.")
            print(f"   Response: {response.json().get('bot_message')}")
        else:
            print(f"   [FAIL] Login Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAIL] Connection Error: {e}")
        return False
        
    print("\n[SUCCESS] Security System Verified.")
    return True

if __name__ == "__main__":
    # Ensure dependencies
    try:
        import requests
    except:
        print("Installing requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    
    test_auth()
