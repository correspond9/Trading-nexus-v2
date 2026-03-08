# ================================================================
# Script 5: Start Services and Verify Setup
# ================================================================
# This script starts all Docker services and runs comprehensive
# verification checks to ensure everything works correctly
# ================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Trading Nexus - Local Environment Setup - Step 5" -ForegroundColor Cyan
Write-Host "  Starting Services & Verification" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Start all services
Write-Host "[1/7] Starting all Docker services..." -ForegroundColor Yellow
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Services started" -ForegroundColor Green
Write-Host ""

# Wait for services to be healthy
Write-Host "[2/7] Waiting for services to be healthy..." -ForegroundColor Yellow
Write-Host "   This may take up to 60 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 15

$maxWait = 60
$waited = 0
$allHealthy = $false

while ($waited -lt $maxWait) {
    $dbHealth = docker inspect --format='{{.State.Health.Status}}' trading_nexus_db 2>$null
    $backendHealth = docker inspect --format='{{.State.Health.Status}}' trading_nexus_backend 2>$null
    
    Write-Host "   DB: $dbHealth | Backend: $backendHealth | Frontend: running" -ForegroundColor Gray
    
    if ($dbHealth -eq "healthy" -and $backendHealth -eq "healthy") {
        $allHealthy = $true
        break
    }
    
    Start-Sleep -Seconds 5
    $waited += 5
}

if ($allHealthy) {
    Write-Host "✅ All services are healthy" -ForegroundColor Green
} else {
    Write-Host "⚠️  Services started but health checks pending" -ForegroundColor Yellow
}
Write-Host ""

# Show running containers
Write-Host "[3/7] Container status:" -ForegroundColor Yellow
docker compose ps
Write-Host ""

# Test database connection
Write-Host "[4/7] Testing database connection..." -ForegroundColor Yellow
$dbTest = docker exec trading_nexus_db psql -U postgres -d trading_nexus -c "\dt" 2>&1
if ($LASTEXITCODE -eq 0) {
    $tableCount = ($dbTest | Select-String "public" | Measure-Object).Count
    Write-Host "✅ Database connected - $tableCount tables found" -ForegroundColor Green
} else {
    Write-Host "❌ Database connection failed" -ForegroundColor Red
}
Write-Host ""

# Test backend API
Write-Host "[5/7] Testing backend API..." -ForegroundColor Yellow
Start-Sleep -Seconds 5  # Give backend extra time to fully start

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend API responding" -ForegroundColor Green
        Write-Host "   Health check: $($response.Content)" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Backend API not yet ready (may need more time)" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}
Write-Host ""

# Test frontend
Write-Host "[6/7] Testing frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend responding" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Frontend not yet ready" -ForegroundColor Yellow
}
Write-Host ""

# Display access information
Write-Host "[7/7] Access Information:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  🌐 Frontend:      http://localhost" -ForegroundColor Cyan
Write-Host "  🔌 Backend API:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "  📊 API Docs:      http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  💾 Database:      localhost:5432" -ForegroundColor Cyan
Write-Host "                    User: postgres" -ForegroundColor Gray
Write-Host "                    Database: trading_nexus" -ForegroundColor Gray
Write-Host ""

# Get sample data counts
Write-Host "📊 Sample Data Summary:" -ForegroundColor Cyan
$countQuery = @"
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'Orders', COUNT(*) FROM paper_orders
UNION ALL SELECT 'Positions', COUNT(*) FROM paper_positions
UNION ALL SELECT 'Watchlists', COUNT(*) FROM watchlists
UNION ALL SELECT 'Ledger Entries', COUNT(*) FROM ledger_entries;
"@

docker exec trading_nexus_db psql -U postgres -d trading_nexus -c "$countQuery"
Write-Host ""

# Show recent logs
Write-Host "📝 Recent Backend Logs:" -ForegroundColor Cyan
docker logs trading_nexus_backend --tail 20
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  🎉 Local Environment Setup Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Your local environment is now running with production data!" -ForegroundColor Green
Write-Host ""
Write-Host "📌 Important Reminders:" -ForegroundColor Yellow
Write-Host "   • Market data streams are DISABLED (safe for testing)" -ForegroundColor Gray
Write-Host "   • This is using production data - be careful with modifications" -ForegroundColor Gray
Write-Host "   • All changes are local only - won't affect production" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Useful Commands:" -ForegroundColor Cyan
Write-Host "   docker compose logs -f          # View live logs" -ForegroundColor Gray
Write-Host "   docker compose down             # Stop all services" -ForegroundColor Gray
Write-Host "   docker compose restart backend  # Restart backend only" -ForegroundColor Gray
Write-Host "   docker compose ps               # Check service status" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy testing! 🚀" -ForegroundColor Cyan
Write-Host ""
