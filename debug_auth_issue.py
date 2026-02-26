#!/usr/bin/env python3
"""Debug the authentication issue"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("="*80)
print("DEBUG: Authentication and Historic Position Issue")
print("="*80)

# Step 1: Login
print("\n[Step 1] Login as admin...")
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})

if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    print(r.text)
    exit(1)

login_data = r.json()
token = login_data.get('access_token')
print(f"✅ Login successful")
print(f"   Token: {token}")
print(f"   Token type: {type(token)}")
print(f"   Token length: {len(token)}")

# Step 2: Try to use token in different ways
print("\n[Step 2] Testing token with different header formats...")

test_headers = [
    {
        'name': 'X-AUTH header',
        'headers': {'X-AUTH': token}
    },
    {
        'name': 'Authorization: Bearer header',
        'headers': {'Authorization': f'Bearer {token}'}
    }
]

for test in test_headers:
    print(f"\n   Testing: {test['name']}")
    
    # Try a simple endpoint first to verify auth works
    r = requests.get(f'{BASE_URL}/user',
                    verify=False,
                    headers=test['headers'])
    
    print(f"   GET /user response: {r.status_code}")
    
    if r.status_code == 200:
        print(f"      ✅ Auth works!")
    elif r.status_code == 401:
        print(f"      ❌ Unauthorized - Session invalid")
        print(f"      Detail: {r.json().get('detail', 'N/A')}")
    elif r.status_code == 403:
        print(f"      ❌ Forbidden - User not admin")
    else:
        print(f"      ⚠️  Unexpected: {r.status_code}")
        print(f"      Body: {r.text[:200]}")

# Step 3: Try backdate with explicit header error catching
print("\n[Step 3] Testing backdate-position with error details...")

headers = {'Authorization': f'Bearer {token}'}
payload = {
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

print(f"\nPayload:")
print(json.dumps(payload, indent=2))

r = requests.post(f'{BASE_URL}/admin/backdate-position',
                 verify=False,
                 headers=headers,
                 json=payload)

print(f"\nResponse Status: {r.status_code}")
print(f"Response Headers: {dict(r.headers)}")
print(f"Response Body:")
print(r.text[:500])

# If HTML response, it might be an error page
if 'html' in r.headers.get('content-type', '').lower():
    print("\n⚠️  ERROR: Got HTML response (likely server error page)")
    print("   This suggests the backend is crashing")
    print("   Check backend logs for Java/Python exceptions")
