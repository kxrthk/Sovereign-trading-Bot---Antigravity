import requests

URL = "http://localhost:8000/api/chat"
TOKEN = "test_token_placeholder" # We turned off strict auth for chat? No, verify dependency
# Wait, dashboard_server.py has `current_user: str = Depends(get_current_user)` check on /api/chat?
# I need not just a token, but a VALID token.

# Let's check if I can bypass auth for testing or generate a mock one.
# Actually, I can use the login endpoint to get a real token first.

def get_token():
    try:
        res = requests.post("http://localhost:8000/token", data={"username": "admin", "password": "sovereign"})
        if res.status_code == 200:
            return res.json()["access_token"]
        else:
            print(f"Login Failed: {res.text}")
            return None
    except Exception as e:
        print(f"Login Error: {e}")
        return None

token = get_token()

if token:
    print(f"Got Token: {token[:10]}...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "message": "Hello Jarvis",
        "voice": "female",
        "context": "Test Script"
    }
    
    print(f"Sending POST to {URL}...")
    try:
        res = requests.post(URL, json=payload, headers=headers, timeout=30)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Request Error: {e}")
else:
    print("Skipping chat test due to login failure.")
