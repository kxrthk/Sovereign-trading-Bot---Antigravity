import os
import itertools
import google.generativeai as genai
import anthropic

class KeyManager:
    def __init__(self):
        # Initial Keys (Will be populated by User)
        self.keys = []
        
        # Load from multiple env vars
        base_key = os.getenv("GEMINI_API_KEY", "")
        if base_key: self.keys.append(base_key)
        
        # Check for backup keys
        for i in range(2, 6): # Check GEMINI_API_KEY_2 ... _5
            k = os.getenv(f"GEMINI_API_KEY_{i}", "")
            if k: self.keys.append(k)
            
        # Hardcoded slots (will be replaced by agent when user provides keys)
        self.hardcoded_keys = [
            "AIzaSyDwQW_dROY_cG3-kufXDcfYCO50OMSg4fE",
            "AIzaSyBuBGQtfaEc4Qbda76tzSjnA61DwI49USQ",
            "AIzaSyBKgLnewvosKTVAavKJqnGA7y5QV0TqeuA"
        ]
        self.keys.extend(self.hardcoded_keys)
        
        # Deduplicate
        self.keys = list(set(self.keys))
        self.keys = [k for k in self.keys if k and len(k) > 10]
        
        if not self.keys:
            print("[KEY MANAGER] ⚠️ No API Keys found!")
            self.iterator = itertools.cycle([""])
        else:
            print(f"[KEY MANAGER] Loaded {len(self.keys)} API Keys.")
            self.iterator = itertools.cycle(self.keys)
            
        self.current_key = next(self.iterator)
        self._configure_current()

        # --- ANTHROPIC INIT ---
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic_client = None
        if self.anthropic_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
                print("[KEY MANAGER] [OK] Anthropic Client Initialized.")
            except Exception as e:
                print(f"[KEY MANAGER] [ERROR] Anthropic Init Failed: {e}")

    def _configure_current(self):
        if self.current_key:
            # print(f"[KEY MANAGER] Switching to Key: ...{self.current_key[-4:]}")
            genai.configure(api_key=self.current_key)

    def rotate_key(self):
        """Switches to the next available key in the pool."""
        if not self.keys: return False
        
        prev_key = self.current_key
        self.current_key = next(self.iterator)
        
        # If we cycled back to the same key, we are out of fresh keys
        if len(self.keys) == 1:
            print("[KEY MANAGER] Only 1 key available. Cannot rotate.")
            return False
            
        print(f"[KEY MANAGER] 🔄 Rotating Key because of Quota...")
        self._configure_current()
        return True

    def get_model(self, model_name='gemini-2.0-flash'):
        return genai.GenerativeModel(model_name)
        
    def get_anthropic(self):
        """Returns the Anthropic Client instance (or None)"""
        return self.anthropic_client

# Global Instance
key_rotator = KeyManager()
