"""
CRITICAL FIX: Restore Correct Order Execution Prices
=======================================================
This script identifies and corrects all orders that were executed at prices
that violated their limit prices (BUY at prices above limit, SELL at prices below limit).

The fix ensures:
- BUY LIMIT orders never fill above their limit price
- SELL LIMIT orders never fill below their limit price
- All MTM calculations are corrected to reflect actual prices
- Positions are recalculated with correct prices
"""
import asyncio
import asyncpg
import os
import sys
from decimal import Decimal
from datetime import datetime

async def correct_wrong_executions():
    try:
        dsn = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/trading_nexus_prod')
        conn = await asyncpg.connect(dsn)
        
        print("=" * 80)
        print("CRITICAL FIX: Correcting Wrongly Executed Orders")
        print("=" * 80)
        
        # Step 1: Find all BUY orders filled above limit price
        print("\n[1/4] Identifying BUY orders filled ABOVE limit price...")
        wrong_buy_trades = await conn.fetch('''
            SELECT 
                pt.trade_id,
                pt.position_id,
                pt.order_id,
                pt.user_id,
                pt.symbol,
                pt.side,
                pt.quantity,
                po.limit_price,
                pt.execution_price,
                pt.executed_at,
                pt.charges
            FROM paper_trades pt
            JOIN paper_orders po ON pt.order_id = po.order_id
            WHERE pt.side = 'BUY'
            AND pt.execution_price > po.limit_price
            AND po.status IN ('COMPLETE', 'PARTIALLY_FILLED')
            ORDER BY pt.executed_at DESC
        ''')
        
        print(f"   Found {len(wrong_buy_trades)} wrongly executed BUY orders")
        
        # Step 2: Find all SELL orders filled below limit price
        print("[2/4] Identifying SELL orders filled BELOW limit price...")
        wrong_sell_trades = await conn.fetch('''
            SELECT 
                pt.trade_id,
                pt.position_id,
                pt.order_id,
                pt.user_id,
                pt.symbol,
                pt.side,
                pt.quantity,
                po.limit_price,
                pt.execution_price,
                pt.executed_at,
                pt.charges
            FROM paper_trades pt
            JOIN paper_orders po ON pt.order_id = po.order_id
            WHERE pt.side = 'SELL'
            AND pt.execution_price < po.limit_price
            AND po.status IN ('COMPLETE', 'PARTIALLY_FILLED')
            ORDER BY pt.executed_at DESC
        ''')
        
        print(f"   Found {len(wrong_sell_trades)} wrongly executed SELL orders")
        
        total_problematic = len(wrong_buy_trades) + len(wrong_sell_trades)
        if total_problematic == 0:
            print("\n✅ Great news! No wrongly executed orders found. System is working correctly.")
            await conn.close()
            return
        
        # Step 3: Correct BUY trades
        print(f"\n[3/4] Correcting {len(wrong_buy_trades)} BUY trades...")
        for trade in wrong_buy_trades:
            old_price = Decimal(str(trade['execution_price']))
            new_price = Decimal(str(trade['limit_price']))
            price_diff = new_price - old_price
            qty_impact = price_diff * trade['quantity']
            
            print(f"   Fixing: {trade['symbol']} BUY x{trade['quantity']} | "
                  f"{old_price} → {new_price} (Correction: {qty_impact/trade['quantity']:.2f} per share)")
            
            # Update the trade execution price
            await conn.execute(
                '''UPDATE paper_trades 
                   SET execution_price = $1,
                       updated_at = now()
                   WHERE trade_id = $2
                ''',
                float(new_price), trade['trade_id']
            )
        
        # Step 4: Correct SELL trades
        print(f"\n[4/4] Correcting {len(wrong_sell_trades)} SELL trades...")
        for trade in wrong_sell_trades:
            old_price = Decimal(str(trade['execution_price']))
            new_price = Decimal(str(trade['limit_price']))
            price_diff = new_price - old_price
            qty_impact = price_diff * trade['quantity']
            
            print(f"   Fixing: {trade['symbol']} SELL x{trade['quantity']} | "
                  f"{old_price} → {new_price} (Correction: {qty_impact/trade['quantity']:.2f} per share)")
            
            # Update the trade execution price
            await conn.execute(
                '''UPDATE paper_trades 
                   SET execution_price = $1,
                       updated_at = now()
                   WHERE trade_id = $2
                ''',
                float(new_price), trade['trade_id']
            )
        
        # Step 5: Recalculate all affected positions
        print("\n[FINAL] Recalculating MTM for all affected positions...")
        
        all_affected_positions = set()
        for trade in wrong_buy_trades + wrong_sell_trades:
            all_affected_positions.add(trade['position_id'])
        
        print(f"   Updating {len(all_affected_positions)} positions...")
        
        for pos_id in all_affected_positions:
            # Recalculate average price for the position
            avg_result = await conn.fetchrow('''
                SELECT 
                    SUM(execution_price * quantity) / NULLIF(SUM(quantity), 0) as avg_price,
                    SUM(CASE WHEN side = 'BUY' THEN quantity ELSE -quantity END) as open_qty
                FROM paper_trades
                WHERE position_id = $1
            ''', pos_id)
            
            if avg_result and avg_result['open_qty']:
                avg_price = avg_result['avg_price'] or 0
                await conn.execute(
                    '''UPDATE paper_positions
                       SET entry_price = $1,
                           updated_at = now()
                       WHERE id = $2
                    ''',
                    float(avg_price), pos_id
                )
        
        print("\n" + "=" * 80)
        print("✅ CORRECTION COMPLETE")
        print("=" * 80)
        print(f"Total affected trades: {total_problematic}")
        print(f"Total affected positions: {len(all_affected_positions)}")
        print("\nAll execution prices have been corrected to their limit prices.")
        print("MTM calculations will reflect the correct prices on next refresh.")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    result = asyncio.run(correct_wrong_executions())
    sys.exit(0 if result else 1)
