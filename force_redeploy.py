import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('=' * 80)
print('FORCING FULL REDEPLOY (PULL + BUILD + START)')
print('=' * 80)
print()

# Try different endpoints that might trigger a full redeploy
endpoints_to_try = [
    ('deploy', f'{base}/applications/{uuid}/deploy'),
    ('restart with force_rebuild', f'{base}/applications/{uuid}/restart?force_rebuild=true'),
]

for name, url in endpoints_to_try:
    print(f'Trying {name}...')
    try:
        r = requests.post(url, headers=headers, timeout=10)
        print(f'  Status: {r.status_code}')
        if r.status_code == 200:
            print(f'  ✅ Success via {name}')
            print()
            break
        elif r.status_code in [404, 405]:
            print(f'  ❌ Endpoint not valid')
        else:
            print(f'  Response: {r.text[:200]}')
    except Exception as e:
        print(f'  Error: {str(e)[:100]}')
    print()

print('Waiting 30 seconds for deployment...')
time.sleep(30)

print('\nChecking status...')
r = requests.get(f'{base}/applications/{uuid}', headers=headers)
data = r.json()
if isinstance(data, list):
    app = data[0]
else:
    app = data.get('data', data)

print(f'Status: {app.get("status")}')
print(f'Git Commit: {app.get("git_commit_sha", "N/A")}')

print('\nTesting endpoints...')
for path in ['/health', '/api/v2/health']:
    try:
        r = requests.get(f'http://api.tradingnexus.pro{path}', timeout=5)
        icon = '✅' if r.status_code == 200 else '❌'
        print(f'{icon} {path:20} HTTP {r.status_code}')
    except Exception as e:
        print(f'❌ {path:20} ERROR')
