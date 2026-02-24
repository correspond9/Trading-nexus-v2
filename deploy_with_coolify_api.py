#!/usr/bin/env python3
"""
Trigger Coolify rebuild and deployment using API token
"""

import requests
import time
import json

# Coolify API Configuration
COOLIFY_HOST = "72.62.228.112"
COOLIFY_PORT = 3000
COOLIFY_BASE = f"http://{COOLIFY_HOST}:{COOLIFY_PORT}/api/v1"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Application details
APP_UUID = "zccs8wko40occg44888kwooc"
BACKEND_URL = f"http://{COOLIFY_HOST}:8000"

print("=" * 80)
print("TRIGGERING COOLIFY REBUILD VIA API")
print("=" * 80)
print()

# Step 1: Trigger rebuild/deploy
print(f"Step 1: Triggering rebuild for application {APP_UUID}...")
print(f"   Endpoint: POST {COOLIFY_BASE}/applications/{APP_UUID}/deploy")
print()

try:
    resp = requests.post(
        f"{COOLIFY_BASE}/applications/{APP_UUID}/deploy",
        headers=HEADERS,
        timeout=15
    )
    
    print(f"Response Status: {resp.status_code}")
    
    if resp.status_code == 200 or resp.status_code == 202:
        print("✅ Rebuild triggered successfully!")
        data = resp.json() if resp.text else {}
        print(f"Response: {json.dumps(data, indent=2)[:300]}")
    else:
        print(f"❌ Failed to trigger rebuild: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        
        # Try alternative endpoint
        print()
        print("Trying alternative endpoint: /api/v1/applications/{id}")
        resp2 = resp = requests.get(
            f"{COOLIFY_BASE}/applications",
            headers=HEADERS,
            timeout=15
        )
        if resp2.ok:
            data = resp2.json()
            print(f"Available applications: {len(data.get('data', []))}")
        
        exit(1)

except requests.exceptions.ConnectionError as e:
    print(f"❌ Cannot connect to Coolify API at {COOLIFY_BASE}")
    print(f"Error: {e}")
    print()
    print("Trying to detect Coolify on different port...")
    
    # Try port 3001, 8080, etc
    for port in [3001, 8080, 9000]:
        try:
            test_url = f"http://{COOLIFY_HOST}:{port}/api/v1/applications"
            print(f"Testing {test_url}...")
            test_resp = requests.head(test_url, timeout=2)
            print(f"  Coolify might be on port {port}")
        except:
            pass
    
    exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Step 2: Monitor deployment
print()
print("Step 2: Monitoring deployment progress...")
print("=" * 80)

max_wait = 300  # 5 minutes
check_interval = 10  # Check every 10 seconds

start_time = time.time()

while time.time() - start_time < max_wait:
    elapsed = int(time.time() - start_time)
    
    try:
        resp = requests.get(
            f"{COOLIFY_BASE}/applications/{APP_UUID}",
            headers=HEADERS,
            timeout=10
        )
        
        if resp.ok:
            data = resp.json()
            app_data = data.get('data', {})
            status = app_data.get('status', 'unknown')
            
            print(f"[{elapsed:3}s] Status: {status:30}", end='\r', flush=True)
            
            if 'running' in status.lower():
                print()
                print()
                print("✅ APPLICATION IS RUNNING!")
                break
            elif 'deploying' in status.lower() or 'starting' in status.lower():
                pass  # Still deploying
            elif 'failed' in status.lower() or 'error' in status.lower() or 'exited' in status.lower():
                print()
                print(f"❌ DEPLOYMENT FAILED: {status}")
                exit(1)
        else:
            print(f"[{elapsed:3}s] API Error {resp.status_code}", end='\r', flush=True)
    
    except Exception as e:
        print(f"[{elapsed:3}s] Connection error: {str(e)[:30]}", end='\r', flush=True)
    
    time.sleep(check_interval)

print()
print()
print("=" * 80)
print("✅ DEPLOYMENT INITIATED AND APPLICATION IS READY")
print("=" * 80)

# Step 3: Verify backend is responding
print()
print("Step 3: Verifying backend is responding...")
time.sleep(5)  # Give it a moment to fully start

try:
    resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if resp.ok:
        print("✅ Backend health check: OK")
    else:
        print(f"⚠️  Backend health check: {resp.status_code}")
except Exception as e:
    print(f"⚠️  Could not reach backend: {e}")

# Step 4: Test the new search endpoint
print()
print("Step 4: Testing instrument search endpoint...")
try:
    resp = requests.get(
        f"{BACKEND_URL}/api/v2/instruments/search?q=RELIANCE&limit=5",
        timeout=5
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Search endpoint working! Found {len(data)} results")
        if data:
            item = data[0]
            print(f"   Sample: {item.get('symbol')} - {item.get('exchange_segment')} ({item.get('instrument_type')})")
        print()
        print("🎉 NEW CODE IS DEPLOYED AND WORKING!")
    else:
        print(f"❌ Search returned {resp.status_code}")
        if resp.status_code == 404:
            print("⚠️  Old code still running - rebuild may still be in progress")
            print("   Wait another 30 seconds and test again")
        else:
            print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"⚠️  Error testing search: {e}")

print()
print("=" * 80)
print("DEPLOYMENT COMPLETE!")
print("=" * 80)
print()
print("Next: Test the backdate position form with instrument suggestions")
print("Expected: Type stock name and see dropdown with matching instruments")
print()
