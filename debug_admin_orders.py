import asyncio
import asyncpg
import os
from datetime import date

async def main():
    # Get database connection details from environment or use defaults
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_name = os.getenv('DB_NAME', 'trading_nexus')
    db_user = os.getenv('DB_USER', 'postgres')
    db_pass = os.getenv('DB_PASS', '')
    
    try:
        conn = await asyncpg.connect(user=db_user, password=db_pass, database=db_name, host=db_host, port=db_port)
        
        # First, get the SUPER_ADMIN user's ID
        admin_user = await conn.fetchrow("SELECT id, mobile, role FROM users WHERE mobile = '9999999999' OR email = 'admin@example.com'")
        print(f"Admin user: {admin_user}")
        
        if admin_user:
            admin_id = admin_user['id']
            
            # Check how many FILLED orders the admin user has
            count = await conn.fetchval("SELECT COUNT(*) FROM paper_orders WHERE status = 'FILLED' AND user_id = $1", admin_id)
            print(f"Admin user {admin_id} has {count} FILLED orders")
            
            # Get all unique user_ids that have FILLED orders
            users_with_filled = await conn.fetch("SELECT DISTINCT user_id FROM paper_orders WHERE status = 'FILLED' LIMIT 5")
            print(f"\nUsers with FILLED orders: {users_with_filled}")
            
            # Check total FILLED orders in system
            total_filled = await conn.fetchval("SELECT COUNT(*) FROM paper_orders WHERE status = 'FILLED'")
            print(f"Total FILLED orders in system: {total_filled}")
            
            # Get one sample FILLED order
            sample = await conn.fetchrow("SELECT * FROM paper_orders WHERE status = 'FILLED' LIMIT 1")
            print(f"\nSample FILLED order:")
            print(f"  Order ID: {sample['id']}")
            print(f"  User ID: {sample['user_id']}")
            print(f"  Symbol: {sample['symbol']}")
            print(f"  Status: {sample['status']}")
            print(f"  Placed At: {sample['placed_at']}")
        
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
