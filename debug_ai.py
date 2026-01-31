import os
import json
import traceback
import json
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

    print("\n2. Testing Gemini Model (via model_factory)...")
    try:
        import model_factory
        # No need to configure genai here, model_factory handles it
        
        prompt = "Based on the Daily Intelligence Brief, what are the top 3 Geopolitical or Global Trade risks today?"
        
        print("   Sending request...")
        # Get wrapper from factory
        model = model_factory.get_functional_model() # This initializes client/wrapper
        if not model:
             print("   [FAIL] No model available.")
             return

        response = model.generate_content(prompt)
        print(f"   [OK] Response: {response.text}")
        
    except Exception as e:
        print(f"   [FAIL] Model Error: {e}")
        # Factory handles fallbacks, so no complex logic needed here unless we manually retry
        traceback.print_exc()

if __name__ == "__main__":
    test_ai()
