import os

TARGET_DIR = "dashboard/src"
SEARCH_STR = "http://localhost:8000"
REPLACE_STR = "" # Relative path

def refactor_frontend():
    print(f"Refactoring Frontend in {TARGET_DIR}...")
    count = 0
    
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".jsx") or file.endswith(".js"):
                path = os.path.join(root, file)
                
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if SEARCH_STR in content:
                    print(f"Updating: {file}")
                    new_content = content.replace(SEARCH_STR, REPLACE_STR)
                    
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    count += 1
    
    print(f"[OK] Refactored {count} files to use relative paths.")

if __name__ == "__main__":
    refactor_frontend()
