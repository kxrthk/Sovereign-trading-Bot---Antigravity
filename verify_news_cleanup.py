import os
import time
import shutil
from news_scout import cleanup_old_news, NEWS_DIR

def setup_test_files():
    if not os.path.exists(NEWS_DIR): os.makedirs(NEWS_DIR)
    
    now = time.time()
    day = 86400
    
    # 1. Fresh File (2 days old) -> KEEP
    with open(os.path.join(NEWS_DIR, "TEST_Fresh.txt"), "w") as f: f.write("Just random noise")
    os.utime(os.path.join(NEWS_DIR, "TEST_Fresh.txt"), (now - 2*day, now - 2*day))
    
    # 2. Old Noise (10 days old, no keywords) -> DELETE
    with open(os.path.join(NEWS_DIR, "TEST_OldNoise.txt"), "w") as f: f.write("Market was flat yesterday.")
    os.utime(os.path.join(NEWS_DIR, "TEST_OldNoise.txt"), (now - 10*day, now - 10*day))
    
    # 3. Old Strategy (15 days old, has 'Outlook') -> KEEP
    with open(os.path.join(NEWS_DIR, "TEST_OldStrategy.txt"), "w") as f: f.write("The market Outlook is bullish.")
    os.utime(os.path.join(NEWS_DIR, "TEST_OldStrategy.txt"), (now - 15*day, now - 15*day))
    
    # 4. Ancient Strategy (40 days old, has 'Outlook') -> DELETE (Too old)
    with open(os.path.join(NEWS_DIR, "TEST_Ancient.txt"), "w") as f: f.write("Ancient Outlook.")
    os.utime(os.path.join(NEWS_DIR, "TEST_Ancient.txt"), (now - 40*day, now - 40*day))

    print("[TEST] Created dummy files.")

def verify_cleanup():
    setup_test_files()
    
    print("\n[TEST] Running Cleanup...")
    cleanup_old_news()
    
    files = os.listdir(NEWS_DIR)
    
    print("\n[TEST] Results:")
    
    if "TEST_Fresh.txt" in files: print("[OK] Fresh File: Kept")
    else: print("[FAIL] Fresh File: DELETED (Error)")
    
    if "TEST_OldNoise.txt" not in files: print("[OK] Old Noise: Deleted")
    else: print("[FAIL] Old Noise: KEPT (Error)")
    
    if "TEST_OldStrategy.txt" in files: print("[OK] Old Strategy: Kept")
    else: print("[FAIL] Old Strategy: DELETED (Error)")
    
    if "TEST_Ancient.txt" not in files: print("[OK] Ancient File: Deleted")
    else: print("[FAIL] Ancient File: KEPT (Error)")
    
    # Cleanup Test Junk
    for f in files:
        if f.startswith("TEST_"):
            try: os.remove(os.path.join(NEWS_DIR, f))
            except: pass

if __name__ == "__main__":
    verify_cleanup()
