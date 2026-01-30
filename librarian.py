import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

import config # Use Central Config for Decryption

api_key = config.GEMINI_API_KEY

if not api_key:
    # Fallback to local .env if persistent missing
    pass 

if api_key:
    genai.configure(api_key=api_key)

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
                # We interpret the URI name to get the file object
                # Usually uri is 'files/xxxx'
                remote_file = genai.get_file(uri)
                
                # Check state (ACTIVE means ready, PROCESSING means wait)
                if remote_file.state.name == "ACTIVE":
                    print(f"   [CACHE] Using Cached: {filename}")
                    active_files.append(remote_file)
                    continue # Skip upload!
                elif remote_file.state.name == "FAILED":
                    print(f"   [FAIL] Cached file failed. Re-uploading: {filename}")
            except Exception:
                print(f"   [EXPIRED] Cache expired for {filename}. Re-uploading...")
        
        # 4. Upload (If new or expired)
        try:
            print(f"   [UP] Uploading New: {filename}...", end=" ")
            uploaded_file = genai.upload_file(path=file_path, display_name=filename)
            
            # Wait for processing (Critical for big PDFs)
            while uploaded_file.state.name == "PROCESSING":
                print(".", end="")
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)
                
            if uploaded_file.state.name == "ACTIVE":
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

if __name__ == "__main__":
    # Test Context Switch
    print("Testing Librarian Logic...")
    # get_knowledge_base(regime="CRASH")
    print(get_knowledge_text())

