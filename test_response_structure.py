import requests
import json

s = requests.Session()
s.verify = False

base = 'https://tradingnexus.pro/api/v2'

# Login
login = s.post(f'{base}/auth/login', json={'mobile':'9999999999','password':'admin123'}, timeout=20).json()
token = login.get('token') or login.get('access_token') or login.get('data',{}).get('token')
h = {'X-AUTH': token}

print('Full response structure from /trading/orders/historic/orders')
r = s.get(f'{base}/trading/orders/historic/orders', headers=h, params={'from_date':'2026-02-01','to_date':'2026-03-03'}, timeout=20)
data = r.json()

print(f'Top-level keys: {list(data.keys())}')
print(f'Type of "data" key: {type(data.get("data"))}')
print(f'Length of "data": {len(data.get("data", []))}')
print(f'\nFirst record in "data":')
if data.get('data'):
    print(json.dumps(data['data'][0], indent=2, default=str)[:500])
