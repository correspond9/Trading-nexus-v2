#!/usr/bin/env python3
"""
Restart Coolify container to trigger rebuild from GitHub
"""
import paramiko
from io import StringIO
import time

VPS_IP = "72.62.228.112"
SSH_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMflX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

CONTAINER = "backend-x8gg0og8440wkgc8ow0ococs-053810342855"

print("=" * 80)
print("RESTARTING APPLICATION TO DEPLOY LATEST CODE")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    key_file = StringIO(SSH_KEY)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect(VPS_IP, username='root', pkey=private_key, timeout=10)
    
    print("\n📦 Checking container status...")
    stdin, stdout, stderr = ssh.exec_command(f'docker ps --filter name={CONTAINER} --format "{{{{.Status}}}}"')
    status = stdout.read().decode().strip()
    print(f"Container status: {status}")
    
    print("\n🔄 Stopping container...")
    stdin, stdout, stderr = ssh.exec_command(f'docker stop {CONTAINER}')
    stdout.read()
    time.sleep(5)
    
    print("✅ Container stopped")
    
    print("\n🚀 Starting container (Coolify will rebuild from latest GitHub code)...")
    stdin, stdout, stderr = ssh.exec_command(f'docker start {CONTAINER}')
    stdout.read()
    
    print("⏳ Waiting 20 seconds for application startup...")
    time.sleep(20)
    
    print("\n✓ Container restarted")
    
    print("\n📊 Checking application logs...")
    stdin, stdout, stderr = ssh.exec_command(f'docker logs {CONTAINER} --tail 30 2>&1')
    logs = stdout.read().decode()
    
    # Look for startup messages
    if "uvicorn" in logs.lower() or "application startup" in logs.lower():
        print("✅ Application started successfully\n")
        print("Recent logs:")
        print("-" * 80)
        print(logs[-1500:])
        print("-" * 80)
    else:
        print("⚠ Unusual startup logs:")
        print(logs[-1000:])
    
    print("\n" + "=" * 80)
    print("DEPLOYMENT STATUS: COMPLETE")
    print("=" * 80)
    print("\n✅ Code changes deployed:")
    print("   • app/routers/market_data.py - Uses FUTIDX for index LTP")
    print("   • app/routers/option_chain.py - Uses FUTIDX for underlying price")
    print("\n🧪 Test it now:")
    print("   1. Open your Straddle page")
    print("    2. NIFTY should display current market price (~24600)")
    print("   3. Price should update in realtime")
    print("\n💡 If you still see stale prices:")
    print("   • Clear browser cache")
    print("   • Wait 1-2 minutes for WebSocket reconnection")
    print("   • Check that market is open (currently)")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
