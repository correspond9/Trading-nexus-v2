import paramiko
import sys

# VPS credentials
VPS_IP = "72.62.228.112"
VPS_USER = "root"
PRIVATE_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

def check_positions():
    """Check orders, trades, and positions for discrepancies"""
    
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Load private key
        from io import StringIO
        key = paramiko.Ed25519Key.from_private_key(StringIO(PRIVATE_KEY))
        
        print(f"Connecting to {VPS_IP}...")
        ssh.connect(VPS_IP, username=VPS_USER, pkey=key, timeout=10)
        
        # Find DB container
        stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}' | grep '^db-'")
        db_container = stdout.read().decode().strip()
        
        if not db_container:
            print("ERROR: Could not find database container")
            return
            
        print(f"Found database container: {db_container}\n")
        
        # Check all orders
        print("=" * 80)
        print("ALL ORDERS (including cancelled):")
        print("=" * 80)
        query1 = """
        SELECT 
            order_id,
            user_id,
            symbol,
            side,
            quantity,
            filled_qty,
            remaining_qty,
            status,
            created_at
        FROM paper_orders
        ORDER BY created_at DESC
        LIMIT 20;
        """
        
        cmd = f"""docker exec {db_container} psql -U postgres -d trading_terminal -c "{query1}" """
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        
        # Check all trades
        print("\n" + "=" * 80)
        print("ALL TRADES:")
        print("=" * 80)
        query2 = """
        SELECT 
            trade_id,
            order_id,
            user_id,
            symbol,
            side,
            quantity,
            fill_qty,
            fill_price,
            traded_at
        FROM paper_trades
        ORDER BY traded_at DESC
        LIMIT 20;
        """
        
        cmd = f"""docker exec {db_container} psql -U postgres -d trading_terminal -c "{query2}" """
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        
        # Check if there's a positions table
        print("\n" + "=" * 80)
        print("CHECKING FOR POSITIONS TABLE:")
        print("=" * 80)
        query3 = "\\dt paper_positions"
        
        cmd = f"""docker exec {db_container} psql -U postgres -d trading_terminal -c "{query3}" """
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode()
        print(result)
        
        # If positions table exists, check its contents
        if "paper_positions" in result:
            print("\n" + "=" * 80)
            print("POSITIONS DATA:")
            print("=" * 80)
            query4 = """
            SELECT 
                position_id,
                user_id,
                symbol,
                side,
                quantity,
                avg_price,
                current_price,
                unrealised_pnl,
                created_at,
                updated_at
            FROM paper_positions
            ORDER BY updated_at DESC
            LIMIT 20;
            """
            
            cmd = f"""docker exec {db_container} psql -U postgres -d trading_terminal -c "{query4}" """
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
        
        # Calculate positions from trades (how it should work)
        print("\n" + "=" * 80)
        print("CALCULATED POSITIONS FROM TRADES:")
        print("=" * 80)
        query5 = """
        SELECT 
            user_id,
            symbol,
            side,
            SUM(COALESCE(fill_qty, quantity)) as total_qty,
            AVG(fill_price) as avg_price,
            COUNT(*) as num_trades
        FROM paper_trades
        GROUP BY user_id, symbol, side
        ORDER BY user_id, symbol, side;
        """
        
        cmd = f"""docker exec {db_container} psql -U postgres -d trading_terminal -c "{query5}" """
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        
        # Check for unmatched positions (buy without corresponding sell)
        print("\n" + "=" * 80)
        print("NET POSITIONS (BUY - SELL):")
        print("=" * 80)
        query6 = """
        WITH trade_summary AS (
            SELECT 
                user_id,
                symbol,
                side,
                SUM(COALESCE(fill_qty, quantity)) as total_qty
            FROM paper_trades
            GROUP BY user_id, symbol, side
        ),
        buy_trades AS (
            SELECT user_id, symbol, total_qty as buy_qty
            FROM trade_summary
            WHERE side = 'BUY'
        ),
        sell_trades AS (
            SELECT user_id, symbol, total_qty as sell_qty
            FROM trade_summary
            WHERE side = 'SELL'
        )
        SELECT 
            COALESCE(b.user_id, s.user_id) as user_id,
            COALESCE(b.symbol, s.symbol) as symbol,
            COALESCE(b.buy_qty, 0) as total_buy,
            COALESCE(s.sell_qty, 0) as total_sell,
            COALESCE(b.buy_qty, 0) - COALESCE(s.sell_qty, 0) as net_position
        FROM buy_trades b
        FULL OUTER JOIN sell_trades s ON b.user_id = s.user_id AND b.symbol = s.symbol
        WHERE COALESCE(b.buy_qty, 0) - COALESCE(s.sell_qty, 0) != 0
        ORDER BY user_id, symbol;
        """
        
        cmd = f"""docker exec {db_container} psql -U postgres -d trading_terminal -c "{query6}" """
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == "__main__":
    check_positions()
