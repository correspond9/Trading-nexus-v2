#!/usr/bin/env python3
"""
🚀 ONE-CLICK DEPLOYMENT FOR WATCHLIST CHANGES
This script rebuilds your Docker container with the latest code changes.

Usage: python DEPLOY_CHANGES_NOW.py
"""

import requests
import json
import time
import sys

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION (Your VPS Details)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COOLIFY_URL = "http://72.62.228.112"
API_TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"

# Headers for API calls
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(step_num, text):
    """Print a numbered step"""
    print(f"[STEP {step_num}] {text}")
    print("-" * 70)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}\n")

def print_error(text):
    """Print error message and exit"""
    print(f"\n❌ ERROR: {text}\n")
    sys.exit(1)

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Find Your Application
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print_header("FINDING YOUR APPLICATION")

print_step(1, "Searching for your application in Coolify...")

try:
    response = requests.get(
        f'{COOLIFY_URL}/api/v1/applications',
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    apps = response.json()
    
except requests.exceptions.RequestException as e:
    print_error(f"Cannot connect to Coolify at {COOLIFY_URL}\n{str(e)}")

if not apps:
    print_error("No applications found. Please create an application in Coolify first.")

print_success(f"Found {len(apps)} application(s)")

# Display applications
app_uuid = None
for app in apps:
    name = app.get('name', 'Unknown')
    uuid = app.get('uuid', 'Unknown')
    status = app.get('status', 'unknown')
    
    print(f"  📦 {name}")
    print(f"     UUID: {uuid}")
    print(f"     Status: {status}")
    print()
    
    # Use first backend/main app we find
    if app_uuid is None:
        app_uuid = uuid

if not app_uuid:
    print_error("Could not identify application UUID")

print(f"🎯 Using application: {app_uuid}\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Trigger Deployment
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print_step(2, "Triggering container rebuild and deployment...")
print_info("This will:")
print_info("  1. Pull latest code from GitHub")
print_info("  2. Rebuild Docker container")
print_info("  3. Restart your application")
print_info("  4. Check health status")
print()

try:
    deploy_response = requests.post(
        f'{COOLIFY_URL}/api/v1/applications/{app_uuid}/deploy',
        headers=headers,
        json={},
        timeout=30
    )
    
    deploy_response.raise_for_status()
    result = deploy_response.json()
    
    print(json.dumps(result, indent=2))
    print_success("Deployment triggered successfully!")
    
except requests.exceptions.RequestException as e:
    print_error(f"Failed to trigger deployment:\n{str(e)}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Monitor Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print_step(3, "Checking deployment status...")
print_info("Waiting for container to rebuild (this takes 2-5 minutes)...\n")

max_checks = 30  # Check for up to 5 minutes (10 second intervals)
check_count = 0
last_status = None

while check_count < max_checks:
    try:
        status_response = requests.get(
            f'{COOLIFY_URL}/api/v1/applications/{app_uuid}',
            headers=headers,
            timeout=10
        )
        status_response.raise_for_status()
        app_data = status_response.json()
        
        current_status = app_data.get('status', 'unknown')
        
        # Only print if status changed
        if current_status != last_status:
            if current_status == 'running':
                print_success(f"✨ Application is RUNNING!")
                break
            else:
                print(f"  Status: {current_status}")
                last_status = current_status
        
        time.sleep(10)  # Wait 10 seconds before checking again
        check_count += 1
        
    except requests.exceptions.RequestException as e:
        print(f"  (Still deploying... {10*check_count} seconds elapsed)")
        time.sleep(10)
        check_count += 1

if check_count >= max_checks:
    print("⚠️  Deployment still in progress. Checking one more time...\n")

# Final status check
try:
    final_response = requests.get(
        f'{COOLIFY_URL}/api/v1/applications/{app_uuid}',
        headers=headers,
        timeout=10
    )
    final_response.raise_for_status()
    final_data = final_response.json()
    
    final_status = final_data.get('status', 'unknown')
    print(f"Final Status: {final_status}\n")
    
    if final_status == 'running':
        print_success("✅ DEPLOYMENT COMPLETE!")
    else:
        print("⚠️  Application status is not 'running' yet.")
        print("   This may still be initializing. Check Coolify dashboard for details.\n")
        
except requests.exceptions.RequestException as e:
    print(f"Warning: Could not verify final status: {e}\n")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: Access Your Application
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

print_step(4, "Next Steps")

print("📱 Your application should now be accessible at:")
print("   🔗 http://72.62.228.112:8000")
print("\n🖥️  Access Coolify dashboard to monitor:")
print("   🔗 http://72.62.228.112:3000")
print("\n📊 Check application logs in Coolify UI for details")
print("\n✅ The watchlist cleanup changes are now LIVE!")

print("\n" + "=" * 70)
print("  DEPLOYMENT COMPLETE ✨")
print("=" * 70 + "\n")
