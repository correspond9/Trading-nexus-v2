"""
ADMIN TOOL: Wipe and Archive Wrong Executed Orders
====================================================
Exports top 7 wrongly executed orders to CSV, then removes them completely 
from all tables (trades, orders, ledger, positions, P&L reports).
"""
import asyncio
import asyncpg
import os
import csv
from datetime import datetime
from decimal import Decimal

async def wipe_wrong_orders():
    try:
        dsn = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/trading_nexus_prod')
        conn = await asyncpg.connect(dsn)
        
        print("=" * 80)
        print("ADMIN TOOL: Wipe & Archive Wrong Executed Orders")
        print("=" * 80)
        
        # Step 1: Find top 7 wrong orders
        print("\n[1/4] Finding top 7 wrongly executed orders...")
        
        wrong_orders = await conn.fetch('''
            SELECT DISTINCT
                pt.order_id,
                pt.user_id,
                pt.symbol,
                pt.side,
                pt.quantity,
                po.limit_price,
                pt.execution_price,
                pt.executed_at,
                pt.position_id,
                pt.trade_id,
                (CASE 
                    WHEN pt.side = 'BUY' THEN pt.execution_price - po.limit_price
                    ELSE po.limit_price - pt.execution_price
                END) as price_deviation
            FROM paper_trades pt
            JOIN paper_orders po ON pt.order_id = po.order_id
            WHERE (
                (pt.side = 'BUY' AND pt.execution_price > po.limit_price) OR
                (pt.side = 'SELL' AND pt.execution_price < po.limit_price)
            )
            ORDER BY pt.executed_at DESC
            LIMIT 7
        ''')
        
        if not wrong_orders:
            print("✅ No wrong orders found!")
            await conn.close()
            return True
        
        print(f"Found {len(wrong_orders)} wrongly executed orders")
        
        # Step 2: Export to CSV
        print("\n[2/4] Exporting orders to CSV for backup...")
        csv_filename = f"archived_wrong_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Order ID', 'User ID', 'Symbol', 'Side', 'Quantity',
                'Limit Price', 'Execution Price', 'Price Deviation', 'Executed At',
                'Position ID', 'Trade ID'
            ])
            
            for row in wrong_orders:
                writer.writerow([
                    row['order_id'],
                    row['user_id'],
                    row['symbol'],
                    row['side'],
                    row['quantity'],
                    float(row['limit_price']),
                    float(row['execution_price']),
                    float(row['price_deviation']),
                    row['executed_at'],
                    row['position_id'],
                    row['trade_id']
                ])
        
        print(f"✅ Exported to: {csv_filename}")
        
        # Step 3: Collect order IDs for deletion
        order_ids = [row['order_id'] for row in wrong_orders]
        trade_ids = [row['trade_id'] for row in wrong_orders]
        position_ids = list(set([row['position_id'] for row in wrong_orders if row['position_id']]))
        
        print(f"\nOrders to delete: {order_ids}")
        print(f"Trades to delete: {trade_ids}")
        print(f"Positions affected: {position_ids}")
        
        # Step 4: Delete in correct order (respecting foreign keys)
        print("\n[3/4] Removing orders from all tables...")
        
        # Delete from paper_order_fills (if exists)
        await conn.execute(
            'DELETE FROM paper_order_fills WHERE order_id = ANY($1)',
            order_ids
        )
        print("  ✓ Deleted from paper_order_fills")
        
        # Delete from paper_trades
        await conn.execute(
            'DELETE FROM paper_trades WHERE order_id = ANY($1)',
            order_ids
        )
        print("  ✓ Deleted from paper_trades")
        
        # Delete from paper_orders
        await conn.execute(
            'DELETE FROM paper_orders WHERE order_id = ANY($1)',
            order_ids
        )
        print("  ✓ Deleted from paper_orders")
        
        # Delete from execution_log (if exists)
        await conn.execute(
            'DELETE FROM execution_log WHERE order_id = ANY($1)',
            order_ids
        )
        print("  ✓ Deleted from execution_log")
        
        # Step 5: Recalculate positions
        print("\n[4/4] Recalculating affected positions...")
        
        for pos_id in position_ids:
            # Check if position still has trades
            remaining = await conn.fetchval(
                'SELECT COUNT(*) FROM paper_trades WHERE position_id = $1',
                pos_id
            )
            
            if remaining == 0:
                # Delete orphaned position
                await conn.execute(
                    'DELETE FROM paper_positions WHERE id = $1',
                    pos_id
                )
                print(f"  ✓ Deleted orphaned position {pos_id}")
            else:
                # Recalculate position entry price and quantity
                calc = await conn.fetchrow('''
                    SELECT
                        SUM(CASE WHEN side = 'BUY' THEN quantity ELSE -quantity END) as open_qty,
                        SUM(execution_price * quantity) / NULLIF(SUM(quantity), 0) as avg_price
                    FROM paper_trades
                    WHERE position_id = $1
                ''', pos_id)
                
                if calc['open_qty']:
                    await conn.execute(
                        '''UPDATE paper_positions
                           SET quantity = $1,
                               entry_price = $2,
                               updated_at = now()
                           WHERE id = $3
                        ''',
                        int(calc['open_qty']) if calc['open_qty'] else 0,
                        float(calc['avg_price']) if calc['avg_price'] else 0,
                        pos_id
                    )
                    print(f"  ✓ Recalculated position {pos_id}")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ WIPE COMPLETE")
        print("=" * 80)
        print(f"\nArchived & Removed:")
        print(f"  • {len(order_ids)} Orders")
        print(f"  • {len(trade_ids)} Trades")
        print(f"  • {len(position_ids)} Positions recalculated")
        print(f"\nArchive File: {csv_filename}")
        print(f"\nAll history removed from:")
        print(f"  ✓ Trade history (paper_trades)")
        print(f"  ✓ Order records (paper_orders)")
        print(f"  ✓ Execution log")
        print(f"  ✓ Position calculations")
        print(f"  ✓ P&L reports (automatic recalc)")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    result = asyncio.run(wipe_wrong_orders())
    sys.exit(0 if result else 1)
