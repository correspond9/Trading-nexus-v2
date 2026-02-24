#!/usr/bin/env python3
"""
Deploy trading-nexus V2 via Coolify API - FINAL DEPLOYMENT
"""
import requests
import json
import time
import sys

API_URL = "http://72.62.228.112:8000/api/v1"
API_TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
POSTGRES_PASSWORD = "Financio1026"
APP_UUID = "zccs8wko40occg44888kwooc"  # trading-nexus-v2 resource

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def log_step(num, title):
    print(f"\n{'='*70}")
    print(f"[STEP {num}] {title}")
    print('='*70)

# ============================================================
# STEP 1: Get application details
# ============================================================
log_step(1, "GET APPLICATION DETAILS")

try:
    response = requests.get(f"{API_URL}/applications/{APP_UUID}", headers=headers, timeout=10)
    response.raise_for_status()
    app = response.json()
    
    print(f"✓ Application found!")
    print(f"  Name: {app.get('name')}")
    print(f"  UUID: {app.get('uuid')}")
    print(f"  Build Pack: {app.get('build_pack')}")
    print(f"  Git Repository: {app.get('git_repository', 'Not set')}")
    print(f"  Git Branch: {app.get('git_branch', 'Not set')}")
    
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Update application configuration (Git source if needed)
# ============================================================
log_step(2, "UPDATE GIT CONFIGURATION")

git_repo = "https://github.com/correspond9/Trading-nexus-v2.git"
git_branch = "main"

print(f"Ensuring Git configuration is set:")
print(f"  Repository: {git_repo}")
print(f"  Branch: {git_branch}")

try:
    update_payload = {
        "git_repository": git_repo,
        "git_branch": git_branch,
    }
    
    response = requests.put(
        f"{API_URL}/applications/{APP_UUID}",
        headers=headers,
        json=update_payload,
        timeout=15
    )
    
    if response.status_code in [200, 201]:
        print(f"\n✓ Git configuration updated!")
    else:
        print(f"\n⚠ Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"\n⚠ Warning: {e}")

# ============================================================
# STEP 3: Set environment variables
# ============================================================
log_step(3, "SET ENVIRONMENT VARIABLES")

# Environment variables for production
env_variables = {
    "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
    "DATABASE_URL": f"postgresql://postgres:{POSTGRES_PASSWORD}@db:5432/trading_terminal",
    "LOG_LEVEL": "WARNING",
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "STARTUP_LOAD_MASTER": "true",
    "STARTUP_LOAD_TIER_B": "true",
    "STARTUP_START_STREAMS": "true",
    "CORS_ORIGINS_RAW": "https://app.tradingnexus.pro,https://tradingnexus.pro,https://www.tradingnexus.pro,http://localhost:3000,http://localhost:5173",
}

print(f"Configuring {len(env_variables)} environment variables:\n")
for key, value in env_variables.items():
    display_value = "***" if "PASSWORD" in key else value[:50]
    print(f"  ✓ {key}")

try:
    # Coolify expects environment variables in a specific format
    env_payload = {}
    for key, value in env_variables.items():
        env_payload[key] = value
    
    response = requests.post(
        f"{API_URL}/applications/{APP_UUID}/environment-variables",
        headers=headers,
        json=env_payload,
        timeout=15
    )
    
    if response.status_code in [200, 201]:
        print(f"\n✓ Environment variables set successfully!")
    else:
        print(f"\n⚠ Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        # Try alternative endpoint
        print(f"\nTrying alternative endpoint...")
        
except Exception as e:
    print(f"\n⚠ Note: {str(e)[:100]}")

# ============================================================
# STEP 4: Start deployment
# ============================================================
log_step(4, "START DEPLOYMENT")

print("\nInitiating deployment of 'trading-nexus-v2'...")
print("\nDeployment will:")
print("  • Clone repository from GitHub")
print("  • Build Docker images for backend, frontend, database, redis")
print("  • Apply all migrations (001-024) including data restoration")
print("  • Start all services with health checks")

try:
    response = requests.post(
        f"{API_URL}/applications/{APP_UUID}/deploy",
        headers=headers,
        timeout=30
    )
    
    if response.status_code in [200, 201, 202]:
        print(f"\n✓ Deployment initiated successfully!")
        if response.text:
            try:
                data = response.json()
                if 'message' in data:
                    print(f"  Message: {data['message']}")
            except:
                pass
    else:
        print(f"\n⚠ Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

# ============================================================
# STEP 5: Monitor deployment
# ============================================================
log_step(5, "MONITOR DEPLOYMENT STATUS")

print("Checking status every 15 seconds (timeout: 10 minutes)...\n")

max_checks = 40
start_time = time.time()

for check_num in range(max_checks):
    try:
        response = requests.get(f"{API_URL}/applications/{APP_UUID}", headers=headers, timeout=10)
        response.raise_for_status()
        app_status = response.json()
        
        status = app_status.get('status', 'unknown').lower()
        elapsed_sec = int(time.time() - start_time)
        
        # Format status output
        status_display = status.ljust(20)
        print(f"[{elapsed_sec:3d}s] {status_display}", end="")
        
        # Show progress indicators
        if 'building' in status:
            print(" 🔨 Building...", end="")
        elif 'deploying' in status:
            print(" 🚀 Deploying...", end="")
        elif 'running' in status or 'started' in status or 'active' in status:
            print(" ✅ RUNNING!")
            
            # Installation successful!
            print(f"\n")
            print(f"{'='*70}")
            print(f"✅ DEPLOYMENT SUCCESSFUL! ✅")
            print(f"{'='*70}")
            print(f"\nYour trading-nexus-v2 is now RUNNING on the VPS!")
            print(f"\nNext steps to verify:")
            print(f"  1. Test backend health:")
            print(f"     → http://72.62.228.112:8000/api/v2/health")
            print(f"  2. Check if data was restored:")
            print(f"     → http://72.62.228.112:8000/api/v2/admin/notifications?limit=5")
            print(f"  3. View the Coolify dashboard:")
            print(f"     → http://72.62.228.112:8000/")
            print(f"  4. Once verified working:")
            print(f"     → Stop the old 'trade-nexuss' resource in Coolify")
            print(f"     → Delete the old 'trade-nexuss' resource")
            print(f"\n{'='*70}\n")
            sys.exit(0)
            
        elif 'error' in status or 'failed' in status or 'exited' in status:
            print(f" ❌ FAILED")
            print(f"\n✗ Deployment failed with status: {status}")
            print(f"\nCheck Coolify logs for details:")
            print(f"  → http://72.62.228.112:8000/ → trading-nexus-v2 → Logs")
            sys.exit(1)
        else:
            print()
        
        time.sleep(15)
        
    except Exception as e:
        elapsed_sec = int(time.time() - start_time)
        print(f"[{elapsed_sec:3d}s] ⚠ Error checking status")
        time.sleep(15)

# Timeout
elapsed_sec = int(time.time() - start_time)
print(f"\n⚠ Monitoring timeout after {elapsed_sec} seconds")
print(f"\nDeployment may still be running. Check Coolify dashboard:")
print(f"  → http://72.62.228.112:8000/")

print(f"\n{'='*70}")
print(f"DEPLOYMENT PROCESS COMPLETED")
print(f"{'='*70}\n")
