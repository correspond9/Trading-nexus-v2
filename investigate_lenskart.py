#!/usr/bin/env python3
"""Investigate Lenskart data discrepancy"""

import requests
import warnings
import csv

warnings.filterwarnings('ignore')

print('INVESTIGATING LENSKART')
print('='*70)

# 1. Check search results
print('\n1. SEARCH API RESULTS:')
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=Lenskart', verify=False)
data = r.json()
print(f'   Found {len(data)} results')
if data:
    for i, item in enumerate(data[:3], 1):
        print(f'\n   Result {i}:')
        print(f'     symbol: "{item.get("symbol")}"')
        print(f'     display_name: "{item.get("display_name")}"')
        print(f'     instrument_type: "{item.get("instrument_type")}"')
        print(f'     exchange_segment: "{item.get("exchange_segment")}"')

# 2. Check CSV data
print('\n\n2. CSV DATA:')
with open('instrument_master/api-scrip-master-detailed.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        if 'LENSKART' in (row.get('DISPLAY_NAME', '') or '').upper() or 'LENSKART' in (row.get('SYMBOL_NAME', '') or '').upper():
            count += 1
            if count <= 3:
                print(f'\n   CSV Row {count}:')
                print(f'     SYMBOL_NAME: "{row.get("SYMBOL_NAME")}"')
                print(f'     DISPLAY_NAME: "{row.get("DISPLAY_NAME")}"')
                print(f'     UNDERLYING_SYMBOL: "{row.get("UNDERLYING_SYMBOL")}"')
                print(f'     INSTRUMENT: "{row.get("INSTRUMENT")}"')
                print(f'     EXCH_ID: "{row.get("EXCH_ID")}"')
                print(f'     SEGMENT: "{row.get("SEGMENT")}"')
    print(f'\n   Total LENSKART entries in CSV: {count}')

# 3. Test backend lookup with exact search result
print('\n\n3. TESTING BACKEND LOOKUP:')
if data and len(data) > 0:
    first = data[0]
    symbol_to_test = first.get('symbol')
    exchange_seg = first.get('exchange_segment')
    inst_type = first.get('instrument_type')
    
    print(f'   Testing with:')
    print(f'     symbol: "{symbol_to_test}"')
    print(f'     exchange_segment: "{exchange_seg}"')
    print(f'     instrument_type: "{inst_type}"')
    
    # Login as admin
    r = requests.post('https://tradingnexus.pro/api/v2/auth/login',
                     verify=False,
                     json={'mobile': '8888888888', 'password': 'admin123'})
    token = r.json()['access_token']
    
    # Extract base exchange
    base_exchange = exchange_seg.split('_')[0] if exchange_seg else 'NSE'
    
    # Try to create position
    r = requests.post('https://tradingnexus.pro/api/v2/admin/backdate-position',
                     verify=False,
                     headers={'Authorization': f'Bearer {token}'},
                     json={
                         'user_id': '00000000-0000-0000-0000-000000000003',
                         'symbol': symbol_to_test,
                         'qty': 100,
                         'price': 500.0,
                         'trade_date': '23-02-2026',
                         'instrument_type': inst_type or 'EQ',
                         'exchange': base_exchange
                     })
    
    resp = r.json()
    print(f'\n   Backend response:')
    print(f'     success: {resp.get("success")}')
    if resp.get('success'):
        print(f'     message: {resp.get("message")}')
    else:
        print(f'     detail: {resp.get("detail")}')
