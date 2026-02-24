#!/usr/bin/env python3
"""Test equity instruments specifically to see DISPLAY_NAME values"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

print('SEARCHING FOR EQUITY INSTRUMENTS')
print('='*70)

# Search for RELIANCE and filter for equities
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=RELIANCE', verify=False)
data = r.json()

equities = [d for d in data if d.get('instrument_type') == 'EQUITY']
print(f'\nTotal results: {len(data)}')
print(f'Equity results: {len(equities)}')

if equities:
    print('\nFirst 5 equities:')
    for i, eq in enumerate(equities[:5], 1):
        print(f'{i}. Symbol: {eq.get("symbol")}')
        print(f'   Display Name: {eq.get("display_name")}')
        print(f'   Exchange: {eq.get("exchange_segment")}')
        print()

# Search for MARUTI equities
print('\n' + '='*70)
print('MARUTI RESULTS')
r = requests.get('https://tradingnexus.pro/api/v2/instruments/search?q=MARUTI', verify=False)
data = r.json()

equities = [d for d in data if d.get('instrument_type') == 'EQUITY']
print(f'Total: {len(data)}, Equities: {len(equities)}')
if equities:
    print('First equity:')
    eq = equities[0]
    print(f'Symbol: {eq.get("symbol")}')
    print(f'Display Name: {eq.get("display_name")}')
    print(f'Exchange: {eq.get("exchange_segment")}')
    print(f'Token: {eq.get("instrument_token")}')
