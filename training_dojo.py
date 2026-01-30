import sys
import argparse
from datetime import datetime
import pandas as pd
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv
import librarian  # Imports the librarian module

# --- PERSISTENT SECRETS LOADING ---
load_dotenv()
user_secrets_path = os.path.join(os.path.expanduser("~"), "sovereign_secrets.env")
if os.path.exists(user_secrets_path):
    load_dotenv(user_secrets_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key Missing. Please run Setup_Secrets.bat")
    exit()

genai.configure(api_key=api_key)
# Fallback logic handled by the user request to use 1.5-flash for context window
model = genai.GenerativeModel('gemini-2.0-flash') 

def start_training_session():
    # 1. Load the "Textbooks" from training_raw
    print("\n[DOJO] ENTERING THE DOJO...")
    textbooks = librarian.get_knowledge_base()
    
    if not textbooks:
        return

    # 2. Load Historical Data
    # For now, we try to grab the first CSV we find in memories/history since that exists
    history_dir = "memories/history"
    data_file = None
    
    if os.path.exists(history_dir):
        files = [f for f in os.listdir(history_dir) if f.endswith(".csv")]
        if files:
            data_file = os.path.join(history_dir, files[0])
    
    if not data_file or not os.path.exists(data_file):
        print("[ERR] STOCK DATA MISSING. Please run the bot once to download NIFTY data.")
        return
        
    print(f"[DATA] Loading Training Data from: {data_file}")
    print(f"[DATA] Loading Training Data from: {data_file}")
    df = pd.read_csv(data_file)
    
    # Ensure numeric types
    num_cols = ['Close', 'Adj Close', 'High', 'Low', 'Open']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    
    df = df.dropna() # Remove any bad conversions
    
    # 3. Argument Parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Run in automated mode (5 rounds, no input)")
    args = parser.parse_args()
    
    max_rounds = 5 if args.auto else 999
    rounds_played = 0
    training_log = []

    # 4. The Challenge Loop
    while rounds_played < max_rounds:
        rounds_played += 1
        print(f"\n[ROUND] NEW CHALLENGE ROUND ({rounds_played}/{max_rounds})")
        
        # Pick a random day (avoiding the very start/end)
        if len(df) < 60:
            print("Not enough data to train.")
            break
            
        random_idx = random.randint(50, len(df)-5)
        
        # Get the "Question" (Price Data)
        row = df.iloc[random_idx]
        
        # Get the "Answer Key" (Did price go up next day?)
        next_day = df.iloc[random_idx + 1]
        
        # Handle differing column names (yfinance cleanup)
        close_price = row.get('Close', row.get('Adj Close', 0))
        next_close = next_day.get('Close', next_day.get('Adj Close', 0))
        
        pct_move = ((next_close - close_price) / close_price) * 100
        result = "UP" if pct_move > 0 else "DOWN"
        
        print(f"[DATE] Index: {random_idx}")
        print(f"[PRICE] {close_price:.2f} (Next: {next_close:.2f})")
        
        # 4. Ask the AI (The Test)
        prompt = (
            f"You are a Sovereign Trading Bot. "
            f"Consult the attached {len(textbooks)} research papers in your context. "
            f"Current Market Data: Price {close_price:.2f}. "
            f"Based strictly on the risk management rules and chart patterns in these papers, "
            f"would you BUY or SELL here? "
            f"Cite the specific paper name and page number that justifies your decision."
        )
        
        print("[THINKING] AI is thinking (Reading 25+ papers)...")
        ai_response = ""
        try:
             # Pass the uploaded files (textbooks) + the prompt
             response = model.generate_content(textbooks + [prompt])
             ai_response = response.text
             print(f"\n[STRATEGY]:\n{ai_response[:200]}...") # Truncate for console if auto
        except Exception as e:
             print(f"[ERROR] AI Error: {e}")
             ai_response = f"Error: {e}"
        
        # 5. The Reality Check
        print("-" * 30)
        print(f"[REALITY] The stock went {result} ({pct_move:.2f}%)")
        
        # Log to list
        entry = f"## Round {rounds_played} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        entry += f"**Scenario**: Price {close_price:.2f} (Index {random_idx})\n"
        entry += f"**AI Thought**: {ai_response}\n"
        entry += f"**Reality**: {result} ({pct_move:.2f}%)\n"
        entry += "-"*20 + "\n"
        training_log.append(entry)

        if not args.auto:
            print("\n[Enter] Next Round | [q] Quit")
            user_input = input(">> ")
            if user_input.lower() == 'q':
                break
    
    if args.auto:
        # Save to file
        log_path = "memories/training_log.md"
        with open(log_path, "a") as f: # Append mode
            f.write("\n".join(training_log))
        print(f"\n[DOJO] Training Complete. Log saved to {log_path}")

if __name__ == "__main__":
    start_training_session()
