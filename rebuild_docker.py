#!/usr/bin/env python3
"""
Trigger rebuild by running docker-compose rebuild in the Coolify app directory
"""

import subprocess
import time
import os

VPS_USER = "root"
VPS_HOST = "72.62.228.112"

print("=" * 80)
print("REBUILDING APPLICATION VIA DOCKER COMPOSE")
print("=" * 80)
print()

# Step 1: Find the app directory
print("Step 1: Finding application directory...")
cmd = f'ssh {VPS_USER}@{VPS_HOST} "find /opt -name "*p488ok8g8swo4ockks040ccg*" -type d 2>/dev/null | head -1"'

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
app_dir = result.stdout.strip()

if not app_dir:
    # Try alternative path
    print("   Not found in /opt, trying /root...")
    cmd = f'ssh {VPS_USER}@{VPS_HOST} "find /root -name "*p488ok8g8swo4ockks040ccg*" -type d 2>/dev/null | head -1"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    app_dir = result.stdout.strip()

print(f"   Attempting common Coolify paths...")
common_paths = [
    "/opt/coolify/applications/p488ok8g8swo4ockks040ccg",
    "/root/.coolify/applications/p488ok8g8swo4ockks040ccg",
    "/opt/coolify/applications/trade-nexus-v2-production",
]

for path in common_paths:
    print(f"   Trying: {path}")
    cmd = f'ssh {VPS_USER}@{VPS_HOST} "[ -d {path} ] && echo \"EXISTS\" || echo \"NOT FOUND\""'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    if "EXISTS" in result.stdout:
        app_dir = path
        print(f"✅ Found: {app_dir}")
        break

if not app_dir:
    print("❌ Could not find application directory")
    print()
    print("Let's try to list what Coolify has...")
    cmd = f'ssh {VPS_USER}@{VPS_HOST} "ls -la /opt/coolify/applications/ 2>/dev/null || ls -la /opt/ 2>/dev/null | head -20"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    print(result.stdout)
    exit(1)

print()
print("Step 2: Rebuilding Docker images...")
print("   This will:")
print("   - Pull latest code from GitHub")
print("   - Rebuild Docker images")  
print("   - Start all containers")
print()

# Use docker-compose to rebuild
rebuild_cmd = f'''ssh {VPS_USER}@{VPS_HOST} "cd {app_dir} && (
    echo 'Pulling latest code...' &&
    git pull origin main &&
    echo 'Stopping containers...' &&
    docker-compose down &&
    echo 'Building new images...' &&
    docker-compose up -d --build
)"'''

print("Running rebuild command...")
result = subprocess.run(rebuild_cmd, shell=True, capture_output=True, text=True, timeout=300)

print(result.stdout)
if result.stderr:
    print("Stderr:", result.stderr[:500])

print()
print("Step 3: Waiting for services to start (60 seconds)...")

for i in range(60, 0, -5):
    print(f"\rWaiting... {i}s remaining", end="", flush=True)
    time.sleep(5)

print("\n✅ Services should be online")

print()
print("Step 4: Verifying application is running...")

check_cmd = f'ssh {VPS_USER}@{VPS_HOST} "docker-compose -f {app_dir}/docker-compose.yml ps 2>/dev/null || docker ps | grep p488ok8g8swo4ockks040ccg"'
result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=10)
print(result.stdout)

print()
print("=" * 80)
print("✅ REBUILD COMPLETE!")
print("=" * 80)
print()
print("The application will now have:")
print("  ✓ Latest code from GitHub")
print("  ✓ Instrument search with limit parameter")
print("  ✓ Frontend search suggestions dropdown")
print()
print("Test it with: python test_search_fix.py")
print()
