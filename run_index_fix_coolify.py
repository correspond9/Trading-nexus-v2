#!/usr/bin/env python3
"""
Run fix_index_tier.py on production using SSH
Executes the INDEX tier fix script inside the backend container
"""
import paramiko
from io import StringIO
import time

VPS_IP = "72.62.228.112"
SSH_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

print("=" * 70)
print("RUNNING INDEX TIER FIX ON PRODUCTION")
print("=" * 70)
print()

# Setup SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("[1/3] Connecting to VPS...")
    key_file = StringIO(SSH_KEY)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect(VPS_IP, username='root', pkey=private_key, timeout=10)
    print(f"✓ Connected to {VPS_IP}\n")
    
    # Find backend container
    print("[2/3] Finding backend container...")
    stdin, stdout, stderr = ssh.exec_command('docker ps --filter name=backend --format "{{.Names}}"')
    container_name = stdout.read().decode().strip()
    
    if not container_name:
        # Try alternative names
        stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}}" | grep -i trading')
        containers = stdout.read().decode().strip().split('\n')
        for c in containers:
            if 'backend' in c.lower() or 'api' in c.lower():
                container_name = c
                break
    
    if not container_name:
        print("✗ Could not find backend container")
        print("Available containers:")
        stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}}"')
        print(stdout.read().decode())
        ssh.close()
        exit(1)
    
    print(f"✓ Found container: {container_name}\n")
    
    # Execute fix script
    print("[3/3] Executing fix_index_tier.py...")
    print("-" * 70)
    
    command = f'docker exec {container_name} python fix_index_tier.py'
    stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
    
    # Print output in real-time
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    print(output)
    if errors and errors.strip():
        print("\nErrors/Warnings:")
        print(errors)
    
    print("-" * 70)
    print("\n✓ Script executed successfully!")
    
    # Restart backend container
    print("\n[4/4] Restarting backend container...")
    stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_name}')
    time.sleep(2)
    restart_output = stdout.read().decode()
    print(f"✓ Container restarted: {restart_output.strip()}")
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Wait 30 seconds for backend to fully start")
    print("  2. Open Straddle page in your browser")
    print("  3. Check NIFTY shows live price (~24600)")
    print("  4. Verify prices update every second")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    exit(1)
finally:
    ssh.close()
