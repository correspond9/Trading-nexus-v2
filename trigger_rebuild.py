#!/usr/bin/env python3
"""Trigger rebuild via Coolify API"""
import requests
import time

API_URL = "http://72.62.228.112:8000/api/v1"
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
APP_UUID = "bsgc4kwsk88s04kgws0408c4"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 70)
print("TRIGGER REBUILD - Trading Nexus Backend")
print("=" * 70)
print()

print(f"1. Checking resources...")
try:
    response = requests.get(f"{API_URL}/resources", headers=headers, timeout=10)
    resources = response.json()
    
    for resource in resources:
        if 'trading-nexus' in resource.get('name', '').lower():
            print(f"   ✓ Found: {resource['name']}")
            print(f"   UUID: {resource['uuid']}")
            print(f"   Status: {resource.get('status', 'unknown')}")
            APP_UUID = resource['uuid']
            break
except Exception as e:
    print(f"   Warning: {e}")
    print(f"   Using UUID from config: {APP_UUID}")

print()
print(f"2. Triggering rebuild for UUID: {APP_UUID}")
print()

# Method 1: Restart with force rebuild
print("   Trying: POST /applications/{uuid}/restart?force_rebuild=true")
try:
    response = requests.post(
        f"{API_URL}/applications/{APP_UUID}/restart?force_rebuild=true",
        headers=headers,
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    if response.status_code in [200, 201, 202]:
        print("   ✓ Rebuild triggered successfully!")
        print()
        print("3. Monitoring deployment...")
        
        for i in range(20):
            time.sleep(5)
            try:
                status_response = requests.get(
                    f"{API_URL}/applications/{APP_UUID}",
                    headers=headers,
                    timeout=10
                )
                if status_response.status_code == 200:
                    data = status_response.json()
                    status = data[0]['status'] if isinstance(data, list) else data.get('status', 'unknown')
                    print(f"   [{i*5:3d}s] Status: {status}")
                    
                    if 'running' in status.lower():
                        print()
                        print("✓ DEPLOYMENT COMPLETE!")
                        break
            except:
                pass
    else:
        print(f"   ✗ Failed: {response.text}")
        
        # Method 2: Try deploy endpoint
        print()
        print("   Trying: POST /applications/{uuid}/deploy")
        response2 = requests.post(
            f"{API_URL}/applications/{APP_UUID}/deploy",
            headers=headers,
            timeout=30
        )
        print(f"   Status: {response2.status_code}")
        print(f"   Response: {response2.text[:200]}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print()
print("=" * 70)
print("DONE")
print("=" * 70)
