#!/usr/bin/env python3
"""
Safely restart the backend container and verify Tier-B subscriptions load.
"""
import subprocess
import time
import requests
import json

VPS_HOST = "72.62.228.112"
VPS_USER = "root"
APP_UUID = "p488ok8g8swo4ockks040ccg"

print("\n" + "=" * 80)
print("BACKEND RESTART PROCEDURE")
print("=" * 80 + "\n")

# Step 1: Find the backend container
print("[1] Finding backend container...")
cmd = f"""ssh {VPS_USER}@{VPS_HOST} "docker ps --format '{{{{.Names}}}}' | grep 'backend-{APP_UUID}'" """
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
backend_container = result.stdout.strip()

if not backend_container:
    print("❌ Backend container not found!")
    exit(1)

print(f"✓ Found: {backend_container}\n")

# Step 2: Stop the container
print("[2] Stopping backend container...")
stop_cmd = f"ssh {VPS_USER}@{VPS_HOST} \"docker stop {backend_container}\""
result = subprocess.run(stop_cmd, shell=True, capture_output=True, text=True, timeout=30)
if result.returncode == 0:
    print(f"✓ Container stopped")
else:
    print(f"⚠ Warning: {result.stderr}")

time.sleep(3)

# Step 3: Start the container
print("\n[3] Starting backend container...")
start_cmd = f"ssh {VPS_USER}@{VPS_HOST} \"docker start {backend_container}\""
result = subprocess.run(start_cmd, shell=True, capture_output=True, text=True, timeout=30)
if result.returncode == 0:
    print(f"✓ Container started")
else:
    print(f"❌ Failed to start: {result.stderr}")
    exit(1)

# Step 4: Wait for backend to be ready
print("\n[4] Waiting for backend to initialize (30-60 seconds)...")
for i in range(30):
    time.sleep(2)
    try:
        resp = requests.get('https://api.tradingnexus.pro/api/v2/health', timeout=5)
        if resp.status_code == 200:
            print(f"✓ Backend is responding after {i*2} seconds")
            time.sleep(5)  # Give it a few more seconds to fully initialize
            break
    except:
        if i % 5 == 0:
            print(f"  [{i*2}s] Still waiting for backend...")

# Step 5: Check DhanHQ status
print("\n[5] Checking DhanHQ subscription status...")
token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
headers = {'X-AUTH': token}

try:
    resp = requests.get('https://api.tradingnexus.pro/api/v2/admin/dhan/status', 
                       headers=headers, timeout=10)
    status = resp.json()
    
    total_tokens = sum(s.get('tokens', 0) for s in status.get('slots', []))
    
    print(f"✓ DhanHQ Status:")
    print(f"  Credentials: {status.get('has_credentials')}")
    print(f"  Connected: {status.get('connected')}")
    print(f"  Total tokens subscribed: {total_tokens}")
    print()
    
    if total_tokens > 0:
        print("✅ SUCCESS! Tier-B subscriptions loaded!")
        print()
        print("Per-slot breakdown:")
        for slot in status.get('slots', []):
            tokens = slot.get('tokens', 0)
            capacity = slot.get('capacity', 5000)
            print(f"  WS-{slot['slot']}: {tokens:,} / {capacity:,} tokens")
        print()
        print("✓ WebSocket data should now be flowing!")
    else:
        print("⚠ Still no tokens subscribed - initialization may not have completed")
        print("Wait a few more minutes and check again...")
        
except Exception as e:
    print(f"❌ Error checking status: {e}")
    exit(1)

print("\n" + "=" * 80)
print("RESTART COMPLETE")
print("=" * 80 + "\n")
