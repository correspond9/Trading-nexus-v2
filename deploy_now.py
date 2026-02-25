#!/usr/bin/env python3
"""
Deploy trading-nexus V2 - FINAL DEPLOYMENT WITH CORRECT DOCKER COMPOSE FILE
"""
import requests
import time
import sys

API_URL = "http://72.62.228.112:8000/api/v1"
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
APP_UUID = "x8gg0og8440wkgc8ow0ococs"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def log_step(num, title):
    print(f"\n{'='*70}")
    print(f"[STEP {num}] {title}")
    print('='*70)

# ============================================================
# STEP 1: Verify application configuration
# ============================================================
log_step(1, "VERIFY APPLICATION CONFIGURATION")

try:
    response = requests.get(f"{API_URL}/applications/{APP_UUID}", headers=headers, timeout=10)
    app = response.json()
    
    print(f"Application: {app.get('name')}")
    print(f"Docker Compose Location: {app.get('docker_compose_location')}")
    print(f"Git Repository: {app.get('git_repository')}")
    print(f"Git Branch: {app.get('git_branch')}")
    print(f"Build Pack: {app.get('build_pack')}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Restart application to trigger deployment
# ============================================================
log_step(2, "RESTART APPLICATION & TRIGGER DEPLOYMENT")

print("Sending restart command...")
print("\nDeployment will:")
print("  • Pull latest code from GitHub (with data migration 024)")
print("  • Build Docker images for all services (backend, frontend, db, redis)")
print("  • Apply all SQL migrations (001-024) including production data restore")
print("  • Start all services and run health checks")
print("  • Configure Traefik routing to domains")

try:
    response = requests.post(
        f"{API_URL}/applications/{APP_UUID}/restart",
        headers=headers,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"\n✓ Restart command sent!")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)

# ============================================================
# STEP 3: Monitor deployment progress
# ============================================================
log_step(3, "MONITOR DEPLOYMENT (This typically takes 3-5 minutes)")

print("Checking every 20 seconds...\n")

max_checks = 50  # 50 * 20 = ~1000 seconds (17 minutes)
start_time = time.time()
previous_status = None

for check_num in range(max_checks):
    try:
        response = requests.get(f"{API_URL}/applications/{APP_UUID}", headers=headers, timeout=10)
        app_status = response.json()
        
        status = app_status.get('status', 'unknown').lower()
        elapsed_sec = int(time.time() - start_time)
        
        # Print status updates
        if status != previous_status or check_num % 3 == 0:
            status_display = status.ljust(25)
            print(f"[{elapsed_sec:3d}s] {status_display}", end="")
            
            if 'building' in status:
                print(" 🔨")
            elif 'deploying' in status or 'restarting' in status:
                print(" 🚀")
            elif 'running' in status or 'healthy' in status or 'active' in status:
                print(" ✅")
            else:
                print()
            
            previous_status = status
        
        # Success condition
        if 'running' in status or 'healthy' in status:
            elapsed_sec = int(time.time() - start_time)
            
            print(f"\n{'='*70}")
            print(f"✅✅✅ DEPLOYMENT SUCCESSFUL! ✅✅✅")
            print(f"{'='*70}")
            print(f"\n🎉 Your 'trading-nexus-v2' is now RUNNING!")
            print(f"Deployment took: {elapsed_sec} seconds ({elapsed_sec//60} min {elapsed_sec%60} sec)")
            print(f"\n" + "="*70)
            print(f"NEXT STEPS - VERIFICATION")
            print(f"="*70)
            
            # Wait a moment for services to fully stabilize
            print(f"\nGiving services 10 seconds to fully stabilize...")
            time.sleep(10)
            
            print(f"\n1️⃣  TEST BACKEND HEALTH:")
            print(f"    curl http://72.62.228.112:8000/api/v2/health")
            print(f"\n2️⃣  CHECK DATABASE DATA WAS RESTORED:")
            print(f"    curl http://72.62.228.112:8000/api/v2/admin/notifications?limit=5")
            print(f"\n3️⃣  VIEW COOLIFY DASHBOARD:")
            print(f"    → http://72.62.228.112:8000/")
            print(f"    → Projects → trade-nexuss → trade-nexus-v2 → Logs")
            
            print(f"\n4️⃣  ONCE VERIFIED - CLEAN UP OLD RESOURCE:")
            print(f"    • Stop old 'trade-nexuss' (the previous version)")
            print(f"    • Delete old 'trade-nexuss' resource")
            print(f"    • Keep 'trade-nexus-v2' as your main app")
            
            print(f"\n5️⃣  TEST KEY ENDPOINTS:")
            print(f"    • GET /api/v2/health (backend health)")
            print(f"    • GET /api/v2/market/stream-status (market data)")
            print(f"    • GET /api/v2/admin/notifications (data verification)")
            print(f"    • GET /api/v2/admin/dhan/status (DhanHQ integration)")
            
            print(f"\n" + "="*70)
            sys.exit(0)
        
        # Failed state
        elif 'error' in status or 'failed' in status:
            print(f"\n✗ Deployment failed: {status}")
            print(f"\nCheck Coolify logs for error details:")
            print(f"  → http://72.62.228.112:8000/")
            sys.exit(1)
        
        # Exited without running
        elif 'exited' in status and check_num > 5:  # After 2 minutes
            print(f"\n⚠️  Container exited: {status}")
            print(f"\nCheck Coolify logs:")
            print(f"  → http://72.62.228.112:8000/")
            sys.exit(1)
        
        time.sleep(20)
        
    except Exception as e:
        elapsed_sec = int(time.time() - start_time)
        print(f"[{elapsed_sec:3d}s] ⚠ Error checking status")
        time.sleep(20)

# Timeout
elapsed_sec = int(time.time() - start_time)
print(f"\n⚠️  Monitoring timeout after {elapsed_sec} seconds")
print(f"\nDeployment may still be running. Check Coolify dashboard:")
print(f"  → http://72.62.228.112:8000/\n")
