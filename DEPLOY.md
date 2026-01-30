# Deployment Guide: Operation Sovereign

This guide covers how to deploy the Sovereign Trading Bot to a remote environment (VPS or Cloud) while maintaining security.

> [!WARNING]
> **Security Notice**: Never expose your bot to the public internet without **Basic Auth** (Enabled) or a VPN.
> The bot controls real money (or simulates it). Treat it like a bank vault.

## 1. Prerequisites

- **VPS**: A Windows or Linux server (e.g., AWS, DigitalOcean, or a spare PC).
- **Python 3.10+**: Installed and added to PATH.
- **Git**: To pull the latest code.
- **Dhan Account**: API Credentials ready in `.env`.

## 2. Configuration Setup

1. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your secrets.
   ```ini
   WEB_USERNAME=admin
   WEB_PASSWORD=your_strong_password_here
   ```
   > [!IMPORTANT]
   > Change the default `admin/sovereign` password immediately in your `.env` file!

2. **Dhan Credentials**:
   Ensure `DHAN_CLIENT_ID` and `DHAN_ACCESS_TOKEN` are populated.

## 3. Remote Access (The Easy Way: Ngrok)

If you are running this on a home PC but want to access it from mobile/laptop elsewhere:

1. **Install Ngrok**: [Download Here](https://ngrok.com/download)
2. **Start the Bot**:
   Run `Launch_Sovereign_Bot.bat`
3. **Expose the Dashboard**:
   ```bash
   ngrok http 8000 --basic-auth="admin:your_password"
   ```
   *Note: Since we added Internal Basic Auth to the bot, you strictly don't need Ngrok's auth, but Double Auth is better.*

## 4. VPS Deployment (The Pro Way)

1. **Upload Code**:
   Use SCP or Git to get your `sovereign_trading_bot` folder to the VPS.
   
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run as Service**:
   Use `systemd` (Linux) or Task Scheduler (Windows) to keep `Launch_Sovereign_Bot.bat` running.

4. **Accessing the Dashboard**:
   - **Option A (SSH Tunnel - Most Secure)**:
     ```bash
     ssh -L 8000:localhost:8000 user@your_vps_ip
     ```
     Then open `http://localhost:8000` on your local machine.

   - **Option B (Public IP)**:
     - Allow port 8000 in Firewall.
     - Access `http://your_vps_ip:8000`.
     - **Constraint**: You MUST rely on the Bot's Internal Basic Auth.

## 5. Mobile Access

1. Open your browser on Android/iOS.
2. Navigate to your Ngrok URL or VPS IP.
3. Login when prompted.
4. **Add to Home Screen**: The dashboard is PWA-ready. Tap "Add to Home Screen" for a native app feel.

## 6. Emergency Stop

If the bot goes rogue or you suspect a hack:
1. **Kill Switch**: Login to Dashboard -> Click "System Status" -> "Emergency Stop".
2. **Hard Stop**: SSH into server and run `python emergency_stop.py`.

---
*Verified on Windows 11 & Linux (Ubuntu 22.04)*
