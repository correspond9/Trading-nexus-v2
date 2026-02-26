#!/usr/bin/env python3
"""Check all users and their details"""

import requests
import json
import warnings

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'

r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

print("CHECKING ALL USERS IN SYSTEM:\n")

r = requests.get(f'{BASE_URL}/admin/users', verify=False, headers=headers)

if r.status_code == 200:
    data = r.json()
    
    if 'users' in data:
        users = data['users']
    else:
        users = data.get('data', [])
    
    print(f"Total users: {len(users)}\n")
    
    for u in users:
        print(f"User ID: {u.get('id', 'N/A')}")
        print(f"  Mobile: {u.get('mobile')}")
        print(f"  Name: {u.get('name')}")
        print(f"  Role: {u.get('role')}")
        print(f"  User No: {u.get('user_no')}")
        print()
else:
    print(f"Failed: {r.status_code}")
    print(r.text[:300])
