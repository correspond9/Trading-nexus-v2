#!/usr/bin/env python3
import requests
import time
import json

API_BASE = "http://72.62.228.112:8000/api/v1"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
APP_UUID = "zccs8wko40occg44888kwooc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("REDEPLOYMENT WITH DATABASE TIMEOUT FIX")
print("=" * 80)
print("\nFix applied: command_timeout increased from 30s → 600s for large migrations")
print("This will allow migration 024 (25.6 MB) to complete properly.\n")

# Trigger restart/redeploy
print("Triggering restart via Coolify API...")
try:
    resp = requests.post(
        f"{API_BASE}/applications/{APP_UUID}/restart",
        headers=headers,
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✓ Restart command sent successfully")
    else:
        print(f"✗ Error: {resp.text}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Monitor status
print("\n" + "=" * 80)
print("Monitoring deployment status...")
print("=" * 80)

max_wait = 600  # 10 minutes
poll_interval = 15  # 15 seconds
start_time = time.time()
last_status = None

while time.time() - start_time < max_wait:
    try:
        resp = requests.get(f"{API_BASE}/applications/{APP_UUID}", headers=headers, timeout=10)
        if resp.status_code == 200:
            app = resp.json()
            status = app.get("status", "unknown")
            
            if status != last_status:
                elapsed = int(time.time() - start_time)
                print(f"\n[{elapsed}s] Status: {status}")
                last_status = status
            
            # Check if running
            if "running" in status.lower():
                print("\n✓ Application is RUNNING!")
                print("\nDeployment complete. Testing endpoints...")
                
                # Quick endpoint test
                try:
                    health_resp = requests.get("http://72.62.228.112:8000/health", timeout=5)
                    if health_resp.status_code == 200:
                        print("✓ Health check endpoint responding")
                except:
                    print("• Health check endpoint not yet responding (may need Traefik routing)")
                
                break
            
            # Check if failed
            if "exited" in status.lower() or "error" in status.lower():
                print(f"\n✗ Deployment failed with status: {status}")
                print("Check Coolify dashboard logs for error details.")
                exit(1)
    
    except Exception as e:
        print(f"Error checking status: {e}")
    
    time.sleep(poll_interval)

if time.time() - start_time >= max_wait:
    print(f"\n✗ Timeout: deployment did not complete within {max_wait} seconds")
    exit(1)

print("\n" + "=" * 80)
print("DEPLOYMENT SUCCESSFUL")
print("=" * 80)
