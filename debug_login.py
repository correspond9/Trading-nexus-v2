#!/usr/bin/env python3
"""Test login with detailed error handling"""

import requests
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

print("Testing login endpoint...\n")

r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})

print(f"Status Code: {r.status_code}")
print(f"Headers: {dict(r.headers)}")
print(f"Response Text: {r.text[:500]}")
print(f"Response Content: {r.content[:500]}")
