import os
import os
from dotenv import load_dotenv

# --- PERSISTENT SECRETS LOADING ---
load_dotenv() 
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

# --- DECRYPT IF NEEDED ---
if api_key and api_key.startswith("ENC:"):
    try:
        from crypto_vault import decrypt_secret
        api_key = decrypt_secret(api_key[4:])
        print("[CHECK] API Key decrypted successfully.")
    except ImportError:
        print("[CHECK] Warning: crypto_vault not found, cannot decrypt key.")
    except Exception as e:
        print(f"[CHECK] Error decrypting key: {e}")

if not api_key:
    print("No API Key found.")
else:
    print(f"Key found: {api_key[:5]}...")
    print(f"Key found: {api_key[:5]}...")
    
    from google import genai
    client = genai.Client(api_key=api_key)
    
    print("\nAvailable Models:")
    try:
        for m in client.models.list():
             print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
