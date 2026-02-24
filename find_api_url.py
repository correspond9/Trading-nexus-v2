#!/usr/bin/env python
"""Test different API endpoints."""

import requests

# Try different base URLs
urls_to_try = [
    "https://api.tradingnexus.pro",
    "http://72.62.228.112:8000/api/v2",
    "https://tradingnexus.pro/api/v2",
]

for base_url in urls_to_try:
    print(f"\n{'='*80}")
    print(f"Testing: {base_url}")
    print('='*80)
    
    try:
        # Test health
        health = requests.get(f"{base_url}/health", timeout=5, verify=False)
        print(f"Health: {health.status_code} - {health.text[:100]}")
        
        # Test login
        login = requests.post(
            f"{base_url}/auth/login",
            json={"phone": "8888888888", "password": "admin123"},
            timeout=5,
            verify=False
        )
        print(f"Login: {login.status_code}")
        if login.status_code == 200:
            print(f"✅ SUCCESS! Use this URL: {base_url}")
            print(f"Token: {login.json().get('access_token', 'N/A')[:50]}...")
            break
        else:
            print(f"Response: {login.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
