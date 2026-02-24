import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Attempting to get logs...\n')

# Try different log endpoints
endpoints = [
    f'{base}/applications/{uuid}/logs',
    f'{base}/applications/{uuid}/deployments',
    f'{base}/deployments/{uuid}',
]

for endpoint in endpoints:
    print(f'Trying: {endpoint}')
    try:
        r = requests.get(endpoint, headers=headers, timeout=10)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print(f'Response keys: {list(data.keys()) if isinstance(data, dict) else "list"}')
            print(f'Data: {str(data)[:500]}')
        print()
    except Exception as e:
        print(f'Error: {str(e)[:100]}\n')
