#!/usr/bin/env python3
"""Get position ID for user 1003's LENSKART SOLUTIONS position"""
import asyncpg
import asyncio

async def get_position_info():
    pool = await asyncpg.create_pool(
        host='127.0.0.1',
        port=5432,
        user='postgres',
        password='postgres',
        database='trading_nexus'
    )
    
    try:
        # Get LENSKART position for user 1003 that is OPEN
        positions = await pool.fetch("""
            SELECT 
                p.id, 
                p.user_id, 
                p.symbol, 
                p.qty, 
                p.entry_price, 
                p.entry_date,
                p.status
            FROM paper_positions p
            WHERE p.user_id = 1003 
            AND LOWER(p.symbol) LIKE LOWER('%lenskart%')
            AND p.status = 'OPEN'
            ORDER BY p.entry_date DESC
            LIMIT 10
        """)
        
        print("Open LENSKART positions for user 1003:")
        for pos in positions:
            print(f"  Position ID: {pos['id']}")
            print(f"  Symbol: {pos['symbol']}")
            print(f"  Qty: {pos['qty']}")
            print(f"  Entry Price: {pos['entry_price']}")
            print(f"  Entry Date: {pos['entry_date']}")
            print(f"  Status: {pos['status']}")
            print()
        
        if positions:
            print(f"\nTo force exit, use Position ID: {positions[0]['id']}")
        else:
            print("\nNo open LENSKART positions found for user 1003")
            
    finally:
        await pool.close()

if __name__ == '__main__':
    asyncio.run(get_position_info())
