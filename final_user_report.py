import paramiko
import re

# SSH connection details
hostname = "72.62.228.112"
username = "root"
key_path = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"

# Database details
db_container = "db-x8gg0og8440wkgc8ow0ococs-064710036566"
db_name = "trading_terminal"
db_user = "postgres"

mobile = "9326890165"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def run_query_output(ssh, query):
    """Run a SQL query and return output"""
    cmd = f"""docker exec {db_container} psql -U {db_user} -d {db_name} -c "{query}" """
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8')
    return output

try:
    # Load private key
    private_key = paramiko.Ed25519Key.from_private_key_file(key_path)
    
    # Connect
    print(f"Connecting to {hostname}...")
    ssh.connect(hostname, username=username, pkey=private_key, timeout=10)
    print("✅ Connected successfully\n")
    
    print("=" * 100)
    print(f"COMPLETE USER REPORT FOR MOBILE: {mobile}")
    print("=" * 100)
    
    # 1. Get user info and extract UUID
    print("\n1. USER BASIC INFORMATION")
    print("=" * 100)
    query = f"SELECT id, mobile, created_at, is_active FROM users WHERE mobile = '{mobile}';"
    output = run_query_output(ssh, query)
    print(output)
    
    # Extract user_id (UUID format)
    uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    match = re.search(uuid_pattern, output)
    if not match:
        print("❌ Could not extract user ID!")
        exit(1)
    
    user_id = match.group(1)
    print(f"\n➡️ User ID: {user_id}")
    
    # 2. Margin information
    print("\n2. MARGIN INFORMATION")
    print("=" * 100)
    query = f"""
    SELECT 
        ROUND(pa.margin_allotted::numeric, 2) as margin_allotted,
        pa.created_at as account_created,
        ROUND(COALESCE((
            SELECT SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment::text,
                    pp.quantity,
                    pp.product_type::text
                )
            )
            FROM paper_positions pp
            WHERE pp.user_id = '{user_id}' AND pp.status = 'OPEN'
        ), 0)::numeric, 2) as used_margin,
        ROUND((pa.margin_allotted - COALESCE((
            SELECT SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment::text,
                    pp.quantity,
                    pp.product_type::text
                )
            )
            FROM paper_positions pp
            WHERE pp.user_id = '{user_id}' AND pp.status = 'OPEN'
        ), 0))::numeric, 2) as available_margin
    FROM paper_accounts pa
    WHERE pa.user_id = '{user_id}';
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 3. Open positions
    print("\n3. OPEN POSITIONS")
    print("=" * 100)
    query = f"""
    SELECT 
        pp.symbol,
        pp.exchange_segment as exchange,
        pp.quantity as qty,
        pp.product_type as product,
        ROUND(pp.average_price::numeric, 2) as avg_price,
        ROUND(pp.last_price::numeric, 2) as last_price,
        ROUND(((pp.last_price - pp.average_price) * pp.quantity)::numeric, 2) as pnl,
        ROUND(calculate_position_margin(
            pp.instrument_token,
            pp.symbol,
            pp.exchange_segment::text,
            pp.quantity,
            pp.product_type::text
        )::numeric, 2) as margin
    FROM paper_positions pp
    WHERE pp.user_id = '{user_id}' AND pp.status = 'OPEN'
    ORDER BY pp.created_at DESC;
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 4. Closed positions (last 10)
    print("\n4. CLOSED POSITIONS (Last 10)")
    print("=" * 100)
    query = f"""
    SELECT 
        pp.symbol,
        pp.exchange_segment as exchange,
        pp.quantity as qty,
        ROUND(pp.average_price::numeric, 2) as avg_price,
        ROUND(pp.realized_pnl::numeric, 2) as pnl,
        pp.closed_at
    FROM paper_positions pp
    WHERE pp.user_id = '{user_id}' AND pp.status = 'CLOSED'
    ORDER BY pp.closed_at DESC
    LIMIT 10;
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 5. Order summary
    print("\n5. ORDERS SUMMARY")
    print("=" * 100)
    query = f"""
    SELECT 
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')) as pending,
        COUNT(*) FILTER (WHERE status IN ('FILLED', 'EXECUTED')) as completed,
        COUNT(*) FILTER (WHERE status IN ('CANCELLED', 'REJECTED')) as cancelled
    FROM paper_orders
    WHERE user_id = '{user_id}';
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 6. Pending/Open orders
    print("\n6. PENDING/OPEN ORDERS")
    print("=" * 100)
    query = f"""
    SELECT 
        LEFT(po.id::text, 8) as order_id,
        po.symbol,
        po.side,
        po.order_type as type,
        po.quantity as qty,
        ROUND(COALESCE(po.price, 0)::numeric, 2) as price,
        po.status,
        po.filled_quantity as filled,
        po.created_at
    FROM paper_orders po
    WHERE po.user_id = '{user_id}' 
      AND po.status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')
    ORDER BY po.created_at DESC
    LIMIT 20;
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 7. Completed orders (last 15)
    print("\n7. COMPLETED ORDERS (Last 15)")
    print("=" * 100)
    query = f"""
    SELECT 
        LEFT(po.id::text, 8) as order_id,
        po.symbol,
        po.side,
        po.order_type as type,
        po.quantity as qty,
        ROUND(COALESCE(po.average_price, 0)::numeric, 2) as avg_price,
        po.filled_quantity as filled,
        po.created_at
    FROM paper_orders po
    WHERE po.user_id = '{user_id}' 
      AND po.status IN ('FILLED', 'EXECUTED')
    ORDER BY po.created_at DESC
    LIMIT 15;
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 8. Recent trades (last 25)
    print("\n8. RECENT TRADES (Last 25)")
    print("=" * 100)
    query = f"""
    SELECT 
        LEFT(pt.id::text, 8) as trade_id,
        LEFT(pt.order_id::text, 8) as order_id,
        po.symbol,
        po.side,
        pt.quantity as qty,
        ROUND(pt.price::numeric, 2) as price,
        pt.executed_at
    FROM paper_trades pt
    JOIN paper_orders po ON pt.order_id = po.id
    WHERE po.user_id = '{user_id}'
    ORDER BY pt.executed_at DESC
    LIMIT 25;
    """
    output = run_query_output(ssh, query)
    print(output)
    
    # 9. Portfolio summary
    print("\n9. PORTFOLIO SUMMARY")
    print("=" * 100)
    query = f"""
    SELECT 
        COUNT(*) FILTER (WHERE status = 'OPEN') as open_positions,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN average_price * ABS(quantity) ELSE 0 END), 0)::numeric, 2) as invested,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN last_price * ABS(quantity) ELSE 0 END), 0)::numeric, 2) as current_value,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN (last_price - average_price) * quantity ELSE 0 END), 0)::numeric, 2) as unrealized_pnl,
        ROUND(COALESCE(SUM(CASE WHEN status = 'CLOSED' THEN realized_pnl ELSE 0 END), 0)::numeric, 2) as realized_pnl,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN (last_price - average_price) * quantity ELSE 0 END), 0)::numeric 
            + COALESCE(SUM(CASE WHEN status = 'CLOSED' THEN realized_pnl ELSE 0 END), 0)::numeric, 2) as total_pnl
    FROM paper_positions
    WHERE user_id = '{user_id}';
    """
    output = run_query_output(ssh, query)
    print(output)
    
    print("\n" + "=" * 100)
    print("END OF REPORT")
    print("=" * 100)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
