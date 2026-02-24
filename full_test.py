import requests
import json

print('COMPLETE BACKDATE POSITION TEST')
print('=' * 70)

# 1. Login as admin
print('\n1. Logging in as admin (8888888888)...')
login_r = requests.post(
    'https://tradingnexus.pro/api/v2/auth/login',
    json={'mobile': '8888888888', 'password': 'admin123'},
    verify=False
)

if login_r.status_code != 200:
    print(f'   FAILED: {login_r.status_code}')
    print(f'   {login_r.json()}')
    exit(1)

token = login_r.json()['access_token']
print(f'   OK - Token: {token[:25]}...')

# 2. Get all users to find the correct IDs
print('\n2. Fetching all users...')
headers = {'Authorization': f'Bearer {token}'}
users_r = requests.get('https://tradingnexus.pro/api/v2/admin/users', headers=headers, verify=False)

if users_r.status_code != 200:
    print(f'   FAILED: {users_r.status_code}')
    print(f'   {users_r.json()}')
    exit(1)

users = users_r.json()
print(f'   Response keys: {users.keys() if isinstance(users, dict) else "list"}')

# Extract users from response (might be wrapped in 'data' key)
user_list = users.get('data', users) if isinstance(users, dict) else users

user_id = None
if isinstance(user_list, list) and len(user_list) > 0:
    # Find Trader 1 first
    for user in user_list:
        if isinstance(user, dict):
            name = (user.get('first_name', '') + ' ' + user.get('last_name', '')).lower()
            if 'trader' in name:
                user_id = user.get('id')
                print(f'   Found Trader 1: {user.get("first_name")} (ID: {user_id})')
                break
    
    # If not found, use first non-admin user
    if not user_id and len(user_list) > 1:
        for user in user_list:
            if isinstance(user, dict) and user.get('role') != 'ADMIN':
                user_id = user.get('id')
                print(f'   Using user: {user.get("first_name")} (ID: {user_id})')
                break
    
    # If still not found, use first user
    if not user_id and isinstance(user_list[0], dict):
        user_id = user_list[0].get('id')
        print(f'   Using first user (fallback): {user_list[0].get("first_name")} (ID: {user_id})')
    
    print(f'   Using user ID: {user_id}')

if not user_id:
    print('   ERROR: Could not find user ID')
    exit(1)

# 3. Test backdate position
print('\n3. Testing backdate position...')
print('   Payload:')
payload = {
    'user_id': user_id,
    'symbol': 'LENSKART SOLUTIONS LTD',  # Correct symbol from search
    'qty': 370,
    'price': 524.70,
    'trade_date': '19-02-2026',
    'instrument_type': 'EQ',
    'exchange': 'NSE'
}
print(json.dumps(payload, indent=6))

backdate_r = requests.post(
    'https://tradingnexus.pro/api/v2/admin/backdate-position',
    json=payload,
    headers=headers,
    verify=False
)

print(f'\n   Status: {backdate_r.status_code}')
resp = backdate_r.json()
print(f'   Response:')
print(json.dumps(resp, indent=6))

if backdate_r.status_code == 200 and resp.get('success'):
    print('\n' + '='*70)
    print('SUCCESS! Backdate position created!')
    print('='*70)
elif 'Invalid exchange' in str(resp):
    print('\nERROR: Backend still rejecting NSE exchange')
else:
    print('\nCheck error details above')
