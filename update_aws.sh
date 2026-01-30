#!/bin/bash

# SOVEREIGN TRADING BOT - UPDATE SCRIPT
# Run this on your AWS Server when you want to apply changes you made on your Laptop.

echo "=================================================="
echo "   SOVEREIGN BOT - SYSTEM UPDATE SEQUENCE"
echo "=================================================="

# 1. Go to Repo
cd Sovereign-trading-Bot---Antigravity || exit

# 2. Pull Latest Code
echo "[1/3] Pulling from GitHub..."
git reset --hard HEAD
git pull origin main

# 3. Update Dependencies (Just in case)
echo "[2/3] Checking for new libraries..."
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart the Bot
echo "[3/3] Restarting Neural Engine..."
pm2 restart sovereign-bot

echo "=================================================="
echo "   UPDATE COMPLETE. SYSTEMS GREEN."
echo "=================================================="
pm2 status
