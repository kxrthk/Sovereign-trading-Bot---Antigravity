import sys
import os
import time
sys.path.append(os.getcwd())

try:
    from voice_module import VoiceModule
    print("--- Testing Oracle's Whisper (Audio via PowerShell) ---")
    
    vm = VoiceModule()
    print("[TEST] Speaking: 'Auditory circuits initialized.'")
    vm.speak("Auditory circuits initialized.")
    time.sleep(2) # Wait for thread
    print("[PASS] Audio command sent to OS.")
        
except ImportError as e:
    print(f"[FAIL] Import Error: {e}")
except Exception as e:
    print(f"[FAIL] Check failed: {e}")

if __name__ == "__main__":
    pass
