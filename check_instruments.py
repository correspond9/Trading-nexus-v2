#!/usr/bin/env python3
"""Check available instruments"""

import requests
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

print("Checking available endpoints...\n")

# Try to find instruments
endpoints_to_try = [
    '/portfolio/instruments',
    '/instruments',
    '/market/instruments',
    '/search?symbol=A',
]

for endpoint in endpoints_to_try:
    url = f'{BASE_URL}{endpoint}'
    print(f"Testing {endpoint}...")
    try:
        r = requests.get(url, verify=False, headers=headers, timeout=5)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Response preview: {str(data)[:150]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()

# Try without symbol to see if there's a list
print("Trying search with different parameters...\n")
for symbol in ['', 'A', 'SBIN', 'NIFTY']:
    url = f'{BASE_URL}/portfolio/search'
    if symbol:
        url += f'?symbol={symbol}'
    print(f"GET {url}")
    try:
        r = requests.get(url, verify=False, headers=headers, timeout=5)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            print(f"  Response: {str(r.json())[:150]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
