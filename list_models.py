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

from google import genai

# --- INIT CLIENT ---
# Simplified for list_models (assume decrypted or raw)
if api_key.startswith("ENC:"):
    try:
        from crypto_vault import decrypt_secret
        api_key = decrypt_secret(api_key[4:])
    except: pass

client = genai.Client(api_key=api_key)

print("Listing Available Models:")
try:
    # v2 SDK: client.models.list() returns an iterator
    for m in client.models.list():
        # m.name is usually "models/gemini-pro"
        # We can filter if needed, but client.models.list() usually returns usable models.
        print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
