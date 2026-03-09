"""
DIAGNOSIS: Why is SUNDARAM LIMIT order not executing?
Check the complete execution flow from order placement to tick processing.
"""
import asyncio
import asyncpg
import json
from decimal import Decimal

async def main():
    print("=" * 80)
    print("LIMIT ORDER EXECUTION DIAGNOSIS")
    print("=" * 80)
    
    # Connect to DB
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="trading_terminal"
    )
    
    print("\n[1] PENDING ORDER STATUS")
    print("-" * 80)
    pending = await conn.fetch("""
        SELECT order_id, user_id, symbol, instrument_token, side, order_type,
               quantity, limit_price, trigger_price, product_type, status,
               placed_at
        FROM paper_orders
        WHERE status = 'PENDING'
        ORDER BY placed_at DESC
        LIMIT 5
    """)
    
    if not pending:
        print("    ❌ NO PENDING ORDERS FOUND!")
    else:
        for row in pending:
            print(f"\n    Order ID: {row['order_id']}")
            print(f"    Symbol: {row['symbol']}")
            print(f"    Token: {row['instrument_token']}")
            print(f"    Side: {row['side']}")
            print(f"    Type: {row['order_type']}")
            print(f"    Qty: {row['quantity']}")
            print(f"    Limit Price: {row['limit_price']}")
            print(f"    Product: {row['product_type']}")  # Check if NULL or MIS
            print(f"    Status: {row['status']}")
            print(f"    Placed: {row['placed_at']}")
    
    print("\n\n[2] MARKET DATA FOR PENDING ORDERS")
    print("-" * 80)
    for row in pending:
        token = row['instrument_token']
        md = await conn.fetchrow("""
            SELECT instrument_token, symbol, ltp, bid_depth, ask_depth, updated_at
            FROM market_data
            WHERE instrument_token = $1
        """, token)
        
        if not md:
            print(f"\n    ❌ No market data for {row['symbol']} (token: {token})")
            continue
            
        print(f"\n    Symbol: {md['symbol']}")
        print(f"    LTP: {md['ltp']}")
        print(f"    Last Update: {md['updated_at']}")
        
        # Parse depths
        bid_depth = json.loads(md['bid_depth']) if md['bid_depth'] else []
        ask_depth = json.loads(md['ask_depth']) if md['ask_depth'] else []
        
        print(f"\n    Bid Depth:")
        for i, lvl in enumerate(bid_depth[:3], 1):
            print(f"      {i}. Price: {lvl.get('price')} | Qty: {lvl.get('qty')}")
        
        print(f"\n    Ask Depth:")
        for i, lvl in enumerate(ask_depth[:3], 1):
            print(f"      {i}. Price: {lvl.get('price')} | Qty: {lvl.get('qty')}")
        
        # Check if order should have been filled
        limit_price = Decimal(str(row['limit_price']))
        side = row['side']
        
        if side == "BUY" and ask_depth:
            best_ask = Decimal(str(ask_depth[0]['price']))
            print(f"\n    📊 SHOULD EXECUTE?")
            print(f"       Order: BUY @ {limit_price}")
            print(f"       Best Ask: {best_ask}")
            if best_ask <= limit_price:
                print(f"       ✅ YES! Best ask ({best_ask}) <= limit ({limit_price})")
                print(f"       ⚠️  BUT ORDER IS STILL PENDING - EXECUTION ENGINE NOT WORKING!")
            else:
                print(f"       ❌ No. Best ask ({best_ask}) > limit ({limit_price})")
        elif side == "SELL" and bid_depth:
            best_bid = Decimal(str(bid_depth[0]['price']))
            print(f"\n    📊 SHOULD EXECUTE?")
            print(f"       Order: SELL @ {limit_price}")
            print(f"       Best Bid: {best_bid}")
            if best_bid >= limit_price:
                print(f"       ✅ YES! Best bid ({best_bid}) >= limit ({limit_price})")
                print(f"       ⚠️  BUT ORDER IS STILL PENDING - EXECUTION ENGINE NOT WORKING!")
            else:
                print(f"       ❌ No. Best bid ({best_bid}) < limit ({limit_price})")
    
    print("\n\n[3] PAPER MODE STATUS")
    print("-" * 80)
    paper_mode = await conn.fetchval("""
        SELECT value FROM settings WHERE setting_key = 'paper_mode'
    """)
    
    if paper_mode is None:
        print("    ⚠️  paper_mode setting not found in database - using default (True)")
    else:
        enabled = paper_mode.lower() in ('true', '1', 'yes')
        if enabled:
            print(f"    ✅ Paper mode: ENABLED")
        else:
            print(f"    ❌ Paper mode: DISABLED - THIS BREAKS LIMIT ORDER EXECUTION!")
    
    print("\n\n[4] INSTRUMENT MASTER DATA")
    print("-" * 80)
    for row in pending:
        token = row['instrument_token']
        inst = await conn.fetchrow("""
            SELECT instrument_token, symbol, exchange_segment, lot_size, tick_size
            FROM instrument_master
            WHERE instrument_token = $1
        """, token)
        
        if inst:
            print(f"\n    {inst['symbol']}:")
            print(f"      Token: {inst['instrument_token']}")
            print(f"      Segment: {inst['exchange_segment']}")
            print(f"      Lot Size: {inst['lot_size']}")
            print(f"      Tick Size: {inst['tick_size']}")
    
    print("\n\n[5] SUMMARY & ROOT CAUSE ANALYSIS")
    print("=" * 80)
    
    issues_found = []
    
    # Check for missing product_type
    for row in pending:
        if row['product_type'] is None or row['product_type'] == '':
            issues_found.append(
                f"❌ Order {row['order_id'][:8]}... has NULL product_type (will default to MIS)"
            )
    
    # Check for orders that should have executed
    for row in pending:
        token = row['instrument_token']
        md = await conn.fetchrow(
            "SELECT ltp, bid_depth, ask_depth FROM market_data WHERE instrument_token = $1",
            token
        )
        if md:
            bid_depth = json.loads(md['bid_depth']) if md['bid_depth'] else []
            ask_depth = json.loads(md['ask_depth']) if md['ask_depth'] else []
            
            limit_price = Decimal(str(row['limit_price']))
            side = row['side']
            
            if side == "BUY" and ask_depth:
                best_ask = Decimal(str(ask_depth[0]['price']))
                if best_ask <= limit_price:
                    issues_found.append(
                        f"❌ {row['symbol']} BUY@{limit_price} should execute (ask={best_ask})"
                    )
            elif side == "SELL" and bid_depth:
                best_bid = Decimal(str(bid_depth[0]['price']))
                if best_bid >= limit_price:
                    issues_found.append(
                        f"❌ {row['symbol']} SELL@{limit_price} should execute (bid={best_bid})"
                    )
    
    if not issues_found:
        print("\n✅ No critical issues found.")
    else:
        print(f"\n🚨 Found {len(issues_found)} critical issues:\n")
        for issue in issues_found:
            print(f"   {issue}")
    
    print("\n\n[6] LIKELY ROOT CAUSES")
    print("=" * 80)
    print("""
1. ❌ _mock_mode check in execution_engine.on_tick() (line 130-132)
   - If _mock_mode is False, on_tick() returns immediately
   - This prevents all LIMIT order execution
   
2. ❌ tick_processor.pending_count() check (line 262-264)
   - If pending_count() returns 0, execution engine is skipped
   - Check if orders are properly enqueued in memory
   
3. ❌ Product type missing in INSERT queries
   - LIMIT/SL orders don't save product_type
   - Database DEFAULT 'MIS' is used instead
   
4. ❌ WebSocket connection or tick flow
   - Check if market data ticks are flowing
   - Check if tick_processor is running
    """)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
