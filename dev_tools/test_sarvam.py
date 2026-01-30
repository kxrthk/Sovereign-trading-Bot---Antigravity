import requests
import base64
import json
import os

API_KEY = "sk_zsitm528_Y4FJQhpTAfEpmyj6quedWPoF"
URL = "https://api.sarvam.ai/text-to-speech"

payload = {
    "inputs": ["Hello, this is a test of the Sovereign Trading Bot voice system."],
    "target_language_code": "en-IN",
    "speaker": "meera",
    "pitch": 0,
    "pace": 1.0,
    "loudness": 1.5,
    "speech_sample_rate": 16000,
    "enable_preprocessing": True,
    "model": "bulbul:v1"
}

headers = {
    "Content-Type": "application/json",
    "api-subscription-key": API_KEY
}

print("Sending request to Sarvam AI...")
try:
    response = requests.post(URL, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Response Keys:", data.keys())
        if "audios" in data and len(data["audios"]) > 0:
            print("[SUCCESS] Audio data received (Base64).")
            # Try saving it
            with open("test_sarvam.wav", "wb") as f: # API docs say wav usually
                f.write(base64.b64decode(data["audios"][0]))
            print("[SUCCESS] Saved to test_sarvam.wav")
        else:
            print("[FAILURE] No 'audios' field in response.")
            print(json.dumps(data, indent=2))
    else:
        print(f"[FAILURE] Error: {response.text}")

except Exception as e:
    print(f"[FAILURE] Exception: {e}")
