#!/usr/bin/env python3
"""Restart Coolify control service"""

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

print("Restarting Coolify control service...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Navigate to Coolify source directory and restart
    print("\n1. Stopping existing containers:")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker-compose down 2>&1 | head -20')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    print("\n2. Starting Coolify services:")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker-compose up -d 2>&1')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    print("\n3. Waiting for services to start...")
    time.sleep(5)
    
    print("\n4. Checking service status:")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep -E "coolify|traefik" | grep -v sentinel')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    print("\n5. Testing Coolify API (localhost:3000):")
    stdin, stdout, stderr = ssh.exec_command('sleep 3 && curl -s http://localhost:3000/api/v1/health 2>&1 | head -5')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(waiting for API to start...)'}")
    
    print("\n✓ Restart initiated. Coolify should be back online shortly.")
    print("  The API should be available at http://localhost:3000")
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
