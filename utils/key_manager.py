import os
import itertools
from google import genai
import time

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
        
        # Deduplicate
        self.keys = list(set(self.keys))
        self.keys = [k for k in self.keys if k and len(k) > 10]
        
        if not self.keys:
            print("[KEY MANAGER] ⚠️ No API Keys found!")
            self.iterator = itertools.cycle(["NO_KEY"])
        else:
            print(f"[KEY MANAGER] Loaded {len(self.keys)} API Keys.")
            # Create a client for EACH key to be ready
            self.clients = []
            for k in self.keys:
                try:
                    # Handle Encrypted Keys
                    if k.startswith("ENC:"):
                        from crypto_vault import decrypt_secret
                        k = decrypt_secret(k[4:])
                    
                    client = genai.Client(api_key=k)
                    self.clients.append(client)
                except Exception as e:
                    print(f"[KEY MANAGER] Bad Key: {e}")
            
            if self.clients:
                self.iterator = itertools.cycle(self.clients)
            else:
                self.iterator = itertools.cycle([None])
            
        self.current_client = next(self.iterator)

    def get_client(self):
        """Returns the current active client"""
        return self.current_client

    def rotate_key(self):
        """Switches to the next available client/key."""
        if not self.clients: return False
        
        print(f"[KEY MANAGER] 🔄 Rotating API Key (Load Balancing)...")
        self.current_client = next(self.iterator)
        return True

# Global Instance
key_rotator = KeyManager()
