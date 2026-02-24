import requests
import json

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
project_uuid = 'mkwg4osgoo880k4ogswgw08o'  # trade-nexus-v2 project
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print('Creating new application resource...')

payload = {
    'name': 'trade-nexus-v2-production',
    'description': 'Trading Nexus Production - V2',
    'docker_compose_location': '/docker-compose.prod.yml',
    'git_repository': 'https://github.com/correspond9/Trading-nexus-v2.git',
    'git_branch': 'main',
    'git_commit_sha': '',
}

r = requests.post(
    f'{base}/projects/{project_uuid}/applications',
    json=payload,
    headers=headers,
    timeout=10
)

print(f'Status: {r.status_code}')
if r.status_code in [200, 201]:
    data = r.json().get('data', r.json())
    if isinstance(data, list):
        data = data[0] if data else {}
    app_uuid = data.get('uuid')
    print(f'Created! UUID: {app_uuid}')
    print(f'Name: {data.get("name")}')
else:
    print(f'Error: {r.text}')
