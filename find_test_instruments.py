#!/usr/bin/env python
"""Find suitable EQUITY instruments for testing."""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

# Login
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Common search terms
queries = [
    "Reliance",
    "HDFC",
    "Tata",
    "Info",
    "Wipro",
    "ITC",
    "Axis",
    "Bharti",
    "Maruti"
]

found_instruments = []

for q in queries:
    r = requests.get(f'{BASE_URL}/instruments/search', params={'q': q}, 
                    headers=headers, verify=False)
    
    if r.status_code == 200:
        results = r.json()
        equity_results = [x for x in results if x.get('instrument_type') == 'EQUITY']
        
        if equity_results:
            print(f"\n✅ '{q}' → {len(equity_results)} EQUITY results:")
            for inst in equity_results[:2]:  # Show first 2
                print(f"   - {inst.get('symbol')} | {inst.get('exchange_segment')}")
                found_instruments.append({
                    'search_term': q,
                    'symbol': inst.get('symbol'),
                    'exchange_segment': inst.get('exchange_segment')
                })
        else:
            print(f"❌ '{q}' → No EQUITY results")

print(f"\n{'='*80}")
print(f"Found {len(found_instruments)} usable instruments")
print("="*80)

if len(found_instruments) >= 3:
    print("\n✅ Recommended test instruments:")
    for i, inst in enumerate(found_instruments[:3], 1):
        print(f"  {i}. Search: '{inst['search_term']}' → {inst['symbol']} ({inst['exchange_segment']})")
