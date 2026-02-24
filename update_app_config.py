import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print('Updating application configuration...\n')

# Update exposed port and domain
update_data = {
    'ports_exposes': '8000',  # Backend port
    'fqdn': 'api.tradingnexus.pro',  # Domain
}

print(f'Sending update: {update_data}')
r = requests.patch(f'{base}/applications/{uuid}', headers=headers, json=update_data, timeout=10)
print(f'Status: {r.status_code}')
print(f'Response: {r.text}')

if r.status_code in [200, 201]:
    print('\n✅ Configuration updated successfully!')
    print('\nVerifying...')
    r2 = requests.get(f'{base}/applications/{uuid}', headers=headers)
    data = r2.json()
    if isinstance(data, list):
        app = data[0]
    else:
        app = data.get('data', data)
    
    print(f'ports_exposes: {app.get("ports_exposes")}')
    print(f'fqdn: {app.get("fqdn")}')
else:
    print('\n❌ Update failed')
