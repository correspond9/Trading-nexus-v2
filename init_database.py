#!/usr/bin/env python3
"""Properly initialize the database"""

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

print("Initializing database...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # First, create the database and user as postgres superuser
    print("\n1. Creating database and user...")
    create_db_sql = "CREATE DATABASE trading_nexus; CREATE USER appuser WITH PASSWORD 'password123'; GRANT ALL PRIVILEGES ON DATABASE trading_nexus TO appuser;"
    
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec trading_nexus_db psql -U postgres -c \"{create_db_sql}\" 2>&1"
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    time.sleep(3)
    
    # Run the first migration
    print("\n2. Running initial schema migration...")
    # We'll copy the migration file to the container and run it
    stdin, stdout, stderr = ssh.exec_command(
        "docker cp /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/migrations/001_initial_schema.sql trading_nexus_db:/tmp/"
    )
    stdout.read()
    stdout.read()
    
    # Run the migration
    stdin, stdout, stderr = ssh.exec_command(
        "docker exec trading_nexus_db psql -U appuser trading_nexus -f /tmp/001_initial_schema.sql 2>&1 | tail -50"
    )
    output = stdout.read().decode().strip()
    print(f"   {output[:500]}")
    
    # Check tables
    print("\n3. Checking tables...")
    stdin, stdout, stderr = ssh.exec_command(
        "docker exec trading_nexus_db psql -U appuser trading_nexus -c \"\\\\dt\" 2>&1 | head -40"
    )
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    ssh.close()
    print("\n✓ Database initialization started")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
