# ☁️ Operation: Sky Castle (AWS Deployment Guide)

This guide will help you move your "Brain" from your Laptop to the AWS Cloud.
**Goal**: Run the bot 24/7 without your laptop being on.

## Prerequisites
1.  **AWS Account Active** (Verification Complete).
2.  **EC2 Instance Running** (Ubuntu 24.04).
3.  **Key Pair File** (`sovereign-key.pem`) downloaded to your computer.

---

## Step 1: Connect to the Server (SSH)
On your laptop, open a terminal (PowerShell or Git Bash) where your `.pem` key is.

```bash
# Set permissions (Linux/Mac only, skip on Windows)
chmod 400 "sovereign-key.pem"

# Connect (Replace 1.2.3.4 with your AWS Public IP)
ssh -i "sovereign-key.pem" ubuntu@1.2.3.4
```

## Step 2: Install the Brain
Once inside the black screen (AWS Terminal), run these commands:

```bash
# 1. Download the Setup Script
curl -O https://raw.githubusercontent.com/kxrthk/Sovereign-trading-Bot---Antigravity/main/setup_aws.sh

# 2. Make it Executable
chmod +x setup_aws.sh

# 3. Run It
./setup_aws.sh
```

## Step 3: Activate the Secrets
You need to copy your API Keys (`.env`) to the server.
Since you can't easily drag-and-drop, we will create the file manually.

1.  Type: `nano .env`
2.  Open `.env` on your **Laptop**, copy all text.
3.  Paste it into the AWS Terminal (Right-click usually pastes).
4.  Save: `Ctrl + O`, `Enter`, `Ctrl + X`.

## Step 4: ignite the Engine
We use `pm2` to keep the bot running forever.

```bash
# Enter the folder
cd Sovereign-trading-Bot---Antigravity

# Start the Bot
pm2 start dashboard_server.py --name "sovereign-bot" --interpreter python3

# Save the state (so it restarts if server reboots)
pm2 save
pm2 startup
```

## Step 5: Update the Frontend
1.  Go to Vercel Dashboard.
2.  Go to **Settings** -> **Environment Variables**.
3.  Update `VITE_API_BASE_URL` (or `NEXT_PUBLIC_API_URL` depending on setup) to:
    `http://1.2.3.4:8000` (Your AWS IP).
4.  Redeploy Vercel.

**MISSION COMPLETE.** 🚀
The bot is now creating its own destiny in the cloud.
