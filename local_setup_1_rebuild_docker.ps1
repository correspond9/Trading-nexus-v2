# ================================================================
# Script 1: Rebuild Docker Images for Local Environment
# ================================================================
# This script rebuilds both backend and frontend Docker images
# with the latest code from your repository
# ================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Trading Nexus - Local Environment Setup - Step 1" -ForegroundColor Cyan
Write-Host "  Rebuilding Docker Images" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/5] Checking Docker Desktop status..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker Desktop is not running. Please start Docker Desktop first." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker command not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Stop existing containers
Write-Host "[2/5] Stopping existing containers..." -ForegroundColor Yellow
docker compose down
Write-Host "✅ Containers stopped" -ForegroundColor Green
Write-Host ""

# Remove old images (optional - uncomment if you want to force rebuild)
Write-Host "[3/5] Removing old images..." -ForegroundColor Yellow
docker rmi trading-nexus-backend 2>$null
docker rmi trading-nexus-frontend 2>$null
Write-Host "✅ Old images removed (if they existed)" -ForegroundColor Green
Write-Host ""

# Rebuild images with no cache
Write-Host "[4/5] Building fresh Docker images (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host "    Building backend..." -ForegroundColor Cyan
docker compose build --no-cache backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Backend image built successfully" -ForegroundColor Green

Write-Host "    Building frontend..." -ForegroundColor Cyan
docker compose build --no-cache frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Frontend image built successfully" -ForegroundColor Green
Write-Host ""

# Verify images
Write-Host "[5/5] Verifying built images..." -ForegroundColor Yellow
$images = docker images --format "{{.Repository}}" | Select-String "trading"
Write-Host "Built images:"
docker images | Select-String "trading"
Write-Host "✅ All images built successfully" -ForegroundColor Green
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Step 1 Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run ./local_setup_2_export_production_db.ps1" -ForegroundColor Yellow
Write-Host "           to export production database" -ForegroundColor Yellow
Write-Host ""
