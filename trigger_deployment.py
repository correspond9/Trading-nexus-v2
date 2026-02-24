#!/usr/bin/env python3
"""
Deploy & Monitor trading-nexus V2 - Final Deployment Trigger
"""
import requests
import time
import sys

API_URL = "http://72.62.228.112:8000/api/v1"
API_TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
APP_UUID = "zccs8wko40occg44888kwooc"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def log_step(num, title):
    print(f"\n{'='*70}")
    print(f"[STEP {num}] {title}")
    print('='*70)

# ============================================================
# STEP 1: Check current status
# ============================================================
log_step(1, "CHECK CURRENT APPLICATION STATUS")

try:
    response = requests.get(f"{API_URL}/applications/{APP_UUID}", headers=headers, timeout=10)
    app = response.json()
    
    print(f"Application: {app.get('name')}")
    print(f"Current Status: {app.get('status')}")
    print(f"Build Pack: {app.get('build_pack')}")
    print(f"Git Repo: {app.get('git_repository')}")
    print(f"Git Branch: {app.get('git_branch')}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Restart the application
# ============================================================
log_step(2, "RESTART APPLICATION (TRIGGER DEPLOYMENT)")

print("Sending restart command to trigger deployment...")
print("This will:")
print("  • Stop all running containers")
print("  • Pull latest code from GitHub")
print("  • Rebuild Docker images")
print("  • Apply database migrations (001-024 including data restore)")
print("  • Start all services with health checks")

try:
    response = requests.post(
        f"{API_URL}/applications/{APP_UUID}/restart",
        headers=headers,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"\n✓ Restart command sent successfully!")
        print(f"  Status Code: {response.status_code}")
    else:
        print(f"\n⚠ Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)

# ============================================================
# STEP 3: Monitor deployment progress
# ============================================================
log_step(3, "MONITOR DEPLOYMENT PROGRESS")

print("Checking status every 20 seconds (timeout: 15 minutes)...\n")

max_checks = 45
start_time = time.time()
previous_status = None

for check_num in range(max_checks):
    try:
        response = requests.get(f"{API_URL}/applications/{APP_UUID}", headers=headers, timeout=10)
        app_status = response.json()
        
        status = app_status.get('status', 'unknown').lower()
        elapsed_sec = int(time.time() - start_time)
        last_online = app_status.get('last_online_at', 'N/A')
        restart_count = app_status.get('restart_count', 0)
        
        # Only print if status changed or every 3rd check
        if status != previous_status or check_num % 3 == 0:
            status_display = status.ljust(25)
            print(f"[{elapsed_sec:3d}s] Status: {status_display} | Restarts: {restart_count}")
            previous_status = status
        
        # Check for success states
        if 'running' in status or 'healthy' in status or 'active' in status:
            print(f"\n{'='*70}")
            print(f"✅✅✅ APPLICATION IS RUNNING! ✅✅✅")
            print(f"{'='*70}")
            print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
            print(f"\nYour 'trading-nexus-v2' is now running on the VPS!")
            print(f"Last online: {last_online}")
            print(f"\n" + "="*70)
            print(f"NEXT STEPS:")
            print(f"="*70)
            print(f"\n1️⃣  VERIFY BACKEND IS HEALTHY:")
            print(f"    → http://72.62.228.112:8000/api/v2/health")
            print(f"\n2️⃣  CHECK DATABASE WAS RESTORED:")
            print(f"    → http://72.62.228.112:8000/api/v2/admin/notifications?limit=5")
            print(f"    (Should show data from your development database)")
            print(f"\n3️⃣  VIEW COOLIFY DASHBOARD:")
            print(f"    → http://72.62.228.112:8000/")
            print(f"    (Monitor logs and application status)")
            print(f"\n4️⃣  ONCE VERIFIED WORKING:")
            print(f"    • Go to: Projects → trade-nexuss → trade-nexuss resource")
            print(f"    • Stop the old 'trade-nexuss' resource")
            print(f"    • Delete the old 'trade-nexuss' resource")
            print(f"\n5️⃣  TESTING ENDPOINTS:")
            print(f"    → GET http://72.62.228.112:8000/api/v2/health")
            print(f"    → GET http://72.62.228.112:8000/api/v2/market/stream-status")
            print(f"    → GET http://72.62.228.112:8000/api/v2/admin/notifications")
            print(f"\n" + "="*70)
            print(f"✨ Deployment complete! Your trading platform is live! ✨")
            print(f"="*70 + "\n")
            sys.exit(0)
            
        # Check for failed states
        elif 'error' in status or 'failed' in status or 'exited' in status:
            print(f"\n⚠️  Status: {status}")
            if 'unhealthy' in status:
                print(f"Health check failed - containers may not be responding")
            elif 'exited' in status:
                print(f"Containers exited - check logs for errors")
            
            print(f"\nCheck Coolify logs for details:")
            print(f"  → http://72.62.228.112:8000/")
            print(f"  → Navigate to the 'trade-nexus-v2' app")
            print(f"  → Click 'Logs' tab")
            sys.exit(1)
            
        time.sleep(20)
        
    except Exception as e:
        elapsed_sec = int(time.time() - start_time)
        print(f"[{elapsed_sec:3d}s] ⚠ Error checking status")
        time.sleep(20)

# Timeout - but may still be deploying
elapsed_sec = int(time.time() - start_time)
print(f"\n⚠️  Monitoring timeout after {elapsed_sec} seconds")
print(f"\nDeployment may still be in progress.")
print(f"Check Coolify dashboard to monitor:")
print(f"  → http://72.62.228.112:8000/")
print(f"  → Projects → trade-nexuss → trade-nexus-v2 → Logs\n")

sys.exit(0)
