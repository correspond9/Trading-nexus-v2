#!/usr/bin/env python3
"""
Test script to debug PositionsUserwise endpoint and database state
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db, get_pool

async def check_database_state():
    """Check database state for OPEN positions"""
    await init_db()
    pool = get_pool()
    
    print("=" * 80)
    print("CHECKING DATABASE STATE")
    print("=" * 80)
    
    # Check paper_positions table
    print("\n1. Total positions in database:")
    result = await pool.fetchval("""
        SELECT COUNT(*) FROM paper_positions
    """)
    print(f"   Total positions: {result}")
    
    if result == 0:
        print("   ❌ NO POSITIONS IN DATABASE - This is likely the issue!")
        return
    
    # Status distribution
    print("\n2. Position status distribution:")
    results = await pool.fetch("""
        SELECT status, COUNT(*) as cnt FROM paper_positions GROUP BY status
    """)
    for r in results:
        print(f"   {r['status']}: {r['cnt']}")
    
    # OPEN positions
    print("\n3. Sample OPEN positions:")
    results = await pool.fetch("""
        SELECT 
            id, user_id, symbol, quantity, avg_price, status, 
            opened_at, closed_at, instrument_token
        FROM paper_positions 
        WHERE status = 'OPEN' 
        LIMIT 10
    """)
    if results:
        for r in results:
            print(f"   {r['id']}: {r['symbol']} x{r['quantity']} @ {r['avg_price']} (user={r['user_id'][:8]}...)")
    else:
        print("   ❌ NO OPEN POSITIONS FOUND!")
    
    # Check users with OPEN positions
    print("\n4. Users with OPEN positions:")
    results = await pool.fetch("""
        SELECT DISTINCT user_id, COUNT(*) as pos_count
        FROM paper_positions
        WHERE status = 'OPEN'
        GROUP BY user_id
        ORDER BY pos_count DESC
        LIMIT 5
    """)
    if results:
        for r in results:
            uid = r['user_id']
            if isinstance(uid, str):
                uid = uid[:8]
            print(f"   {uid}...: {r['pos_count']} OPEN positions")
    else:
        print("   ❌ NO USERS HAVE OPEN POSITIONS")
    
    # Check market data
    print("\n5. Checking market_data table:")
    mdata_count = await pool.fetchval("SELECT COUNT(*) FROM market_data")
    print(f"   Market data records: {mdata_count}")
    
    # Check filtered_pos CTE logic
    print("\n6. Checking IST market hours logic:")
    ist_results = await pool.fetch("""
        WITH ist_today AS (
            SELECT (date_trunc('day', NOW() AT TIME ZONE 'Asia/Kolkata')
                    AT TIME ZONE 'Asia/Kolkata') AS day_start
        )
        SELECT ist_today.day_start FROM ist_today
    """)
    if ist_results:
        print(f"   IST day start: {ist_results[0]['day_start']}")
    
    print("\n7. Checking filtered_pos results (OPEN or closed today):")
    results = await pool.fetch("""
        WITH ist_today AS (
            SELECT (date_trunc('day', NOW() AT TIME ZONE 'Asia/Kolkata')
                    AT TIME ZONE 'Asia/Kolkata') AS day_start
        ),
        filtered_pos AS (
            SELECT
                pp.*,
                COALESCE(md.ltp, pp.avg_price) AS ltp
            FROM paper_positions pp
            LEFT JOIN market_data md ON md.instrument_token = pp.instrument_token
            CROSS JOIN ist_today
            WHERE
                pp.status = 'OPEN'
                OR (
                    pp.status = 'CLOSED'
                    AND pp.closed_at IS NOT NULL
                    AND pp.closed_at >= ist_today.day_start
                )
        )
        SELECT COUNT(*) as cnt FROM filtered_pos
    """)
    print(f"   Filtered positions: {results[0]['cnt']}")
    
    # Test the actual positions_userwise query
    print("\n8. Testing full positions_userwise query:")
    rows = await pool.fetch(
        """
        WITH ist_today AS (
            SELECT (date_trunc('day', NOW() AT TIME ZONE 'Asia/Kolkata')
                    AT TIME ZONE 'Asia/Kolkata') AS day_start
        ),
        filtered_pos AS (
            SELECT
                pp.*,
                COALESCE(md.ltp, pp.avg_price) AS ltp,
                COALESCE((md.ltp - pp.avg_price) * pp.quantity, 0) AS mtm_calc
            FROM paper_positions pp
            LEFT JOIN market_data md ON md.instrument_token = pp.instrument_token
            CROSS JOIN ist_today
            WHERE
                pp.status = 'OPEN'
                OR (
                    pp.status = 'CLOSED'
                    AND pp.closed_at IS NOT NULL
                    AND pp.closed_at >= ist_today.day_start
                )
        )
        SELECT
            u.id::text AS user_id,
            u.user_no,
            COALESCE(
                NULLIF(TRIM(COALESCE(u.first_name,'') || ' ' || COALESCE(u.last_name,'')), ''),
                u.name,
                u.mobile
            ) AS display_name,
            COALESCE(
                JSON_AGG(
                    JSON_BUILD_OBJECT(
                        'instrument_token', fp.instrument_token,
                        'symbol', fp.symbol,
                        'status', fp.status
                    )
                ) FILTER (WHERE fp.instrument_token IS NOT NULL),
                '[]'::json
            ) AS positions
        FROM users u
        LEFT JOIN filtered_pos fp ON fp.user_id = u.id
        GROUP BY u.id, u.user_no, u.name, u.first_name, u.last_name, u.mobile
        ORDER BY u.user_no NULLS LAST
        LIMIT 5
        """
    )
    
    print(f"   Users returned: {len(rows)}")
    for row in rows:
        positions = row['positions'] if isinstance(row['positions'], list) else []
        open_count = sum(1 for p in positions if p.get('status') == 'OPEN')
        print(f"   - {row['user_no'] or row['user_id'][:8]}: {len(positions)} total, {open_count} open")
        if positions and open_count == 0:
            print(f"     First 2 positions: {positions[:2]}")

async def main():
    try:
        await check_database_state()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
