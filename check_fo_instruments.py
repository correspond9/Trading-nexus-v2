#!/usr/bin/env python
"""Check what BANKBARODA and NIFTY options actually exist in database."""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

# Login
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*80)
print("CHECKING WHICH F&O INSTRUMENTS ACTUALLY EXIST")
print("="*80)

# Search for BANKBARODA
print("\n[1] BANKBARODA options:")
r = requests.get(f'{BASE_URL}/instruments/search', params={'q': 'BANK'}, 
                headers=headers, verify=False)
if r.status_code == 200:
    results = r.json()
    optstk = [x for x in results if x.get('instrument_type') == 'OPTSTK']
    bankbaroda = [x for x in optstk if 'BANKBARODA' in x.get('symbol', '').upper()]
    
    print(f"   Found {len(bankbaroda)} BANKBARODA options:")
    for opt in bankbaroda[:5]:
        print(f"   - {opt.get('symbol')}")

# Search for NIFTY
print("\n[2] NIFTY options:")
r = requests.get(f'{BASE_URL}/instruments/search', params={'q': 'NIFTY'}, 
                headers=headers, verify=False)
if r.status_code == 200:
    results = r.json()
    optidx = [x for x in results if x.get('instrument_type') == 'OPTIDX']
    
    print(f"   Found {len(optidx)} NIFTY options:")
    for opt in optidx[:5]:
        print(f"   - {opt.get('symbol')}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("If 'BANKBARODA 24 FEB 145 CALL' is in the list → it existed yesterday")
print("If it's NOT in the list → those contracts may have expired (24 FEB was yesterday!)")
print("="*80)
