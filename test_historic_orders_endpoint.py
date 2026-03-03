import requests

s = requests.Session()
s.verify = False

base = 'https://tradingnexus.pro/api/v2'

# Login
login = s.post(f'{base}/auth/login', json={'mobile':'9999999999','password':'admin123'}, timeout=20).json()
token = login.get('token') or login.get('access_token') or login.get('data',{}).get('token')
h = {'X-AUTH': token}

print('Testing /trading/orders/historic/orders')
r = s.get(f'{base}/trading/orders/historic/orders', headers=h, params={'from_date':'2026-02-01','to_date':'2026-03-03'}, timeout=20)
print(f'Status: {r.status_code}')
data = r.json()
count = len(data.get('data', []))
print(f'Record count: {count}')
if data.get('data'):
    rec = data['data'][0]
    print(f'Sample: Symbol={rec.get("symbol")}, Status={rec.get("status")}')
    if count == 0:
        print(f'Response keys: {list(data.keys())}')
