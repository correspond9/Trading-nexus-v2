#!/usr/bin/env python
"""Quick debug to check API status."""

import requests

BASE_URL = "http://72.62.228.112:8000"

print("Testing API connectivity...")
print(f"URL: {BASE_URL}")

# Test health endpoint
try:
    health = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"\n✅ Health check: {health.status_code}")
    print(f"   Response: {health.text[:200]}")
except Exception as e:
    print(f"\n❌ Health check failed: {e}")

# Test login
print("\n" + "="*80)
print("Testing login...")
try:
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": "8888888888", "password": "admin123"},
        timeout=10
    )
    print(f"Status: {login_resp.status_code}")
    print(f"Response text: {login_resp.text[:500]}")
    
    if login_resp.status_code == 200:
        data = login_resp.json()
        print(f"\n✅ Login successful!")
        print(f"   Token: {data.get('access_token', 'N/A')[:50]}...")
    else:
        print(f"\n❌ Login failed with status {login_resp.status_code}")
except Exception as e:
    print(f"\n❌ Login request failed: {e}")
