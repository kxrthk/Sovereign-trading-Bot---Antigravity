@echo off
TITLE MISSION CONTROL - LAUNCHER
COLOR 0A
CLS

ECHO ========================================================
ECHO      SOVEREIGN TRADING BOT - MISSION CONTROL
ECHO           "One Button to Rule Them All"
ECHO ========================================================
ECHO.
ECHO [1/2] Launching The Brain (Bot + Dashboard)...
start "Sovereign Brain" "Launch_Sovereign_Bot.bat"

ECHO [2/2] Opening Secure Tunnel (Remote Access)...
start "Sovereign Tunnel" "Launch_Remote_Access.bat"

ECHO.
ECHO [SUCCESS] All Systems Engaged.
ECHO.
ECHO You can minimize this window.
ECHO.
TIMEOUT /T 5 >NUL
EXIT
