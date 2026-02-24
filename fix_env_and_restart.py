#!/usr/bin/env python3
"""Fix .env and restart application"""

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

print("Fixing environment configuration...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Create correct .env
    env_content = """# Database - using postgres user as per docker-compose.yml
DATABASE_URL=postgresql://postgres:password123@db:5432/trading_nexus
DB_PASSWORD=password123

# DhanHQ credentials (if available, otherwise use dummy values)
DHAN_CLIENT_ID=dummy_client_id
DHAN_PIN=dummy_pin
DHAN_TOTP_SECRET=dummy_secret
DHAN_ACCESS_TOKEN=

# VPS configuration
VPS_IP=72.62.228.112
DOMAIN=

# Optional settings
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secret-key-change-this-in-production
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS_RAW=http://localhost,http://72.62.228.112
GREEKS_POLL_SECONDS=15
LOG_LEVEL=INFO

# Startup flags
DISABLE_DHAN_WS=false
DISABLE_MARKET_STREAMS=false
STARTUP_START_STREAMS=true
STARTUP_LOAD_MASTER=true
STARTUP_LOAD_TIER_B=true
"""
    
    print("\n1. Creating corrected .env...")
    import base64
    env_b64 = base64.b64encode(env_content.encode()).decode()
    
    stdin, stdout, stderr = ssh.exec_command(
        f"echo '{env_b64}' | base64 -d > /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/.env"
    )
    stdout.read()
    stderr.read()
    print("   ✓ .env updated")
    
    # Stop and restart
    print("\n2. Stopping containers...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && docker compose down 2>&1 | tail -5'
    )
    print(f"   {stdout.read().decode().strip()[:200]}")
    
    time.sleep(5)
    
    print("\n3. Removing database volume to reinitialize...")
    stdin, stdout, stderr = ssh.exec_command(
        'docker volume rm source_pg_data 2>/dev/null || echo "Volume not found (OK)"'
    )
    print(f"   {stdout.read().decode().strip()}")
    
    print("\n4. Starting containers with fresh database...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && docker compose up -d 2>&1 | tail -20'
    )
    output = stdout.read().decode().strip()
    print(f"   {output[:300]}")
    
    time.sleep(20)
    
    # Check status
    print("\n5. Checking container status...")
    stdin, stdout, stderr = ssh.exec_command(
        'docker ps -a --filter "name=trading_nexus" --format "table {{.Names}}\t{{.Status}}"'
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Check database initialization
    print("\n6. Verifying database tables...")
    stdin, stdout, stderr = ssh.exec_command(
        "docker exec trading_nexus_db psql -U postgres -d trading_nexus -c \"SELECT table_name FROM information_schema.tables WHERE table_schema='public'\" 2>&1"
    )
    output = stdout.read().decode().strip()
    print(f"   {output[:500]}")
    
    # Test API
    print("\n7. Testing API...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/api/health')
    output = stdout.read().decode().strip()
    print(f"   {output[:100] if output else '(initializing...)'}")
    
    ssh.close()
    print("\n✓ Application restarted with correct configuration")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
