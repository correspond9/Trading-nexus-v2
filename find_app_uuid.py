#!/usr/bin/env python3
import requests

token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print("Fetching all Coolify applications...\n")

# Get all applications
resp = requests.get('http://72.62.228.112:8000/api/v1/applications', headers=headers, timeout=30)
if resp.status_code == 200:
    data = resp.json()
    # Could be list or dict
    if isinstance(data, dict) and 'data' in data:
        apps = data['data']
    elif isinstance(data, list):
        apps = data
    else:
        apps = [data] if data else []
    
    print(f"Found {len(apps)} application(s):\n")
    for app in apps:
        uuid = app.get('uuid') if isinstance(app, dict) else '?'
        name = app.get('name') if isinstance(app, dict) else '?'
        print(f"  UUID: {uuid}")
        print(f"  Name: {name}\n")
else:
    print(f'Error: {resp.status_code} - {resp.text}')
