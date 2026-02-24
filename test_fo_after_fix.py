#!/usr/bin/env python
"""Test F&O positions AFTER the exchange_segment fix."""

import requests
import json
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

print("="*80)
print("F&O POSITION TEST - AFTER EXCHANGE_SEGMENT FIX")
print("="*80)

# Wait a bit for deployment
print("\n⏳ Waiting 90 seconds for deployment to complete...")
time.sleep(90)

# Login
print("\n[1] Logging in as admin...")
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("✅ Logged in")

TRADER1_ID = '00000000-0000-0000-0000-000000000003'

# Test 1: OPTSTK (Stock Option)
print("\n" + "="*80)
print("TEST 1: OPTSTK (Bank of Baroda Stock Option)")
print("="*80)

payload1 = {
    'user_id': TRADER1_ID,
    'symbol': 'BANKBARODA 24 FEB 145 CALL',
    'qty': 50,
    'price': 12.50,
    'trade_date': '25-02-2026',
    'instrument_type': 'OPTSTK',
    'exchange': 'NSE'
}

print(f"Payload: {json.dumps(payload1, indent=2)}")
r = requests.post(f'{BASE_URL}/admin/backdate-position',
                 headers=headers,
                 json=payload1,
                 verify=False)

print(f"\nStatus: {r.status_code}")
resp = r.json()
print(f"Response:")
print(json.dumps(resp, indent=2))

if resp.get('success') == True:
    print("\n✅ OPTSTK WORKS!")
else:
    print(f"\n❌ OPTSTK FAILED: {resp.get('detail')}")

time.sleep(2)

# Test 2: OPTIDX (Index Option)
print("\n" + "="*80)
print("TEST 2: OPTIDX (Nifty Index Option)")  
print("="*80)

payload2 = {
    'user_id': TRADER1_ID,
    'symbol': 'NIFTY 02 MAR 19600 CALL',
    'qty': 25,
    'price': 125.00,
    'trade_date': '25-02-2026',
    'instrument_type': 'OPTIDX',
    'exchange': 'NSE'
}

print(f"Payload: {json.dumps(payload2, indent=2)}")
r = requests.post(f'{BASE_URL}/admin/backdate-position',
                 headers=headers,
                 json=payload2,
                 verify=False)

print(f"\nStatus: {r.status_code}")
resp = r.json()
print(f"Response:")
print(json.dumps(resp, indent=2))

if resp.get('success') == True:
    print("\n✅ OPTIDX WORKS!")
else:
    print(f"\n❌ OPTIDX FAILED: {resp.get('detail')}")

print("\n" + "="*80)
print("FINAL VERDICT")
print("="*80)
print("If both show ✅ WORKS → F&O is now fixed and working")
print("If either fails → There's still an issue")
print("="*80)
