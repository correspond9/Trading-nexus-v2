#!/bin/bash
# Run Database Migrations Script
# This will apply all pending migrations without deleting existing data

set -e

echo "=========================================================="
echo "  TRADING NEXUS - RUN DATABASE MIGRATIONS"
echo "=========================================================="
echo ""

echo "1. Checking backend container status..."
CONTAINER_NAME="trading-nexus-backend-1"
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✗ Backend container is not running!"
    echo "  Starting it now..."
    docker start "$CONTAINER_NAME"
    sleep 10
fi

echo "✓ Backend container is running"
echo ""

echo "2. Running migrations manually..."
docker exec "$CONTAINER_NAME" python3 -c "
import asyncio
from app.database import init_db

async def main():
    print('Initializing database and running migrations...')
    await init_db()
    print('✓ Migrations complete!')

asyncio.run(main())
"

echo ""
echo "3. Verifying database tables..."
docker exec "$CONTAINER_NAME" python3 -c "
import asyncio
import asyncpg
from app.config import get_settings

async def check():
    cfg = get_settings()
    # Parse DATABASE_URL
    # Format: postgresql://user:pass@host:port/dbname
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+)', cfg.database_url)
    if not match:
        print('Could not parse DATABASE_URL')
        return
    
    user, password, host, port, dbname = match.groups()
    
    conn = await asyncpg.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=dbname
    )
    
    # List all tables
    tables = await conn.fetch(
        'SELECT table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY table_name',
        'public'
    )
    print(f'\\n✓ Database has {len(tables)} tables:')
    for t in tables:
        count = await conn.fetchval(f'SELECT COUNT(*) FROM {t[\"table_name\"]}')
        print(f'  - {t[\"table_name\"]}: {count} rows')
    
    await conn.close()

try:
    asyncio.run(check())
except Exception as e:
    print(f'Error checking database: {e}')
    print('\\nTrying alternative check...')
    # If the above fails, just check users table
    import os
    os.system(f'docker exec trading-nexus-db-1 psql -U postgres -d trading_terminal -c \"SELECT table_name FROM information_schema.tables WHERE table_schema = \\\'public\\\'\"')
"

echo ""
echo "=========================================================="
echo "  ✓ MIGRATIONS CHECK COMPLETE"
echo "=========================================================="
echo ""
echo "If you still see errors, you may need to reset the database completely."
echo "Run: ./reset_production_database.sh"
echo ""
