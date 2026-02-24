# Deep dive: Check if Tier-B initialization ran
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "TIER-B INITIALIZATION CHECK" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Find backend container
$findCmd = "docker ps --format '{{.Names}}' | grep 'backend-$APP_UUID'"
$backendContainer = ssh ${VPS_USER}@${VPS_HOST} $findCmd 2>$null

if (-not $backendContainer) {
    Write-Host "❌ Backend container not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Backend Container: $backendContainer`n" -ForegroundColor Green

# Check backend logs for Tier-B initialization
Write-Host "Checking startup logs for Tier-B initialization..." -ForegroundColor Yellow

$logsCmd = "docker logs $backendContainer 2>&1 | grep -i 'Tier-B\|initializing\|subscription map\|startup'"
ssh ${VPS_USER}@${VPS_HOST} $logsCmd | Select-Object -First 50

Write-Host "`nChecking for STARTUP_LOAD_TIER_B setting..." -ForegroundColor Yellow

$findEnvCmd = "docker inspect $backendContainer | grep -i 'STARTUP_LOAD_TIER_B\|STARTUP_START_STREAMS'"
ssh ${VPS_USER}@${VPS_HOST} $findEnvCmd

Write-Host "`nChecking environment variables..." -ForegroundColor Yellow

$envCmd = "docker exec $backendContainer env | grep -i 'STARTUP\|DISABLE_DHAN'"
ssh ${VPS_USER}@${VPS_HOST} $envCmd

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
