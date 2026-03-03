import requests
import json

s = requests.Session()
s.verify = False

base = 'https://tradingnexus.pro/api/v2'

# Login
login = s.post(f'{base}/auth/login', json={'mobile':'9999999999','password':'admin123'}, timeout=20).json()
token = login.get('token') or login.get('access_token') or login.get('data',{}).get('token')
h = {'X-AUTH': token}

print("="*60)
print("TEST 1: /trading/orders endpoint")
print("="*60)
r1 = s.get(f'{base}/trading/orders', headers=h, params={'from_date':'2026-02-01','to_date':'2026-03-03'}, timeout=20)
print(f'Status: {r1.status_code}')
data1 = r1.json()
print(f'Record count: {len(data1.get("data", []))}')
if data1.get('data'):
    print(f'Sample (first): {json.dumps(data1["data"][0], indent=2, default=str)[:300]}')

print("\n" + "="*60)
print("TEST 2: /trading/orders/executed endpoint")
print("="*60)
r2 = s.get(f'{base}/trading/orders/executed', headers=h, params={'from_date':'2026-02-01','to_date':'2026-03-03'}, timeout=20)
print(f'Status: {r2.status_code}')
if r2.status_code == 200:
    data2 = r2.json()
    print(f'Record count: {len(data2.get("data", []))}')
    if data2.get('data'):
        print(f'Sample (first): {json.dumps(data2["data"][0], indent=2, default=str)[:300]}')
else:
    print(f'Response: {r2.text[:500]}')

print("\n" + "="*60)
print("TEST 3: Check what the frontend is actually receiving")
print("="*60)
# The frontend code shows it's calling /trading/orders, let's check what statuses it's getting
print(f'Statuses in /trading/orders response:')
if data1.get('data'):
    statuses = set(o.get('status') for o in data1['data'])
    print(f'  Statuses found: {statuses}')
    
    # Filter for FILLED
    filled = [o for o in data1['data'] if o.get('status') == 'FILLED']
    print(f'  FILLED orders: {len(filled)}')
