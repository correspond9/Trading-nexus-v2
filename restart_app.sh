#!/bin/bash
set -e

echo "=========================================="
echo "Restarting Trading Nexus Backend"
echo "=========================================="

cd /opt/coolify/applications

# Find the backend container and restart it
echo "Finding backend container..."
CONTAINER=$(docker ps --filter "name=backend" --filter "name=p488ok8g8swo4ockks040ccg" -q | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ Backend container not found"
    docker ps --filter "name=trading" -a
    exit 1
fi

echo "✅ Found container: $CONTAINER"
echo "Restarting container..."

docker restart "$CONTAINER"

echo "Waiting 15 seconds for container to restart..."
sleep 15

# Verify it's running
if docker ps | grep -q "$CONTAINER"; then
    echo "✅ Container is running"
else
    echo "❌ Container failed to start"
    docker logs "$CONTAINER" | tail -50
    exit 1
fi

echo "=========================================="
echo "✅ Restart complete"
echo "=========================================="
