import os
import json
import time
import os
import json
import time
from dotenv import load_dotenv
from google import genai

import config # Use Central Config for Decryption

# --- CLIENT INIT ---
api_key = config.GEMINI_API_KEY
client = None
if api_key:
    if api_key.startswith("ENC:"):
         from crypto_vault import decrypt_secret
         api_key = decrypt_secret(api_key[4:])
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[LIBRARIAN] Client Init Error: {e}")

# CONFIGURATION
# Supports multiple formats for robust knowledge base
KNOWLEDGE_DIR = "training_raw"     
LIBRARY_CARD = "library_card.json" # Local registry file

def _load_registry():
    """Reads the local record of uploaded files."""
    if os.path.exists(LIBRARY_CARD):
        try:
            with open(LIBRARY_CARD, 'r') as f:
                return json.load(f)
        except:
             return {}
    return {}

def _save_registry(registry):
    """Saves the record of uploaded files."""
    with open(LIBRARY_CARD, 'w') as f:
        json.dump(registry, f, indent=4)

def get_knowledge_base(tags=None, regime=None):
    """
    The Master Function.
    1. Scans your 'training_raw' folder.
    2. Checks if files are already online and valid.
    3. Uploads ONLY new or expired files.
    4. Returns a list of Gemini File objects ready for the AI.
    """
    # Using simple bracket tags instead of emojis for Windows safety
    print(f"[LIBRARIAN] Opening vault '{KNOWLEDGE_DIR}'...")
    
    if not api_key:
        print("[ERROR] API Key Missing. Please run Setup_Secrets.bat")
        return []

    registry = _load_registry()
    active_files = []
    files_to_update = False

    # 1. Check if folder exists
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"[ERROR] Folder '{KNOWLEDGE_DIR}' missing.")
        return []

    # 2. Scan local documents (PDFs, PPTs, TXT) - RECURSIVE
    supported = ('.pdf', '.ppt', '.pptx', '.txt', '.csv', '.md')
    local_docs = []
    
    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        for file in files:
            if file.lower().endswith(supported):
                # We store relative path to keep unique ID if name duplicates in folders
                # But Librarian ID logic uses filename. 
                # For simplicity, we just add the filename, assuming unique names or flattening.
                # Actually, let's keep it flattening for now to avoid registry breaking changes.
                local_docs.append(file)
                # Note: This logic assumes flattened filenames in the registry for now.
                # To support deep structure, we might need full path handling, 
                # but 'genai.upload_file' takes the path correctly below.
                
                # We need to construct the full path loop below differently if we use os.walk here.
                pass

    # Re-implmenting the loop below to handle paths correctly
    # Let's verify how step 3 uses 'filename'. 
    # It does: file_path = os.path.join(KNOWLEDGE_DIR, filename)
    # This BREAKS if filename is in a subdir.
    
    # CORRECT APPROACH: Get full relative paths
    local_docs_map = {} # filename -> full_path
    
    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        for file in files:
            if file.lower().endswith(supported):
                local_docs_map[file] = os.path.join(root, file)
                
    local_docs = list(local_docs_map.keys())
    
    if not local_docs:
        print("[WARN] EMPTY VAULT: No supported docs found.")
        return []

    print(f"   Found {len(local_docs)} local research papers/docs.")

    # 3. Process each file
    for filename in local_docs:
        # Resolve full path from map (if available) or default (backward compat)
        if 'local_docs_map' in locals() and filename in local_docs_map:
            file_path = local_docs_map[filename]
        else:
            file_path = os.path.join(KNOWLEDGE_DIR, filename)
        
        # Check if we have a record of this file
        if filename in registry:
            file_info = registry[filename]
            uri = file_info.get('uri')
            
            # VERIFY: Is the file still alive on Google's server?
            try:
                # v2 SDK: client.files.get(name=...)
                remote_file = client.files.get(name=uri)
                
                # Check state (ACTIVE means ready, PROCESSING means wait)
                # v2 SDK: state is an enum? or string? usually remote_file.state is enough comparison
                # Safest to print and check, but standard is similar.
                if str(remote_file.state) == "State.ACTIVE" or str(remote_file.state) == "ACTIVE":
                    print(f"   [CACHE] Using Cached: {filename}")
                    active_files.append(remote_file)
                    continue # Skip upload!
                elif "FAILED" in str(remote_file.state):
                    print(f"   [FAIL] Cached file failed. Re-uploading: {filename}")
            except Exception:
                print(f"   [EXPIRED] Cache expired for {filename}. Re-uploading...")
        
        # 4. Upload (If new or expired)
        try:
            print(f"   [UP] Uploading New: {filename}...", end=" ")
            # v2 SDK: client.files.upload
            uploaded_file = client.files.upload(file=file_path, config={'display_name': filename})
            
            # Wait for processing (Critical for big PDFs)
            while "PROCESSING" in str(uploaded_file.state):
                print(".", end="")
                time.sleep(1)
                uploaded_file = client.files.get(name=uploaded_file.name)
                
            if "ACTIVE" in str(uploaded_file.state):
                print(" Ready.")
                active_files.append(uploaded_file)
                
                # Update Registry
                registry[filename] = {
                    "uri": uploaded_file.name,
                    "upload_time": time.time()
                }
                files_to_update = True
            else:
                print(f" FAILED (State: {uploaded_file.state.name})")
                
        except Exception as e:
            print(f"[ERROR] {e}")

    # 5. Save changes to Library Card
    if files_to_update:
        _save_registry(registry)
        print("[SAVE] Library Card Updated.")

    print(f"[READY] KNOWLEDGE BASE: {len(active_files)} Papers Loaded.")
    
    # 6. Filtering Logic (Context Switching)
    if not tags and not regime:
        return active_files

    # A. Regime Mapping
    if regime:
        regime_map = {
            "CRASH": ["Risk", "Macro", "Psychology"],
            "TREND": ["Strategy", "Technical", "Momentum"],
            "CHOP":  ["Psychology", "Range", "Oscillators"],
            "UNKNOWN": [] # Load All
        }
        tags = regime_map.get(regime, [])
        if tags:
             print(f"[LIBRARIAN] Context Switch: Loading papers for {regime} ({tags})...")

    # B. Tag Filtering
    if tags:
        filtered_files = []
        for f in active_files:
            fname = f.display_name.lower()
            # Simple keyword matching
            # e.g. "Risk" matches "Risk_Management.pdf"
            for tag in tags:
                if tag.lower() in fname:
                    filtered_files.append(f)
                    break 
        
        # If filter kills everything, return all as fallback
        if not filtered_files:
             print(f"[WARN] No papers found for tags {tags}. Loading Grid (All).")
             return active_files
             
        print(f"[LIBRARIAN] Focused Knowledge: {len(filtered_files)} papers selected.")
        return filtered_files

    return active_files

