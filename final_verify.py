#!/usr/bin/env python3
import requests
import json

vps = 'http://72.62.228.112:8000/api/v2'

endpoints = {
    '/health': 'Health Check',
    '/admin/notifications?limit=1': 'Data Query',
}

print('=' * 80)
print('DEPLOYMENT VERIFICATION')
print('=' * 80)
print()

success = True
for path, desc in endpoints.items():
    print(f'Testing: {desc}')
    try:
        resp = requests.get(f'{vps}{path}', timeout=5)
        if resp.status_code == 200:
            print(f'  ✓ Status 200 OK')
            try:
                data = resp.json()
                print(f'  ✓ Response received')
                if data:
                    print(f'  ✓ Data present')
            except:
                print(f'  ✓ Non-JSON response')
        else:
            print(f'  ✗ Status {resp.status_code}')
            success = False
    except Exception as e:
        print(f'  ✗ Error: {e}')
        success = False
    print()

print('=' * 80)
if success:
    print('✓ DEPLOYMENT SUCCESSFUL - All endpoints responding')
else:
    print('⚠ Some endpoints not responding - wait 30s and retry')
print('=' * 80)
