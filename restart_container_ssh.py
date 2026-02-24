#!/usr/bin/env python3
"""
Restart the Trading Nexus backend container on Coolify
Requires: paramiko library
Install with: pip install paramiko
"""

import sys
try:
    import paramiko
except ImportError:
    print("❌ paramiko not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], check=True)
    import paramiko

import time

print("=" *80)
print("TRADING NEXUS CONTAINER RESTART SCRIPT")
print("=" * 80)
print()

# Configuration
VPS_HOST = "72.62.228.112"
VPS_USER = "root"
VPS_PASSWORD_FILE = None  # Will prompt if not set

print(f"Connecting to {VPS_USER}@{VPS_HOST}...")

try:
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect
    try:
        client.connect(VPS_HOST, username=VPS_USER, allow_agent=False, look_for_keys=False)
        print("✅ Connected via SSH key")
    except:
        print("⚙️  SSH key auth failed, trying password...")
        # Read password from stdin
        import getpass
        password = getpass.getpass(f"Enter password for {VPS_USER}@{VPS_HOST}: ")
        client.connect(VPS_HOST, username=VPS_USER, password=password)
        print("✅ Connected via password")
    
    # Step 1: Find the backend container
    print("\nStep 1: Finding backend container...")
    stdin, stdout, stderr = client.exec_command(
        "docker ps --format '{{.Names}}' | grep -iE 'backend|p488ok8g8swo4ockks040ccg' | head -1"
    )
    container_name = stdout.read().decode().strip()
    
    if not container_name:
        print("❌ Backend container not found!")
        print("\nTrying to list all containers...")
        stdin, stdout, stderr = client.exec_command("docker ps --format 'table {{.Names}}\t{{.Status}}'")
        print(stdout.read().decode())
        client.close()
        exit(1)
    
    print(f"✅ Found container: {container_name}")
    
    # Step 2: Check current status
    print("\nStep 2: Checking container status...")
    stdin, stdout, stderr = client.exec_command(f"docker inspect {container_name} --format='{{{{.State.Running}}}}'")
    is_running = stdout.read().decode().strip() == "true"
    print(f"   Container is {'running' if is_running else 'not running'}")
    
    # Step 3: Restart container
    print("\nStep 3: Restarting container...")
    stdin, stdout, stderr = client.exec_command(f"docker restart {container_name}")
    output = stdout.read().decode().strip()
    errors = stderr.read().decode().strip()
    
    if errors:
        print(f"❌ Error: {errors}")
        client.close()
        exit(1)
    
    print(f"✅ Restart command sent: {output}")
    
    # Step 4: Wait and verify
    print("\nStep 4: Waiting for container to restart (20 seconds)...")
    time.sleep(20)
    
    # Check if running
    stdin, stdout, stderr = client.exec_command(f"docker inspect {container_name} --format='{{{{.State.Running}}}}'")
    is_running = stdout.read().decode().strip() == "true"
    
    if is_running:
        print("✅ Container is running")
    else:
        print("⚠️  Container may not be fully started yet")
    
    # Step 5: Check logs
    print("\nStep 5: Checking startup logs...")
    stdin, stdout, stderr = client.exec_command(f"docker logs {container_name} --tail 20")
    logs = stdout.read().decode()
    if "Application startup complete" in logs or "Uvicorn running" in logs:
        print("✅ Application appears to be running correctly")
    else:
        print("⚠️  Check logs manually")
        print(logs[:500])
    
    client.close()
    
    print("\n" + "=" * 80)
    print("✅ RESTART COMPLETE")
    print("=" * 80)
    print("\nTesting new authentication suggestions endpoint...")
    print("Run this in another terminal:")
    print('  python test_search_fix.py')
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
