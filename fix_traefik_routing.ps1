# Fix Traefik routing configuration on the VPS
# This script removes broken Traefik labels and restarts the application

$VPS_IP = "72.62.228.112"
$SSH_USER = "root"
$APP_UUID = "p488ok8g8swo4ockks040ccg"
$APP_DIR = "/data/coolify/applications/${APP_UUID}"
$COMPOSE_FILE = "${APP_DIR}/docker-compose.yaml"

Write-Host "=== TRAEFIK ROUTING FIX ===" -ForegroundColor Cyan
Write-Host "Connecting to VPS: $VPS_IP" -ForegroundColor Yellow

# Step 1: Backup the original file
Write-Host ""
Write-Host "Step 1: Backing up original docker-compose.yaml..." -ForegroundColor Yellow
ssh root@$VPS_IP "cp $COMPOSE_FILE $COMPOSE_FILE.backup && echo 'Backup created'"

# Step 2: Remove broken Traefik labels
Write-Host ""
Write-Host "Step 2: Removing broken Traefik http-0 router labels..." -ForegroundColor Yellow
ssh root@$VPS_IP @"
cd $APP_DIR
# Remove broken labels
sed -i '/traefik.http.routers.http-0-p488ok8g8swo4ockks040ccg-backend/d' docker-compose.yaml
sed -i '/traefik.http.middlewares.http-0-p488ok8g8swo4ockks040ccg-backend-stripprefix/d' docker-compose.yaml
sed -i '/caddy_0/d' docker-compose.yaml
sed -i '/caddy_ingress_network/d' docker-compose.yaml
echo 'Broken labels removed'
"@

# Step 3: Restart application
Write-Host ""
Write-Host "Step 3: Restarting application..." -ForegroundColor Yellow
ssh root@$VPS_IP @"
cd $APP_DIR
docker compose down
docker compose up -d
sleep 20
"@

# Step 4: Test the endpoints
Write-Host ""
Write-Host "Step 4: Testing API endpoints..." -ForegroundColor Yellow

Write-Host "  - Testing /health endpoint..." -ForegroundColor Gray
$health = curl.exe -s "http://${VPS_IP}:8000/health" 2>&1
Write-Host "    Response: $($health -join ' ')" -ForegroundColor Gray

Write-Host "  - Testing /api/v2/health endpoint..." -ForegroundColor Gray
$health_v2 = curl.exe -s "http://${VPS_IP}:8000/api/v2/health" 2>&1
Write-Host "    Response: $($health_v2 -join ' ')" -ForegroundColor Gray

Write-Host "  - Testing /api/v2/instruments/search endpoint..." -ForegroundColor Gray
$search = curl.exe -s "http://${VPS_IP}:8000/api/v2/instruments/search?q=RELIANCE&limit=5" 2>&1
if ($search -like '*404*') {
    Write-Host "    ❌ Still returning 404" -ForegroundColor Red
    Write-Host "    Response: $search" -ForegroundColor Gray
} else {
    Write-Host "    ✅ Success! Got response" -ForegroundColor Green
    Write-Host "    Response: $($search | ConvertFrom-Json | Select-Object -First 3 | Format-Table | Out-String)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== FIX COMPLETE ===" -ForegroundColor Cyan
Write-Host "If endpoints are still returning 404, the issue may be with Traefik labels." -ForegroundColor Yellow
Write-Host "Check Traefik logs: docker logs coolify-proxy | tail -50" -ForegroundColor Yellow
