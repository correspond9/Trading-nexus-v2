# Comprehensive WebSocket subscription diagnostic
$VPS_HOST = "72.62.228.112"
$VPS_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "WEBSOCKET SUBSCRIPTION DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Find database and backend containers
Write-Host "Finding containers..." -ForegroundColor Yellow
$findCmd = "docker ps --format '{{.Names}}' | grep -E '(db-|backend-)' | grep '$APP_UUID'"
$containers = ssh ${VPS_USER}@${VPS_HOST} $findCmd 2>$null

$dbContainer = $containers -split "`n" | Where-Object { $_ -match 'db-' } | Select-Object -First 1
$backendContainer = $containers -split "`n" | Where-Object { $_ -match 'backend-' } | Select-Object -First 1

if (-not $dbContainer) {
    Write-Host "❌ Database container not found!" -ForegroundColor Red
    exit 1
}

if (-not $backendContainer) {
    Write-Host "❌ Backend container not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ DB Container: $dbContainer" -ForegroundColor Green
Write-Host "✓ Backend Container: $backendContainer`n" -ForegroundColor Green

# ============================================================
# 1. Check subscription_lists table
# ============================================================

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "1. CHECKING SUBSCRIPTION_LISTS TABLE" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$subscriptionQuery = @"
SELECT 
    list_name,
    COUNT(*) as symbol_count
FROM subscription_lists
GROUP BY list_name
ORDER BY list_name;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$subscriptionQuery`""
Write-Host "`nSubscription Lists Status:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# Check total symbols
$countQuery = "SELECT COUNT(*) FROM subscription_lists;"
$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -t -c `"$countQuery`""
$totalSymbols = ssh ${VPS_USER}@${VPS_HOST} $sqlCmd
Write-Host "`nTotal subscription list entries: $($totalSymbols.Trim())" -ForegroundColor Cyan

# ============================================================
# 2. Check Tier-B instruments in database
# ============================================================

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "2. CHECKING TIER-B INSTRUMENTS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$tierBQuery = @"
SELECT 
    COUNT(*) as total,
    COUNT(DISTINCT ws_slot) as slot_count,
    MIN(ws_slot) as min_slot,
    MAX(ws_slot) as max_slot
FROM instrument_master
WHERE tier = 'B' AND ws_slot IS NOT NULL;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$tierBQuery`""
Write-Host "`nTier-B Summary:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# Check distribution by slot
$slotDistQuery = @"
SELECT 
    COALESCE(ws_slot, 'NULL') as slot,
    COUNT(*) as token_count
FROM instrument_master
WHERE tier = 'B'
GROUP BY ws_slot
ORDER BY ws_slot;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$slotDistQuery`""
Write-Host "`nTier-B Distribution by WS Slot:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# ============================================================
# 3. Check Tier-A instruments
# ============================================================

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "3. CHECKING TIER-A INSTRUMENTS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$tierAQuery = @"
SELECT COUNT(*) as tier_a_total
FROM instrument_master
WHERE tier = 'A';
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$tierAQuery`""
Write-Host "`nTier-A Total Count:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# ============================================================
# 4. Check instrument master statistics
# ============================================================

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "4. INSTRUMENT MASTER STATISTICS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$statsQuery = @"
SELECT
    COUNT(*) as total_instruments,
    COUNT(CASE WHEN tier = 'A' THEN 1 END) as tier_a,
    COUNT(CASE WHEN tier = 'B' THEN 1 END) as tier_b,
    COUNT(CASE WHEN tier IS NULL THEN 1 END) as no_tier,
    COUNT(DISTINCT exchange_segment) as segments,
    COUNT(DISTINCT underlying) as underlyings
FROM instrument_master;
"@

$sqlCmd = "docker exec $dbContainer psql -U postgres -d trading_terminal -c `"$statsQuery`""
Write-Host "`nInstrument Master Summary:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $sqlCmd

# ============================================================
# 5. Check backend logs for WebSocket initialization
# ============================================================

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "5. BACKEND WEBSOCKET INITIALIZATION LOGS (last 50 lines)" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$logsCmd = "docker logs --tail 50 $backendContainer 2>&1 | tail -50"
Write-Host "`nBackend Logs:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $logsCmd | Select-Object -Last 50

# ============================================================
# 6. Check if DHAN is enabled
# ============================================================

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "6. CHECKING DHAN CONFIGURATION" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

$dhanCheckCmd = "docker exec $backendContainer grep -i 'DISABLE_DHAN_WS\|STARTUP_START_STREAMS\|STARTUP_LOAD_TIER_B' /app/.env 2>/dev/null || echo 'Checking config.py...'"
Write-Host "`nDhan Configuration:" -ForegroundColor Yellow
ssh ${VPS_USER}@${VPS_HOST} $dhanCheckCmd

# ============================================================
# 7. Check WebSocket connections status
# ============================================================

Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "7. TESTING API ENDPOINT" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

Write-Host "`nTesting endpoint health..." -ForegroundColor Yellow
python -c "
import requests
import json

try:
    resp = requests.get('https://api.tradingnexus.pro/api/v2/health', timeout=5)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f'API Status: {data.get(\"status\")}')
        print(f'Database: {data.get(\"database\")}')
        print(f'DhanHQ: {data.get(\"dhan_api\")}')
except Exception as e:
    print(f'Error: {e}')
"

Write-Host "`n" + ("=" * 80) -ForegroundColor Green
Write-Host "DIAGNOSTIC COMPLETE" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. If subscription_lists is empty, the seeding from CSV failed" -ForegroundColor Gray
Write-Host "2. If Tier-B has 0 instruments, they weren't loaded into instrument_master" -ForegroundColor Gray
Write-Host "3. Check backend logs for WebSocket initialization errors" -ForegroundColor Gray
Write-Host "4. Verify DHAN is enabled (DISABLE_DHAN_WS should be false)" -ForegroundColor Gray
Write-Host "5. Check if STARTUP_START_STREAMS and STARTUP_LOAD_TIER_B are enabled`n" -ForegroundColor Gray
