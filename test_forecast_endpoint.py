import requests
import json

def test_forecast():
    url = "http://127.0.0.1:8000/api/forecast"
    payload = {
        "symbol": "RELIANCE.NS",
        "days": 30
    }
    
    print(f"Testing {url}...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("SUCCESS: Forecast generated.")
                print(f"Verdict: {data['metrics'].get('insight')}")
                print(f"Process: {data['metrics'].get('reasoning')}")
            else:
                print(f"FAILED: API returned error: {data}")
        else:
            print(f"FAILED: Server returned {response.text}")
            
    except Exception as e:
        print(f"CRASH: {e}")

if __name__ == "__main__":
    test_forecast()
