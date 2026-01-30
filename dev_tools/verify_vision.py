import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from vision_agent import VisionAgent
import time

def verify_vision():
    print("1. Initializing Vision Agent...")
    try:
        agent = VisionAgent()
    except Exception as e:
        print(f"FAILED to init: {e}")
        return

    # Use a real file we found
    image_path = "memories/uploads/20260122_195128_Screenshot 2026-01-22 181711.png"
    
    if not os.path.exists(image_path):
        print(f"Skipping: Test Image not found at {image_path}")
        return

    print(f"2. Sending {image_path} to Gemini...")
    start = time.time()
    
    result = agent.analyze_chart(image_path, mode="SCALP")
    
    duration = time.time() - start
    print(f"3. Analysis Received in {duration:.2f}s")
    print("-" * 50)
    print(result[:300] + "...") # Print first 300 chars
    print("-" * 50)
    
    if "Vision Agent Error" in result or "ALL MODELS FAILED" in result:
        print("❌ VERIFICATION FAILED")
        sys.exit(1)
    else:
        print("✅ VERIFICATION SUCCESS")

if __name__ == "__main__":
    verify_vision()
