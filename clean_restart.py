import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

uuid = 'zccs8wko40occg44888kwooc'

print('Checking current application status...')
resp = requests.get(f'{base}/applications/{uuid}', headers=headers, timeout=10)
data = resp.json()
status = data[0]['status'] if isinstance(data, list) else data['status']
print(f'Current status: {status}')
print()

if 'starting' in status.lower() or 'restarting' in status.lower():
    print('Application is still deploying. Stopping it...')
    resp = requests.post(f'{base}/applications/{uuid}/stop', headers=headers, timeout=10)
    print(f'Stop request: {resp.status_code}')
    time.sleep(5)
    print()

print('Triggering fresh restart...')
resp = requests.post(f'{base}/applications/{uuid}/restart', headers=headers, timeout=10)
print(f'Restart request: {resp.status_code}')
print()
print('Monitoring deployment (2 minutes)...')
print()

for i in range(24):
    resp = requests.get(f'{base}/applications/{uuid}', headers=headers, timeout=10)
    data = resp.json()
    status = data[0]['status'] if isinstance(data, list) else data['status']
    
    elapsed = i * 5
    print(f'[{elapsed:>3}s] {status}')
    
    if 'running' in status.lower():
        print()
        print('✓ DEPLOYMENT SUCCESSFUL!')
        break
    if 'exited' in status.lower():
        print()
        print('✗ Deployment failed')
        break
    
    time.sleep(5)
