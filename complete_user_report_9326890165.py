import psycopg2
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    host="72.62.228.112",
    port=5432,
    database="trading_nexus",
    user="postgres",
    password="hbP2vHzLCauHB5SUJNDX2uj6PH19oF"
)

mobile = "9326890165"

print("=" * 80)
print(f"COMPLETE USER REPORT FOR MOBILE: {mobile}")
print(f"Generated at: {datetime.now()}")
print("=" * 80)

cur = conn.cursor()

# 1. USER BASIC INFO
print("\n" + "=" * 80)
print("1. USER BASIC INFORMATION")
print("=" * 80)
cur.execute("""
    SELECT u.id, u.mobile, u.created_at, u.is_active
    FROM users u
    WHERE u.mobile = %s
""", (mobile,))
user_row = cur.fetchone()
if not user_row:
    print(f"❌ No user found with mobile {mobile}")
    conn.close()
    exit(1)

user_id, user_mobile, created_at, is_active = user_row
print(f"User ID: {user_id}")
print(f"Mobile: {user_mobile}")
print(f"Created At: {created_at}")
print(f"Active: {'✅ Yes' if is_active else '❌ No'}")

# 2. MARGIN INFORMATION
print("\n" + "=" * 80)
print("2. MARGIN INFORMATION")
print("=" * 80)
cur.execute("""
    SELECT 
        pa.margin_allotted,
        pa.created_at as account_created
    FROM paper_accounts pa
    WHERE pa.user_id = %s
""", (user_id,))
account_row = cur.fetchone()
if not account_row:
    print(f"❌ No paper account found for user {user_id}")
    margin_allotted = 0
else:
    margin_allotted, account_created = account_row
    print(f"Margin Allotted: ₹{margin_allotted:,.2f}")
    print(f"Account Created: {account_created}")

# Calculate used margin from positions
cur.execute("""
    SELECT 
        pp.instrument_token,
        pp.symbol,
        pp.exchange_segment,
        pp.quantity,
        pp.product_type,
        pp.average_price,
        pp.last_price,
        calculate_position_margin(
            pp.instrument_token,
            pp.symbol,
            pp.exchange_segment::text,
            pp.quantity,
            pp.product_type::text
        ) as margin_used
    FROM paper_positions pp
    WHERE pp.user_id = %s
      AND pp.status = 'OPEN'
""", (user_id,))
position_margins = cur.fetchall()

total_used_margin = sum(row[7] for row in position_margins if row[7] is not None)
available_margin = margin_allotted - total_used_margin

print(f"Used Margin: ₹{total_used_margin:,.2f}")
print(f"Available Margin: ₹{available_margin:,.2f}")
print(f"Usage Percentage: {(total_used_margin/margin_allotted*100) if margin_allotted > 0 else 0:.2f}%")

# 3. POSITIONS DETAILS
print("\n" + "=" * 80)
print("3. OPEN POSITIONS")
print("=" * 80)
if position_margins:
    print(f"Total Open Positions: {len(position_margins)}")
    print()
    for idx, pos in enumerate(position_margins, 1):
        token, symbol, exchange, qty, product, avg_price, ltp, margin = pos
        pnl = (ltp - avg_price) * qty if ltp and avg_price else 0
        print(f"Position #{idx}:")
        print(f"  Symbol: {symbol}")
        print(f"  Exchange: {exchange}")
        print(f"  Quantity: {qty:,}")
        print(f"  Product Type: {product}")
        print(f"  Average Price: ₹{avg_price:.2f}")
        print(f"  Last Price: ₹{ltp:.2f}" if ltp else "  Last Price: N/A")
        print(f"  P&L: ₹{pnl:,.2f} ({'+' if pnl >= 0 else ''}{pnl:.2f})")
        print(f"  Margin Used: ₹{margin:,.2f}" if margin else "  Margin Used: N/A")
        print()
else:
    print("No open positions")

# 4. CLOSED POSITIONS
print("\n" + "=" * 80)
print("4. CLOSED POSITIONS (Last 10)")
print("=" * 80)
cur.execute("""
    SELECT 
        pp.symbol,
        pp.exchange_segment,
        pp.quantity,
        pp.average_price,
        pp.realized_pnl,
        pp.closed_at
    FROM paper_positions pp
    WHERE pp.user_id = %s
      AND pp.status = 'CLOSED'
    ORDER BY pp.closed_at DESC
    LIMIT 10
""", (user_id,))
closed_positions = cur.fetchall()

if closed_positions:
    total_realized = sum(row[4] for row in closed_positions if row[4] is not None)
    print(f"Total Closed Positions (showing last 10): {len(closed_positions)}")
    print(f"Total Realized P&L (last 10): ₹{total_realized:,.2f}")
    print()
    for idx, pos in enumerate(closed_positions, 1):
        symbol, exchange, qty, avg_price, pnl, closed_at = pos
        print(f"Position #{idx}:")
        print(f"  Symbol: {symbol}")
        print(f"  Exchange: {exchange}")
        print(f"  Quantity: {qty:,}")
        print(f"  Average Price: ₹{avg_price:.2f}" if avg_price else "  Average Price: N/A")
        print(f"  Realized P&L: ₹{pnl:,.2f}" if pnl else "  Realized P&L: N/A")
        print(f"  Closed At: {closed_at}")
        print()
else:
    print("No closed positions")

# 5. ALL ORDERS
print("\n" + "=" * 80)
print("5. ALL ORDERS (PENDING & COMPLETED)")
print("=" * 80)
cur.execute("""
    SELECT 
        po.id,
        po.symbol,
        po.exchange_segment,
        po.side,
        po.order_type,
        po.product_type,
        po.quantity,
        po.price,
        po.status,
        po.filled_quantity,
        po.average_price,
        po.created_at,
        po.updated_at,
        (SELECT COUNT(*) FROM paper_trades pt WHERE pt.order_id = po.id) as trade_count
    FROM paper_orders po
    WHERE po.user_id = %s
    ORDER BY po.created_at DESC
""", (user_id,))
orders = cur.fetchall()

