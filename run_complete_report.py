import paramiko
import sys

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

def run_query(ssh, query, description):
    """Run a SQL query and return formatted results"""
    # Escape quotes in query
    escaped_query = query.replace('"', '\\"').replace('$', '\\$')
    docker_cmd = f'docker exec {db_container} psql -U {db_user} -d {db_name} -c "{escaped_query}"'
    
    stdin, stdout, stderr = ssh.exec_command(docker_cmd, get_pty=False)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    return output, error

try:
    # Load private key
    private_key = paramiko.Ed25519Key.from_private_key_file(key_path)
    
    # Connect
    print(f"Connecting to {hostname}...")
    ssh.connect(hostname, username=username, pkey=private_key, timeout=10)
    print("✅ Connected successfully\n")
    
    print("=" * 80)
    print(f"COMPLETE USER REPORT FOR MOBILE: {mobile}")
    print("=" * 80)
    
    # 1. Get user info
    print("\n1. USER BASIC INFORMATION")
    print("=" * 80)
    query = f"SELECT id, mobile, created_at, is_active FROM users WHERE mobile = '{mobile}';"
    output, error = run_query(ssh, query, "User info")
    print(output)
    
    # Extract user_id from output
    lines = output.strip().split('\n')
    if len(lines) > 2:
        data_line = lines[2].strip()
        user_id = data_line.split('|')[0].strip()
        print(f"User ID extracted: {user_id}")
    else:
        print("❌ No user found!")
        sys.exit(1)
    
    # 2. Margin information
    print("\n2. MARGIN INFORMATION")
    print("=" * 80)
    query = f"""
    SELECT 
        pa.margin_allotted,
        pa.created_at,
        (
            SELECT COALESCE(SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment::text,
                    pp.quantity,
                    pp.product_type::text
                )
            ), 0)
            FROM paper_positions pp
            WHERE pp.user_id = {user_id} AND pp.status = 'OPEN'
        ) as used_margin,
        pa.margin_allotted - (
            SELECT COALESCE(SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment::text,
                    pp.quantity,
                    pp.product_type::text
                )
            ), 0)
            FROM paper_positions pp
            WHERE pp.user_id = {user_id} AND pp.status = 'OPEN'
        ) as available_margin
    FROM paper_accounts pa
    WHERE pa.user_id = {user_id};
    """
    output, error = run_query(ssh, query, "Margin info")
    print(output)
    
    # 3. Open positions
    print("\n3. OPEN POSITIONS")
    print("=" * 80)
    query = f"""
    SELECT 
        pp.symbol,
        pp.exchange_segment,
        pp.quantity,
        pp.product_type,
        ROUND(pp.average_price::numeric, 2) as avg_price,
        ROUND(pp.last_price::numeric, 2) as last_price,
        ROUND(((pp.last_price - pp.average_price) * pp.quantity)::numeric, 2) as pnl,
        ROUND(calculate_position_margin(
            pp.instrument_token,
            pp.symbol,
            pp.exchange_segment::text,
            pp.quantity,
            pp.product_type::text
        )::numeric, 2) as margin_used
    FROM paper_positions pp
    WHERE pp.user_id = {user_id} AND pp.status = 'OPEN'
    ORDER BY pp.created_at DESC;
    """
    output, error = run_query(ssh, query, "Open positions")
    print(output)
    
    # 4. Closed positions (last 10)
    print("\n4. CLOSED POSITIONS (Last 10)")
    print("=" * 80)
    query = f"""
    SELECT 
        pp.symbol,
        pp.exchange_segment,
        pp.quantity,
        ROUND(pp.average_price::numeric, 2) as avg_price,
        ROUND(pp.realized_pnl::numeric, 2) as realized_pnl,
        pp.closed_at
    FROM paper_positions pp
    WHERE pp.user_id = {user_id} AND pp.status = 'CLOSED'
    ORDER BY pp.closed_at DESC
    LIMIT 10;
    """
    output, error = run_query(ssh, query, "Closed positions")
    print(output)
    
    # 5. Order counts
    print("\n5. ORDERS SUMMARY")
    print("=" * 80)
    query = f"""
    SELECT 
        COUNT(*) as total_orders,
        COUNT(*) FILTER (WHERE status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')) as pending_orders,
        COUNT(*) FILTER (WHERE status IN ('FILLED', 'EXECUTED')) as completed_orders,
        COUNT(*) FILTER (WHERE status IN ('CANCELLED', 'REJECTED')) as cancelled_orders
    FROM paper_orders
    WHERE user_id = {user_id};
    """
    output, error = run_query(ssh, query, "Order counts")
    print(output)
    
    # 6. Pending/Open orders
    print("\n6. PENDING/OPEN ORDERS")
    print("=" * 80)
    query = f"""
    SELECT 
        po.id,
        po.symbol,
        po.side,
        po.order_type,
        po.quantity,
        ROUND(COALESCE(po.price, 0)::numeric, 2) as price,
        po.status,
        po.filled_quantity,
        po.created_at
    FROM paper_orders po
    WHERE po.user_id = {user_id} 
      AND po.status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')
    ORDER BY po.created_at DESC;
    """
    output, error = run_query(ssh, query, "Pending orders")
    print(output)
    
    # 7. Completed orders (last 10)
    print("\n7. COMPLETED ORDERS (Last 10)")
    print("=" * 80)
    query = f"""
    SELECT 
        po.id,
        po.symbol,
        po.side,
        po.order_type,
        po.quantity,
        ROUND(COALESCE(po.average_price, 0)::numeric, 2) as avg_price,
        po.filled_quantity,
        po.created_at
    FROM paper_orders po
    WHERE po.user_id = {user_id} 
      AND po.status IN ('FILLED', 'EXECUTED')
    ORDER BY po.created_at DESC
    LIMIT 10;
    """
    output, error = run_query(ssh, query, "Completed orders")
    print(output)
    
    # 8. Recent trades (last 20)
    print("\n8. RECENT TRADES (Last 20)")
    print("=" * 80)
    query = f"""
    SELECT 
        pt.id,
        pt.order_id,
        po.symbol,
        po.side,
        pt.quantity,
        ROUND(pt.price::numeric, 2) as price,
        pt.executed_at
    FROM paper_trades pt
    JOIN paper_orders po ON pt.order_id = po.id
    WHERE po.user_id = {user_id}
    ORDER BY pt.executed_at DESC
    LIMIT 20;
    """
    output, error = run_query(ssh, query, "Recent trades")
    print(output)
    
    # 9. Portfolio summary
    print("\n9. PORTFOLIO SUMMARY")
    print("=" * 80)
    query = f"""
    SELECT 
        COUNT(*) FILTER (WHERE status = 'OPEN') as open_positions,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN average_price * quantity ELSE 0 END), 0)::numeric, 2) as total_invested,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN last_price * quantity ELSE 0 END), 0)::numeric, 2) as current_value,
        ROUND(COALESCE(SUM(CASE WHEN status = 'OPEN' THEN (last_price - average_price) * quantity ELSE 0 END), 0)::numeric, 2) as unrealized_pnl,
        ROUND(COALESCE(SUM(CASE WHEN status = 'CLOSED' THEN realized_pnl ELSE 0 END), 0)::numeric, 2) as total_realized_pnl
    FROM paper_positions
    WHERE user_id = {user_id};
    """
    output, error = run_query(ssh, query, "Portfolio summary")
    print(output)
    
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
