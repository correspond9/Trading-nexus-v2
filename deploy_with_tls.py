import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'  # New application UUID
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('=' * 80)
print('DEPLOYING WITH TLS/HTTPS ENABLED')
print('=' * 80)
print()

print('Triggering redeploy...')
r = requests.post(f'{base}/applications/{uuid}/restart?force_rebuild=true', headers=headers, timeout=10)
print(f'Status: {r.status_code}')

if r.status_code != 200:
    print(f'Error: {r.text}')
    exit(1)

print()
print('Monitoring deployment...')
print('-' * 80)

for i in range(60):
    time.sleep(5)
    r = requests.get(f'{base}/applications/{uuid}', headers=headers, timeout=10)
    data = r.json()
    
    if isinstance(data, list):
        status = data[0]['status']
    else:
        status = data.get('data', {}).get('status', data.get('status', 'unknown'))
    
    if i % 6 == 0 or 'running' in status.lower() or 'exited' in status.lower():
        elapsed = i * 5
        print(f'[{elapsed:>3}s] {status}')
    
    if 'running' in status.lower():
        print()
        print('✅ Deployment successful - waiting for SSL certificate generation...')
        print('Waiting 30 seconds for Let\'s Encrypt certificate...')
        time.sleep(30)
        break
    elif 'exited' in status.lower():
        print()
        print('❌ Deployment failed')
        exit(1)

print()
print('Testing HTTPS endpoints...')
print('-' * 80)

endpoints = [
    ('Backend HTTPS Health', 'https://api.tradingnexus.pro/health'),
    ('Backend HTTPS API', 'https://api.tradingnexus.pro/api/v2/health'),
    ('Frontend HTTPS', 'https://tradingnexus.pro'),
]

for name, url in endpoints:
    try:
        r = requests.get(url, timeout=10, verify=False)  # verify=False for self-signed during cert generation
        icon = '✅' if r.status_code == 200 else '⚠️'
        print(f'{icon} {name:25} HTTP {r.status_code}')
    except Exception as e:
        print(f'❌ {name:25} ERROR: {str(e)[:50]}')

print()
print('=' * 80)
print('Note: If you see SSL errors, wait a few minutes for Let\'s Encrypt')
print('      certificate generation to complete, then refresh your browser.')
print('=' * 80)
