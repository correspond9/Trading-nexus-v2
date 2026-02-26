#!/usr/bin/env python3
"""
Debug script to test position exit endpoint
Run this to see exactly what error is occurring when trying to close positions.
"""

import asyncio
import asyncpg
import os

async def debug_position_exit():
    """Test the position close logic directly"""
    
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tradingnexus:LockAndLoad@2025@13.233.113.190:5432/tradingnexus")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Database connection successful\n")
        
        # Check paper_positions table structure
        print("=== PAPER_POSITIONS TABLE STRUCTURE ===")
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'paper_positions'
            ORDER BY ordinal_position;
        """)
        
        has_id_column = False
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
            if col['column_name'] == 'id':
                has_id_column = True
        
        if has_id_column:
            print("\n⚠️  WARNING: paper_positions has an 'id' column")
        else:
            print("\n✅ Confirmed: paper_positions has NO 'id' column (using composite key)")
        
        # Check for open positions
        print("\n=== OPEN POSITIONS ===")
        positions = await conn.fetch("""
            SELECT user_id, instrument_token, symbol, quantity, avg_price, status
            FROM paper_positions 
            WHERE quantity != 0
            ORDER BY user_id, instrument_token
            LIMIT 10;
        """)
        
        if not positions:
            print("No open positions found")
        else:
            for i, pos in enumerate(positions, 1):
                print(f"\n  Position {i}:")
                print(f"    User ID: {pos['user_id']}")
                print(f"    Instrument Token: {pos['instrument_token']}")
                print(f"    Symbol: {pos['symbol']}")
                print(f"    Quantity: {pos['quantity']}")
                print(f"    Avg Price: {pos['avg_price']}")
                print(f"    Status: {pos['status']}")
                
                # Test the UPDATE query that close_position uses
                print(f"\n    Testing UPDATE query for this position...")
                try:
                    # This is the exact query from close_position endpoint
                    test_result = await conn.execute(
                        """
                        UPDATE paper_positions
                        SET quantity = quantity  -- No actual change, just testing the query
                        WHERE user_id = $1::uuid AND instrument_token = $2
                        RETURNING *
                        """,
                        str(pos['user_id']), int(pos['instrument_token'])
                    )
                    print(f"    ✅ UPDATE query syntax is correct: {test_result}")
                except Exception as e:
                    print(f"    ❌ UPDATE query failed: {type(e).__name__}: {e}")
        
        # Check primary key constraints
        print("\n=== PRIMARY KEY CONSTRAINTS ===")
        pk_info = await conn.fetch("""
            SELECT
                tc.constraint_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = 'paper_positions';
        """)
        
        if pk_info:
            print(f"  Primary key columns: {', '.join([row['column_name'] for row in pk_info])}")
        else:
            print("  ⚠️  No primary key found!")
        
        await conn.close()
        print("\n=== DIAGNOSTIC COMPLETE ===")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_position_exit())
