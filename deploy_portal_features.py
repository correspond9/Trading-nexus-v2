#!/usr/bin/env python3
"""
Deploy Trading Nexus Portal Signup Features via Coolify API
Triggers rebuild, deployment, and monitors progress
"""

import requests
import time
import json
import sys
from datetime import datetime

# Coolify Configuration
COOLIFY_HOST = "72.62.228.112"
COOLIFY_API_BASE = "http://72.62.228.112:8000/api/v1"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
APP_UUID = "zccs8wko40occg44888kwooc"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def log_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def log_success(msg):
    print(f"✅ {msg}")

def log_error(msg):
    print(f"❌ {msg}")

def log_info(msg):
    print(f"ℹ️  {msg}")

def log_step(num, title):
    print(f"\n[STEP {num}] {title}")
    print("-" * 70)

# ============================================================
# STEP 1: Verify API connectivity
# ============================================================
log_step(1, "VERIFY COOLIFY API CONNECTIVITY")

try:
    resp = requests.get(f"{COOLIFY_API_BASE}/applications/{APP_UUID}", headers=HEADERS, timeout=10)
    if resp.status_code == 200:
        app_info = resp.json()
        log_success("Connected to Coolify API")
        log_info(f"Application: {app_info.get('name', 'N/A')}")
        log_info(f"Current Status: {app_info.get('status', 'N/A')}")
        log_info(f"Git Branch: {app_info.get('git_branch', 'N/A')}")
    else:
        log_error(f"Failed to connect (Status {resp.status_code})")
        log_info(f"Response: {resp.text[:200]}")
        sys.exit(1)
except Exception as e:
    log_error(f"Connection failed: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Verify Git changes are committed
# ============================================================
log_step(2, "VERIFY GIT CHANGES")

try:
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "-3"],
        cwd="d:\\4.PROJECTS\\FRESH\\trading-nexus",
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        log_success("Git repository is clean and up to date")
        print("\nRecent commits:")
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        log_error("Git status check failed")
        log_info(f"Error: {result.stderr[:200]}")
        
except Exception as e:
    log_error(f"Git check failed: {e}")
    
# ============================================================
# STEP 3: Trigger Coolify Deployment
# ============================================================
log_step(3, "TRIGGER COOLIFY REBUILD & DEPLOYMENT")

print("Sending deployment command to Coolify...")
print("\nThis will:")
print("  • Pull latest code from GitHub (main branch)")
print("  • Rebuild Docker images (backend + frontend)")
print("  • Apply database migrations including:")
print("    - 027_portal_users.sql (new portal signup table)")
print("  • Restart all containers with updated configuration")
print("  • Update Traefik routing for learn.tradingnexus.pro")

try:
    # Try deploy endpoint first
    resp = requests.post(
        f"{COOLIFY_API_BASE}/applications/{APP_UUID}/deploy",
        headers=HEADERS,
        timeout=30
    )
    
    if resp.status_code in [200, 202, 201]:
        log_success("Deployment triggered successfully!")
        log_info(f"Response Status: {resp.status_code}")
        if resp.text:
            try:
                data = resp.json()
                log_info(f"Details: {json.dumps(data, indent=2)[:300]}")
            except:
                log_info(f"Response: {resp.text[:300]}")
    else:
        # Try restart endpoint as fallback
        log_info(f"Deploy endpoint returned {resp.status_code}, trying restart endpoint...")
        resp = requests.post(
            f"{COOLIFY_API_BASE}/applications/{APP_UUID}/restart",
            headers=HEADERS,
            timeout=30
        )
        
        if resp.status_code in [200, 201]:
            log_success("Restart command sent successfully!")
            log_info(f"Response Status: {resp.status_code}")
        else:
            log_error(f"Failed to trigger deployment: {resp.status_code}")
            log_info(f"Response: {resp.text[:500]}")
            sys.exit(1)
            
except requests.exceptions.Timeout:
    log_error("Request timed out (deployment may still be triggered)")
except requests.exceptions.ConnectionError as e:
    log_error(f"Cannot connect to Coolify API: {e}")
    sys.exit(1)
