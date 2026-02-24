# Fix user roles in production database
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FIXING USER ROLES IN PRODUCTION" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Find database container
Write-Host "Finding database container..." -ForegroundColor Yellow
$findCmd = "docker ps --format '{{.Names}}' | grep 'db-$APP_UUID'"
$dbContainer = ssh ${VPS_USER}@${VPS_HOST} $findCmd 2>$null

if (-not $dbContainer) {
    Write-Host "❌ Database container not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found: $dbContainer`n" -ForegroundColor Green

# Update the Super Admin role
Write-Host "Fixing Super Admin role (9999999999)..." -ForegroundColor Yellow

$fixSuperAdminQuery = @"
UPDATE users 
SET role = 'SUPER_ADMIN' 
WHERE mobile = '9999999999';
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$fixSuperAdminQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

Write-Host "`nVerifying fix..." -ForegroundColor Yellow

$verifyQuery = @"
SELECT user_no, mobile, name, role, is_active 
FROM users 
WHERE mobile IN ('9999999999', '8888888888', '7777777777', '6666666666')
ORDER BY user_no;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$verifyQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "✓ ROLE FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green

Write-Host "Please log out and log in again to get new session with correct role." -ForegroundColor Cyan
