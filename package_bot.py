import os
import zipfile
import datetime

def make_zipfile(output_filename, source_dir):
    print(f"Packaging {source_dir} into {output_filename}...")
    
    excludes = {
        'node_modules', '__pycache__', '.git', '.vscode', '.idea', 
        'dist', 'build', 'coverage', '.pytest_cache'
    }
    
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in excludes]
            
            for file in files:
                if file == os.path.basename(output_filename) or file.endswith('.zip'):
                    continue
                    
                file_path = os.path.join(root, file)
                # Archive name should be relative to source_dir
                arcname = os.path.relpath(file_path, source_dir)
                
                print(f"  Adding: {arcname}")
                zipf.write(file_path, arcname)
                
    print(f"\n[SUCCESS] Created {output_filename}")

if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_zip = f"SovereignBot_v55_AI_Journal_{timestamp}.zip"
    
    # Current Directory (Project Root)
    source = os.getcwd()
    
    make_zipfile(output_zip, source)
