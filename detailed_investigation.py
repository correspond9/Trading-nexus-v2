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
user_id = "6785692d-8f36-4183-addb-16c96ea95a88"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def run_query_count(ssh, table, user_id):
    """Count rows in a table for user"""
    cmd = f"""docker exec {db_container} psql -U {db_user} -d {db_name} -t -A -c "SELECT COUNT(*) FROM {table} WHERE user_id = '{user_id}';" """
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode('utf-8').strip()
    return output

def run_query(ssh, query):
    """Run a query and return output"""
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
    print(f"DETAILED INVESTIGATION FOR USER {mobile}")
    print("=" * 100)
    
    # Count records in each table
    print("\nRECORD COUNTS:")
    print("-" * 100)
    orders_count = run_query_count(ssh, "paper_orders", user_id)
    trades_count = run_query_count(ssh, "paper_trades pt JOIN paper_orders po ON pt.order_id = po.id WHERE po", user_id)
    positions_count = run_query_count(ssh, "paper_positions", user_id)
    
    print(f"Orders: {orders_count}")
    print(f"Positions: {positions_count}")
    
    # Get trades count separately
    cmd = f"""docker exec {db_container} psql -U {db_user} -d {db_name} -t -A -c "SELECT COUNT(*) FROM paper_trades pt JOIN paper_orders po ON pt.order_id = po.id WHERE po.user_id = '{user_id}';" """
    stdin, stdout, stderr = ssh.exec_command(cmd)
    trades_count = stdout.read().decode('utf-8').strip()
    print(f"Trades: {trades_count}")
    
    # Check positions details
    print("\n" + "=" * 100)
    print("POSITIONS (ALL - OPEN & CLOSED)")
    print("=" * 100)
    query = f"""
    SELECT 
        pp.symbol,
        pp.exchange_segment,
        pp.quantity,
        pp.product_type,
        pp.status,
        ROUND(pp.average_price::numeric, 2) as avg_price,
        ROUND(pp.last_price::numeric, 2) as last_price,
        pp.created_at,
        pp.closed_at
    FROM paper_positions pp
    WHERE pp.user_id = '{user_id}'
    ORDER BY pp.created_at DESC
    LIMIT 20;
    """
    output = run_query(ssh, query)
    print(output)
    
    # Get all orders with status
    print("\n" + "=" * 100)
    print("ALL ORDERS (Last 20)")
    print("=" * 100)
    query = f"""
    SELECT 
        LEFT(po.id::text, 8) as order_id,
        po.symbol,
        po.side,
        po.order_type,
        po.quantity,
        ROUND(COALESCE(po.price, 0)::numeric, 2) as price,
        po.status,
        po.filled_quantity,
        ROUND(COALESCE(po.average_price, 0)::numeric, 2) as avg_price,
        po.created_at
    FROM paper_orders po
    WHERE po.user_id = '{user_id}'
    ORDER BY po.created_at DESC
    LIMIT 20;
    """
    output = run_query(ssh, query)
    print(output)
    
    # Get pending orders specifically
    print("\n" + "=" * 100)
    print("PENDING ORDERS SPECIFICALLY")
    print("=" * 100)
    query = f"""
    SELECT 
        po.id,
        po.symbol,
        po.side,
        po.order_type,
        po.quantity,
        po.price,
        po.status,
        po.created_at
    FROM paper_orders po
    WHERE po.user_id = '{user_id}' 
      AND po.status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')
    ORDER BY po.created_at DESC;
    """
    output = run_query(ssh, query)
    print(output)
    
    # Get all trades
    print("\n" + "=" * 100)
    print("ALL TRADES (Last 30)")
    print("=" * 100)
    query = f"""
    SELECT 
        LEFT(pt.id::text, 8) as trade_id,
        LEFT(pt.order_id::text, 8) as order_id,
        po.symbol,
        po.side,
        pt.quantity,
        ROUND(pt.price::numeric, 2) as price,
        pt.executed_at
    FROM paper_trades pt
    JOIN paper_orders po ON pt.order_id = po.id
    WHERE po.user_id = '{user_id}'
    ORDER BY pt.executed_at DESC
    LIMIT 30;
    """
    output = run_query(ssh, query)
    print(output)
    
    print("\n" + "=" * 100)
    print("END OF INVESTIGATION")
    print("=" * 100)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✅ Connection closed")
