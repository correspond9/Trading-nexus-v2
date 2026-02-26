#!/usr/bin/env python3
"""Test the positions/userwise API endpoint directly"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("TESTING: Positions Userwise API")
print("="*80)

# Login as admin
print("\n[1] Logging in as admin...")
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})

if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    print(r.text)
    exit(1)

token = r.json().get('access_token')
print(f"✅ Login successful")

headers = {'Authorization': f'Bearer {token}'}

# Test the API endpoint
print("\n[2] Calling /admin/positions/userwise...")
r = requests.get(f'{BASE_URL}/admin/positions/userwise',
                verify=False,
                headers=headers)

print(f"Response Status: {r.status_code}")

if r.status_code != 200:
    print(f"❌ API call failed")
    print(r.text[:500])
    exit(1)

data = r.json()
print(f"\n✅ API Response received")
print(f"   Total users returned: {len(data.get('data', []))}")

# Analyze the data
users_with_positions = [u for u in data.get('data', []) if u.get('positions') and len(u['positions']) > 0]
users_without_positions = [u for u in data.get('data', []) if not u.get('positions') or len(u['positions']) == 0]

print(f"\n[3] Data Analysis:")
print(f"   Users with positions: {len(users_with_positions)}")
print(f"   Users without positions: {len(users_without_positions)}")

# Show sample users with positions
if users_with_positions:
    print(f"\n[4] Sample users with positions:")
    for u in users_with_positions[:3]:
        print(f"\n   User: {u['display_name']} ({u['user_id'][:8]}...)")
        print(f"   Positions count: {len(u['positions'])}")
        for p in u['positions'][:3]:
            print(f"     - {p['symbol']}: {p['quantity']} @ {p['ltp']} (Status: {p['status']})")
        if len(u['positions']) > 3:
            print(f"     ... and {len(u['positions'])-3} more")
else:
    print(f"\n❌ NO USERS WITH POSITIONS IN DATABASE")
    print(f"   This could mean:")
    print(f"   1. No positions have been created")
    print(f"   2. All positions have been deleted/closed")
    print(f"   3. The API query has a bug filtering positions")

# Show full response for first 2 users
print(f"\n[5] Full response for first 2 users:")
for u in data.get('data', [])[:2]:
    print(f"\nUser {u['user_no']} ({u['display_name']}):")
    print(json.dumps(u, indent=2, default=str)[:500])
