#!/usr/bin/env python3
"""
Create test positions for real users
"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("CREATING TEST POSITIONS")
print("="*80)

# Login
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# Real users from the system
users_to_trade = [
    '7777777777',
    '9326890165',
    '8639816880',
]

# Try multiple common symbols
symbols_to_try = ['INFY', 'TCS', 'SBIN', 'HDFC', 'NTPC', 'MARUTI', 'BAJAJ-AUTO', 'LT']

created = 0

for user_mobile in users_to_trade:
    for symbol in symbols_to_try[:2]:  # Try first 2 symbols per user
        print(f"\nCreating {symbol} position for user {user_mobile[:4]}****...")
        
        payload = {
            'user_id': user_mobile,
            'symbol': symbol,
            'qty': 10,
            'price': 2000.00,
            'trade_date': '25-02-2026',
            'trade_time': '10:00',
            'instrument_type': 'EQ',
            'exchange': 'NSE',
            'product_type': 'MIS'
        }
        
        r = requests.post(f'{BASE_URL}/admin/backdate-position',
                         verify=False,
                         headers=headers,
                         json=payload)
        
        if r.status_code == 200:
            resp = r.json()
            if resp.get('success'):
                print(f"  ✅ Created: {resp.get('message')}")
                created += 1
            else:
                print(f"  ⚠️  {resp.get('detail', 'Failed')}")
        else:
            print(f"  ❌ {r.status_code}: {r.text[:100]}")

print(f"\n{'='*80}")
print(f"Successfully created {created} positions")
print(f"{'='*80}")

# Now check userwise endpoint
print("\n[2] Checking /admin/positions/userwise...")
r = requests.get(f'{BASE_URL}/admin/positions/userwise',
                verify=False,
                headers=headers)

if r.status_code == 200:
    data = r.json()
    users_with_pos = [u for u in data.get('data', []) if u.get('positions')]
    
    print(f"\n✅ Users with positions: {len(users_with_pos)}")
    
    for u in users_with_pos[:3]:
        print(f"\n  User {u['user_no']} ({u['mobile']}):")
        for p in u['positions'][:2]:
            print(f"    - {p['symbol']}: {p['quantity']} @ {p['ltp']}")
else:
    print(f"Failed: {r.status_code}")
