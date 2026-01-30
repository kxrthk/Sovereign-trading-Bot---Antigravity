import os
from crypto_vault import encrypt_secret
from dotenv import dotenv_values

ENV_PATH = r"C:\Users\sudha\sovereign_secrets.env"
KEYS_TO_ENCRYPT = [
    "WEB_PASSWORD",
    "GEMINI_API_KEY",
    "DHAN_CLIENT_ID",
    "DHAN_ACCESS_TOKEN",
    "DHAN_PASSWORD",
    "DHAN_TOTP_SECRET",
    "TELEGRAM_BOT_TOKEN"
]

def migrate():
    if not os.path.exists(ENV_PATH):
        print(f"[ERROR] Env file not found at {ENV_PATH}")
        return

    # Read existing
    config = dotenv_values(ENV_PATH)
    new_lines = []
    
    # Read file lines to preserve comments/structure if possible, 
    # but dotenv_values is safer for parsing. 
    # Let's simple re-write for now to ensure correctness.
    
    with open(ENV_PATH, 'r') as f:
        lines = f.readlines()
        
    final_lines = []
    changes_made = 0
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            final_lines.append(line)
            continue
            
        key_part = line.split('=')[0].strip()
        
        # Check if this line is one of our targets
        if key_part in KEYS_TO_ENCRYPT:
            # Get current value from parsed config (handles quotes etc)
            current_val = config.get(key_part)
            
            if current_val and not current_val.startswith("ENC:"):
                print(f"[ENCRYPTING] {key_part}...")
                cipher = encrypt_secret(current_val)
                final_lines.append(f"{key_part}=ENC:{cipher}\n")
                changes_made += 1
            else:
                final_lines.append(line) # Already encrypted or empty
        else:
            final_lines.append(line)
            
    if changes_made > 0:
        with open(ENV_PATH, 'w') as f:
            f.writelines(final_lines)
        print(f"[SUCCESS] Encrypted {changes_made} secrets in {ENV_PATH}")
    else:
        print("[INFO] No unencrypted secrets found.")

if __name__ == "__main__":
    migrate()
