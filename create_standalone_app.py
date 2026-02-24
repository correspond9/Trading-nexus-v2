import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print('Creating standalone application...')

# Try creating without project specification
payload = {
    'name': 'trade-nexus-v2',
    'git_repository': 'https://github.com/correspond9/Trading-nexus-v2.git',
    'git_branch': 'main',
    'docker_compose_location': '/docker-compose.prod.yml',
    'build_pack': 'docker-compose'
}

r = requests.post(f'{base}/applications', json=payload, headers=headers, timeout=10)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:500]}')

if r.status_code in [200, 201]:
    data = r.json()
    print('Successfully created!')
    if isinstance(data, dict) and 'uuid' in data:
        print(f'UUID: {data["uuid"]}')
