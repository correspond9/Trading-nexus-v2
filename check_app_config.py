import requests
import json

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Fetching application configuration...')
print('=' * 70)
print()

r = requests.get(f'{base}/applications/{uuid}', headers=headers, timeout=10)

if r.status_code == 200:
    data = r.json()
    if isinstance(data, dict):
        app = data.get('data', data)
    elif isinstance(data, list):
        app = data[0] if data else {}
    else:
        app = {}
    
    print(f'Name: {app.get("name")}')
    print(f'Status: {app.get("status")}')
    print(f'Build Pack: {app.get("build_pack")}')
    print(f'Docker Compose Location: {app.get("docker_compose_location")}')
    print(f'Git Repo: {app.get("git_repository")}')
    print(f'Git Branch: {app.get("git_branch")}')
    print()
    print(f'Domains (Frontend): {app.get("fqdn")}')
    print(f'Health Check Enabled: {app.get("health_check_enabled")}')
    print(f'Health Check Path: {app.get("health_check_path")}')
    print()
    
    # Show relevant settings
    settings = app.get('settings', {})
    if settings:
        print('Settings:')
        print(f'  - Is Bot: {settings.get("is_bot")}')
else:
    print(f'Error {r.status_code}: {r.text}')
