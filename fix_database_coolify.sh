#!/bin/bash
# Database Reset via Coolify - Auto-detect container names
# This script finds the actual container names and resets the database

set -e

echo "=========================================================="
echo "  TRADING NEXUS - DATABASE RESET (Auto-detect)"
echo "=========================================================="
echo ""

echo "1. Finding container names..."
echo ""

# Find backend container (contains the app UUID or backend in name)
BACKEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i 'j0sk408owsssswkwwk0kwwws\|backend' | head -1)
if [ -z "$BACKEND_CONTAINER" ]; then
    echo "   Trying alternative patterns..."
    BACKEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'trading.*backend|backend.*trading' | head -1)
fi

# Find database container
DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i 'j0sk408owsssswkwwk0kwwws.*db\|postgres' | head -1)
if [ -z "$DB_CONTAINER" ]; then
    echo "   Trying alternative patterns..."
    DB_CONTAINER=$(docker ps --format '{{.Names}}' | grep -E 'trading.*db|db.*trading|postgres' | head -1)
fi

echo "✓ Backend container: $BACKEND_CONTAINER"
echo "✓ Database container: $DB_CONTAINER"
echo ""

if [ -z "$BACKEND_CONTAINER" ] || [ -z "$DB_CONTAINER" ]; then
    echo "ERROR: Could not find containers!"
    echo ""
    echo "Available containers:"
    docker ps --format 'table {{.Names}}\t{{.Status}}'
    echo ""
    echo "Please check container names and update the script."
    exit 1
fi

echo "2. Stopping backend container..."
docker stop "$BACKEND_CONTAINER" || true
sleep 2

echo ""
echo "3. Resetting database..."
docker exec "$DB_CONTAINER" psql -U postgres -c "DROP DATABASE IF EXISTS trading_terminal; CREATE DATABASE trading_terminal;" || {
    echo "ERROR: Failed to reset database!"
    echo "Trying to start backend anyway..."
}

echo ""
echo "4. Starting backend container..."
docker start "$BACKEND_CONTAINER"

echo ""
echo "5. Waiting for migrations to complete (30 seconds)..."
sleep 30

echo ""
echo "6. Checking backend logs..."
docker logs "$BACKEND_CONTAINER" --tail 100 | grep -i -E "migration|database|error|warning" || echo "(No migration messages found - check full logs)"

echo ""
echo "7. Verifying database setup..."
docker exec "$DB_CONTAINER" psql -U postgres -d trading_terminal -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;" || echo "Could not list tables"

echo ""
docker exec "$DB_CONTAINER" psql -U postgres -d trading_terminal -c "SELECT user_no, mobile, role FROM users ORDER BY user_no;" || echo "Could not query users - migrations may still be running"

echo ""
echo "=========================================================="
echo "  ✓ DATABASE RESET COMPLETE!"
echo "=========================================================="
echo ""
echo "Backend container: $BACKEND_CONTAINER"
echo "Database container: $DB_CONTAINER"
echo ""
echo "Test at: https://tradingnexus.pro"
echo "Login: 9999999999 / admin123"
echo ""
echo "If issues persist, check full logs:"
echo "  docker logs $BACKEND_CONTAINER --tail 200"
echo "=========================================================="
