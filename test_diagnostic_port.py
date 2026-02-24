import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('=' * 80)
print('REDEPLOY WITH DIAGNOSTIC PORT 8001')
print('=' * 80)
print()

print('Triggering redeploy...')
r = requests.post(f'{base}/applications/{uuid}/restart?force_rebuild=true', headers=headers, timeout=10)
print(f'Status: {r.status_code}')
print()

print('Waiting 45 seconds for deployment...')
time.sleep(45)

print('\nTesting direct port access (8001)...')
test_urls = [
    ('VPS:8001/health', 'http://72.62.228.112:8001/health'),
    ('VPS:8001/api/v2/health', 'http://72.62.228.112:8001/api/v2/health'),
]

for name, url in test_urls:
    try:
        r = requests.get(url, timeout=5)
        icon = '✅' if r.status_code == 200 else '❌'
        print(f'{icon} {name:30} HTTP {r.status_code}')
        if r.status_code == 200:
            print(f'   Response: {r.text[:100]}')
    except Exception as e:
        print(f'❌ {name:30} ERROR: {str(e)[:50]}')

print('\nTesting Traefik routing (domain)...')
test_urls = [
    ('api.tradingnexus.pro/health', 'http://api.tradingnexus.pro/health'),
    ('api.tradingnexus.pro/api/v2/health', 'http://api.tradingnexus.pro/api/v2/health'),
]

for name, url in test_urls:
    try:
        r = requests.get(url, timeout=5)
        icon = '✅' if r.status_code == 200 else '❌'
        print(f'{icon} {name:30} HTTP {r.status_code}')
    except Exception as e:
        print(f'❌ {name:30} ERROR: {str(e)[:50]}')
