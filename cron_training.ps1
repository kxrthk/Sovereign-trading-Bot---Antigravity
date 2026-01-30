# cron_training.ps1
# Automates the "Training Dojo" for the Sovereign Trading Bot
# Recommendation: Schedule this to run every Sunday night via Windows Task Scheduler.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "[CRON] Starting Weekly Retraining..." -ForegroundColor Cyan

# 0. Scout for Fresh Fundamental Data (Universal Mode)
Write-Host "[CRON] Scouting Fundamentals for ALL Configured Assets..." -ForegroundColor Yellow
python fundamental_scout.py --all

# 0.5 Deep Research (News Wire)
Write-Host "[CRON] Tapping Global News Wires (Deep Research)..." -ForegroundColor Yellow
python news_scout.py

# 1. Activate Environment (if needed)
# Assuming python is in PATH or using standard python
python training_dojo.py --auto

if ($LASTEXITCODE -eq 0) {
    Write-Host "[CRON] Retraining Complete. Wisdom Logged." -ForegroundColor Green
}
else {
    Write-Host "[CRON] Retraining Failed!" -ForegroundColor Red
}

Start-Sleep -Seconds 5
