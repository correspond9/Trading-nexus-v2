#!/usr/bin/env python3
"""Check Coolify docker-compose and see what's wrong"""

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

print("Checking Coolify docker-compose...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    
    # View the docker-compose file
    print("\n1. Coolify docker-compose.yml content (first 50 lines):")
    stdin, stdout, stderr = ssh.exec_command('head -50 /data/coolify/source/docker-compose.yml')
    output = stdout.read().decode().strip()
    print(output)
    
    print("\n2. Checking if soketi service has image:")
    stdin, stdout, stderr = ssh.exec_command('grep -A 5 "soketi:" /data/coolify/source/docker-compose.yml || echo "Not found"')
    output = stdout.read().decode().strip()
    print(output)
    
    # Try starting just the necessary services
    print("\n3. Attempting docker compose build:")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose config 2>&1 | head -20')
    output = stdout.read().decode().strip()
    print(output if output else "(config validation passed)")
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
