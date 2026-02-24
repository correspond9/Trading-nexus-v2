import requests
import time

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

# Old app UUID
old_uuid = 'iwkk4g08gcw4wgc0ocw048k4'

print('=' * 80)
print('STOPPING OLD TRADE-NEXUSS APPLICATION')
print('=' * 80)
print()

# Stop the old app
print('Sending stop request to old application...')
resp = requests.post(f'{base}/applications/{old_uuid}/stop', headers=headers, timeout=10)
print(f'Stop response: {resp.status_code}')
print()

if resp.status_code == 200:
    print('Waiting 10 seconds for containers to stop...')
    time.sleep(10)
    print('Old application should now be stopped.')
else:
    print(f'Error: {resp.text}')
