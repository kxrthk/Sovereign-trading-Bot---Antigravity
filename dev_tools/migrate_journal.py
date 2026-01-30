import pandas as pd
import os
import shutil

JOURNAL_PATH = "trading_journal.csv"
BACKUP_PATH = "trading_journal_backup.csv"

def migrate():
    print("--- Journal Migration Tool ---")
    if not os.path.exists(JOURNAL_PATH):
        print("No journal found. Nothing to migrate.")
        return

    # Backup
    shutil.copy(JOURNAL_PATH, BACKUP_PATH)
    print(f"Backed up to {BACKUP_PATH}")

    # Read
    # Use simple reading, might have no headers or different length rows
    try:
        df = pd.read_csv(JOURNAL_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if 'oracle_confidence' in df.columns:
        print("Column 'oracle_confidence' already exists. Migration skipped.")
        return

    print("Adding 'oracle_confidence' column...")
    df['oracle_confidence'] = 0.0 # Default value
    
    # Save back
    df.to_csv(JOURNAL_PATH, index=False)
    print("✅ Migration Complete.")

if __name__ == "__main__":
    migrate()
