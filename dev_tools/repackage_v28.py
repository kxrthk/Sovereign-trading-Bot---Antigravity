import shutil
import os
import glob

SOURCE_DIR = os.getcwd()
RELEASE_DIR = os.path.join(SOURCE_DIR, "release_v28_visionary")
ZIP_NAME = "SovereignBot_V28_TheVisionary"

def copy_files():
    print(f"[PACKAGER] Preparing Release in: {RELEASE_DIR}")
    
    # 1. Ensure Directory Exists (but preserve dashboard if it's there to save time)
    if not os.path.exists(RELEASE_DIR):
        os.makedirs(RELEASE_DIR)

    # 2. Copy Root Files
    files_to_copy = []
    files_to_copy.extend(glob.glob("*.py"))
    files_to_copy.extend(glob.glob("*.txt"))
    files_to_copy.extend(glob.glob("*.bat"))
    files_to_copy.extend(glob.glob("*.csv"))
    files_to_copy.append("Dockerfile")
    
    for f in files_to_copy:
        if os.path.isfile(f):
            shutil.copy2(f, os.path.join(RELEASE_DIR, f))
            print(f"   -> Copied {f}")

    # 3. Copy Directories (Memories)
    if os.path.exists("memories"):
        target_mem = os.path.join(RELEASE_DIR, "memories")
        if os.path.exists(target_mem): shutil.rmtree(target_mem)
        shutil.copytree("memories", target_mem)
        print("   -> Copied memories/")

    # 4. Create .env
    env_path = os.path.join(RELEASE_DIR, ".env")
    with open(env_path, "w") as f:
        f.write("GEMINI_API_KEY=PASTE_YOUR_AI_KEY_HERE")
    print("   -> Created .env")

    # 5. Zip It
    print("[PACKAGER] Zipping...")
    if os.path.exists(ZIP_NAME + ".zip"):
        os.remove(ZIP_NAME + ".zip")
        
    shutil.make_archive(ZIP_NAME, 'zip', RELEASE_DIR)
    print(f"[SUCCESS] Created {ZIP_NAME}.zip")

if __name__ == "__main__":
    try:
        copy_files()
    except Exception as e:
        print(f"[ERROR] {e}")
