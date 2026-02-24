#!/bin/bash
# Fix broken Traefik labels in docker-compose.yaml

SSHPass=$(cat) # Read password from stdin

sshpass -p "$SSHPass" ssh root@72.62.228.112 << 'EOF'
APP_UUID="p488ok8g8swo4ockks040ccg"
APP_DIR="/data/coolify/applications/${APP_UUID}"
COMPOSE_FILE="${APP_DIR}/docker-compose.yaml"

echo "=== Fixing Traefik Configuration ==="
echo ""
echo "Current malformed routes:"
grep -n 'traefik.http.routers.http-0' "$COMPOSE_FILE" | head -5
echo ""

# Create backup
cp "$COMPOSE_FILE" "$COMPOSE_FILE".backup
echo "Backup created: ${COMPOSE_FILE}.backup"
echo ""

# Remove all broken http-0 router labels
echo "Removing broken http-0 labels..."
sed -i '/- traefik.http.routers.http-0-/d' "$COMPOSE_FILE"
sed -i '/- traefik.http.middlewares.http-0-/d' "$COMPOSE_FILE"
sed -i '/- caddy_/d' "$COMPOSE_FILE"
sed -i '/- caddy_ingress_network/d' "$COMPOSE_FILE"
sed -i '/- 'caddy_/d' "$COMPOSE_FILE"

echo "Broken labels removed"
echo ""

# Verify removal
echo "Remaining Traefik routes:"
grep 'traefik.http.routers' "$COMPOSE_FILE" | grep -v '^\s*#' | head -10
echo ""

# Restart application
echo "Restarting application..."
cd "$APP_DIR"
docker compose down --remove-orphans
sleep 5
docker compose up -d
echo ""

# Wait for stability
echo "Waiting for containers to stabilize..."
sleep 20

# Check status
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$APP_UUID"
echo ""

# Test endpoints
echo "Testing API endpoints..."
echo "  /health:"
curl -s http://127.0.0.1:8000/health | head -c 100
echo ""
echo "  /api/v2/health:"
curl -s http://127.0.0.1:8000/api/v2/health | head -c 100
echo ""

echo "=== Fix Complete ==="
EOF

