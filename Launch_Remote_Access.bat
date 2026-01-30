@echo off
TITLE Sovereign Bot - SECURE REMOTE TUNNEL (Ngrok)
CLS
ECHO ========================================================
ECHO       SOVEREIGN BOT - SECURE REMOTE ACCESS (HTTPS)
ECHO ========================================================
ECHO.
ECHO [INFO] This script opens a secure tunnel to your bot.
ECHO [INFO] You will get a link like "https://xxxx.ngrok-free.app"
ECHO [INFO] Use that link on your mobile to access the dashboard.
ECHO.
ECHO [IMPORTANT] If this is your first time, you may need to login.
ECHO [TIP]  Sign up at https://dashboard.ngrok.com/signup for a free token.
ECHO        Then run: ngrok config add-authtoken <TOKEN>
ECHO.
ECHO [STARTING TUNNEL...]
ECHO.
call "C:\Users\sudha\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http --domain=densimetrically-nontortuous-emerson.ngrok-free.dev 8000
PAUSE
