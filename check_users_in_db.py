import asyncio
import asyncpg

async def check_users():
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        'postgres://postgres:postgres@72.62.228.112:5432/trading_nexus_db'
    )
    
    # Check if users table exists and get count
    try:
        count = await conn.fetchval('SELECT COUNT(*) FROM users')
        print(f"Total users in database: {count}")
        
        if count > 0:
            print("\nFirst 10 users:")
            users = await conn.fetch(
                'SELECT id, email, first_name, last_name, mobile, role, status FROM users ORDER BY id LIMIT 10'
            )
            for u in users:
                print(f"  ID: {u['id']}")
                print(f"    Email: {u['email']}")
                print(f"    Name: {u['first_name']} {u['last_name']}")
                print(f"    Mobile: {u['mobile']}")
                print(f"    Role: {u['role']}")
                print(f"    Status: {u['status']}")
                print()
        else:
            print("No users found in database!")
            
    except Exception as e:
        print(f"Error: {e}")
    
    await conn.close()

asyncio.run(check_users())
