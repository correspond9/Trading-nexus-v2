#!/usr/bin/env python3
"""Diagnose and fix Coolify control panel"""

import paramiko
from io import StringIO
import time

key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaS1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("CRITICAL: Fixing Coolify Control Panel...")
print("="*70)

try:
    key_file = StringIO(key_content)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect('72.62.228.112', username='root', pkey=private_key, timeout=10)
    print("✓ Connected to VPS\n")
    
    # Check what's running
    print("1. Checking Coolify service status...")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep -i coolify | grep -v trading_nexus')
    containers = stdout.read().decode().strip()
    print(f"   Coolify containers:\n   {containers if containers else '(none found)'}\n")
    
    # Check if docker-compose file exists and is valid
    print("2. Validating Coolify docker-compose...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose config > /dev/null 2>&1 && echo "Valid" || echo "Invalid"')
    result = stdout.read().decode().strip()
    print(f"   Status: {result}\n")
    
    if result == "Invalid":
        print("3. Checking docker-compose errors...")
        stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose config 2>&1 | head -20')
        output = stdout.read().decode().strip()
        print(f"   {output}\n")
    
    # Try to start Coolify
    print("4. Stopping old Coolify containers...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose down 2>&1 | tail -10')
    output = stdout.read().decode().strip()
    print(f"   {output[:200]}\n")
    
    time.sleep(5)
    
    print("5. Starting Coolify services...")
    stdin, stdout, stderr = ssh.exec_command('cd /data/coolify/source && docker compose up -d 2>&1 | tail -15')
    output = stdout.read().decode().strip()
    print(f"   {output}\n")
    
    time.sleep(20)
    
    # Check if it's running
    print("6. Checking if Coolify is responding on port 3000...")
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:3000/ | head -20')
    response = stdout.read().decode().strip()
    
    if response:
        print("   ✓ API Response received!")
        print(f"   {response[:300]}\n")
    else:
        print("   ✗ No response - checking logs...\n")
        
        print("7. Coolify container logs:")
        stdin, stdout, stderr = ssh.exec_command('docker logs coolify 2>&1 | tail -50')
        logs = stdout.read().decode().strip()
        print(f"   {logs[:1000]}\n")
    
    # Check ports
    print("8. Checking port bindings...")
    stdin, stdout, stderr = ssh.exec_command('netstat -tlnp 2>/dev/null | grep -E "3000|8080" || ss -tlnp 2>/dev/null | grep -E "3000|8080"')
    output = stdout.read().decode().strip()
    print(f"   {output if output else '(checking ports...)'}\n")
    
    # Final status
    print("9. Final Coolify status:")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep -i coolify || echo "Coolify not running"')
    output = stdout.read().decode().strip()
    print(f"   {output}\n")
    
    ssh.close()
    
    print("="*70)
    print("✓ Diagnosis complete")
    print("\nTo access Coolify control panel:")
    print("  URL: http://72.62.228.112:3000")
    print("  OR: http://72.62.228.112:8080 (alt port)")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
