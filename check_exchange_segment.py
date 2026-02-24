#!/usr/bin/env python
"""Check the exchange_segment for F&O instruments."""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

# Login
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get exact details for the instruments
r = requests.get(f'{BASE_URL}/instruments/search', params={'q': 'BANKBARODA 24 FEB 145 CALL'}, 
                headers=headers, verify=False)

if r.status_code == 200:
    results = r.json()
    if results:
        inst = results[0]
        print("="*80)
        print("BANKBARODA 24 FEB 145 CALL details:")
        print("="*80)
        print(f"Symbol: {inst.get('symbol')}")
        print(f"Exchange Segment: {inst.get('exchange_segment')}")
        print(f"Instrument Type: {inst.get('instrument_type')}")
        print(f"Instrument Token: {inst.get('instrument_token')}")

r = requests.get(f'{BASE_URL}/instruments/search', params={'q': 'NIFTY 02 MAR 19600 CALL'}, 
                headers=headers, verify=False)

if r.status_code == 200:
    results = r.json()
    if results:
        inst = results[0]
        print("\n" + "="*80)
        print("NIFTY 02 MAR 19600 CALL details:")
        print("="*80)
        print(f"Symbol: {inst.get('symbol')}")
        print(f"Exchange Segment: {inst.get('exchange_segment')}")
        print(f"Instrument Type: {inst.get('instrument_type')}")
        print(f"Instrument Token: {inst.get('instrument_token')}")

print("\n" + "="*80)
print("BACKEND MAPPING CHECK")
print("="*80)
print("Backend code says:")
print("  NSE + OPTSTK → exchange_segment = 'NSE_FO'")
print("")
print("If database has 'NSE_FNO' instead → THAT'S THE BUG!")
print("="*80)
