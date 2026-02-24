#!/usr/bin/env python3
"""Check the results of symbol field update"""

import requests
import warnings

warnings.filterwarnings('ignore')

print('CHECKING IF DISPLAY_NAME IS NOW IN SYMBOL FIELD')
print('='*70)

r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=RELIANCE&limit=100', 
                 verify=False)
data = r.json()

print(f'Total results: {len(data)}')

# Filter for specific types
types = {}
for item in data:
    t = item.get('instrument_type', 'UNKNOWN')
    if t not in types:
        types[t] = []
    types[t].append(item)

for itype, items in sorted(types.items()):
    print(f'\n{itype}: {len(items)} items')
    if items:
        first = items[0]
        sym = first.get('symbol')
        disp = first.get('display_name')
        print(f'  Example symbol: {sym}')
        print(f'  Example display_name: {disp}')

# Also search for a known equity
print('\n' + '='*70)
print('SEARCHING FOR SPECIFIC EQUITY')
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=RKEC', 
                verify=False)
data = r.json()
print(f'RKEC results: {len(data)}')
if data:
    first = data[0]
    print(f'Symbol: {first.get("symbol")}')
    print(f'Display Name: {first.get("display_name")}')
    print(f'Type: {first.get("instrument_type")}')
