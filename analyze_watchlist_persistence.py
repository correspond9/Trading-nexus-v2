#!/usr/bin/env python3
"""
Diagnostic: Analyze Watchlist Persistence Issues
Check why watchlist items are being cleared on refresh
"""
import asyncio
import asyncpg
import os
from datetime import datetime

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'trading_nexus'),
}

async def analyze_watchlist():
    """Analyze watchlist status and item persistence"""
    pool = await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=5)
    
    print("="*100)
    print("WATCHLIST PERSISTENCE ANALYSIS")
    print("="*100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Check watchlist structure
    print("1. WATCHLIST STRUCTURE")
    print("-" * 100)
    
    watchlists = await pool.fetch("""
        SELECT w.watchlist_id, w.user_id, w.name, COUNT(wi.instrument_token) as item_count
        FROM watchlists w
        LEFT JOIN watchlist_items wi ON w.watchlist_id = wi.watchlist_id
        GROUP BY w.watchlist_id, w.user_id, w.name
        LIMIT 10
    """)
    
    print(f"{'User ID':<40} {'Watchlist Name':<20} {'Items':<10}")
    print("-" * 100)
    for wl in watchlists:
        print(f"{str(wl['user_id']):<40} {wl['name']:<20} {wl['item_count']:<10}")
    
    print()
    
    # 2. Check watchlist items details
    print("2. WATCHLIST ITEMS DETAIL (First Watchlist)")
    print("-" * 100)
    
    if watchlists:
        first_wl = watchlists[0]
        items = await pool.fetch("""
            SELECT 
                wi.instrument_token,
                im.symbol,
                im.tier,
                im.instrument_type,
                im.expiry_date,
                wi.added_at,
                CASE WHEN EXISTS(
                    SELECT 1 FROM paper_positions pp 
                    WHERE pp.instrument_token = wi.instrument_token 
                    AND pp.quantity != 0
                ) THEN 'YES' ELSE 'NO' END as has_position
            FROM watchlist_items wi
            LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
            WHERE wi.watchlist_id = $1
            ORDER BY wi.added_at DESC
        """, first_wl['watchlist_id'])
        
        print(f"{'Symbol':<20} {'Type':<12} {'Tier':<6} {'Expiry':<15} {'Position':<10} {'Added':<20}")
        print("-" * 100)
        
        for item in items:
            symbol = item['symbol'] or 'UNKNOWN'
            tier = item['tier'] or '?'
            exp = str(item['expiry_date']) if item['expiry_date'] else 'N/A'
            added = item['added_at'].strftime('%Y-%m-%d %H:%M:%S') if item['added_at'] else 'N/A'
            
            print(f"{symbol:<20} {item['instrument_type']:<12} {tier:<6} {exp:<15} "
                  f"{item['has_position']:<10} {added:<20}")
    
    print()
    
    # 3. Check for Tier-A instruments with no positions
    print("3. TIER-A INSTRUMENTS IN WATCHLIST (On-Demand Subscription)")
    print("-" * 100)
    
    tier_a_no_position = await pool.fetch("""
        SELECT 
            im.symbol,
            im.instrument_type,
            im.tier,
            im.expiry_date,
            COUNT(DISTINCT wi.watchlist_id) as in_watchlist_count,
            COUNT(CASE WHEN pp.quantity != 0 THEN 1 END) as position_count
        FROM instrument_master im
        JOIN watchlist_items wi ON wi.instrument_token = im.instrument_token
        LEFT JOIN paper_positions pp ON pp.instrument_token = im.instrument_token AND pp.quantity != 0
        WHERE im.tier = 'A'
        GROUP BY im.symbol, im.instrument_type, im.tier, im.expiry_date
        HAVING COUNT(CASE WHEN pp.quantity != 0 THEN 1 END) = 0
        LIMIT 20
    """)
    
    print(f"Found {len(tier_a_no_position)} Tier-A items in watchlist with NO open positions")
    print(f"{'Symbol':<20} {'Type':<12} {'Expiry':<15} {'In Watchlists':<15}")
    print("-" * 100)
    
    for item in tier_a_no_position:
        exp = str(item['expiry_date']) if item['expiry_date'] else 'N/A'
        print(f"{item['symbol']:<20} {item['instrument_type']:<12} {exp:<15} {item['in_watchlist_count']:<15}")
    
    print()
    
    # 4. Check Tier-A vs Tier-B distinction
    print("4. WATCHLIST ITEM COMPOSITION (Tier-A vs Tier-B)")
    print("-" * 100)
    
    tier_breakdown = await pool.fetch("""
        SELECT 
            im.tier,
            COUNT(*) as item_count,
            COUNT(DISTINCT wi.watchlist_id) as watchlist_count,
            COUNT(DISTINCT pp.order_id) as with_positions
        FROM watchlist_items wi
        LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
        LEFT JOIN paper_positions pp ON pp.instrument_token = wi.instrument_token AND pp.quantity != 0
        WHERE im.tier IS NOT NULL
        GROUP BY im.tier
    """)
    
    print(f"{'Tier':<8} {'Total Items':<15} {'In Watchlists':<15} {'With Position':<15}")
    print("-" * 100)
    for row in tier_breakdown:
        print(f"{row['tier']:<8} {row['item_count']:<15} {row['watchlist_count']:<15} "
              f"{row['with_positions']:<15}")
    
    print()
    
    # 5. Check subscription state
    print("5. SUBSCRIPTION STATE TRACKING")
    print("-" * 100)
    
    sub_state = await pool.fetch("""
        SELECT 
            CASE WHEN is_active THEN 'Active' ELSE 'Inactive' END as status,
            in_watchlist,
            COUNT(*) as count
        FROM subscription_state
        GROUP BY is_active, in_watchlist
    """)
    
    print(f"{'Status':<12} {'In Watchlist':<15} {'Count':<10}")
    print("-" * 100)
    for row in sub_state:
        print(f"{row['status']:<12} {str(row['in_watchlist']):<15} {row['count']:<10}")
    
    print()
    
    # 6. Recommendations
    print("="*100)
    print("RECOMMENDATIONS")
    print("="*100)
    print("""
ISSUE: Watchlist items disappear on refresh

POSSIBLE CAUSES:
1. Items not being returned from GET /watchlist/{user_id} endpoint
2. Items being deleted from database (watchlist_items table)
3. Frontend localStorage being cleared
4. Tier-A items being auto-removed based on position status

DESIRED BEHAVIOR (Per Your Requirement):
- Tier-B (Subscribed) items: Keep permanently until manually deleted
- Tier-A (On-Demand) items: Keep if in open position, auto-remove if not

IMPLEMENTATION PLAN:
1. Modify GET /watchlist/{user_id} to:
   - Return Tier-B items (keep all)
   - Return Tier-A items only if in open positions
   OR
   - Return all items, let frontend decide based on Tier and Position status

2. Add Tier and position info to watchlist response

3. Frontend cleanup:
   - On refresh, remove Tier-A items with no positions
   - Keep Tier-B items regardless

4. Background job:
   - Daily cleanup of Tier-A instruments from watchlist if no position
    """)
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(analyze_watchlist())
