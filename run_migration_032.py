#!/usr/bin/env python3
"""Run migration 032 to add remaining_qty column"""

import paramiko
from io import StringIO

key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("Running migration 032 (remaining_qty column)...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected to VPS")
    
    # Read migration file
    with open('migrations/032_paper_orders_remaining_qty.sql', 'r') as f:
        migration_sql = f.read()
    
    # Escape single quotes for shell
    migration_sql_escaped = migration_sql.replace("'", "'\"'\"'")
    
    # Run migration in database
    print("\n1. Running migration 032...")
    cmd = f"""docker exec db-x8gg0og8440wkgc8ow0ococs-053105957178 psql -U postgres -d trading_terminal -c '{migration_sql_escaped}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode().strip()
    errors = stderr.read().decode().strip()
    
    print(f"   Output: {output}")
    if errors:
        print(f"   Errors: {errors}")
    
    # Verify column exists
    print("\n2. Verifying remaining_qty column...")
    stdin, stdout, stderr = ssh.exec_command(
        """docker exec db-x8gg0og8440wkgc8ow0ococs-053105957178 psql -U postgres -d trading_terminal -c "\\d paper_orders" | grep remaining_qty"""
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Check sample data
    print("\n3. Checking sample orders with remaining_qty...")
    stdin, stdout, stderr = ssh.exec_command(
        """docker exec db-x8gg0og8440wkgc8ow0ococs-053105957178 psql -U postgres -d trading_terminal -c "SELECT order_id, status, quantity, remaining_qty FROM paper_orders ORDER BY created_at DESC LIMIT 5" """
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    ssh.close()
    print("\n✓ Migration 032 completed successfully!")
    print("\n=== You can now place orders without errors ===")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
