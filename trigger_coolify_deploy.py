#!/usr/bin/env python3
"""
Trigger proper Coolify deployment
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

CONTAINER = "backend-x8gg0og8440wkgc8ow0ococs-053810342855"

print("=" * 70)
print("TRIGGERING COOLIFY DEPLOYMENT")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    key_file = StringIO(SSH_KEY)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect(VPS_IP, username='root', pkey=private_key, timeout=10)
    
    print("\n[1/4] Finding repository path inside container...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {CONTAINER} pwd')
    workdir = stdout.read().decode().strip()
    print(f"Work directory: {workdir}")
    
    print("\n[2/4] Pulling latest code from GitHub...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {CONTAINER} git pull origin main')
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(output)
    if error:
        print(f"Errors: {error}")
    
    print("\n[3/4] Checking Python dependencies...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {CONTAINER} pip list | grep -i fastapi')
    print(stdout.read().decode())
    
    print("\n[4/4] Restarting application...")
    # Find and restart the main process (uvicorn/gunicorn)
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {CONTAINER} pgrep -f "uvicorn|gunicorn|python.*main"')
    pids = stdout.read().decode().strip().split('\n')
    
    if pids and pids[0]:
        print(f"Found process IDs: {pids}")
        for pid in pids:
            if pid.strip():
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {CONTAINER} kill -HUP {pid.strip()}')
                print(f"Sent reload signal to PID {pid}")
    else:
        # Fallback: restart entire container
        print("No main process found, restarting container...")
        stdin, stdout, stderr = ssh.exec_command(f'docker restart {CONTAINER}')
        time.sleep(15)
    
    print("\n[5/4] Testing endpoint after 10 seconds...")
    time.sleep(10)
    
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {CONTAINER} curl -s localhost:8000/api/v2/market/underlying-ltp/NIFTY')
    response = stdout.read().decode()
    print(f"\nEndpoint response:")
    print(response[:500])
    
    if '"ltp"' in response or '"price"' in response:
        print("\n✅ SUCCESS! API is responding")
    else:
        print("\n⚠ API response looks unusual, checking logs...")
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {CONTAINER} --tail 50')
        logs = stdout.read().decode()
        print("\nRecent logs:")
        print(logs[-2000:])
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT COMPLETE")
    print("=" * 70)
    print("\nNext: Test the Straddle page - NIFTY should show ~24600")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
