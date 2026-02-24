import asyncio
import asyncpg

async def get_users():
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        'postgres://postgres:postgres@72.62.228.112:5432/trading_nexus_db'
    )
    
    # List all users to find the demo user
    print('All users in the system:')
    users = await conn.fetch(
        'SELECT id, email, username FROM users ORDER BY id LIMIT 20'
    )
    
    if users:
        for u in users:
            print(f'  ID: {u["id"]}, Email: {u["email"]}, Username: {u["username"]}')
    else:
        print('  No users found!')
    
    await conn.close()

asyncio.run(get_users())
