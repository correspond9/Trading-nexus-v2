import requests
import json

COOLIFY_URL = 'http://72.62.228.112:8000'
TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'x8gg0og8440wkgc8ow0ococs'
headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/json'}

# Get app details
print("=== App Details ===")
r = requests.get(f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}', headers=headers, timeout=15)
print('Status:', r.status_code)
data = r.json()
print('Name:', data.get('name'))
print('Status:', data.get('status'))
print('Fqdn:', data.get('fqdn'))
print('Server:', data.get('server'))

# check for db env vars
envs = data.get('environment_variables', [])
print(f'\nEnv vars ({len(envs)}):')
for e in envs:
    k = e.get('key', '')
    v = e.get('value', '')
    if any(x in k.upper() for x in ['DB', 'DATABASE', 'POSTGRES', 'SQL', 'HOST', 'USER', 'PASS', 'URL']):
        print(f'  {k} = {v}')

# Try to list all resources to find DB service
print("\n=== All Resources ===")
r2 = requests.get(f'{COOLIFY_URL}/api/v1/resources', headers=headers, timeout=15)
print('Status:', r2.status_code)
for res in r2.json():
    print(f"  {res.get('name')} | {res.get('type')} | {res.get('uuid')}")

# Try databases endpoint
print("\n=== Databases ===")
r3 = requests.get(f'{COOLIFY_URL}/api/v1/databases', headers=headers, timeout=15)
print('Status:', r3.status_code)
print(json.dumps(r3.json(), indent=2)[:3000])

# Check execute endpoint
print("\n=== Trying execute command endpoint ===")
payload = {"command": "echo hello"}
r4 = requests.post(f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}/execute', headers=headers, json=payload, timeout=15)
print('Status:', r4.status_code)
print(r4.text[:500])