if orders:
    pending_orders = [o for o in orders if o[8] in ('PENDING', 'OPEN', 'PARTIALLY_FILLED')]
    completed_orders = [o for o in orders if o[8] in ('FILLED', 'EXECUTED')]
    cancelled_orders = [o for o in orders if o[8] in ('CANCELLED', 'REJECTED')]
    
    print(f"Total Orders: {len(orders)}")
    print(f"  Pending/Open: {len(pending_orders)}")
    print(f"  Completed: {len(completed_orders)}")
    print(f"  Cancelled/Rejected: {len(cancelled_orders)}")
    print()
    
    # PENDING ORDERS
    if pending_orders:
        print("--- PENDING/OPEN ORDERS ---")
        for idx, order in enumerate(pending_orders, 1):
            order_id, symbol, exchange, side, order_type, product, qty, price, status, filled_qty, avg_price, created, updated, trade_count = order
            print(f"\nOrder #{order_id}:")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Type: {order_type}")
            print(f"  Product: {product}")
            print(f"  Quantity: {qty:,}")
            print(f"  Price: ₹{price:.2f}" if price else "  Price: MARKET")
            print(f"  Status: {status}")
            print(f"  Filled: {filled_qty}/{qty}")
            print(f"  Avg Price: ₹{avg_price:.2f}" if avg_price else "  Avg Price: N/A")
            print(f"  Created: {created}")
            print(f"  Trades: {trade_count}")
        print()
    
    # COMPLETED ORDERS (Last 10)
    if completed_orders:
        print("--- COMPLETED ORDERS (Last 10) ---")
        for idx, order in enumerate(completed_orders[:10], 1):
            order_id, symbol, exchange, side, order_type, product, qty, price, status, filled_qty, avg_price, created, updated, trade_count = order
            print(f"\nOrder #{order_id}:")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Type: {order_type}")
            print(f"  Product: {product}")
            print(f"  Quantity: {qty:,}")
            print(f"  Price: ₹{price:.2f}" if price else "  Price: MARKET")
            print(f"  Status: {status}")
            print(f"  Filled: {filled_qty}/{qty}")
            print(f"  Avg Price: ₹{avg_price:.2f}" if avg_price else "  Avg Price: N/A")
            print(f"  Created: {created}")
            print(f"  Trades: {trade_count}")
        print()
    
    # CANCELLED ORDERS (Last 5)
    if cancelled_orders:
        print("--- CANCELLED/REJECTED ORDERS (Last 5) ---")
        for idx, order in enumerate(cancelled_orders[:5], 1):
            order_id, symbol, exchange, side, order_type, product, qty, price, status, filled_qty, avg_price, created, updated, trade_count = order
            print(f"\nOrder #{order_id}:")
            print(f"  Symbol: {symbol}")
            print(f"  Side: {side}")
            print(f"  Status: {status}")
            print(f"  Quantity: {qty:,}")
            print(f"  Created: {created}")
else:
    print("No orders found")

# 6. RECENT TRADES
print("\n" + "=" * 80)
print("6. RECENT TRADES (Last 20)")
print("=" * 80)
cur.execute("""
    SELECT 
        pt.id,
        pt.order_id,
        po.symbol,
        po.side,
        pt.quantity,
        pt.price,
        pt.executed_at
    FROM paper_trades pt
    JOIN paper_orders po ON pt.order_id = po.id
    WHERE po.user_id = %s
    ORDER BY pt.executed_at DESC
    LIMIT 20
""", (user_id,))
trades = cur.fetchall()

if trades:
    print(f"Total Recent Trades: {len(trades)}")
    print()
    for idx, trade in enumerate(trades, 1):
        trade_id, order_id, symbol, side, qty, price, executed_at = trade
        print(f"Trade #{trade_id} (Order #{order_id}):")
        print(f"  Symbol: {symbol}")
        print(f"  Side: {side}")
        print(f"  Quantity: {qty:,}")
        print(f"  Price: ₹{price:.2f}")
        print(f"  Executed: {executed_at}")
        print()
else:
    print("No trades found")

# 7. PORTFOLIO SUMMARY
print("\n" + "=" * 80)
print("7. PORTFOLIO SUMMARY")
print("=" * 80)
total_positions_value = sum((row[6] or 0) * row[3] for row in position_margins)
total_invested = sum((row[5] or 0) * row[3] for row in position_margins)
unrealized_pnl = total_positions_value - total_invested

print(f"Number of Open Positions: {len(position_margins)}")
print(f"Total Invested Value: ₹{total_invested:,.2f}")
print(f"Current Portfolio Value: ₹{total_positions_value:,.2f}")
print(f"Unrealized P&L: ₹{unrealized_pnl:,.2f} ({'+' if unrealized_pnl >= 0 else ''}{(unrealized_pnl/total_invested*100) if total_invested > 0 else 0:.2f}%)")

# Get total realized P&L
cur.execute("""
    SELECT COALESCE(SUM(realized_pnl), 0)
    FROM paper_positions
    WHERE user_id = %s AND status = 'CLOSED'
""", (user_id,))
total_realized_pnl = cur.fetchone()[0]

print(f"Total Realized P&L (All Time): ₹{total_realized_pnl:,.2f}")
print(f"Total P&L: ₹{unrealized_pnl + total_realized_pnl:,.2f}")

print("\n" + "=" * 80)
print("END OF REPORT")
print("=" * 80)

cur.close()
conn.close()
