# ============================================================================
# MANUAL DELETE POSITIONS FOR USER 9326890165
# PowerShell script to delete via SSH + Docker
# ============================================================================

$VPS_IP = "72.62.228.112"
$USER_MOBILE = "9326890165"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MANUAL POSITION DELETION - User: $USER_MOBILE" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Step 1: Find database container
Write-Host "[1] Finding PostgreSQL container..." -ForegroundColor Green
$findContainerCmd = "docker ps --filter 'ancestor=postgres:15-alpine' --format '{{.ID}}'"

Write-Host "SSH Command: ssh root@$VPS_IP `"$findContainerCmd`"" -ForegroundColor Gray
$containerId = ssh root@$VPS_IP $findContainerCmd

if ([string]::IsNullOrWhiteSpace($containerId)) {
    Write-Host "ERROR: PostgreSQL container not found!" -ForegroundColor Red
    Write-Host "Run this manually to find container:" -ForegroundColor Yellow
    Write-Host "  ssh root@$VPS_IP" -ForegroundColor White
    Write-Host "  docker ps | grep postgres" -ForegroundColor White
    exit 1
}

Write-Host "Found container: $containerId" -ForegroundColor Green
Write-Host ""

# Step 2: Count current positions
Write-Host "[2] Counting current records..." -ForegroundColor Green
$countQuery = @"
SELECT 
    (SELECT COUNT(*) FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE')) AS positions,
    (SELECT COUNT(*) FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE')) AS orders,
    (SELECT COUNT(*) FROM paper_trades WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE')) AS trades,
    (SELECT COUNT(*) FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE')) AS ledger_entries;
"@

$execCmd = "docker exec -i $containerId psql -U trading_user -d trading_terminal -c `"$countQuery`""
Write-Host "Executing count query..." -ForegroundColor Gray

$result = ssh root@$VPS_IP $execCmd
Write-Host $result -ForegroundColor White
Write-Host ""

# Step 3: Confirm deletion
Write-Host "WARNING: This will PERMANENTLY delete ALL positions, orders, trades, and ledger entries!" -ForegroundColor Red
$confirmation = Read-Host "Type 'DELETE' to confirm deletion"

if ($confirmation -ne "DELETE") {
    Write-Host "Deletion cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[3] Deleting records..." -ForegroundColor Green

# Delete in correct order
$deleteQueries = @(
    "DELETE FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE');",
    "DELETE FROM paper_trades WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE');",
    "DELETE FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE');",
    "DELETE FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE');"
)

$steps = @("ledger_entries", "paper_trades", "paper_orders", "paper_positions")
$index = 0

foreach ($query in $deleteQueries) {
    Write-Host "  Deleting $($steps[$index])..." -ForegroundColor Cyan
    $execCmd = "docker exec -i $containerId psql -U trading_user -d trading_terminal -c `"$query`""
    $result = ssh root@$VPS_IP $execCmd
    Write-Host "  $result" -ForegroundColor Gray
    $index++
}

Write-Host ""
Write-Host "[4] Verifying deletion..." -ForegroundColor Green
$verifyQuery = @"
SELECT 
    (SELECT COUNT(*) FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE')) AS remaining_positions,
    (SELECT COUNT(*) FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '$USER_MOBILE')) AS remaining_orders;
"@

$execCmd = "docker exec -i $containerId psql -U trading_user -d trading_terminal -c `"$verifyQuery`""
$result = ssh root@$VPS_IP $execCmd
Write-Host $result -ForegroundColor White

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "DELETION COMPLETE!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "User $USER_MOBILE should now have 0 positions." -ForegroundColor Yellow
Write-Host "Refresh the dashboard to verify." -ForegroundColor Yellow
