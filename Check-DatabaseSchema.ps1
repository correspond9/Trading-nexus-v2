# Check database schema and migrations
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DATABASE SCHEMA CHECK" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Find database container
$findCmd = "docker ps --format '{{.Names}}' | grep 'db-$APP_UUID'"
$dbContainer = ssh ${VPS_USER}@${VPS_HOST} $findCmd 2>$null

Write-Host "Container: $dbContainer`n" -ForegroundColor Yellow

# Check all tables
Write-Host "Checking all tables in database..." -ForegroundColor Yellow

$listTablesQuery = @"
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$listTablesQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# Check users table schema
Write-Host "`nChecking users table columns..." -ForegroundColor Yellow

$userSchemaQuery = @"
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$userSchemaQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "SCHEMA CHECK COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
