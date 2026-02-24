#!/bin/bash
# Fix Coolify Docker Network Routing
# Run this on the VPS: bash fix_coolify_network.sh

set -e

echo "============================================================================"
echo "  COOLIFY DOCKER NETWORK FIX - Trading Nexus Backend"
echo "============================================================================"
echo ""

# Application UUID from Coolify
APP_UUID="p488ok8g8swo4ockks040ccg"

echo "[1] Finding containers for application: $APP_UUID"
echo "--------------------------------------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|$APP_UUID"
echo ""

echo "[2] Identifying backend container..."
BACKEND=$(docker ps --format '{{.Names}}' | grep "${APP_UUID}.*backend" | head -1)

if [ -z "$BACKEND" ]; then
    echo "❌ Backend container not found!"
    echo "Available containers:"
    docker ps --format '{{.Names}}'
    exit 1
fi

echo "✅ Found backend: $BACKEND"
echo ""

echo "[3] Checking current networks for backend..."
docker inspect $BACKEND --format '{{range .NetworkSettings.Networks}}{{.NetworkID}} {{end}}' | while read net; do
    docker network inspect $net --format '{{.Name}}' 2>/dev/null || echo "unknown"
done
echo ""

echo "[4] Checking if 'coolify' network exists..."
if docker network ls | grep -q "coolify"; then
    echo "✅ Coolify network exists"
else
    echo "❌ Coolify network not found!"
    echo "Available networks:"
    docker network ls
    exit 1
fi
echo ""

echo "[5] Checking if backend is already on coolify network..."
if docker inspect $BACKEND --format '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' | xargs -I {} docker network inspect {} --format '{{.Name}}' 2>/dev/null | grep -q "coolify"; then
    echo "✅ Backend already on coolify network"
    echo ""
    echo "The backend is already connected to the coolify network."
    echo "The routing issue might be elsewhere. Let me check Traefik labels..."
    echo ""
    docker inspect $BACKEND --format '{{range $key, $value := .Config.Labels}}{{if or (contains $key "traefik") (contains $key "coolify")}}{{$key}}={{$value}}{{"\n"}}{{end}}{{end}}'
else
    echo "❌ Backend NOT on coolify network - connecting now..."
    echo ""
    
    echo "[6] Connecting backend to coolify network..."
    docker network connect coolify $BACKEND
    echo "✅ Backend connected to coolify network!"
    echo ""
fi

echo "[7] Verifying network connection..."
docker inspect $BACKEND --format '{{range $network, $config := .NetworkSettings.Networks}}Network: {{$network}} (IP: {{$config.IPAddress}}){{"\n"}}{{end}}'
echo ""

echo "[8] Checking Traefik labels on backend..."
echo "--------------------------------------------------------------------"
docker inspect $BACKEND --format '{{range $key, $value := .Config.Labels}}{{if contains $key "traefik"}}{{$key}}={{$value}}{{"\n"}}{{end}}{{end}}'
echo ""

echo "[9] Testing backend health directly..."
BACKEND_IP=$(docker inspect $BACKEND --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' | head -1)
echo "Backend IP: $BACKEND_IP"
if [ ! -z "$BACKEND_IP" ]; then
    echo "Attempting health check on http://$BACKEND_IP:8000/health ..."
    docker run --rm --network coolify curlimages/curl:latest curl -s -m 5 http://$BACKEND_IP:8000/health || echo "(Connection failed - backend may still be starting)"
else
    echo "Backend has no IP address on any network"
fi
echo ""

echo "[10] Testing from host..."
echo "Testing: http://api.tradingnexus.pro/health"
curl -I http://api.tradingnexus.pro/health 2>&1 | head -5
echo ""

echo "============================================================================"
echo "  FIX COMPLETE"
echo "============================================================================"
echo ""
echo "Next steps:"
echo "  1. If you see 'HTTP/1.1 200 OK' above, the routing is fixed!"
echo "  2. If still 404, check Traefik logs: docker logs \$(docker ps | grep traefik | awk '{print \$1}')"
echo "  3. Test the API: curl http://api.tradingnexus.pro/health"
echo ""
