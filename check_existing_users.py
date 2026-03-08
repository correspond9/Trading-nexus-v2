"""
Check existing users in the database
"""
import asyncio
import asyncpg

async def check_users():
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="trading_nexus"
    )
    
    try:
        print("Querying existing users...")
        users = await conn.fetch("SELECT user_id, name, role, balance, is_active FROM users ORDER BY role, user_id")
        
        print(f"\nFound {len(users)} users in database:\n")
        print(f"{'User ID':<15} {'Name':<20} {'Role':<15} {'Balance':<15} {'Active':<10}")
        print("-" * 80)
        
        for user in users:
            print(f"{user['user_id']:<15} {user['name']:<20} {user['role']:<15} ₹{user['balance']:<14.2f} {user['is_active']}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_users())
