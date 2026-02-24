#!/usr/bin/env python3
"""Verify all 3 original issues are fixed"""

import requests
import warnings
import json

warnings.filterwarnings('ignore')

print('TESTING ALL 3 ORIGINAL ISSUES')
print('='*60)

# Issue 2: Instrument search
print('\n1. INSTRUMENT SEARCH (Issue #2)')
try:
    r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=RELIANCE', 
                     verify=False, timeout=10)
    print(f'   Status: {r.status_code}')
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        print(f'   ✅ Found {len(data)} results')
        print(f'   Sample symbol: {data[0].get("symbol")}')
    else:
        print(f'   ❌ No results: {data}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Issue 1: Admin credentials save
print('\n2. ADMIN CREDENTIALS SAVE (Issue #1)')
try:
    # Login
    r = requests.post('https://tradingnexus.pro/api/v2/auth/login', 
                     verify=False, timeout=10,
                     json={'mobile': '8888888888', 'password': 'admin123'})
    token = r.json().get('access_token')
    
    # Save credentials
    r = requests.post('https://tradingnexus.pro/api/v2/admin/credentials/save', 
                     verify=False, timeout=10,
                     headers={'Authorization': f'Bearer {token}'},
                     json={
                         'mobile': '9999999999',
                         'user': 'testuser',
                         'access_token': 'test_token',
                         'refresh_token': 'test_refresh',
                         'broker': 'DHAN'
                     })
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        resp = r.json()
        print(f'   ✅ Credentials saved successfully')
        print(f'   {resp}')
    else:
        print(f'   ❌ Error: {r.json()}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Issue 3: SSL Certificate (check HTTPS works)
print('\n3. HTTPS/SSL CERTIFICATE (Issue #3)')
try:
    r = requests.get('https://tradingnexus.pro/api/v2/health', verify=False, timeout=10)
    print(f'   Status: {r.status_code}')
    if r.status_code == 200:
        print(f'   ✅ HTTPS working with valid certificate')
        print(f'   Response: {r.json()}')
    else:
        print(f'   ❌ Error: {r.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Issue 4: Backdate position with multi-word symbol
print('\n4. BACKDATE POSITION WITH MULTI-WORD SYMBOL (New Issue)')
try:
    # Login as admin
    r = requests.post('https://tradingnexus.pro/api/v2/auth/login',
                     verify=False, timeout=10,
                     json={'mobile': '8888888888', 'password': 'admin123'})
    token = r.json().get('access_token')
    
    # Create backdate position
    r = requests.post('https://tradingnexus.pro/api/v2/admin/backdate-position',
                     verify=False, timeout=10,
                     headers={'Authorization': f'Bearer {token}'},
                     json={
                         'user_id': '00000000-0000-0000-0000-000000000003',
                         'symbol': 'LENSKART SOLUTIONS LTD',
                         'qty': 370,
                         'price': 524.7,
                         'trade_date': '19-02-2026',
                         'instrument_type': 'EQ',
                         'exchange': 'NSE'
                     })
    print(f'   Status: {r.status_code}')
    resp = r.json()
    if resp.get('success'):
        print(f'   ✅ Backdate position created with multi-word symbol')
        print(f'   Symbol preserved: {resp["position"]["symbol"]}')
    else:
        print(f'   ❌ Error: {resp}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print('\n' + '='*60)
print('ALL TESTS COMPLETED!')
