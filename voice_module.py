import subprocess
import threading
import os

class VoiceModule:
    def __init__(self):
        # No init needed for PowerShell approach
        pass

    def speak(self, text):
        # Run in thread to not block main loop
        t = threading.Thread(target=self._speak_thread, args=(text,))
        t.start()

    def _speak_thread(self, text):
        try:
            # Sanitize text for PowerShell
            text = text.replace('"', "").replace("'", "")
            
            # PowerShell Command
            ps_command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}');"
            
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
        except Exception as e:
            print(f"[VOICE] Error: {e}")

if __name__ == "__main__":
    v = VoiceModule()
    v.speak("Systems Online. The Oracle is listening.")
