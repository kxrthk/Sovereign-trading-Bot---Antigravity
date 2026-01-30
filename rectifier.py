import os
import sys
import time
import subprocess
import psutil
import requests
import json
from datetime import datetime

# Component Imports (Integrity Checks)
try:
    import librarian
    import oracle
    from council import Council
    from market_regime import get_market_regime
except ImportError as e:
    print(f"[CRITICAL] Import Failed: {e}")

class SystemDoctor:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "status": "HEALTHY",
            "checks": []
        }
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(self.root_dir, "system_health.log")

    def log(self, message):
        print(message)
        with open(self.log_file, "a") as f:
            f.write(f"[{datetime.now()}] {message}\n")

    def check_process(self, script_name):
        """Checks if a python script is running."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and script_name in ' '.join(proc.info['cmdline']):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def heal_process(self, script_name, launch_cmd):
        """Attempts to restart a dead process."""
        self.log(f"[HEAL] [+] Attempting to restart {script_name}...")
        try:
            # Launch in new console to detach
            subprocess.Popen(launch_cmd, shell=True, cwd=self.root_dir)
            time.sleep(5) # Wait for spin up
            if self.check_process(script_name):
                self.log(f"[HEAL] [OK] {script_name} successfully revived.")
                return True
            else:
                self.log(f"[HEAL] [FAIL] Failed to revive {script_name}.")
                return False
        except Exception as e:
            self.log(f"[HEAL] [ERROR] Error launching {script_name}: {e}")
            return False

    def audit_swarm(self):
        """Checks if the Swarm Engine is active."""
        is_running = self.check_process("swarm_engine.py")
        status = "PASS" if is_running else "FAIL"
        
        self.log(f"[AUDIT] Swarm Engine: {status}")
        self.report["checks"].append({"component": "Swarm", "status": status})
        
        if not is_running:
            self.report["status"] = "DEGRADED"
            # Self-Healing
            self.heal_process("swarm_engine.py", "start cmd /k python swarm_engine.py")

    def audit_dashboard(self):
        """Checks if Dashboard Server is running and responding."""
        is_running = self.check_process("dashboard_server.py")
        api_ok = False
        
        if is_running:
            try:
                res = requests.get("http://localhost:8000/api/status", timeout=2)
                if res.status_code == 200:
                    api_ok = True
            except:
                pass
        
        status = "PASS" if (is_running and api_ok) else "FAIL"
        self.log(f"[AUDIT] Dashboard Backend: {status} (Process: {is_running}, API: {api_ok})")
        self.report["checks"].append({"component": "Dashboard", "status": status})
        
        if not is_running:
            self.report["status"] = "DEGRADED"
            self.heal_process("dashboard_server.py", "start cmd /k python dashboard_server.py")

    def audit_brain_integrity(self):
        """Simulates 'Council' and 'Oracle' thinking."""
        self.log("[AUDIT] Checking Neural Pathways (Import & Logic)...")
        
        # 1. Council
        try:
            c = Council()
            if len(c.shards) == 5:
                self.log("   -> [PASS] Council Assembled (5 Shards).")
            else:
                self.log("   -> [FAIL] Council Malformed.")
                self.report["status"] = "DEGRADED"
        except Exception as e:
            self.log(f"   -> [FAIL] Council Error: {e}")
            self.report["status"] = "DEGRADED"

        # 2. Oracle & Librarian
        try:
            # Quick Context Check
            regime = get_market_regime()
            self.log(f"   -> [PASS] Market Regime Identified: {regime}")
            
            # Librarian Check
            books = librarian.get_knowledge_base(regime=regime)
            if len(books) > 0:
                 self.log(f"   -> [PASS] Librarian retrieved {len(books)} context-aware papers.")
            else:
                 self.log("   -> [WARN] Library Empty or Offline.")
        except Exception as e:
            self.log(f"   -> [FAIL] Oracle/Librarian Error: {e}")
            self.report["status"] = "DEGRADED"

    def generate_prescriptions(self):
        """Writes suggestions to 'doctor_note.md'."""
        with open("doctor_note.md", "w") as f:
            f.write(f"# System Doctor Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"**Overall Status**: {self.report['status']}\n\n")
            f.write("## Component Checks\n")
            for check in self.report["checks"]:
                icon = "[OK]" if check["status"] == "PASS" else "[FAIL]"
                f.write(f"- {icon} **{check['component']}**: {check['status']}\n")
            
            if self.report["status"] != "HEALTHY":
                f.write("\n## Prescriptions (Action Required)\n")
                f.write("1. Check 'ai_error.log' for detailed stack traces.\n")
                f.write("2. Ensure 'start_dashboard.py' or 'swarm_engine.py' are not blocked by Firewall.\n")
                f.write("3. Verify Internet Connection for Market Data.\n")

    def run_full_scan(self):
        self.log("\n[DOCTOR] [+] STARTING FULL SYSTEM SCAN...")
        self.log("-----------------------------------------")
        
        self.audit_swarm()
        self.audit_dashboard()
        self.audit_brain_integrity()
        
        self.generate_prescriptions()
        self.log("-----------------------------------------")
        self.log(f"[DOCTOR] Scan Complete. Status: {self.report['status']}")
        
        return self.report["status"] == "HEALTHY"

if __name__ == "__main__":
    doc = SystemDoctor()
    doc.run_full_scan()
