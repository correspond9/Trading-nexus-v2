import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

uuid = 'zccs8wko40occg44888kwooc'

print('=' * 80)
print('REDEPLOYING WITH FIXED TRAEFIK ROUTING')
print('=' * 80)
print()

# Trigger restart
print('Triggering restart...')
resp = requests.post(f'{base}/applications/{uuid}/restart', headers=headers, timeout=10)
print(f'Restart status: {resp.status_code}')
print()

if resp.status_code == 200:
    print('=' * 80)
    print('Monitoring deployment (2 minutes)...')
    print('=' * 80)
    print()
    
    for i in range(24):
        resp = requests.get(f'{base}/applications/{uuid}', headers=headers, timeout=10)
        data = resp.json()
        status = data[0].get('status', 'unknown') if isinstance(data, list) else data.get('status', 'unknown')
        
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
else:
    print(f'Error: {resp.text}')
