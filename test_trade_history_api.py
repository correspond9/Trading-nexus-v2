import requests
import json

s = requests.Session()
s.verify = False

# Login
base = 'https://tradingnexus.pro/api/v2'
login = s.post(f'{base}/auth/login', json={'mobile':'9999999999','password':'admin123'}, timeout=20).json()
token = login.get('token') or login.get('access_token') or login.get('data',{}).get('token')
h = {'X-AUTH': token, 'Content-Type': 'application/json'}

print('Testing /trading/orders endpoint...')
r = s.get(f'{base}/trading/orders', headers=h, timeout=20)
print(f'Status: {r.status_code}')
data = r.json() if r.status_code == 200 else r.text[:300]
if isinstance(data, dict):
    print(f'Record count: {len(data.get("data", []))}')
    if data.get('data'):
        print(f'Sample: {json.dumps(data["data"][0], indent=2)[:400]}')
else:
    print(f'Response: {data}')

print('\n\nTesting /trading/orders/historic/orders endpoint...')
r2 = s.get(f'{base}/trading/orders/historic/orders', headers=h, params={'from_date':'2025-12-01','to_date':'2026-03-05'}, timeout=20)
print(f'Status: {r2.status_code}')
data2 = r2.json()
if isinstance(data2, dict):
    count = len(data2.get('data', []))
    print(f'Record count: {count}')
    if data2.get('data'):
        rec = data2['data'][0]
        print(f'Fields: {list(rec.keys())}')
        print(f'Sample: Symbol={rec.get("symbol")}, Status={rec.get("status")}, PlacedAt={rec.get("placed_at")}')
else:
    print(f'Response: {data2}')
