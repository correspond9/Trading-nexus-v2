import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
url = 'http://72.62.228.112:8000/api/v1/applications/zccs8wko40occg44888kwooc'
headers = {'Authorization': f'Bearer {token}'}

r = requests.get(url, headers=headers)
app = r.json()

print('=' * 70)
print('DEPLOYMENT STATUS SUMMARY')
print('=' * 70)
print(f"Status:       {app.get('status', 'unknown')}")
print(f"Online:       {app.get('is_online', 'unknown')}")  
print(f"Last Online:  {app.get('last_online_at', 'never')}")
print(f"Server:       {app.get('server_status', 'unknown')}")
print('=' * 70)

status = str(app.get('status', ''))
if 'running' in status.lower():
    print('✅ Application is RUNNING')
    print()
    print('Next Steps:')
    print('1. API accessible at: http://72.62.228.112/api/v2/')
    print('2. Dashboard at: http://72.62.228.112:8000/')
    print('3. Check logs in Coolify if endpoints still return 404')
else:
    print(f'⚠️  Status: {status}')
