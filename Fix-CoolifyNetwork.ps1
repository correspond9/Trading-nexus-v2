# Trading Nexus - Coolify Network Fix
# Run this script on your LOCAL machine (Windows PowerShell)

# VPS Connection Details
$VPS_IP = "72.62.228.112"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  COOLIFY DOCKER NETWORK DIAGNOSTIC & FIX" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will connect to your VPS and fix the Docker network routing." -ForegroundColor Yellow
Write-Host "You'll need your VPS root password." -ForegroundColor Yellow
Write-Host ""

# Test connection
Write-Host "[1] Testing VPS connection..." -ForegroundColor Green
try {
    $testResult = ssh -o StrictHostKeyChecking=accept-new root@$VPS_IP "echo 'Connected'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Connected to VPS" -ForegroundColor Green
    } else {
        Write-Host "❌ Connection failed. Please check your password." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ SSH connection error: $_" -ForegroundColor Red
    exit 1
}

# Find containers
Write-Host ""
Write-Host "[2] Finding application containers..." -ForegroundColor Green
$containers = ssh root@$VPS_IP "docker ps --format '{{.Names}}' | grep $APP_UUID"

if ([string]::IsNullOrWhiteSpace($containers)) {
    Write-Host "❌ No containers found for UUID: $APP_UUID" -ForegroundColor Red
    Write-Host "All running containers:" -ForegroundColor Yellow
    ssh root@$VPS_IP "docker ps --format 'table {{.Names}}\t{{.Status}}'"
    exit 1
}

Write-Host "Found containers:" -ForegroundColor Cyan
$containers -split "`n" | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

# Find backend
$backend = ($containers -split "`n" | Where-Object { $_ -match "backend" } | Select-Object -First 1)
if ([string]::IsNullOrWhiteSpace($backend)) {
    Write-Host "❌ No backend container found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend container: $backend" -ForegroundColor Green

# Check current networks
Write-Host ""
Write-Host "[3] Checking current networks for backend..." -ForegroundColor Green
$networks = ssh root@$VPS_IP "docker inspect $backend --format '{{range `$network, `$config := .NetworkSettings.Networks}}`$network {{end}}'"
Write-Host "Current networks: $networks" -ForegroundColor Cyan

# Check if coolify network exists
Write-Host ""
Write-Host "[4] Checking for coolify network..." -ForegroundColor Green
$coolifyExists = ssh root@$VPS_IP "docker network ls | grep coolify"
if ([string]::IsNullOrWhiteSpace($coolifyExists)) {
    Write-Host "❌ Coolify network not found!" -ForegroundColor Red
    Write-Host "Available networks:" -ForegroundColor Yellow
    ssh root@$VPS_IP "docker network ls"
    exit 1
}
Write-Host "✅ Coolify network exists" -ForegroundColor Green

# Check if backend is on coolify network
Write-Host ""
Write-Host "[5] Checking if backend is on coolify network..." -ForegroundColor Green
if ($networks -match "coolify") {
    Write-Host "✅ Backend is already on coolify network" -ForegroundColor Green
    Write-Host ""
    Write-Host "The network connection is correct. The issue may be with Traefik labels." -ForegroundColor Yellow
    Write-Host "Checking Traefik labels..." -ForegroundColor Green
    ssh root@$VPS_IP "docker inspect $backend --format '{{range `$key, `$value := .Config.Labels}}{{`$key}}={{`$value}}{{`"``n`"}}{{end}}' | grep traefik"
} else {
    Write-Host "❌ Backend NOT on coolify network - connecting now..." -ForegroundColor Red
    Write-Host ""
    Write-Host "[6] Connecting backend to coolify network..." -ForegroundColor Green
    ssh root@$VPS_IP "docker network connect coolify $backend"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully connected backend to coolify network!" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to connect to network" -ForegroundColor Red
        exit 1
    }
}

# Verify connection
Write-Host ""
Write-Host "[7] Verifying network connections..." -ForegroundColor Green
ssh root@$VPS_IP "docker inspect $backend --format '{{range `$network, `$config := .NetworkSettings.Networks}}Network: {{`$network}} (IP: {{`$config.IPAddress}}){{`"``n`"}}{{end}}'"

# Test endpoint
Write-Host ""
Write-Host "[8] Testing API endpoint..." -ForegroundColor Green
Write-Host "Testing: http://api.tradingnexus.pro/health" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://api.tradingnexus.pro/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ SUCCESS! HTTP $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode) {
        Write-Host "❌ HTTP $statusCode" -ForegroundColor Red
    } else {
        Write-Host "❌ Connection failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  DIAGNOSTIC COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
