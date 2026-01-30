@echo off
TITLE Sovereign Trading Bot - THE SINGULARITY
COLOR 0A
CLS

ECHO ========================================================
ECHO    SOVEREIGN TRADING BOT (v56 - Deep Research Edition)
ECHO ========================================================
ECHO.
ECHO [1/3] Initializing Neural Network...
python check_models.py
ECHO.
ECHO [2/3] Scouting Breaking News...
python news_scout.py
ECHO.
ECHO [3/3] Launching Dashboard Server...
ECHO.
ECHO    --------------------------------------------------------
ECHO    [LOCAL COMMAND]  http://localhost:8000  (Fastest)
ECHO    [CLOUD COMMAND]  https://sovereign-trading-bot-antigravity.vercel.app
ECHO    --------------------------------------------------------
ECHO.
python start_dashboard.py
PAUSE
EXIT
