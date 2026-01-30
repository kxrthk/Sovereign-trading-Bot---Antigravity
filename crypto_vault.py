from cryptography.fernet import Fernet
import os
import sys

# Path to the Master Key (Should be kept offline ideally, but local for now)
KEY_FILE = "sovereign_master.key"

def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print(f"[VAULT] New Master Key Generated: {KEY_FILE}")
        # RESTRICT PERMISSION (Windows doesn't have chmod 600 easily, but logic stands)
        return key

def encrypt_secret(plain_text):
    key = load_or_create_key()
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

def decrypt_secret(cipher_text):
    key = load_or_create_key()
    f = Fernet(key)
    try:
        return f.decrypt(cipher_text.encode()).decode()
    except Exception as e:
        return "[DECRYPTION FAILED]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crypto_vault.py <secret_to_encrypt>")
    else:
        secret = sys.argv[1]
        encrypted = encrypt_secret(secret)
        print("\n--- ENCRYPTED SECRET ---")
        print(f"ENC:{encrypted}")
        print("------------------------")
        print("Copy the line above (including ENC:) into your .env file or config.")
