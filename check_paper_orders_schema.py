#!/usr/bin/env python3
"""Check paper_orders schema"""

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

print("Checking paper_orders schema...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected to VPS")
    
    # Get table schema
    print("\npaper_orders columns:")
    stdin, stdout, stderr = ssh.exec_command(
        """docker exec db-x8gg0og8440wkgc8ow0ococs-053105957178 psql -U postgres -d trading_terminal -c "\\d paper_orders" """
    )
    output = stdout.read().decode().strip()
    print(output)
    
    # Get a sample row
    print("\n\nSample order:")
    stdin, stdout, stderr = ssh.exec_command(
        """docker exec db-x8gg0og8440wkgc8ow0ococs-053105957178 psql -U postgres -d trading_terminal -c "SELECT * FROM paper_orders LIMIT 1" """
    )
    output = stdout.read().decode().strip()
    print(output)
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
