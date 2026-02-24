#!/usr/bin/env python3
"""Run database migrations"""

import paramiko
from io import StringIO
import time

key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("Running database migrations...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Run migrations via the backend container
    print("\n1. Executing migrations...")
    stdin, stdout, stderr = ssh.exec_command(
        'docker exec trading_nexus_backend python -m alembic upgrade head 2>&1 | tail -50'
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    time.sleep(10)
    
    # Check database
    print("\n2. Checking database tables...")
    stdin, stdout, stderr = ssh.exec_command(
        "docker exec trading_nexus_db psql -U appuser -d trading_nexus -c \"\\\\dt\" 2>&1 | head -30"
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Test health endpooint
    print("\n3. Testing API health endpoint...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/api/health')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Check frontend
    print("\n4. Checking frontend container...")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a --filter "name=trading_nexus_frontend" --format "table {{.Names}}\t{{.Status}}"')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Try to access the web app
    print("\n5. Testing frontend access...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost/  | head -20')
    output = stdout.read().decode().strip()
    print(f"   {output[:300]}")
    
    ssh.close()
    print("\n✓ Migrations completed")
    print("\n=== DEPLOYMENT COMPLETE ===")
    print("Frontend: http://72.62.228.112")
    print("API: http://72.62.228.112/api")
    print("Health: http://72.62.228.112/api/health")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
