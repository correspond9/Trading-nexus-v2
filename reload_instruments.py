#!/usr/bin/env python3
"""Reload instrument master with new CSV structure"""

import requests
import warnings
import time

warnings.filterwarnings('ignore')

print('Triggering instrument master reload...')
print('='*70)

# Login as admin
r = requests.post('https://tradingnexus.pro/api/v2/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']

# Trigger reload
print('\nReloading instrument master from local CSV...')
r = requests.post('https://tradingnexus.pro/api/v2/admin/reload-scrip-master',
                 verify=False,
                 headers={'Authorization': f'Bearer {token}'})

print(f'Status: {r.status_code}')
if r.status_code == 200:
    resp = r.json()
    print(f'Response: {resp}')
else:
    print(f'Error: {r.text[:500]}')

# Wait a bit for reload to complete
print('\nWaiting 10 seconds for reload to complete...')
time.sleep(10)

# Test search again
print('\nTesting search after reload:')
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=Lenskart', verify=False)
data = r.json()
if data:
    first = data[0]
    print(f'Symbol: "{first.get("symbol")}"')
    print(f'Display Name: "{first.get("display_name")}"')
    print(f'Exchange: "{first.get("exchange_segment")}"')
    print(f'Type: "{first.get("instrument_type")}"')
