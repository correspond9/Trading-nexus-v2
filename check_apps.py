import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('=' * 80)
print('APPLICATIONS ON VPS')
print('=' * 80)
print()

try:
    resp = requests.get(f'{base}/applications', headers=headers, timeout=10)
    data = resp.json()
    apps = data if isinstance(data, list) else data.get('data', [])
    
    for app in apps:
        name = app.get('name', 'N/A')
        uuid = app.get('uuid', 'N/A')
        status = app.get('status', 'N/A')
        online = app.get('is_online', 'N/A')
        print(f'Name:   {name}')
        print(f'UUID:   {uuid}')
        print(f'Status: {status}')
        print(f'Online: {online}')
        print('-' * 80)
        print()
        
except Exception as e:
    print(f'Error: {e}')
