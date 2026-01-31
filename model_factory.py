import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load Secrets
load_dotenv()
load_dotenv(os.path.join(os.path.expanduser("~"), "sovereign_secrets.env"))
from utils.key_manager import key_rotator

# GLOBAL CLIENT (Managed by Rotator)
def get_client():
    return key_rotator.get_client()

CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-1.5-flash", 
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-pro"
]

class GeminiModelWrapper:
    """
    Compatibilty layer to make google.genai (v2) look like google.generativeai (v1).
    """
    def __init__(self, model_name, system_instruction=None):
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.name = f"models/{model_name}" # Compat field

    def generate_content(self, contents):
        """
        Mimics the old generate_content signature.
        """
        if not get_client():
            raise Exception("Gemini Client not initialized (Missing API Key?)")
            
        config = None
        if self.system_instruction:
            config = types.GenerateContentConfig(system_instruction=self.system_instruction)

        try:
            # New SDK Call
            # New SDK Call
            response = get_client().models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            # Auto-Rotate on Quota
            if "429" in str(e) or "quota" in str(e).lower():
                print(f"[FACTORY] Quota Hit. Rotating Key...")
                key_rotator.rotate_key()
                # Retry once
                return get_client().models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
            raise e
            # Basic error handling propogation
            raise e

def get_functional_model(system_instruction=None):
    """
    Tries to find a working model from the candidates list.
    Returns the Wrapper.
    """
    print("[FACTORY] Selecting best available AI model (via google.genai SDK)...")
    
    
    if not get_client():
        print("[FACTORY] CRITICAL: Client is None. Cannot get model.")
        return None

    for model_name in CANDIDATES:
        try:
            # Wrapper Creation
            model = GeminiModelWrapper(model_name, system_instruction)
            
            # LIVE PING
            # New SDK uses 'contents' arg
            # LIVE PING
            # New SDK uses 'contents' arg
            get_client().models.generate_content(model=model_name, contents="Ping")
            
            print(f"   -> Selected: {model_name}")
            return model
            
        except Exception as e:
            print(f"   -> {model_name} failed: {e}")
            continue
            
    print("[FACTORY] CRITICAL: All models failed. Defaulting to 'gemini-1.5-flash' wrapper.")
    return GeminiModelWrapper("gemini-1.5-flash", system_instruction)

def get_model_name_list():
    return CANDIDATES
