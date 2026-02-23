#!/bin/bash
# Database Diagnostic and Fix Script
# Run this on the VPS to check and fix database issues

echo "==========================================="
echo "Trading Nexus Database Diagnostic"
echo "==========================================="
echo ""

echo "1. Checking Docker containers..."
docker ps | grep trading

echo ""
echo "2. Checking database connection..."
docker exec trading-nexus-backend-1 python -c "
import asyncio
import asyncpg

async def test_db():
    try:
        conn = await asyncpg.connect(
            host='db',
            port=5432,
            user='postgres',
            database='trading_terminal'
        )
        print('✓ Database connection successful!')
        
        # Check if users table exists
        result = await conn.fetchval('SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)', 'users')
        print(f'✓ Users table exists: {result}')
        
        # Check if brokerage_plan column exists
        result = await conn.fetchval(
            'SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = $1 AND column_name = $2)',
            'users', 'brokerage_plan'
        )
        print(f'  brokerage_plan column exists: {result}')
        
        # Count users
        count = await conn.fetchval('SELECT COUNT(*) FROM users')
        print(f'✓ User count: {count}')
        
        await conn.close()
        return True
    except Exception as e:
        print(f'✗ Database error: {e}')
        return False

asyncio.run(test_db())
"

echo ""
echo "3. Checking backend logs (last 50 lines)..."
docker logs --tail 50 trading-nexus-backend-1 2>&1 | grep -E "(ERROR|Warning|Exception|Database)"

echo ""
echo "==========================================="
echo "To fix database issues, run:"
echo "  docker exec -it trading-nexus-backend-1 python -c 'from app.database import init_db; import asyncio; asyncio.run(init_db())'"
echo "==========================================="
