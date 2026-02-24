#!/usr/bin/env python3
"""
Configure trading-nexus V2 via Coolify API and deploy
"""
import requests
import json
import time
import sys

API_URL = "http://72.62.228.112:8000/api/v1"
API_TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
POSTGRES_PASSWORD = "Financio1026"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def log_step(num, title):
    print(f"\n{'='*70}")
    print(f"[STEP {num}] {title}")
    print('='*70)

# ============================================================
# STEP 1: Find the trading-nexus resource by name
# ============================================================
log_step(1, "FIND TRADING-NEXUS RESOURCE")

print("Searching for 'trading-nexus-v2' resource...")

try:
    response = requests.get(f"{API_URL}/resources", headers=headers, timeout=10)
    response.raise_for_status()
    resources = response.json()
    
    trading_nexus = None
    for resource in resources:
        print(f"\nFound: {resource.get('name')}")
        if 'trading-nexus-v2' in resource.get('name', '').lower():
            trading_nexus = resource
            print(f"  ✓ This is our resource!")
            break
    
    if not trading_nexus:
        print("\n✗ Resource not found!")
        print("Available resources:")
        for r in resources:
            print(f"  - {r.get('name')}")
        sys.exit(1)
    
    resource_uuid = trading_nexus['uuid']
    print(f"\n✓ Resource found!")
    print(f"  Name: {trading_nexus.get('name')}")
    print(f"  UUID: {resource_uuid}")
    print(f"  Type: {trading_nexus.get('type')}")
    
except requests.exceptions.RequestException as e:
    print(f"\n✗ FAILED: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Get current resource details
# ============================================================
log_step(2, "GET RESOURCE DETAILS")

try:
    response = requests.get(f"{API_URL}/resources/{resource_uuid}", headers=headers, timeout=10)
    response.raise_for_status()
    resource = response.json()
    
    print(f"Current status: {resource.get('status', 'unknown')}")
    print(f"Git repository: {resource.get('git_repository', 'N/A')}")
    print(f"Git branch: {resource.get('git_branch', 'N/A')}")
    
except Exception as e:
    print(f"Warning: Could not get full details: {e}")

# ============================================================
# STEP 3: Set environment variables
# ============================================================
log_step(3, "SET ENVIRONMENT VARIABLES")

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

print(f"Setting {len(env_variables)} environment variables:\n")
for key, value in env_variables.items():
    display_value = "***" if "PASSWORD" in key else value[:60]
    print(f"  ✓ {key} = {display_value}")

try:
    # Build env string format that Coolify expects
    env_string = ""
    for key, value in env_variables.items():
        # Escape any special characters in values
        escaped_value = value.replace('"', '\\"')
        env_string += f"{key}={escaped_value}\n"
    
    # Try updating the resource with environment variables
    payload = {
        "env": env_string
    }
    
    response = requests.put(
        f"{API_URL}/resources/{resource_uuid}",
        headers=headers,
        json=payload,
        timeout=15
    )
    
    if response.status_code in [200, 201]:
        print(f"\n✓ Environment variables set successfully!")
    else:
        print(f"\n⚠ Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
except requests.exceptions.RequestException as e:
    print(f"\n⚠ Note: {e}")
    print("This may be expected - Coolify might handle env vars differently")

# ============================================================
# STEP 4: Start deployment
# ============================================================
log_step(4, "START DEPLOYMENT")

print("Initiating deployment of 'trading-nexus-v2'...")
print("This will:")
print("  • Clone from GitHub (https://github.com/correspond9/Trading-nexus-v2.git)")
print("  • Build Docker images for all services")
print("  • Run database migrations (including data restore from migration 024)")
print("  • Start backend, frontend, database, and redis services")

try:
    response = requests.post(
        f"{API_URL}/resources/{resource_uuid}/deploy",
        headers=headers,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"\n✓ Deployment initiated successfully!")
        deployment_response = response.json() if response.text else {}
        if 'message' in deployment_response:
            print(f"  Message: {deployment_response['message']}")
    else:
        print(f"\n⚠ Status: {response.status_code}")
        if response.text:
            print(f"Response: {response.text[:300]}")
        
except requests.exceptions.RequestException as e:
    print(f"\n✗ FAILED: {e}")
    sys.exit(1)

# ============================================================
# STEP 5: Monitor deployment status
# ============================================================
log_step(5, "MONITOR DEPLOYMENT")

print("Checking deployment status every 15 seconds...\n")

max_checks = 40  # 10 minutes
for check_num in range(max_checks):
    try:
        response = requests.get(f"{API_URL}/resources/{resource_uuid}", headers=headers, timeout=10)
        response.raise_for_status()
        resource = response.json()
        
        status = resource.get('status', 'unknown').lower()
        updated_at = resource.get('updated_at', 'N/A')
        
        elapsed = (check_num + 1) * 15
        print(f"[{elapsed:3d}s] Status: {status:20s} | Updated: {updated_at}")
        
        if status in ['running', 'healthy', 'active', 'started']:
            print(f"\n{'='*70}")
            print(f"✓✓✓ APPLICATION IS RUNNING! ✓✓✓")
            print(f"{'='*70}")
            print(f"\nDeployment successful!")
            print(f"\nNext steps:")
            print(f"  1. Verify application health:")
            print(f"     → http://72.62.228.112:8000/api/v2/health")
            print(f"  2. Check database was restored:")
            print(f"     → http://72.62.228.112:8000/api/v2/admin/notifications")
            print(f"  3. View Coolify logs for details:")
            print(f"     → http://72.62.228.112:8000/")
            print(f"  4. When confirmed working, stop old 'trade-nexuss' resource")
            print(f"\n{'='*70}\n")
            break
            
        elif 'error' in status or 'failed' in status or 'exited' in status:
            print(f"\n✗ Deployment failed with status: {status}")
            print(f"Check Coolify logs for error details")
            break
            
        time.sleep(15)
        
    except requests.exceptions.RequestException as e:
        print(f"[{elapsed:3d}s] ⚠ Error checking status: {str(e)[:50]}")
        time.sleep(15)

if check_num == max_checks - 1:
    print(f"\n⚠ Timeout after {max_checks * 15} seconds")
    print(f"Deployment may still be running. Check Coolify dashboard.")

print("\n" + "="*70)
print("DEPLOYMENT PROCESS COMPLETED")
print("="*70)
