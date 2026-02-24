import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Listing all applications globally...')
r = requests.get(f'{base}/applications', headers=headers, timeout=10)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    # Try to get data from response
    if isinstance(data, dict):
        apps = data.get('data', [])
    elif isinstance(data, list):
        apps = data
    else:
        apps = []
    
    print(f'Found {len(apps)} applications')
    for app in apps:
        name = app.get('name', 'unknown')
        uuid = app.get('uuid', 'unknown')
        status = app.get('status', 'unknown')
        print(f'  - {name}')
        print(f'    UUID: {uuid}')
        print(f'    Status: {status}')
        print()
else:
    print(f'Error: {r.text}')
