import requests
import json

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
headers = {'Authorization': f'Bearer {token}'}
url = 'http://72.62.228.112:8000/api/v1/applications/zccs8wko40occg44888kwooc'

resp = requests.get(url, headers=headers, timeout=5)
print(f'Status Code: {resp.status_code}')

data = resp.json()
print('Response keys:', list(data.keys()))

if 'data' in data:
    app = data['data']
    print(f"\nStatus: {app.get('status', 'N/A')}")
    print(f"Online: {app.get('is_online', 'N/A')}")
    print(f"Last online: {app.get('last_online_at', 'N/A')}")
else:
    print(json.dumps(data, indent=2)[:1000])
