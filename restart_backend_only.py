#!/usr/bin/env python3
"""Restart backend container only"""
import paramiko
import time
import getpass

VPS_HOST = "72.62.228.112"
VPS_USER = "root"

print("=" * 80)
print("RESTARTING BACKEND CONTAINER")
print("=" * 80)
print()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print(f"Connecting to {VPS_USER}@{VPS_HOST}...")
password = getpass.getpass(f"Password: ")
client.connect(VPS_HOST, username=VPS_USER, password=password, allow_agent=False, look_for_keys=False)
print("✅ Connected")

# List all containers first
print("\nRunning containers:")
stdin, stdout, stderr = client.exec_command("docker ps --format 'table {{.Names}}\\t{{.Status}}'")
output = stdout.read().decode()
print(output)

# Find backend container - specifically exclude frontend
stdin, stdout, stderr = client.exec_command(
    "docker ps --format='{{.Names}}' | grep backend | grep -v frontend | head -1"
)
backend_container = stdout.read().decode().strip()

if backend_container:
    print(f"\n✅ Found backend: {backend_container}")
    print("Restarting...")
    stdin, stdout, stderr = client.exec_command(f"docker restart {backend_container}")
    print(f"Restart command output: {stdout.read().decode().strip()}")
    
    print("Waiting 15 seconds for container to start...")
    time.sleep(15)
    
    # Verify running
    stdin, stdout, stderr = client.exec_command(
        f"docker inspect {backend_container} --format='{{{{.State.Running}}}}'"
    )
    is_running = stdout.read().decode().strip() == "true"
    print(f"Container is running: {is_running}")
    
    if is_running:
        print("\n✅ BACKEND RESTARTED SUCCESSFULLY!")
        print("\nThe new code with instrument search suggestions is now loaded.")
        print("Test the search endpoint:")
        print("  python test_search_fix.py")
    else:
        print("⚠️  Container status unclear, waiting longer...")
        time.sleep(15)
else:
    print("❌ Could not find backend container")
    print("\nManual next step:")
    print("1. SSH to root@72.62.228.112")
    print("2. Run: docker ps | grep backend")
    print("3. Run: docker restart <container_name>")

client.close()
print("=" * 80)
