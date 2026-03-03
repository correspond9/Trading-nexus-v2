import requests
import json

s = requests.Session()
s.verify = False

base = 'https://tradingnexus.pro/api/v2'
login = s.post(f'{base}/auth/login', json={'mobile':'9999999999','password':'admin123'}, timeout=20).json()
token = login.get('token') or login.get('access_token') or login.get('data',{}).get('token')
h = {'X-AUTH': token}

print('Testing /trading/orders/executed endpoint...')
r = s.get(f'{base}/trading/orders/executed', headers=h, params={'from_date':'2025-12-01','to_date':'2026-03-05'}, timeout=20)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    count = len(data.get('data', []))
    print(f'Executed trades count: {count}')
    if data.get('data'):
        rec = data['data'][0]
        print(f'Sample: Symbol={rec.get("symbol")}, Status={rec.get("status")}, Side={rec.get("side")}')
else:
    print(f'Error: {r.text[:200]}')
