import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
headers = {'Authorization': f'Bearer {token}'}
url = 'http://72.62.228.112:8000/api/v1/applications/zccs8wko40occg44888kwooc'

resp = requests.get(url, headers=headers, timeout=5)
app = resp.json()

print(f"Status: {app.get('status', 'N/A')}")
print(f"Online: {app.get('is_online', 'N/A')}")
print(f"Last online: {app.get('last_online_at', 'N/A')}")
print(f"Restart count: {app.get('restart_count', 'N/A')}")
print(f"Server status: {app.get('server_status', 'N/A')}")
