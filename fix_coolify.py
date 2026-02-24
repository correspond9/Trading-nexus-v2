#!/usr/bin/env python3
"""Fix and restart Coolify"""

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
    print("\n1. Adding soketi image to docker-compose.yml...")
    
    # Fix: Add image to soketi service
    fixed_content = compose_content.replace(
        'soketi:\n        container_name: coolify-realtime',
        'soketi:\n        image: quay.io/soketi/soketi:latest\n        container_name: coolify-realtime'
    )
    
    # Also need to fix coolify service - add image
    if 'image: ' not in fixed_content.split('services:')[1].split('coolify:')[1].split('postgres:')[0]:
        fixed_content = fixed_content.replace(
            'coolify:\n        container_name: coolify',
            'coolify:\n        image: ghcr.io/coollabsio/coolify:latest\n        container_name: coolify'
        )
    
    # Write back the fixed file
    print("2. Writing fixed docker-compose.yml...")
    with open('/tmp/docker-compose.yml', 'w') as f:
        f.write(fixed_content)
    
    # Copy it to VPS
    stdin, stderr = ssh.exec_command(
        f'cat > /data/coolify/source/docker-compose.yml << \'EOF\'\n{fixed_content}\nEOF'
    )[0:2]
    err = stderr.read().decode()
    if err:
        print(f"   Error: {err}")
    else:
        print("   ✓ File updated")
    
    time.sleep(1)
    
    # Try to start services now
    print("\n3. Starting Coolify services...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose up -d 2>&1 | tail -20')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    time.sleep(15)
    
    print("\n4. Checking if Coolify API is responding...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:3000/api/v1/health')
    output = stdout.read().decode().strip()
    if 'ok' in output.lower() or output:
        print(f"   ✓ API responding!")
    else:
        print(f"   ⚠ Still initializing...")
    
    ssh.close()
    print("\n✓ Coolify restart completed. API should be online.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
