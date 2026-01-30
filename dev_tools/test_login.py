import requests

URL = "http://localhost:8000/token"
payload = {"username": "admin", "password": "sovereign"}
headers = {"Content-Type": "application/x-www-form-urlencoded"}

try:
    print(f"Testing Login at {URL}...")
    response = requests.post(URL, data=payload, headers=headers)
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESS!")
        print("Token received:", response.json().get("access_token")[:20] + "...")
    else:
        print(f"❌ LOGIN FAILED: {response.status_code}")
        print("Response:", response.text)

except Exception as e:
    print(f"Error: {e}")
