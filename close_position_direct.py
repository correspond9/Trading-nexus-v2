#!/usr/bin/env python3
"""Direct database script to close user 1003's LENSKART position"""
import asyncpg
import asyncio
from datetime import datetime
import os

# Get connection string from environment or use default
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'trading_nexus')

async def close_position():
    """Find and close user 1003's LENSKART position"""
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        min_size=1,
        max_size=5
    )
    
    try:
        # Find user 1003's LENSKART SOLUTIONS position that is OPEN
        positions = await pool.fetch("""
            SELECT id, symbol, qty, status, entry_price
            FROM paper_positions
            WHERE user_id = (SELECT id FROM users WHERE CAST(mobile AS TEXT) = '1003' LIMIT 1)
            AND LOWER(symbol) LIKE LOWER('%lenskart%')
            AND status = 'OPEN'
        """)
        
        if not positions:
            print("❌ No open LENSKART positions found for user 1003")
            # Try alternative: numeric user_id
            positions = await pool.fetch("""
                SELECT id, symbol, qty, status, entry_price
                FROM paper_positions
                WHERE user_id::text = '1003'
                AND LOWER(symbol) LIKE LOWER('%lenskart%')
                AND status = 'OPEN'
            """)
            
            if not positions:
                print("❌ Still no positions found. Trying direct ID = 1003...")
                positions = await pool.fetch("""
                    SELECT id, symbol, qty, status, entry_price
                    FROM paper_positions
                    WHERE user_id = (SELECT id FROM users WHERE id = '1003'::uuid LIMIT 1)
                    AND LOWER(symbol) LIKE LOWER('%lenskart%')
                    AND status = 'OPEN'
                    LIMIT 5
                """)
        
        if positions:
            print(f"✓ Found {len(positions)} LENSKART position(s):")
            for pos in positions:
                print(f"\n  Position ID: {pos['id']}")
                print(f"  Symbol: {pos['symbol']}")
                print(f"  Qty: {pos['qty']}")
                print(f"  Status: {pos['status']}")
                print(f"  Entry Price: {pos['entry_price']}")
                
                # Close this position
                result = await pool.execute("""
                    UPDATE paper_positions
                    SET status = 'CLOSED', closed_at = NOW()
                    WHERE id = $1
                """, pos['id'])
                print(f"  → Marked as CLOSED (rows updated: {result})")
        else:
            print("❌ No LENSKART positions found for user 1003")
            print("\nShowing all OPEN positions for any user containing 'lenskart':")
            all_pos = await pool.fetch("""
                SELECT user_id, id, symbol, qty, status FROM paper_positions
                WHERE LOWER(symbol) LIKE LOWER('%lenskart%')
                AND status = 'OPEN'
                LIMIT 10
            """)
            for p in all_pos:
                print(f"  User {p['user_id']}: {p['symbol']} ({p['qty']} qty)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await pool.close()

if __name__ == '__main__':
    asyncio.run(close_position())
