import requests
import json
from datetime import datetime

api_token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
headers = {'Authorization': f'Bearer {api_token}'}
base_url = 'http://72.62.228.112:8000/api/v1'

print('=== CHECKING DEPLOYMENT STATUS & LOGS ===')
dep_uuid = 'jgwg88c000ckok8ggscc4c08'
try:
    r = requests.get(f'{base_url}/deployments/{dep_uuid}', headers=headers, timeout=10)
    if r.status_code == 200:
        dep = r.json()
        print(f'Deployment ID: {dep.get("id")}')
        print(f'Status: {dep.get("status")}')
        print(f'Created: {dep.get("created_at")}')
        print(f'Updated: {dep.get("updated_at")}')
        logs = dep.get('logs', '')
        print(f'\nLogs (last 1500 chars):\n{str(logs)[-1500:]}')
    else:
        print(f'Error {r.status_code}: {r.text[:500]}')
except Exception as e:
    print(f'Error: {e}')

print('\n=== CHECKING ALL APPLICATIONS ===')
try:
    r = requests.get(f'{base_url}/applications', headers=headers, timeout=10)
    if r.status_code == 200:
        apps = r.json()
        if isinstance(apps, list):
            print(f'Found {len(apps)} applications')
            for app in apps[:10]:
                print(f"\nApp: {app.get('name')}")
                print(f"  Status: {app.get('status')}")
                print(f"  Updated: {app.get('updated_at')}")
        else:
            print(json.dumps(apps, indent=2)[:1000])
    else:
        print(f'Error {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

print('\n=== CHECKING RECENT DEPLOYMENTS (all) ===')
try:
    r = requests.get(f'{base_url}/deployments?limit=10', headers=headers, timeout=10)
    if r.status_code == 200:
        deps = r.json()
        if isinstance(deps, list):
            for dep in deps[:5]:
                print(f"\nID: {dep.get('id')}")
                print(f"  Status: {dep.get('status')}")
                print(f"  Created: {dep.get('created_at')}")
        else:
            print(json.dumps(deps, indent=2)[:1000])
    else:
        print(f'Error {r.status_code}')
except Exception as e:
    print(f'Error: {e}')
