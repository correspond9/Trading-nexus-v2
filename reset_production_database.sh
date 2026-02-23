#!/bin/bash
# Complete Production Database Reset Script
# WARNING: This will DELETE ALL DATA and recreate the database from scratch
# Run this on your VPS server

set -e

echo "=========================================================="
echo "  TRADING NEXUS - PRODUCTION DATABASE RESET"
echo "=========================================================="
echo ""
echo "WARNING: This will DELETE all existing data!"
echo "Press Ctrl+C now to cancel, or Enter to continue..."
read

echo ""
echo "1. Stopping backend container..."
docker stop trading-nexus-backend-1 || true

echo ""
echo "2. Dropping and recreating database..."
docker exec trading-nexus-db-1 psql -U postgres -c "
DROP DATABASE IF EXISTS trading_terminal;
CREATE DATABASE trading_terminal;
GRANT ALL PRIVILEGES ON DATABASE trading_terminal TO postgres;
"

echo ""
echo "3. Starting backend container (migrations will run automatically)..."
docker start trading-nexus-backend-1

echo ""
echo "4. Waiting for backend to start (30 seconds)..."
sleep 30

echo ""
echo "5. Checking if migrations completed..."
docker logs --tail 100 trading-nexus-backend-1 | grep -i "migration"

echo ""
echo "6. Verifying database setup..."
docker exec trading-nexus-backend-1 python3 -c "
import asyncio
import asyncpg

async def verify():
    conn = await asyncpg.connect(
        host='db',
        port=5432,
        user='postgres',
        database='trading_terminal'
    )
    
    tables = await conn.fetch(\"\"\"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    \"\"\")
    
    print(f'✓ Found {len(tables)} tables:')
    for t in tables:
        print(f'  - {t[\"table_name\"]}')
    
    user_count = await conn.fetchval('SELECT COUNT(*) FROM users')
    print(f'\\n✓ Demo users created: {user_count}')
    
    if user_count > 0:
        users = await conn.fetch('SELECT user_no, mobile, role FROM users ORDER BY user_no')
        for u in users:
            print(f'  {u[\"user_no\"]}: {u[\"mobile\"]} ({u[\"role\"]})')
    
    await conn.close()

asyncio.run(verify())
"

echo ""
echo "=========================================================="
echo "  ✓ DATABASE RESET COMPLETE!"
echo "=========================================================="
echo ""
echo "Default login credentials:"
echo "  SUPER_ADMIN: 9999999999 / admin123"
echo "  ADMIN:       8888888888 / admin123"
echo "  SUPER_USER:  6666666666 / super123"
echo "  USER:        7777777777 / user123"
echo ""
echo "Test at: https://tradingnexus.pro"
echo "=========================================================="
