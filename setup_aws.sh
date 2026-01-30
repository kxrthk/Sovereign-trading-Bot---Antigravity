#!/bin/bash

# SOVEREIGN TRADING BOT - AWS SETUP SCRIPT
# Run this on a fresh Ubuntu 22.04/24.04 Server

echo "=================================================="
echo "   SOVEREIGN BOT - CLOUD INITIATION SEQUENCE"
echo "=================================================="

# 1. Update System
echo "[1/5] Updating System Packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git unzip

# 2. Install Node.js (for PM2)
echo "[2/5] Installing Node.js & PM2..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# 3. Clone Repository (If not already present)
# Note: User must provide GITHUB_TOKEN or use Public Repo
if [ ! -d "Sovereign-trading-Bot---Antigravity" ]; then
    echo "[3/5] Cloning Repository..."
    git clone https://github.com/kxrthk/Sovereign-trading-Bot---Antigravity.git
else
    echo "[3/5] Repo already exists. Pulling latest..."
    cd Sovereign-trading-Bot---Antigravity
    git pull
    cd ..
fi

# 4. Setup Python Environment
echo "[4/5] Setting up Python Environment..."
cd Sovereign-trading-Bot---Antigravity
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Final Instructions
echo "=================================================="
echo "   SETUP COMPLETED SUCCESSFULLY"
echo "=================================================="
echo "Next Steps:"
echo "1. Upload your .env file to this folder."
echo "2. Run: pm2 start ecosystem.config.js"
echo "   (Or: pm2 start dashboard_server.py --interpreter ./venv/bin/python)"
echo "=================================================="
