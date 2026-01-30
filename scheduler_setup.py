import os
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_scheduler():
    if not is_admin():
        # Re-run the program with admin rights
        print("[SETUP] Requesting Administrator Privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        return

    cwd = os.getcwd()
    print(f"[SETUP] Configuring Auto-Startup from: {cwd}")
    
    # 1. Main Bot (Dashboard + Brain)
    task_bot = "SovereignBot_Main"
    script_bot = os.path.join(cwd, "Launch_Sovereign_Bot.bat")
    
    cmd_bot = (
        f'schtasks /Create /F /TN "{task_bot}" '
        f'/TR "\'{script_bot}\'" '
        f'/SC ONLOGON '
        f'/RL HIGHEST'
    )
    
    print(f"\n--- Creating Task: {task_bot} ---")
    res_bot = os.system(cmd_bot)
    if res_bot == 0: print("[OK] Success")
    else: print("[FAIL] Failed")

    # 2. Remote Access (Ngrok)
    task_remote = "SovereignBot_Remote"
    script_remote = os.path.join(cwd, "Launch_Remote_Access.bat")
    
    cmd_remote = (
        f'schtasks /Create /F /TN "{task_remote}" '
        f'/TR "\'{script_remote}\'" '
        f'/SC ONLOGON '
        f'/RL HIGHEST'
    )
    
    print(f"\n--- Creating Task: {task_remote} ---")
    res_remote = os.system(cmd_remote)
    if res_remote == 0: print("[OK] Success")
    else: print("[FAIL] Failed")

    print("\n[INFO] Tasks scheduled. They will run automatically on next reboot.")
    input("Press Enter to Exit...")
