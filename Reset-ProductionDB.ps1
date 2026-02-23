# Production Database Reset - PowerShell Version
# Run this if you have SSH access to your VPS from Windows

Write-Host "=========================================================="
Write-Host "  TRADING NEXUS - DATABASE RESET (PowerShell)"  -ForegroundColor Cyan
Write-Host "=========================================================="
Write-Host ""

# VPS connection details
$VPS_IP = "72.62.228.112"
$VPS_USER = "root"  # Change if different

Write-Host "This script will SSH to your VPS and reset the database" -ForegroundColor Yellow
Write-Host "VPS: $VPS_USER@$VPS_IP" -ForegroundColor White
Write-Host ""
Write-Host "WARNING: This will DELETE all data!" -ForegroundColor Red
Write-Host "Press Ctrl+C to cancel, or any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Connecting to VPS..." -ForegroundColor Cyan

# Commands to run on VPS
$commands = @"
echo 'Stopping backend...'
docker stop trading-nexus-backend-1 || true

echo 'Resetting database...'
docker exec trading-nexus-db-1 psql -U postgres -c 'DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;'

echo 'Starting backend (migrations will run)...'
docker start trading-nexus-backend-1

echo 'Waiting 30 seconds for startup...'
sleep 30

echo 'Checking migrations...'
docker logs trading-nexus-backend-1 --tail 50 | grep -i migration

echo 'Verifying users...'
docker exec trading-nexus-db-1 psql -U postgres -d trading_terminal -c 'SELECT user_no, mobile, role FROM users ORDER BY user_no;'

echo ''
echo '✓ Database reset complete!'
echo 'Login at: https://tradingnexus.pro'
echo 'Credentials: 9999999999 / admin123'
"@

# Execute via SSH
ssh "$VPS_USER@$VPS_IP" $commands

Write-Host ""
Write-Host "=========================================================="
Write-Host "  ✓ COMPLETE!" -ForegroundColor Green
Write-Host "=========================================================="
Write-Host ""
Write-Host "Test your application at: https://tradingnexus.pro" -ForegroundColor Cyan
Write-Host "Default login: 9999999999 / admin123" -ForegroundColor Cyan
