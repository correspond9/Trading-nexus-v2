#!/usr/bin/env powershell

# TRADING NEXUS - FULL REBUILD SCRIPT (Windows/PowerShell)
# This script rebuilds the entire deployment (frontend + backend)
# Run this on the VPS via PowerShell where docker-compose.prod.yml is located

param(
    [string]$ProjectDir = "."
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "TRADING NEXUS - FULL REBUILD" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Project directory: $ProjectDir" -ForegroundColor Yellow
Write-Host ""

# Check if docker-compose.prod.yml exists
$composeFile = Join-Path $ProjectDir "docker-compose.prod.yml"
if (-not (Test-Path $composeFile)) {
    Write-Host "ERROR: docker-compose.prod.yml not found in $ProjectDir" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found docker-compose.prod.yml" -ForegroundColor Green
Write-Host ""

# Step 1: Build everything without cache
Write-Host "Step 1: Building all services (frontend + backend) without cache..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

Push-Location $ProjectDir
docker-compose -f docker-compose.prod.yml build --no-cache

Write-Host "✓ Build complete" -ForegroundColor Green
Write-Host ""

# Step 2: Stop existing containers
Write-Host "Step 2: Stopping existing containers..." -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml down

Write-Host "✓ Old containers stopped" -ForegroundColor Green
Write-Host ""

# Step 3: Start everything
Write-Host "Step 3: Starting all services..." -ForegroundColor Cyan
docker-compose -f docker-compose.prod.yml up -d

Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

# Step 4: Check status
Write-Host "Step 4: Checking service status..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
docker-compose -f docker-compose.prod.yml ps

Pop-Location

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Services deployed:" -ForegroundColor Green
Write-Host "  ✓ Frontend: tradingnexus.pro, www.tradingnexus.pro, learn.tradingnexus.pro" -ForegroundColor Green
Write-Host "  ✓ Backend: api.tradingnexus.pro" -ForegroundColor Green
Write-Host "  ✓ Database: PostgreSQL (internal)" -ForegroundColor Green
Write-Host "  ✓ Cache: Redis (internal)" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Wait 30 seconds for services to fully start" -ForegroundColor Yellow
Write-Host "  2. Test backend: curl http://api.tradingnexus.pro/api/v2/health" -ForegroundColor Yellow
Write-Host "  3. Test frontend: curl http://tradingnexus.pro/" -ForegroundColor Yellow
Write-Host "  4. Hard refresh browser: Ctrl+Shift+R" -ForegroundColor Yellow
Write-Host ""

Write-Host "If there are issues, check logs:" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor Cyan
Write-Host ""
