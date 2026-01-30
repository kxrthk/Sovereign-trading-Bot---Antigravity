import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- PERSISTENT SECRETS LOADING ---
load_dotenv() 
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("No API Key found.")
else:
    print(f"Key found: {api_key[:5]}...")
    genai.configure(api_key=api_key)
    
    print("\nAvailable Models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
