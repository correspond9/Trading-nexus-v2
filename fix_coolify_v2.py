#!/usr/bin/env python3
"""Fix and restart Coolify - corrected version"""

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

print("Fixing Coolify docker-compose.yml...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Read current file
    stdin, stdout, stderr = ssh.exec_command('cat /data/coolify/source/docker-compose.yml')
    compose_content = stdout.read().decode()
    
    # Add soketi docker image
    print("\n1. Fixing soketi service with image...")
    
    # Fix: Add image to soketi service and coolify service
    fixed_content = compose_content.replace(
        'soketi:\n        container_name: coolify-realtime',
        'soketi:\n        image: quay.io/soketi/soketi:latest\n        container_name: coolify-realtime'
    )
    
    # Also add image to coolify service if missing
    if 'coolify:\n        image:' not in fixed_content:
        fixed_content = fixed_content.replace(
            'coolify:\n        container_name: coolify',
            'coolify:\n        image: ghcr.io/coollabsio/coolify:latest\n        container_name: coolify'
        )
    
    # Write back via SSH
    print("2. Writing fixed docker-compose.yml...")
    import base64
    content_b64 = base64.b64encode(fixed_content.encode()).decode()
    
    # Use echo with base64 to avoid shell quoting issues
    stdin, stdout, stderr = ssh.exec_command(
        f"echo '{content_b64}' | base64 -d > /data/coolify/source/docker-compose.yml"
    )
    stdout.read()
    err = stderr.read().decode()
    if err:
        print(f"   Warning: {err}")
    else:
        print("   ✓ File updated")
    
    time.sleep(1)
    
    # Verify it was written
    stdin, stdout, stderr = ssh.exec_command('grep "image:" /data/coolify/source/docker-compose.yml | head -3')
    output = stdout.read().decode().strip()
    print(f"   Verification: {output}")
    
    # Try to start services now
    print("\n3. Starting Cool ify services...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose up -d')
    output = stdout.read().decode().strip()
    print(f"   {output[:200]}")
    
    time.sleep(20)
    
    print("\n4. Checking Coolify API...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:3000/api/v1/health')
    output = stdout.read().decode().strip()
    if output:
        print(f"   ✓ API responding: {output[:100]}")
    else:
        print(f"   ⚠ Still waiting for API...")
    
    print("\n5. Checking container status:")
    stdin, stdout, stderr = ssh.exec_command('docker ps --no-trunc | grep -E "coolify|soketi"')
    output = stdout.read().decode().strip()
    if output:
        for line in output.split('\n')[:5]:
            print(f"   {line[:120]}")
    
    ssh.close()
    print("\n✓ Coolify restart initiated")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
