#!/bin/bash

# TRADING NEXUS - FULL REBUILD SCRIPT
# This script rebuilds the entire deployment (frontend + backend)
# Run this on the VPS where docker-compose.prod.yml is located

set -e

echo "========================================================================"
echo "TRADING NEXUS - FULL REBUILD"
echo "========================================================================"

PROJECT_DIR="${1:-.}"

echo ""
echo "Project directory: $PROJECT_DIR"
echo ""

# Check if docker-compose.prod.yml exists
if [ ! -f "$PROJECT_DIR/docker-compose.prod.yml" ]; then
    echo "ERROR: docker-compose.prod.yml not found in $PROJECT_DIR"
    exit 1
fi

echo "✓ Found docker-compose.prod.yml"
echo ""

# Step 1: Build everything without cache
echo "Step 1: Building all services (frontend + backend) without cache..."
echo "This may take 5-10 minutes..."
echo ""

cd "$PROJECT_DIR"
docker-compose -f docker-compose.prod.yml build --no-cache

echo ""
echo "✓ Build complete"
echo ""

# Step 2: Stop existing containers
echo "Step 2: Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

echo "✓ Old containers stopped"
echo ""

# Step 3: Start everything
echo "Step 3: Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

echo "✓ Services started"
echo ""

# Step 4: Check status
echo "Step 4: Checking service status..."
sleep 3
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "========================================================================"
echo "DEPLOYMENT COMPLETE"
echo "========================================================================"
echo ""
echo "Services deployed:"
echo "  ✓ Frontend: tradingnexus.pro, www.tradingnexus.pro, learn.tradingnexus.pro"
echo "  ✓ Backend: api.tradingnexus.pro"
echo "  ✓ Database: PostgreSQL (internal)"
echo "  ✓ Cache: Redis (internal)"
echo ""
echo "Next steps:"
echo "  1. Wait 30 seconds for services to fully start"
echo "  2. Test backend: curl http://api.tradingnexus.pro/api/v2/health"
echo "  3. Test frontend: curl http://tradingnexus.pro/"
echo "  4. Hard refresh browser: Ctrl+Shift+R"
echo ""
echo "If there are issues, check logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
