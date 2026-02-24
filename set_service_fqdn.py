import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print('Setting SERVICE_FQDN environment variables for Traefik routing...\n')

# Set environment variables
env_data = {
    'key': 'SERVICE_FQDN_BACKEND',
    'value': 'api.tradingnexus.pro',
    'is_build_time': False,
    'is_preview': False
}

print(f'Setting: SERVICE_FQDN_BACKEND=api.tradingnexus.pro')
r = requests.post(
    f'{base}/applications/{uuid}/envs',
    headers=headers,
    json=env_data,
    timeout=10
)
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:200]}')
print()

# Try the batch endpoint instead if above fails
if r.status_code not in [200, 201]:
    print('Trying batch environment update...')
    env_batch = {
        'SERVICE_FQDN_BACKEND': 'api.tradingnexus.pro',
        'SERVICE_FQDN_FRONTEND': 'tradingnexus.pro',
    }
    
    r2 = requests.patch(
        f'{base}/applications/{uuid}',
        headers=headers,
        json={'env_variables': env_batch},
        timeout=10
    )
    print(f'Batch status: {r2.status_code}')
    print(f'Batch response: {r2.text[:200]}')
