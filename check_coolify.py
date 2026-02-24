#!/usr/bin/env python3
"""Check and restart Coolify if needed"""

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

print("Checking Coolify status...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Check coolify-control docker-compose
    print("\n1. Checking Coolify directory structure:")
    stdin, stdout, stderr = ssh.exec_command('ls -la /data/coolify/ 2>/dev/null | head -20')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(directory does not exist)'}")
    
    # Check for coolify docker-compose file
    print("\n2. Checking for coolify docker-compose:")
    stdin, stdout, stderr = ssh.exec_command('ls -la /root/coolify* 2>/dev/null')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(not found)'}")
    
    # Check docker network
    print("\n3. Checking docker networks:")
    stdin, stdout, stderr = ssh.exec_command('docker network ls')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    # Try to restart docker and coolify
    print("\n4. Checking /opt/coolify (usual location):")
    stdin, stdout, stderr = ssh.exec_command('ls -la /opt/coolify 2>/dev/null | head -10')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(not at /opt/coolify)'}")
    
    # Check docker compose files
    print("\n5. Finding docker-compose files:")
    stdin, stdout, stderr = ssh.exec_command('find / -name "docker-compose.yml" -path "*/coolify*" 2>/dev/null')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(none found)'}")
    
    # Check if there's a traefik config
    print("\n6. Checking network connectivity test:")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8080/ | head -5')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(no response)'}")
    
    ssh.close()
    print("\n✗ CRITICAL: Coolify control service is not running!")
    print("  Traefik proxy is up but the API service is down.")
    print("  This may have happened when we wiped the application.")
    print("\n  Need to restore or restart Coolify properly.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
