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

---

## 💰 Cost & Future Proofing
**"Is it free forever?"**

### 1. AWS Free Tier
- **Duration**: 12 Months (usually).
- **Limit**: 750 hours/month of `t2.micro` or `t3.micro`.
- **After 12 Months**: Approx $8 - $10 USD / month.

### 2. The "Always Free" Alternative: Oracle Cloud
If you want **$0 Forever**, Oracle Cloud offers an "Always Free" tier (ARM Ampere instances).
- **Pros**: Stronger CPU (4 OCPU, 24GB RAM), Free forever.
- **Cons**: Slightly harder to sign up (verification is strict).
- **Migration**: The `update_aws.sh` script works there too (just install git/python).

### 3. Portability
Your bot is **100% Code**. It is not locked to AWS.
You can move it to:
- DigitalOcean ($4/mo)
- Google Cloud
- Your old laptop in a closet
- Raspberry Pi ($50 one-time)

**Recommendation**: Enjoy AWS for the first year. If the bot makes profit, $8/mo is negligible. If not, move to Oracle.
