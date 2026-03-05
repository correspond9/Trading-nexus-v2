import asyncio
import asyncpg
import os
from decimal import Decimal

async def check_wrong_prices():
    try:
        dsn = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/trading_nexus_prod')
        conn = await asyncpg.connect(dsn)
        
        # Check for BUY orders filled above limit price
        print('=== BUY Orders Filled ABOVE Limit Price (WRONG) ===')
        wrong_buys = await conn.fetch('''
            SELECT 
                pt.position_id,
                pt.order_id,
                pt.user_id,
                pt.symbol,
                pt.side,
                pt.quantity,
                po.limit_price,
                pt.execution_price,
                pt.executed_at,
                (pt.execution_price - po.limit_price) as overpay_per_share,
                ((pt.execution_price - po.limit_price) * pt.quantity) as total_overpay
            FROM paper_trades pt
            JOIN paper_orders po ON pt.order_id = po.order_id
            WHERE pt.side = 'BUY'
            AND pt.execution_price > po.limit_price
            AND po.status IN ('COMPLETE', 'PARTIALLY_FILLED')
            ORDER BY pt.executed_at DESC
            LIMIT 20
        ''')
        
        if wrong_buys:
            for row in wrong_buys:
                print(f"Position: {row['position_id']}, Order: {row['order_id']}, User: {row['user_id']}")
                print(f"  Symbol: {row['symbol']}, Qty: {row['quantity']}")
                print(f"  Limit Price: {row['limit_price']}, Actual Execution: {row['execution_price']}")
                print(f"  Overpay: {row['total_overpay']} (per share: {row['overpay_per_share']})")
                print(f"  Executed At: {row['executed_at']}")
                print()
        else:
            print("No BUY orders filled above limit price\n")
        
        # Check for SELL orders filled below limit price
        print('\n=== SELL Orders Filled BELOW Limit Price (WRONG) ===')
        wrong_sells = await conn.fetch('''
            SELECT 
                pt.position_id,
                pt.order_id,
                pt.user_id,
                pt.symbol,
                pt.side,
                pt.quantity,
                po.limit_price,
                pt.execution_price,
                pt.executed_at,
                (po.limit_price - pt.execution_price) as undersell_per_share,
                ((po.limit_price - pt.execution_price) * pt.quantity) as total_undersell
            FROM paper_trades pt
            JOIN paper_orders po ON pt.order_id = po.order_id
            WHERE pt.side = 'SELL'
            AND pt.execution_price < po.limit_price
            AND po.status IN ('COMPLETE', 'PARTIALLY_FILLED')
            ORDER BY pt.executed_at DESC
            LIMIT 20
        ''')
        
        if wrong_sells:
            for row in wrong_sells:
                print(f"Position: {row['position_id']}, Order: {row['order_id']}, User: {row['user_id']}")
                print(f"  Symbol: {row['symbol']}, Qty: {row['quantity']}")
                print(f"  Limit Price: {row['limit_price']}, Actual Execution: {row['execution_price']}")
                print(f"  Undersell: {row['total_undersell']} (per share: {row['undersell_per_share']})")
                print(f"  Executed At: {row['executed_at']}")
                print()
        else:
            print("No SELL orders filled below limit price\n")
        
        # Summary
        buy_count = len(wrong_buys)
        sell_count = len(wrong_sells)
        print(f"\nSUMMARY: {buy_count} BUY orders + {sell_count} SELL orders = {buy_count + sell_count} total problematic orders")
        
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(check_wrong_prices())
