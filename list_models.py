import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API Key found")
    exit()

genai.configure(api_key=api_key)

print("Listing Available Models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
