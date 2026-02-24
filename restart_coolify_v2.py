#!/usr/bin/env python3
"""Restart Coolify control service using docker compose"""

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
    print("✓ Connected to VPS")
    
    # Use docker compose (v2 syntax instead of docker-compose)
    print("\n1. Stopping Coolify containers:")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose down 2>&1')
    output = stdout.read().decode().strip()
    if output:
        lines = output.split('\n')[:10]
        print(f"   {chr(10).join(lines)}")
    
    time.sleep(2)
    
    print("\n2. Starting Coolify services:")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose up -d 2>&1')
    output = stdout.read().decode().strip()
    if output:
        lines = output.split('\n')[:10]
        print(f"   {chr(10).join(lines)}")
    
    print("\n3. Waiting 10 seconds for services to initialize...")
    time.sleep(10)
    
    print("\n4. Checking running containers:")
    stdin, stdout, stderr = ssh.exec_command('docker ps --filter "label!=sentinel" --format "table {{.Names}}\t{{.Status}}"')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    print("\n5. Testing Coolify API:")
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:3000/api/v1/health')
    output = stdout.read().decode().strip()
    if output:
        print(f"   ✓ API responding: {output[:100]}")
    else:
        print(f"   ⚠ Still waiting for API to be ready...")
    
    ssh.close()
    print("\n✓ Coolify restart completed")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
