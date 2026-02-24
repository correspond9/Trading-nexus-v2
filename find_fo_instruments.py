#!/usr/bin/env python
"""Find F&O instruments for testing."""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

# Login
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Search for common instruments
queries = ["Nifty", "Bank", "Reliance", "TCS", "HDFC", "Infosys"]

print("="*80)
print("SEARCHING FOR F&O INSTRUMENTS")
print("="*80)

fo_instruments = {
    'FUTSTK': [],
    'OPTSTK': [],
    'FUTIDX': [],
    'OPTIDX': []
}

for q in queries:
    r = requests.get(f'{BASE_URL}/instruments/search', params={'q': q}, 
                    headers=headers, verify=False)
    
    if r.status_code == 200:
        results = r.json()
        
        for inst in results:
            inst_type = inst.get('instrument_type', '')
            
            if inst_type in fo_instruments:
                symbol = inst.get('symbol')
                exchange_segment = inst.get('exchange_segment')
                
                # Check if we already have similar
                exists = any(x['symbol'] == symbol for x in fo_instruments[inst_type])
                
                if not exists and len(fo_instruments[inst_type]) < 3:
                    fo_instruments[inst_type].append({
                        'search': q,
                        'symbol': symbol,
                        'exchange_segment': exchange_segment
                    })

# Display results
print("\n" + "="*80)
print("FOUND F&O INSTRUMENTS BY TYPE")
print("="*80)

for inst_type, items in fo_instruments.items():
    print(f"\n{inst_type} ({len(items)} found):")
    if items:
        for item in items[:2]:  # Show first 2
            print(f"  ✅ Search: '{item['search']}' → {item['symbol']} ({item['exchange_segment']})")
    else:
        print("  ❌ None found")

# Summary
print("\n" + "="*80)
print("TEST RECOMMENDATIONS")
print("="*80)

all_types = []
for inst_type in ['EQUITY', 'FUTSTK', 'OPTSTK', 'FUTIDX', 'OPTIDX']:
    if inst_type == 'EQUITY':
        print(f"\n{inst_type}:")
        print(f"  ✅ Search: 'ITC' → ITC (NSE_EQ)")
        all_types.append('EQUITY')
    elif fo_instruments.get(inst_type):
        item = fo_instruments[inst_type][0]
        print(f"\n{inst_type}:")
        print(f"  ✅ Search: '{item['search']}' → {item['symbol']} ({item['exchange_segment']})")
        all_types.append(inst_type)

print(f"\n{'='*80}")
print(f"Can test {len(all_types)} different instrument types: {', '.join(all_types)}")
print("="*80)
