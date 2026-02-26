#!/usr/bin/env python3
"""
Force delete a specific position for user 9326890165
Position: FIVE STAR BUSINESS FINANCE, 450 qty, NORMAL product
"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("FORCE DELETE POSITION - FIVE STAR BUSINESS FINANCE")
print("="*80)

# Login as admin
print("\n[1] Logging in as super admin...")
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '9999999999', 'password': 'admin123'})

if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    exit(1)

token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print(f"✅ Logged in")

# Get user's positions
user_mobile = '9326890165'
print(f"\n[2] Fetching positions for user {user_mobile}...")
r = requests.get(f'{BASE_URL}/admin/users/{user_mobile}/positions',
                verify=False,
                headers=headers)

if r.status_code != 200:
    print(f"❌ Failed to fetch positions: {r.status_code}")
    print(r.text[:200])
    exit(1)

data = r.json()
positions = data.get('positions', [])
print(f"✅ Found {len(positions)} positions")

# Find the FIVE STAR BUSINESS FINANCE position
target_position = None
for pos in positions:
    if 'FIVE STAR' in pos['symbol'].upper():
        print(f"\n   Found potential match: {pos['symbol']}")
        print(f"   - Qty: {pos['quantity']}")
        print(f"   - Avg: {pos['avg_price']}")
        print(f"   - Status: {pos['status']}")
        print(f"   - Product: {pos['product_type']}")
        print(f"   - Position ID: {pos['position_id']}")
        
        if pos['quantity'] == 450 and pos['product_type'] == 'NORMAL':
            target_position = pos
            break

if not target_position:
    print("\n❌ Position not found! Showing all positions:")
    for pos in positions:
        print(f"   - {pos['symbol']}: {pos['quantity']} @ {pos['avg_price']} ({pos['product_type']})")
    exit(1)

# Confirm deletion
print(f"\n[3] Preparing to delete position:")
print(f"   Symbol: {target_position['symbol']}")
print(f"   Quantity: {target_position['quantity']}")
print(f"   Product Type: {target_position['product_type']}")
print(f"   Position ID: {target_position['position_id']}")

position_id = target_position['position_id']

# Use the selective delete endpoint with single position
print(f"\n[4] Deleting via API...")
r = requests.post(f'{BASE_URL}/admin/users/{user_mobile}/positions/delete-specific',
                 verify=False,
                 headers=headers,
                 json={'position_ids': [position_id]})

if r.status_code == 200:
    resp = r.json()
    print(f"✅ Deletion successful!")
    print(f"   Response: {resp}")
else:
    print(f"❌ Deletion failed: {r.status_code}")
    print(f"   Error: {r.text[:300]}")
    exit(1)

# Verify deletion
print(f"\n[5] Verifying deletion...")
r = requests.get(f'{BASE_URL}/admin/users/{user_mobile}/positions',
                verify=False,
                headers=headers)

if r.status_code == 200:
    positions = r.json().get('positions', [])
    five_star_exists = any('FIVE STAR' in p['symbol'].upper() for p in positions)
    
    if five_star_exists:
        print(f"❌ Position still exists!")
    else:
        print(f"✅ Position successfully deleted!")
        print(f"   User now has {len(positions)} positions remaining")
        print(f"\n   Remaining positions:")
        for p in positions:
            print(f"   - {p['symbol']}: {p['quantity']} @ {p['avg_price']}")
