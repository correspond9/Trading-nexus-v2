# Check if DhanHQ credentials are in database
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECKING DHAN CREDENTIALS IN DATABASE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Find database container
$findCmd = "docker ps --format '{{.Names}}' | grep 'db-$APP_UUID'"
$dbContainer = ssh ${VPS_USER}@${VPS_HOST} $findCmd 2>$null

if (-not $dbContainer) {
    Write-Host "❌ Database container not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Database Container: $dbContainer`n" -ForegroundColor Green

# Check system_config table for credentials
Write-Host "Checking system_config table for DhanHQ credentials..." -ForegroundColor Yellow

$credQuery = @"
SELECT key, 
       CASE 
           WHEN LENGTH(value) > 20 THEN SUBSTRING(value, 1, 20) || '...'
           ELSE value
       END as value_preview
FROM system_config
WHERE key LIKE '%dhan%' OR key LIKE '%credential%' OR key LIKE '%client%'
ORDER BY key;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$credQuery`""
Write-Host "`nCredentials in system_config:" -ForegroundColor Cyan
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# Check if there's any config data at all
$countQuery = "SELECT COUNT(*) FROM system_config;"
$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -t -c `"$countQuery`""
$total = ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

Write-Host "`nTotal config entries: $($total.Trim())" -ForegroundColor Cyan

# Show all keys
$allKeysQuery = "SELECT key FROM system_config ORDER BY key LIMIT 20;"
$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$allKeysQuery`""
Write-Host "`nAll config keys:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "CHECK COMPLETE" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green
