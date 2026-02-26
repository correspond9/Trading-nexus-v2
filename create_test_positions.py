#!/usr/bin/env python3
"""
Create test positions and verify they appear in userwise endpoint
"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("STEP 1: Create test positions")
print("="*80)

# Login as admin
print("\n[1] Logging in as admin...")
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print(f"✅ Logged in")

# Create positions for different users using backdate endpoint
test_positions = [
    {
        'user_id': '9326890165',  # Trader 1
        'symbol': 'RELIANCE',
        'qty': 100,
        'price': 2850.00,
        'trade_date': '25-02-2026',
        'trade_time': '10:00',
        'instrument_type': 'EQ',
        'exchange': 'NSE',
        'product_type': 'MIS'
    },
    {
        'user_id': '9326890165',
        'symbol': 'INFOEDGE',
        'qty': 50,
        'price': 1500.00,
        'trade_date': '25-02-2026',
        'trade_time': '10:30',
        'instrument_type': 'EQ',
        'exchange': 'NSE',
        'product_type': 'NORMAL'
    },
    {
        'user_id': '9327567890',  # Trader 2 (if exists)
        'symbol': 'TCS',
        'qty': 25,
        'price': 3500.00,
        'trade_date': '25-02-2026',
        'trade_time': '11:00',
        'instrument_type': 'EQ',
        'exchange': 'NSE',
        'product_type': 'MIS'
    }
]

created_count = 0
for i, pos in enumerate(test_positions, 1):
    print(f"\n[{i}] Creating position: {pos['symbol']} for user {pos['user_id'][:4]}****")
    r = requests.post(f'{BASE_URL}/admin/backdate-position',
                     verify=False,
                     headers=headers,
                     json=pos)
    
    if r.status_code == 200:
        resp = r.json()
        if resp.get('success'):
            print(f"   ✅ Created: {resp.get('message')}")
            created_count += 1
        else:
            print(f"   ❌ Failed: {resp.get('detail')}")
    else:
        print(f"   ❌ API Error {r.status_code}: {r.text[:200]}")

print(f"\n✅ Created {created_count}/{len(test_positions)} positions")

# Now test the userwise endpoint again
print("\n" + "="*80)
print("STEP 2: Check if positions appear in userwise endpoint")
print("="*80)

r = requests.get(f'{BASE_URL}/admin/positions/userwise',
                verify=False,
                headers=headers)

data = r.json()
users_with_positions = [u for u in data.get('data', []) if u.get('positions') and len(u['positions']) > 0]

print(f"\n✅ Users with positions: {len(users_with_positions)}")

for u in users_with_positions:
    print(f"\nUser: {u['display_name']} ({u['mobile']})")
    print(f"  Positions: {len(u['positions'])}")
    print(f"  P&L: {u['pandl']:.2f} ({u['pandl_pct']:.2f}%)")
    for p in u['positions']:
        print(f"    - {p['symbol']}: {p['quantity']} units @ {p['ltp']:.2f} (Status: {p['status']})")