# --- CLAUDE SUPPORT (TEXT EXTRACTION) ---
def get_knowledge_text(tags=None):
    """
    Extracts RAW TEXT from local documents for Claude.
    Unlike Gemini, we process text locally.
    """
    import pypdf
    context_text = ""
    
    print("[LIBRARIAN] 📜 Extracting Text for Claude...")
    
    local_docs_map = {}
    supported = ('.pdf', '.txt', '.md', '.csv')
    
    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        for file in files:
            if file.lower().endswith(supported):
                local_docs_map[file] = os.path.join(root, file)
                
    for filename, path in local_docs_map.items():
        try:
            content = ""
            if filename.lower().endswith(".pdf"):
                reader = pypdf.PdfReader(path)
                for page in reader.pages:
                    content += page.extract_text() + "\n"
            else:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            
            # Append nicely
            context_text += f"\n\n--- DOCUMENT: {filename} ---\n{content[:5000]} [TRUNCATED]\n" # Truncate to save tokens for now
            print(f"   [TEXT] Read {filename} ({len(content)} chars)")
            
        except Exception as e:
            print(f"   [ERR] Could not read {filename}: {e}")
            
    return context_text

    return context_text

def ingest_daily_briefing():
    """
    RAG AUTOMATION: Scans 'training_raw/news' for today's files, 
    compiles them into a single 'DAILY_BRIEF_{Date}.md', 
    and uploads it to Gemini.
    """
    today_str = time.strftime("%Y-%m-%d")
    brief_filename = f"DAILY_INTELLIGENCE_BRIEF_{today_str}.md"
    brief_path = os.path.join(KNOWLEDGE_DIR, brief_filename)
    
    # Check if already exists (Don't redo work for 5 mins)
    if os.path.exists(brief_path):
        print("[LIBRARIAN] Daily Brief already exists. Checking for updates...")
        # (For now we skip overwrite to save tokens, user can manual delete if needed)
        pass

    news_dir = os.path.join(KNOWLEDGE_DIR, "news")
    if not os.path.exists(news_dir): return

    print(f"[LIBRARIAN] Compiling Daily Intelligence Dossier: {brief_filename}...")
    
    compiled_text = f"# SOVEREIGN TRADE INTELLIGENCE - {today_str}\n\n"
    article_count = 0
    
    for filename in os.listdir(news_dir):
        if filename.endswith(".txt"):
            # Format: NEWS_{Source}_{Tags}_{Title}.txt
            try:
                with open(os.path.join(news_dir, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Parse Tags from filename or content? Content has it.
                compiled_text += f"\n## ARTICLE {article_count+1}: {filename}\n{content}\n"
                compiled_text += "-"*50 + "\n"
                article_count += 1
            except Exception as e:
                print(f"   [ERR] Skipping {filename}: {e}")
                
    if article_count == 0:
        print("[LIBRARIAN] No news found to compile.")
        return

    # SAVE LOCAL MASTER COPY
    with open(brief_path, "w", encoding="utf-8") as f:
        f.write(compiled_text)
        
    print(f"[LIBRARIAN] Dossier Compiled ({article_count} reports). Uploading to Brain...")
    
    # TRIGGER UPLOAD via get_knowledge_base (It scans root folder, finds new .md, and uploads)
    get_knowledge_base()

if __name__ == "__main__":
    # Test Context Switch
    print("Testing Librarian Logic...")
    # get_knowledge_base(regime="CRASH")
    # ingest_daily_briefing() # Test RAG
    print(get_knowledge_text())

