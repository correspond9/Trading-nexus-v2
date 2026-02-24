import requests
import warnings

warnings.filterwarnings('ignore')

print('TESTING MARUTI SUZUKI INDIA (Multi-word symbol)')
print('='*60)

# Login as admin
r = requests.post('https://tradingnexus.pro/api/v2/auth/login',
                 verify=False,
                 json={'mobile': '8888888888', 'password': 'admin123'})
token = r.json()['access_token']

# Test with MARUTI SUZUKI INDIA (different symbol)
r = requests.post('https://tradingnexus.pro/api/v2/admin/backdate-position',
                 verify=False,
                 headers={'Authorization': f'Bearer {token}'},
                 json={
                     'user_id': '00000000-0000-0000-0000-000000000003',
                     'symbol': 'MARUTI SUZUKI INDIA',
                     'qty': 100,
                     'price': 9100.0,
                     'trade_date': '20-02-2026',
                     'instrument_type': 'EQ',
                     'exchange': 'NSE'
                 })

print(f'Status: {r.status_code}')
resp = r.json()

if resp.get('success'):
    print(f'✅ SUCCESS! Position created with multi-word symbol')
    pos = resp['position']
    print(f'   Symbol: {pos["symbol"]}')
    print(f'   Qty: {pos["quantity"]}')
    print(f'   Price: {pos["avg_price"]}')
else:
    print(f'Response: {resp}')
