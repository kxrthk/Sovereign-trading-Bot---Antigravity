import requests
import os

URL = "http://localhost:8000/api/analyze-chart"
IMAGE_PATH = "dashboard/dist/assets/test_chart.png"

# Ensure we have a test image
if not os.path.exists(IMAGE_PATH):
    # Try to find any png in uploads
    upload_dir = "memories/uploads"
    if os.path.exists(upload_dir):
        files = [f for f in os.listdir(upload_dir) if f.endswith(".png") or f.endswith(".jpg")]
        if files:
            IMAGE_PATH = os.path.join(upload_dir, files[0])
            print(f"Using uploaded image: {IMAGE_PATH}")
        else:
            print("No test image found!")
            exit()

print(f"Testing API with image: {IMAGE_PATH}")
print("Sending request... (This may take 10-20 seconds)")

try:
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": f}
        data = {"mode": "SWING"}
        response = requests.post(URL, files=files, data=data, timeout=60)
        
    print(f"\nStatus Code: {response.status_code}")
    print("\nRAW RESPONSE HEADER:")
    print(response.headers)
    
    print("\nRAW RESPONSE BODY (First 500 chars):")
    print(response.text[:500])
    
    json_data = response.json()
    print("\n[SUCCESS] JSON Parsed Correctly!")
    print("Analysis Length:", len(json_data.get("analysis", "")))
    print("Analysis Preview:", json_data.get("analysis", "")[:100])

except Exception as e:
    print(f"\n[FAIL] Request Error: {e}")
