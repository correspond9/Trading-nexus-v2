#!/usr/bin/env python3
import requests
import time

API_BASE = "http://72.62.228.112:8000/api/v1"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
APP_UUID = "zccs8wko40occg44888kwooc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("DEPLOYING WITH MIGRATION 024 FIX")
print("=" * 80)
print("\nFixes applied:")
print("  - command_timeout: 30s → 600s (for large migration)")
print("  - health check start_period: 180s → 300s")
print("  - TRUNCATE: using IF EXISTS (handles non-existent tables)")
print()

# Trigger restart
print("Triggering restart via Coolify API...")
try:
    resp = requests.post(
        f"{API_BASE}/applications/{APP_UUID}/restart",
        headers=headers,
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        exit(1)
    print("✓ Restart command sent\n")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Monitor status
print("=" * 80)
print("Monitoring deployment (timeout: 20 minutes)...")
print("=" * 80)

max_wait = 1200  # 20 minutes
poll_interval = 20
checks = 0
last_status = None

while checks * poll_interval < max_wait:
    try:
        resp = requests.get(f"{API_BASE}/applications/{APP_UUID}", headers=headers, timeout=10)
        if resp.status_code == 200:
            app = resp.json()
            status = app.get("status", "unknown")
            
            if status != last_status:
                print(f"[{checks * poll_interval}s] Status: {status}")
                last_status = status
            
            # Successfully running
            if "running" in status.lower():
                print("\n" + "=" * 80)
                print("✓ DEPLOYMENT SUCCESSFUL - Application is RUNNING")
                print("=" * 80)
                exit(0)
            
            # Failed
            if "exited" in status.lower() or "error" in status.lower():
                print(f"\n✗ Deployment failed: {status}")
                print("Check Coolify dashboard for error logs")
                exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
    
    checks += 1
    time.sleep(poll_interval)

print(f"\n✗ Timeout after {max_wait} seconds")
exit(1)
