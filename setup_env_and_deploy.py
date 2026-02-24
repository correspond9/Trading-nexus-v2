#!/usr/bin/env python3
"""Setup environment variables and restart application"""

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

print("Setting up environment variables...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Check for .env.example
    print("\n1. Checking for .env.example...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/.env* 2>/dev/null || echo "No env files found"')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Create basic .env file
    env_content = """# Docker Compose Environment Variables
DATABASE_URL=postgresql://appuser:password123@trading_nexus_db:5432/trading_nexus
DB_PASSWORD=password123
DHAN_CLIENT_ID=dummy_client_id
DHAN_PIN=dummy_pin
DHAN_TOTP_SECRET=dummy_secret
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-key-change-this-in-production
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=*
"""
    
    print("\n2. Creating .env file...")
    import base64
    env_b64 = base64.b64encode(env_content.encode()).decode()
    
    stdin, stdout, stderr = ssh.exec_command(
        f"echo '{env_b64}' | base64 -d > /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/.env"
    )
    stdout.read()
    stderr_out = stderr.read().decode()
    if stderr_out:
        print(f"   Warning: {stderr_out}")
    else:
        print("   ✓ .env created")
    
    # Stop and remove old containers
    print("\n3. Stopping old containers...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && docker compose down 2>&1 | tail -10')
    output = stdout.read().decode().strip()
    print(f"   {output[:200] if output else '(no output)'}")
    
    time.sleep(5)
    
    # Start fresh
    print("\n4. Starting application with environment variables...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && docker compose up -d 2>&1')
    output = stdout.read().decode().strip()
    print(f"   {output[:300]}")
    
    time.sleep(15)
    
    # Check status
    print("\n5. Checking container status...")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a --filter "name=trading_nexus" --format "table {{.Names}}\t{{.Status}}"')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Test API
    print("\n6. Testing API after 30 seconds...")
    time.sleep(20)
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/api/health')
    output = stdout.read().decode().strip()
    if output:
        print(f"   ✓ API responding: {output[:100]}")
    else:
        print(f"   Still initializing...")
    
    ssh.close()
    print("\n✓ Application deployment in progress")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
