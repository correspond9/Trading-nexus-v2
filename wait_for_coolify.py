#!/usr/bin/env python3
"""Wait and verify Coolify is up"""

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

print("Waiting for Coolify to fully start...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    
    # Wait and check status
    for i in range(6):
        elapsed = i * 10
        print(f"\n[{elapsed}s] Checking Coolify API...")
        
        stdin, stdout, stderr = ssh.exec_command('curl -s -m 3 http://localhost:3000/api/v1/health')
        response = stdout.read().decode().strip()
        
        if response and 'ok' in response.lower():
            print(f"   ✓ Coolify API is ONLINE!")
            print(f"   Response: {response}")
            ssh.close()
            exit(0)
        else:
            print(f"   Status: {response if response else '(no response yet)'}")
        
        if i < 5:
            print(f"   Waiting 10 seconds...")
            time.sleep(10)
    
    print("\n✗ Coolify API did not come online in 60 seconds")
    print("\nChecking container logs...")
    
    stdin, stdout, stderr = ssh.exec_command('docker logs coolify 2>&1 | tail -30')
    output = stdout.read().decode().strip()
    print(output)
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
