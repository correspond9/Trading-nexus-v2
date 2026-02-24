#!/usr/bin/env python
"""Simple test to see the ACTUAL raw response from backdate API."""

import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"

# Login
r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("="*80)
print("RAW RESPONSE TEST - Creating a brand new position")
print("="*80)

# Try to create a new unique position with current timestamp
import time
timestamp = int(time.time())

payload = {
    'user_id': '00000000-0000-0000-0000-000000000003',
    'symbol': 'ITC',  # Use same symbol but will get "already exists" OR see full response
    'qty': 10,
    'price': 450.00,
    'trade_date': '25-02-2026',
    'instrument_type': 'EQ',
    'exchange': 'NSE'
}

print(f"\nPayload: {json.dumps(payload, indent=2)}")
print("\nSending request...")

r = requests.post(f'{BASE_URL}/admin/backdate-position',
                 headers=headers,
                 json=payload,
                 verify=False)

print(f"\nStatus Code: {r.status_code}")
print(f"\nRAW Response:")
print("="*80)
try:
    response_json = r.json()
    print(json.dumps(response_json, indent=2))
except:
    print(r.text)

print("="*80)

# If it already exists, try with HDFC AMC instead
if r.status_code == 200 and r.json().get('success') == False:
    print("\n\nITC already exists, trying HDFC AMC...")
    payload['symbol'] = 'HDFC AMC'
    
    r = requests.post(f'{BASE_URL}/admin/backdate-position',
                     headers=headers,
                     json=payload,
                     verify=False)
    
    print(f"Status Code: {r.status_code}")
    print(f"\nRAW Response:")
    print("="*80)
    try:
        response_json = r.json()
        print(json.dumps(response_json, indent=2))
    except:
        print(r.text)
    print("="*80)
