import os

TARGET_DIR = "training_raw"
MAX_LEN = 50

def sanitize_directory(directory):
    print(f"Scanning {directory}...")
    if not os.path.exists(directory): return

    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        
        if os.path.isdir(path):
            sanitize_directory(path)
            continue
            
        if len(filename) > MAX_LEN:
            name, ext = os.path.splitext(filename)
            # Truncate to 40 chars + ext
            new_name = name[:40].replace(" ", "_") + "_TRUNC" + ext
            new_path = os.path.join(directory, new_name)
            
            print(f"[RENAME] {filename} -> {new_name}")
            try:
                os.rename(path, new_path)
            except Exception as e:
                print(f"Error renaming {filename}: {e}")

if __name__ == "__main__":
    sanitize_directory(TARGET_DIR)
    # Also fix specific known massive file if safe
