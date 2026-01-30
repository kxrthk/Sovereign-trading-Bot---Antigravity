import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# Load Secrets
load_dotenv()
load_dotenv(os.path.join(os.path.expanduser("~"), "sovereign_secrets.env"))
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-1.5-flash", 
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-flash-latest",
    "gemini-pro"
]

def get_functional_model(system_instruction=None):
    """
    Tries to find a working model from the candidates list.
    Returns the first one that doesn't 404.
    """
    print("[FACTORY] Selecting best available AI model...")
    
    for model_name in CANDIDATES:
        try:
            # We do a 'dry run' to check if model exists/valid
            # Note: We can't really 'ping' without generating, 
            # so we just return the object and let the agent handling 429s.
            # But we can try to list_models if needed, or just trust the priority.
            
            # Simple check: Instantiate AND Ping
            model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
            
            # THE LIVE PING (Crucial for detecting Quota limits)
            response = model.generate_content("Ping") 
            
            print(f"   -> Selected: {model_name}")
            return model
            
        except Exception as e:
            print(f"   -> {model_name} failed: {e}")
            continue
            
        except Exception as e:
            print(f"   -> {model_name} failed: {e}")
            continue
            
    print("[FACTORY] CRITICAL: All models failed. Defaulting to 'gemini-1.5-flash' and praying.")
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)

def get_model_name_list():
    return CANDIDATES
