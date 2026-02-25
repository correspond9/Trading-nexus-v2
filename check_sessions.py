#!/usr/bin/env python3
import asyncpg
import asyncio

async def main():
    conn = await asyncpg.connect(
        host="72.62.228.112",
        user="postgres",
        password="postgres",
        database="trading_nexus"
    )
    
    rows = await conn.fetch("SELECT user_id, token, created_at, expires_at FROM user_sessions LIMIT 5")
    print(f"Total sessions found: {len(rows)}\n")
    
    for i, row in enumerate(rows, 1):
        print(f"Session {i}:")
        print(f"  user_id: {row['user_id']}")
        print(f"  token: {row['token'][:50]}...")
        print(f"  created_at: {row['created_at']}")
        print(f"  expires_at: {row['expires_at']}\n")
    
    # Check user table to see actual UUIDs
    print("\n" + "="*60)
    print("Checking users table:\n")
    users = await conn.fetch("SELECT id, email FROM users LIMIT 5")
    for user in users:
        print(f"  ID: {user['id']}")
        print(f"  Email: {user['email']}\n")
    
    await conn.close()

asyncio.run(main())
