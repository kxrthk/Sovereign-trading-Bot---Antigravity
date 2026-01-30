# Sovereign Bot - Mobile Access Enabler
# Run this script as Administrator to allow phone connections

Write-Host "Setting up Firewall Rules for Sovereign Bot..." -ForegroundColor Cyan

$port = 8000

# Check if rule exists
$rule = Get-NetFirewallRule -DisplayName "SovereignBot-Dashboard" -ErrorAction SilentlyContinue

if ($rule) {
    Write-Host "Rule already exists. Removing old rule..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "SovereignBot-Dashboard"
}

# Create new rule
try {
    New-NetFirewallRule -DisplayName "SovereignBot-Dashboard" `
                        -Direction Inbound `
                        -LocalPort $port `
                        -Protocol TCP `
                        -Action Allow `
                        -Profile Private,Public,Domain
    
    Write-Host "Success! Firewall opened on Port $port." -ForegroundColor Green
    Write-Host "You should now be able to connect via QR Code." -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to create rule. Please run this script as Administrator." -ForegroundColor Red
}

Write-Host "Press any key to exit..."
$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
