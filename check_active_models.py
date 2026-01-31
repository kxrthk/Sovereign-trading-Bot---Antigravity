import os
from dotenv import load_dotenv
from google import genai

load_dotenv("C:\\Users\\sudha\\sovereign_secrets.env")
api_key = os.getenv("GEMINI_API_KEY")

# --- DECRYPT IF NEEDED ---
if api_key and api_key.startswith("ENC:"):
    try:
        from crypto_vault import decrypt_secret
        api_key = decrypt_secret(api_key[4:])
    except Exception as e:
        print(f"Error decrypting key: {e}")

if not api_key:
    # Try local .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: No API Key found.")
    exit(1)

client = genai.Client(api_key=api_key)

print("Listing Available Models:")
try:
    for m in client.models.list():
        print(f"- {m.name}")
    
    print("\nAttempting Generation Check...")
    resp = client.models.generate_content(model="gemini-2.0-flash", contents="Hello")
    print(f"Generation Success: {resp.text}")
except Exception as e:
    print(f"ERROR: {e}")
