#!/usr/bin/env python3
import asyncpg
import asyncio
import sys

async def main():
    try:
        conn = await asyncpg.connect(
            host="72.62.228.112",
            user="postgres",
            password="postgres",
            database="trading_nexus",
            timeout=5
        )
        
        # Check user_sessions
        print("="*70)
        print("USER SESSIONS IN DATABASE:")
        print("="*70)
        rows = await conn.fetch(
            "SELECT user_id, token, created_at, expires_at FROM user_sessions ORDER BY created_at DESC LIMIT 3"
        )
        
        if rows:
            for i, row in enumerate(rows, 1):
                print(f"\nSession {i}:")
                print(f"  user_id type: {type(row['user_id'])}")
                print(f"  user_id: {row['user_id']}")
                print(f"  token (first 40 chars): {str(row['token'])[:40]}...")
        else:
            print("No sessions found!")
        
        # Check users table
        print("\n" + "="*70)
        print("USERS IN DATABASE:")
        print("="*70)
        users = await conn.fetch("SELECT id, email FROM users LIMIT 3")
        for user in users:
            print(f"\nUser ID: {user['id']}")
            print(f"  Type: {type(user['id'])}")
            print(f"  Email: {user['email']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
