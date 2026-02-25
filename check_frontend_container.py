#!/usr/bin/env python3
"""
Check Coolify and frontend container status via VPS
"""

import requests
import json

vps_ip = "72.62.228.112"
coolify_port = "8000"

print("="*70)
print("CHECKING FRONTEND CONTAINER STATUS")
print("="*70)

# Step 1: Check Coolify API
print("\n1. Checking Coolify Dashboard...")
try:
    # Try to get Coolify status
    r = requests.get(f"http://{vps_ip}:{coolify_port}/api/v1/status", headers={"Accept": "application/json"}, timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   Error: {str(e)[:80]}")

# Step 2: Check if frontend is accessible via VPS IP directly
print("\n2. Checking frontend via VPS IP (port 3000)...")
try:
    r = requests.get(f"http://{vps_ip}:3000/", timeout=10, allow_redirects=False)
    print(f"   Status: {r.status_code}")
    if r.status_code == 404:
        print("   ✗ Frontend container may not be running on port 3000")
    elif r.status_code == 200:
        print("   ✓ Frontend is running")
        # Check if it has the fixes
        has_string = "String(user" in r.text
        print(f"   Contains 'String(user': {has_string}")
except Exception as e:
    print(f"   Error: {str(e)[:80]}")

# Step 3: Try other common ports
print("\n3. Trying to find frontend on other ports...")
for port in [3000, 5173, 5174, 8080, 8000]:
    try:
        r = requests.get(f"http://{vps_ip}:{port}/", timeout=5, allow_redirects=False)
        if r.status_code != 404:
            print(f"   ✓ Found something on port {port}: Status {r.status_code}")
    except:
        pass

# Step 4: Check if backend API is accessible
print("\n4. Checking backend API...")
try:
    r = requests.get(f"http://{vps_ip}:8000/api/v2/health", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✓ Backend API is running")
        print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   Error: {str(e)[:80]}")

# Step 5: Check docker container status via SSH would be ideal but let's try HTTP APIs
print("\n5. Checking Coolify app details...")
try:
    # Coolify should have apps endpoint but requires auth
    r = requests.get(f"http://{vps_ip}:{coolify_port}/api/v1/applications", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Applications: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"   Note: {str(e)[:80]}")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)
print("""
Key findings:
- Frontend domain (tradingnexus.pro) is returning 404
- This means either:
  1. Domain isn't resolving to frontend container
  2. Frontend container isn't running
  3. Frontend container isn't configured in docker-compose
  4. Coolify hasn't properly deployed the frontend app

ACTION ITEMS:
1. Check Coolify dashboard at http://72.62.228.112:8000
2. Verify the frontend app is created in Coolify
3. Check if docker-compose has a frontend service
4. Check if the frontend was actually deployed
5. May need to manually restart the frontend or trigger rebuild
""")
