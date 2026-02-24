#!/usr/bin/env python3
"""Get position ID via API"""
import requests
import json

# Try to get positions for user 1003
url = "https://tradingnexus.pro/api/v2/portfolio/positions/1003"

# Use auth token from local storage if available
headers = {
    "Content-Type": "application/json",
}

# Try without auth first, or with admin token
try:
    # First, let's login to get a valid token
    login_resp = requests.post(
        "https://tradingnexus.pro/api/v2/auth/login",
        json={
            "mobile": "9999999999",
            "password": "123456"
        },
        verify=False,
        timeout=10
    )
    
    if login_resp.status_code == 200:
        token = login_resp.json().get('token')
        headers['X-AUTH'] = token
        print(f"✓ Logged in, got token: {token[:20]}...")
    else:
        print(f"✗ Login failed: {login_resp.status_code}")
        print(login_resp.text)
        exit(1)
    
    # Now get positions
    resp = requests.get(url, headers=headers, verify=False, timeout=10)
    print(f"\nStatus: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nPositions for user 1003:")
        print(json.dumps(data, indent=2))
        
        # Find LENSKART position
        if isinstance(data, dict) and 'positions' in data:
            positions = data['positions']
        elif isinstance(data, list):
            positions = data
        else:
            positions = []
        
        lenskart_pos = [p for p in positions if p.get('status') == 'OPEN' and 'lenskart' in str(p.get('symbol', '')).lower()]
        
        if lenskart_pos:
            print(f"\n✓ Found LENSKART position:")
            for pos in lenskart_pos:
                print(f"  ID: {pos.get('id')}")
                print(f"  Symbol: {pos.get('symbol')}")
                print(f"  Qty: {pos.get('qty')}")
        else:
            print(f"\n✗ No open LENSKART position found")
    else:
        print(f"✗ Failed to get positions: {resp.status_code}")
        print(resp.text)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