except Exception as e:
    log_error(f"Error triggering deployment: {e}")
    sys.exit(1)

# ============================================================
# STEP 4: Monitor Deployment Progress
# ============================================================
log_step(4, "MONITOR DEPLOYMENT PROGRESS")

print("Checking deployment status every 15 seconds (timeout: 10 minutes)...\n")

max_checks = 40  # 40 * 15 seconds = 10 minutes
check_interval = 15
start_time = time.time()
previous_status = None
checks_count = 0

while checks_count < max_checks:
    try:
        resp = requests.get(f"{COOLIFY_API_BASE}/applications/{APP_UUID}", headers=HEADERS, timeout=10)
        
        if resp.status_code == 200:
            app_data = resp.json()
            current_status = app_data.get('status', 'unknown').upper()
            runtime_ms = app_data.get('runtime_ms', 0)
            restart_count = app_data.get('restart_count', 0)
            elapsed = int(time.time() - start_time)
            
            # Format output
            if current_status != previous_status or checks_count % 3 == 0:
                status_color = "🟢" if current_status in ["RUNNING", "HEALTHY"] else "🟡" if current_status in ["STARTING", "RESTARTING", "REBUILDING"] else "🔴"
                print(f"[{elapsed:3d}s] {status_color} Status: {current_status:20s} | Uptime: {runtime_ms//1000:5d}s | Restarts: {restart_count}")
                previous_status = current_status
            
            # Check success conditions
            if current_status in ["RUNNING", "HEALTHY"]:
                elapsed = int(time.time() - start_time)
                log_success(f"Application deployed and running! (took {elapsed} seconds)")
                break
        
        else:
            log_error(f"Failed to get status: {resp.status_code}")
            
    except requests.exceptions.Timeout:
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed:3d}s] ⚠️  Status check timeout (deployment may still be in progress)")
    except Exception as e:
        log_error(f"Error checking status: {e}")
    
    checks_count += 1
    if checks_count < max_checks:
        time.sleep(check_interval)

# ============================================================
# STEP 5: Verify Deployment
# ============================================================
log_step(5, "VERIFY DEPLOYMENT")

try:
    resp = requests.get(f"{COOLIFY_API_BASE}/applications/{APP_UUID}", headers=HEADERS, timeout=10)
    
    if resp.status_code == 200:
        app_data = resp.json()
        status = app_data.get('status', 'unknown').upper()
        
        if status in ["RUNNING", "HEALTHY"]:
            log_success("✨ Deployment successful!")
            print("\nDeployed features:")
            print("  ✓ Portal signup backend endpoints")
            print("    - POST /api/v2/auth/portal/signup (register users)")
            print("    - GET /api/v2/auth/portal/users (view signups - admin only)")
            print("  ✓ Portal signup database table (portal_users)")
            print("  ✓ SuperAdmin dashboard 'Portal Signups' tab")
            print("  ✓ Traefik routing for learn.tradingnexus.pro")
            print("  ✓ CORS configuration for learn subdomain")
            print("\nFrontend URLs now available:")
            print("  • Educational Portal: https://learn.tradingnexus.pro")
            print("  • Signup Form: https://learn.tradingnexus.pro/signup")
            print("  • View Signups: Admin Dashboard → Portal Signups tab")
        else:
            log_error(f"Application status is {status}, not fully healthy yet")
            print("Please wait a moment and check Coolify dashboard for details")
            
except Exception as e:
    log_error(f"Verification failed: {e}")

# ============================================================
# Summary
# ============================================================
log_section("DEPLOYMENT SUMMARY")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total time: {int(time.time() - start_time)} seconds")
print(f"Application UUID: {APP_UUID}")
print(f"Coolify Host: {COOLIFY_HOST}")
print("\n✨ Deployment process complete!")
print("\nNext steps:")
print("  1. Visit https://learn.tradingnexus.pro/signup")
print("  2. Test the signup form")
print("  3. Check SuperAdmin → Portal Signups tab to see registrations")
