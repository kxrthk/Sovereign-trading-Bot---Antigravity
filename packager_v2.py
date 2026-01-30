import shutil
import os
import datetime

def make_archive_exclude(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    
    print(f"Zipping {source} to {destination}...")
    
    shutil.make_archive(name, format, source)
    shutil.move('%s.%s'%(name,format), destination)

def zip_project():
    # Name with Timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    # Reduced length name to assist with extraction paths
    zip_name = f"Bot_v56_{timestamp}.zip"
    
    # Current Directory
    source_dir = os.getcwd()
    
    # Create a temporary directory to copy allowed files (to handle exclusion easily)
    # Actually, shutil.make_archive doesn't support easy exclusion of sub-sub-folders cleanly without a custom function.
    # So we'll use a zipfile module with a filter.
    
    import zipfile
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude node_modules and .git and __pycache__
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'dist', 'build']]
            
            for file in files:
                if file == zip_name: continue # Don't zip self
                if file.endswith(".zip"): continue
                
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source_dir)
                
                print(f"Adding: {arcname}")
                zipf.write(file_path, arcname)
                
    print(f"\n[SUCCESS] Project archived => {zip_name}")
    print(f"Location: {os.path.join(source_dir, zip_name)}")

if __name__ == "__main__":
    zip_project()
