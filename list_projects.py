import requests
import json

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Listing projects...')
r = requests.get(f'{base}/projects', headers=headers, timeout=10)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        projects = data
    else:
        projects = data.get('data', [])
    print(f'Found {len(projects)} projects')
    for p in projects:
        print(f'  - Name: {p.get("name")}')
        print(f'    UUID: {p.get("uuid")}')
else:
    print(f'Error: {r.text}')
