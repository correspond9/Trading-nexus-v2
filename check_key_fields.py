import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

r = requests.get(f'{base}/applications/{uuid}', headers=headers)
data = r.json()

if isinstance(data, list):
    app = data[0]
else:
    app = data.get('data', data)

# Print only key fields
keys_to_check = [
    'fqdn', 'domains', 'ports_exposes', 'ports_mappings', 
    'manual_webhook_secret_github', 'docker_compose_pr_location',
    'docker_compose_custom_start_command', 'docker_compose_custom_build_command',
]

print('Key Configuration Fields:')
print('=' * 60)
for key in keys_to_check:
    value = app.get(key, 'NOT_FOUND')
    print(f'{key:40}: {value}')
