import asyncio
import os
from voice_assistant import OracleVoice

async def diagnose():
    print("--- VOICE DIAGNOSTIC ---")
    v = OracleVoice()
    
    # 1. Check Output Dir
    print(f"Target Dir: {v.OUTPUT_DIR if hasattr(v, 'OUTPUT_DIR') else 'dashboard/dist/assets/audio'}")
    
    # 2. Generate
    print("Generating audio...")
    path = await v.generate_speech("Testing voice path integrity.")
    
    if path:
        print(f"Returned Web Path: {path}")
        # Reconstruct file system path
        # server mounts /assets -> dashboard/dist/assets
        # so /assets/audio/x.mp3 -> dashboard/dist/assets/audio/x.mp3
        fs_path = "dashboard/dist" + path
        
        print(f"Checking File System Path: {fs_path}")
        if os.path.exists(fs_path):
            size = os.path.getsize(fs_path)
            print(f"File Exists. Size: {size} bytes")
            if size > 100:
                print("✅ SUCCESS: valid audio file created.")
            else:
                print("❌ FAILURE: File created but empty.")
        else:
            print("❌ FAILURE: File NOT found at expected path.")
    else:
        print("❌ FAILURE: generate_speech returned None.")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(diagnose())
