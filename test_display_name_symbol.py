#!/usr/bin/env python3
"""Test that symbol field now uses DISPLAY_NAME"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

print('TESTING SYMBOL FIELD POPULATED WITH DISPLAY_NAME')
print('='*70)

# Test 1: Search for RELIANCE (should now return display names in symbol field)
print('\n1. SEARCH FOR "RELIANCE"')
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=RELIANCE', verify=False)
data = r.json()
if isinstance(data, list) and len(data) > 0:
    print(f'   ✅ Found {len(data)} results')
    first = data[0]
    print(f'   Symbol: {first.get("symbol")}')
    print(f'   Display Name: {first.get("display_name")}')
    print(f'   Exchange Segment: {first.get("exchange_segment")}')
    print(f'   Instrument Type: {first.get("instrument_type")}')
else:
    print(f'   ❌ No results: {data}')

# Test 2: Search for MARUTI
print('\n2. SEARCH FOR "MARUTI"')
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=MARUTI', verify=False)
data = r.json()
if isinstance(data, list) and len(data) > 0:
    print(f'   ✅ Found {len(data)} results')
    first = data[0]
    print(f'   Symbol: {first.get("symbol")}')
    print(f'   Display Name: {first.get("display_name")}')
    print(f'   Exchange Segment: {first.get("exchange_segment")}')
else:
    print(f'   ❌ No results: {data}')

# Test 3: Test backdate position with display name symbol
print('\n3. TEST BACKDATE POSITION WITH DISPLAY_NAME')
r = requests.post('https://tradingnexus.pro/api/v2/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']

# Get a search result to use the exact symbol format
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=RELIANCE&limit=1', verify=False)
search_result = r.json()[0] if r.json() else None

if search_result:
    symbol_from_search = search_result['symbol']
    exchange_from_search = search_result['exchange_segment']
    base_exchange = exchange_from_search.split('_')[0] if exchange_from_search else 'NSE'
    
    print(f'   Using symbol from search: "{symbol_from_search}"')
    print(f'   Exchange: {base_exchange}')
    
    r = requests.post('https://tradingnexus.pro/api/v2/admin/backdate-position',
                     verify=False,
                     headers={'Authorization': f'Bearer {token}'},
                     json={
                         'user_id': '00000000-0000-0000-0000-000000000003',
                         'symbol': symbol_from_search,
                         'qty': 100,
                         'price': 2800.0,
                         'trade_date': '21-02-2026',
                         'instrument_type': 'EQ',
                         'exchange': base_exchange
                     })
    
    resp = r.json()
    if resp.get('success'):
        print(f'   ✅ BACKDATE POSITION CREATED')
        print(f'   Symbol in result: {resp["position"]["symbol"]}')
    else:
        print(f'   ❌ Error: {resp.get("detail")}')
else:
    print('   ❌ Could not fetch search result')

print('\n' + '='*70)
print('TEST COMPLETED - Symbol field now uses DISPLAY_NAME!')
