@echo off
if not exist ".env" (
    echo GEMINI_API_KEY=PASTE_KEY_HERE > .env
)
notepad .env
