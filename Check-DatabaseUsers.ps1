# Check database users on production VPS
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "PRODUCTION DATABASE DIAGNOSTIC" -ForegroundColor Cyan
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

# Check users table
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "CHECKING USERS TABLE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$checkUsersQuery = @"
SELECT 
    user_no,
    mobile, 
    name,
    role,
    is_active
FROM users 
ORDER BY user_no;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$checkUsersQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# Check active sessions
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "CHECKING ACTIVE SESSIONS (last hour)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$checkSessionsQuery = @"
SELECT 
    LEFT(s.token::text, 8) || '...' as token,
    u.mobile,
    u.name,
    u.role,
    (s.expires_at > NOW()) as is_valid
FROM user_sessions s
JOIN users u ON u.id = s.user_id
WHERE s.expires_at > NOW() - INTERVAL '1 hour'
ORDER BY s.created_at DESC
LIMIT 10;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$checkSessionsQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# Check seed user migration
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "CHECKING SEED USER MIGRATION" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$checkMigrationQuery = @"
SELECT name, applied_at 
FROM _migrations 
WHERE name LIKE '%seed%' OR name = '022_ensure_seed_users'
ORDER BY id DESC;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$checkMigrationQuery`""
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
