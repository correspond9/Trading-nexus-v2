import requests
import json

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Getting full application configuration...\n')
r = requests.get(f'{base}/applications/{uuid}', headers=headers)
data = r.json()

if isinstance(data, list):
    app = data[0]
else:
    app = data.get('data', data)

# Print all relevant configuration
print('=' * 80)
print('FULL APPLICATION CONFIGURATION')
print('=' * 80)
print(json.dumps(app, indent=2))
