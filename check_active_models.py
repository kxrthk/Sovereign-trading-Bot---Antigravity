import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("C:\\Users\\sudha\\sovereign_secrets.env")
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: No API Key found.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing Available Models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"ERROR: {e}")
