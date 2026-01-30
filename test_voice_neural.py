import asyncio
from voice_assistant import OracleVoice
import os

async def test_voice():
    print("--- Testing Oracle's Neural Voice (Edge TTS) ---")
    v = OracleVoice()
    
    print("[1] Generating Male Voice...")
    v.set_voice("male")
    path = await v.generate_speech("System Online. The Oracle is ready to serve.")
    
    if path and os.path.exists(f"dashboard/dist{path}"):
        print(f"[PASS] Audio generated at: {path}")
    else:
        print("[FAIL] Audio generation failed.")

    print("[2] Generating Female Voice...")
    v.set_voice("female")
    path = await v.generate_speech("Protocol Alpha initiated.")
    
    if path and os.path.exists(f"dashboard/dist{path}"):
        print(f"[PASS] Audio generated at: {path}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(test_voice())
