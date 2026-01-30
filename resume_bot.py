import os

def resume_systems():
    if os.path.exists("STOP.flag"):
        os.remove("STOP.flag")
        print("[OK] SYSTEMS RESTORED. PLEASE RESTART AUTO-PILOT.")
    else:
        print("[INFO] No Stop Flag found. Systems are clear.")

if __name__ == "__main__":
    resume_systems()
