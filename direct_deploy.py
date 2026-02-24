#!/usr/bin/env python3
"""Deploy Trading Nexus directly with docker-compose, bypassing Coolify UI"""

import paramiko
from io import StringIO
import time
import json

key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("Deploying Trading Nexus directly with docker-compose...")
try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected to VPS")
    
    # Check if the application directory exists
    print("\n1. Checking application source...")
    stdin, stdout, stderr = ssh.exec_command('ls -la /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/')
    output = stdout.read().decode().strip()
    
    if 'docker-compose.yml' in output:
        print("   ✓ Application source found")
        
        # Show docker-compose content
        print("\n2. Current docker-compose.yml:")
        stdin, stdout, stderr = ssh.exec_command('head -30 /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/docker-compose.yml')
        output = stdout.read().decode().strip()
        print(output[:500])
        
        # Check git clone
        print("\n3. Checking if git repository needs to be cloned...")
        stdin, stdout, stderr = ssh.exec_command('ls /data/coolify/applications/p488ok8g8swo4ockks040ccg/source/.git 2>/dev/null && echo "Git repo exists" || echo "Need to clone"')
        output = stdout.read().decode().strip()
        print(f"   {output}")
        
        if 'Need to clone' in output:
            print("\n4. Cloning GitHub repository...")
            stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && git clone --depth 1 --branch main https://github.com/correspond9/Trading-nexus-v2.git . 2>&1 | tail -10')
            output = stdout.read().decode().strip()
            print(f"   {output}")
            time.sleep(5)
        
        # Build and start with docker compose
        print("\n5. Building and starting application...")
        stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && docker compose build --no-cache 2>&1 | tail -20')
        output = stdout.read().decode().strip()
        print(f"   Build output:\n   {output}")
        
        time.sleep(10)
        
        print("\n6. Starting containers...")
        stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/applications/p488ok8g8swo4ockks040ccg/source && docker compose up -d 2>&1')
        output = stdout.read().decode().strip()
        print(f"   {output}")
        
        time.sleep(20)
        
        print("\n7. Checking container status...")
        stdin, stdout, stderr = ssh.exec_command('docker ps --filter "label=com.docker.compose.project=p488ok8g8swo4ockks040ccg" --format "table {{.Names}}\t{{.Status}}"')
        output = stdout.read().decode().strip()
        print(f"   {output if output else '(containers starting...)'}")
        
        print("\n8. Testing API...")
        stdin, stdout, stderr = ssh.exec_command('sleep 10 && curl -s http://localhost:8000/api/health | head -20')
        output = stdout.read().decode().strip()
        print(f"   {output if output else '(API not yet responding)'}")
        
        print("\n✓ Direct deployment initiated!")
        print("  Application should be starting at http://72.62.228.112:8000")
        
    else:
        print("   ✗ Application source directory not found or incomplete")
        print(f"   Directory contents: {output}")
    
    ssh.close()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
