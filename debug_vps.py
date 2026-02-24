#!/usr/bin/env python3
"""Debug Coolify connectivity"""

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

print("Testing VPS connectivity...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected")
    
    # Test basic commands
    print("\n1. Checking if curl exists:")
    stdin, stdout, stderr = ssh.exec_command('which curl')
    print(f"   {stdout.read().decode().strip()}")
    
    print("\n2. Testing basic curl to localhost:3000:")
    stdin, stdout, stderr = ssh.exec_command('curl -v http://localhost:3000/api/v1/health 2>&1 | head -30')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    print("\n3. Checking docker status:")
    stdin, stdout, stderr = ssh.exec_command('docker ps | head -5')
    print(f"   {stdout.read().decode().strip()}")
    
    print("\n4. Checking if any coolify containers exist:")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep -i coolify')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(none found)'}")
    
    print("\n5. Checking running containers:")
    stdin, stdout, stderr = ssh.exec_command('docker ps')
    output = stdout.read().decode().strip()
    print(f"   {output}")
    
    ssh.close()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
