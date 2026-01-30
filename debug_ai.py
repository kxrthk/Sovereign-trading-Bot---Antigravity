import os
import json
import traceback
import google.generativeai as genai
import librarian
import re
from dotenv import load_dotenv

# Load Secrets just like server
load_dotenv()
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path, override=True)

print(f"API KEY PRESENT: {bool(os.getenv('GEMINI_API_KEY'))}")

def test_ai():
    print("1. Testing Librarian...")
    try:
        kb = librarian.get_knowledge_base()
        print(f"   [OK] Library Loaded. Items: {len(kb)}")
    except Exception as e:
        print(f"   [FAIL] Librarian Error: {e}")
        traceback.print_exc()
        return

    print("\n2. Testing Gemini Model (gemini-2.0-flash)...")
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = "Hello. Reply with JSON: {\"status\": \"ok\"}"
        
        print("   Sending request...")
        response = model.generate_content([prompt])
        print(f"   [OK] Response: {response.text}")
        
    except Exception as e:
        print(f"   [FAIL] Model Error: {e}")
        # Try fallback model
        print("   Attempting fallback to 'gemini-1.5-flash'...")
        try:
             model = genai.GenerativeModel("gemini-1.5-flash")
             response = model.generate_content([prompt])
             print(f"   [OK] Fallback Success: {response.text}")
        except Exception as e2:
             print(f"   [FAIL] Fallback Failed: {e2}")
        traceback.print_exc()

if __name__ == "__main__":
    test_ai()
