@echo off
TITLE Setup Auto-Start (Admin Required)
CLS

ECHO ===================================================
ECHO   SETTING UP AUTO-STARTUP (ADMIN REQUIRED)
ECHO ===================================================
ECHO.
ECHO [!] We need Administrator rights to add the Scheduled Task.
ECHO [!] A popup will ask for permission. Click YES.
ECHO.

:: PowerShell command to run the python script as Administrator
powershell -Command "Start-Process python -ArgumentList 'scheduler_setup.py' -Verb RunAs"

ECHO.
ECHO [INFO] Request sent. If you clicked YES, tasks are added.
ECHO [INFO] You can verify by running: schtasks /Query /TN SovereignBot_Main
ECHO.
PAUSE
