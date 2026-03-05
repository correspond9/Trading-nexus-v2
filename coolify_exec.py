import requests
import json

COOLIFY_URL = 'http://72.62.228.112:8000'
TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'x8gg0og8440wkgc8ow0ococs'
SERVER_UUID = 'zk0wks40sw4cw8gg8s8kogko'
DB_CONTAINER = 'db-x8gg0og8440wkgc8ow0ococs-185216949781'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def get(path):
    return requests.get(f'{COOLIFY_URL}{path}', headers=headers, timeout=15)

def post(path, payload=None):
    return requests.post(f'{COOLIFY_URL}{path}', headers=headers, json=payload, timeout=30)

# Try all possible execute/command endpoints
endpoints_to_try = [
    ('POST', f'/api/v1/servers/{SERVER_UUID}/execute', {"command": "docker ps --filter name=db-x8gg --format '{{{{.Names}}}}'"}),
    ('POST', f'/api/v1/servers/{SERVER_UUID}/command', {"command": "docker ps"}),
    ('POST', f'/api/v1/execute', {"server_uuid": SERVER_UUID, "command": "docker ps"}),
    ('GET',  f'/api/v1/applications/{APP_UUID}/envs', None),
    ('GET',  f'/api/v1/applications/{APP_UUID}/environment-variables', None),
    ('GET',  f'/api/v1/services', None),
]

for method, path, payload in endpoints_to_try:
    try:
        if method == 'GET':
            r = get(path)
        else:
            r = post(path, payload)
        print(f"{method} {path} => {r.status_code}")
        if r.status_code not in [404, 405]:
            print(r.text[:1000])
        print()
    except Exception as e:
        print(f"{method} {path} => ERROR: {e}\n")

# Try getting full app details again
print("\n=== Full App Env Variables ===")
r = get(f'/api/v1/applications/{APP_UUID}')
data = r.json()
for key in sorted(data.keys()):
    val = data[key]
    if val and any(x in key.lower() for x in ['env', 'var', 'db', 'database', 'config']):
        print(f"  {key}: {str(val)[:300]}")
