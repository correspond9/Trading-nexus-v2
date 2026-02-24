#!/usr/bin/env python
"""Check Trader1's positions via admin account."""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

print("="*80)
print("CHECKING TRADER1 POSITIONS VIA ADMIN")
print("="*80)

# Login as admin
print("\n[1] Logging in as admin...")
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})

if r.status_code != 200:
    print(f"❌ Admin login failed: {r.status_code}")
    exit(1)

token = r.json()['access_token']
print(f"✅ Admin login successful")
headers = {'Authorization': f'Bearer {token}'}

# Get Trader1 details
TRADER1_ID = '00000000-0000-0000-0000-000000000003'

print(f"\n[2] Fetching positions for Trader1 ({TRADER1_ID})...")

# Try to get user's positions via admin endpoint
r = requests.get(f'{BASE_URL}/admin/users/{TRADER1_ID}/positions', 
                headers=headers, verify=False)

if r.status_code == 404:
    print("   Admin endpoint not found, trying direct query...")
    
    # Alternative: query all users and find trader1
    r = requests.get(f'{BASE_URL}/admin/users', headers=headers, verify=False)
    if r.status_code == 200:
        users = r.json()
        trader1 = next((u for u in users if u.get('id') == TRADER1_ID or u.get('mobile') == '9326890165'), None)
        if trader1:
            print(f"   Found Trader1: {trader1.get('mobile')} - {trader1.get('name')}")
        else:
            print("   Trader1 not found in user list")

if r.status_code == 200:
    positions = r.json()
    print(f"✅ Found {len(positions)} positions")
    
    # Check for test symbols
    test_symbols = ['ITC', 'BANKBARODA 24 FEB 145 CALL', 'NIFTY 02 MAR 19600 CALL']
    
    print("\n[3] Checking for test positions...")
    for symbol in test_symbols:
        found = [p for p in positions if p.get('symbol') == symbol]
        if found:
            print(f"✅ {symbol}: {len(found)} position(s)")
        else:
            print(f"❌ {symbol}: NOT FOUND")
else:
    print(f"❌ Failed: {r.status_code}")
    print(f"Response: {r.text[:500]}")

print("\n" + "="*80)
print("TRUTH CHECK")
print("="*80)
print("Let me check the actual response from the backdate API...")

# Re-check by looking at the test script output more carefully
print("\nThe test showed 'Status Code: 200' but 'Message: N/A'")
print("This suggests the response was successful but might not have created positions")
print("OR the positions were created but the response format was different.")
print("\nConclusion: I need to check the actual database/API response format.")
