#!/usr/bin/env python3
"""Test to identify why historic position add is failing"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("TESTING: Why Historic Position Add is Failing")
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

# Test different scenarios to find the failure point
test_cases = [
    {
        'name': 'Complete request with all fields',
        'payload': {
            'user_id': '9326890165',
            'symbol': 'RELIANCE',
            'qty': 100,
            'price': 2850.00,
            'trade_date': '20-02-2026',
            'trade_time': '09:15',
            'instrument_type': 'EQ',
            'exchange': 'NSE',
            'product_type': 'MIS'
        }
    },
    {
        'name': 'Request WITHOUT trade_time (might be missing)',
        'payload': {
            'user_id': '9326890165',
            'symbol': 'RELIANCE',
            'qty': 100,
            'price': 2850.00,
            'trade_date': '20-02-2026',
            # Missing trade_time
            'instrument_type': 'EQ',
            'exchange': 'NSE',
            'product_type': 'MIS'
        }
    },
    {
        'name': 'Request WITHOUT product_type',
        'payload': {
            'user_id': '9326890165',
            'symbol': 'RELIANCE',
            'qty': 100,
            'price': 2850.00,
            'trade_date': '20-02-2026',
            'trade_time': '09:15',
            'instrument_type': 'EQ',
            'exchange': 'NSE',
            # Missing product_type
        }
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {test['name']}")
    print('='*80)
    
    payload = test['payload']
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    r = requests.post(f'{BASE_URL}/admin/backdate-position',
                     verify=False,
                     headers=headers,
                     json=payload)
    
    print(f"\nResponse Status: {r.status_code}")
    
    try:
        resp = r.json()
        print(f"Response Body:")
        print(json.dumps(resp, indent=2))
        
        if resp.get('success'):
            print(f"\n✅ SUCCESS: {resp.get('message')}")
        else:
            print(f"\n❌ FAILED: {resp.get('detail')}")
    except:
        print(f"Response (raw):")
        print(r.text[:500])

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
The above tests show which parameter is causing the failure.
If Test 1 passes but Test 2 fails: trade_time is required
If Test 1 passes but Test 3 fails: product_type is required  
If Test 1 fails: There's another issue (check error message)
""")
