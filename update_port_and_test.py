import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print('Updating exposed port to 8000...\n')

update_data = {
    'ports_exposes': '8000',
}

print(f'Sending update: {update_data}')
r = requests.patch(f'{base}/applications/{uuid}', headers=headers, json=update_data, timeout=10)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:200]}')

if r.status_code in [200, 201]:
    print('\n✅ Port configuration updated!')
 
    print('\nRedeploying...')
    r2 = requests.post(f'{base}/applications/{uuid}/restart?force_rebuild=true', headers=headers)
    print(f'Status: {r2.status_code}')
    
    print('\nWaiting 45 seconds...')
    time.sleep(45)
    
    print('\nTesting endpoints...')
    for path in ['/health', '/api/v2/health']:
        try:
            url = f'http://api.tradingnexus.pro{path}'
            r3 = requests.get(url, timeout=5)
            icon = '✅' if r3.status_code == 200 else '❌'
            print(f'{icon} {path:20} HTTP {r3.status_code}')
            if r3.status_code == 200:
                print(f'   {r3.text[:100]}')
        except Exception as e:
            print(f'❌ {path:20} ERROR')
else:
    print('\n❌ Update failed') 
