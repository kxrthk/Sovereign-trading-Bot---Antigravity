import subprocess
import time
import os
import sys
import webbrowser

def start_dashboard():
    print("Initializing Mission Control...")
    
    # 1. Start Backend
    print("Starting Neural Link (Backend)...")
    backend = subprocess.Popen(
        [sys.executable, "dashboard_server.py"],
        cwd=os.getcwd(),
        shell=True
    )
    
    # 2. Start Frontend
    print("Launching Visual Interface (Frontend)...")
    frontend_dir = os.path.join(os.getcwd(), "dashboard")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )
    
    print("Waiting for systems to sync...")
    time.sleep(5)
    
    print("Mission Control ONLINE.")
    print("Access at: http://localhost:5173")
    try:
        webbrowser.open("http://localhost:5173")
    except:
        pass
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Mission Control...")
        backend.terminate()
        frontend.terminate()
        sys.exit(0)

if __name__ == "__main__":
    start_dashboard()
