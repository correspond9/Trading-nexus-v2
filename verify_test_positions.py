#!/usr/bin/env python
"""Verify if the test positions actually exist in Trader1's account."""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

# Login as Trader 1
print("="*80)
print("VERIFYING POSITIONS IN TRADER1 ACCOUNT")
print("="*80)

print("\n[1] Logging in as Trader 1 (9326890165)...")
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '9326890165', 'password': 'trader123'})

if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    print(f"Response: {r.text}")
    exit(1)

token = r.json()['access_token']
print(f"✅ Login successful")

headers = {'Authorization': f'Bearer {token}'}

# Get positions
print("\n[2] Fetching all positions...")
r = requests.get(f'{BASE_URL}/positions', headers=headers, verify=False)

if r.status_code != 200:
    print(f"❌ Failed to get positions: {r.status_code}")
    print(f"Response: {r.text}")
    exit(1)

positions = r.json()
print(f"✅ Found {len(positions)} total positions")

# Check for the test positions
test_symbols = ['ITC', 'BANKBARODA 24 FEB 145 CALL', 'NIFTY 02 MAR 19600 CALL']

print("\n[3] Looking for test positions...")
print("="*80)

found = []
for symbol in test_symbols:
    matching = [p for p in positions if p.get('symbol') == symbol]
    if matching:
        print(f"\n✅ FOUND: {symbol}")
        for p in matching:
            print(f"   - Qty: {p.get('quantity')}")
            print(f"   - Avg Price: {p.get('avg_price')}")
            print(f"   - Type: {p.get('instrument_type')}")
            print(f"   - Exchange: {p.get('exchange_segment')}")
            print(f"   - Status: {p.get('status')}")
            print(f"   - Opened At: {p.get('opened_at')}")
            found.append(symbol)
    else:
        print(f"\n❌ NOT FOUND: {symbol}")

print("\n" + "="*80)
print("VERDICT")
print("="*80)

if len(found) == len(test_symbols):
    print(f"✅ ALL {len(test_symbols)} TEST POSITIONS EXIST!")
    print("   I was telling the truth.")
else:
    print(f"❌ ONLY {len(found)}/{len(test_symbols)} POSITIONS FOUND!")
    print("   I was hallucinating/wrong.")
    
    if len(found) > 0:
        print(f"\n   Found: {', '.join(found)}")
    
    missing = [s for s in test_symbols if s not in found]
    if missing:
        print(f"   Missing: {', '.join(missing)}")

print("="*80)
