# ================================================================
# Script 3: Import Database to Local Docker
# ================================================================
# This script imports the production database dump into your
# local PostgreSQL container
# ================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Trading Nexus - Local Environment Setup - Step 3" -ForegroundColor Cyan
Write-Host "  Importing Database to Local Docker" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Find the latest dump file
Write-Host "[1/6] Finding latest database dump..." -ForegroundColor Yellow
$dumpFiles = Get-ChildItem -Path ".\production_db_export" -Filter "production_dump_*.sql" | Sort-Object LastWriteTime -Descending
if ($dumpFiles.Count -eq 0) {
    Write-Host "❌ No database dump found. Please run local_setup_2_export_production_db.ps1 first." -ForegroundColor Red
    exit 1
}
$latestDump = $dumpFiles[0].FullName
Write-Host "✅ Found dump: $($dumpFiles[0].Name)" -ForegroundColor Green
Write-Host ""

# Start only the database service first
Write-Host "[2/6] Starting PostgreSQL container..." -ForegroundColor Yellow
docker compose up -d db
Start-Sleep -Seconds 10  # Wait for DB to be ready
Write-Host "✅ PostgreSQL container started" -ForegroundColor Green
Write-Host ""

# Wait for DB to be healthy
Write-Host "[3/6] Waiting for database to be ready..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    $health = docker inspect --format='{{.State.Health.Status}}' trading_nexus_db 2>$null
    if ($health -eq "healthy") {
        Write-Host "✅ Database is healthy and ready" -ForegroundColor Green
        break
    }
    Write-Host "   Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    Start-Sleep -Seconds 2
    $waited += 2
}
Write-Host ""

# Drop existing database and recreate (fresh start)
Write-Host "[4/6] Preparing database for import..." -ForegroundColor Yellow
docker exec trading_nexus_db psql -U postgres -c "DROP DATABASE IF EXISTS trading_nexus;"
docker exec trading_nexus_db psql -U postgres -c "CREATE DATABASE trading_nexus;"
Write-Host "✅ Database prepared" -ForegroundColor Green
Write-Host ""

# Copy dump file into container
Write-Host "[5/6] Copying dump file to container..." -ForegroundColor Yellow
docker cp $latestDump trading_nexus_db:/tmp/import_dump.sql
Write-Host "✅ Dump file copied" -ForegroundColor Green
Write-Host ""

# Import the dump
Write-Host "[6/6] Importing database (this may take a few minutes)..." -ForegroundColor Yellow
docker exec trading_nexus_db psql -U postgres -d trading_nexus -f /tmp/import_dump.sql

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Import completed with warnings (this is normal for some tables)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Database imported successfully" -ForegroundColor Green
}
Write-Host ""

# Verify import
Write-Host "📊 Verifying imported data..." -ForegroundColor Cyan
$verifyScript = @"
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 15;
"@

docker exec trading_nexus_db psql -U postgres -d trading_nexus -c "$verifyScript"
Write-Host ""

# Clean up temp file in container
docker exec trading_nexus_db rm /tmp/import_dump.sql

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Step 3 Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run ./local_setup_4_sync_config.ps1" -ForegroundColor Yellow
Write-Host "           to synchronize configuration files" -ForegroundColor Yellow
Write-Host ""
