#!/usr/bin/env python3
"""
Get valid symbols and users to create test positions
"""

import requests
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("GATHERING SYSTEM INFO FOR TEST DATA")
print("="*80)

# Login as admin
print("\n[1] Logging in...")
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print(f"✅ Logged in")

# Get all users
print("\n[2] Fetching user list...")
r = requests.get(f'{BASE_URL}/admin/users',
                verify=False,
                headers=headers)
if r.status_code == 200:
    users = r.json().get('users', [])
    trader_users = [u for u in users if u.get('role') in ['TRADER', 'USER']]
    print(f"   Found {len(trader_users)} regular traders (excluding admins)")
    for u in trader_users[:5]:
        print(f"   - {u['mobile']}: {u.get('name', 'N/A')}")
else:
    print(f"   Failed to get users: {r.status_code}")

# Search for a common stock symbol
print("\n[3] Searching for INFY (Infosys) symbol...")
r = requests.get(f'{BASE_URL}/portfolio/search?symbol=INFY',
                verify=False,
                headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f"   Found: {data}")
else:
    print(f"   Status: {r.status_code}")

# Try another symbol
print("\n[4] Searching for TCS symbol...")
r = requests.get(f'{BASE_URL}/portfolio/search?symbol=TCS',
                verify=False,
                headers=headers)
if r.status_code == 200:
    data = r.json()
    print(f"   Found: {data}")
else:
    print(f"   Status: {r.status_code}")
