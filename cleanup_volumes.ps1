# Trading Nexus - Volume Cleanup Script
# Safely removes orphaned Docker volumes from old deployments

Write-Host ""
Write-Host "🧹 Trading Nexus - Volume Cleanup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# List all volumes first
Write-Host "📊 Current Docker volumes:" -ForegroundColor White
docker volume ls --filter "name=trading" --format "table {{.Driver}}\t{{.Name}}"
Write-Host ""

# Identify active volumes
Write-Host "✅ ACTIVE volumes (will NOT be removed):" -ForegroundColor Green
Write-Host "   • trading_nexus_pg_data (mounted to db container)" -ForegroundColor Green
Write-Host ""

# Identify orphaned volumes
Write-Host "❌ ORPHANED volumes (will be removed):" -ForegroundColor Yellow
$orphanedVolumes = @(
    "trading-nexus_postgres_data",
    "trading-nexus_redis_data",
    "data_server_backend_postgres_data",
    "data_server_backend_redis_data",
    "data_server_backend_trading-db-data",
    "data_server_backend_trading-logs"
)

foreach ($vol in $orphanedVolumes) {
    $exists = docker volume ls --filter "name=$vol" --format "{{.Name}}" 2>$null
    if ($exists) {
        Write-Host "   • $vol" -ForegroundColor Yellow
    }
}
Write-Host ""

# Confirm removal
Write-Host "⚠️  WARNING: This will permanently delete orphaned volumes!" -ForegroundColor Red
Write-Host "   Make sure you have backups of any important data." -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "   Continue with cleanup? (type 'yes' to confirm)"

if ($confirm -ne "yes") {
    Write-Host ""
    Write-Host "❌ Cleanup cancelled. No changes made." -ForegroundColor Red
    Write-Host ""
    exit
}

Write-Host ""
Write-Host "🗑️  Removing orphaned volumes..." -ForegroundColor Cyan
Write-Host ""

$removedCount = 0
$notFoundCount = 0

foreach ($vol in $orphanedVolumes) {
    Write-Host "   Processing: $vol... " -NoNewline
    
    $result = docker volume rm $vol 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Removed" -ForegroundColor Green
        $removedCount++
    } else {
        if ($result -like "*No such volume*" -or $result -like "*no such volume*") {
            Write-Host "⚠️  Not found (already removed)" -ForegroundColor DarkGray
            $notFoundCount++
        } else {
            Write-Host "❌ Error: $result" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "📊 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "   • Removed: $removedCount volumes" -ForegroundColor Green
Write-Host "   • Not found: $notFoundCount volumes" -ForegroundColor DarkGray
Write-Host "   • Total processed: $($orphanedVolumes.Count) volumes" -ForegroundColor White
Write-Host ""

# Show remaining volumes
Write-Host "📦 Remaining volumes:" -ForegroundColor Cyan
docker volume ls --filter "name=trading" --format "table {{.Driver}}\t{{.Name}}"
Write-Host ""

Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""

# Optionally run docker system prune
Write-Host "💡 Suggestion: You can also run 'docker volume prune' to remove ALL unused volumes" -ForegroundColor DarkGray
Write-Host "   (This will remove any volume not attached to a container)" -ForegroundColor DarkGray
Write-Host ""
