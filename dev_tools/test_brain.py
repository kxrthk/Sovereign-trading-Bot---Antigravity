import sys
import os

# Add parent dir to path to find config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import config
    print(f"[TEST] Config Loaded.")
    
    key = config.GEMINI_API_KEY
    if key:
        print(f"[TEST] Key Found: {key[:5]}...{key[-5:] if len(key)>5 else ''}")
    else:
        print(f"[TEST] ❌ GEMINI_API_KEY is Empty/None in config.")

    import google.generativeai as genai
    
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    print("[TEST] asking Gemini...")
    resp = model.generate_content("Say Hello")
    print(f"[TEST] Response: {resp.text}")

except Exception as e:
    print(f"[TEST] ❌ FAILURE: {e}")
    import traceback
    traceback.print_exc()
