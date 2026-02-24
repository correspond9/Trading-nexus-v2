import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
project_uuid = 'mkwg4osgoo880k4ogswgw08o'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Listing applications in project...')
r = requests.get(f'{base}/projects/{project_uuid}/applications', headers=headers, timeout=10)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    apps = data.get('data', data) if isinstance(data, dict) else data
    if isinstance(apps, list):
        print(f'Found {len(apps)} applications')
        for app in apps:
            print(f'  - {app.get("name")} ({app.get("uuid")})')
    else:
        print(f'Response: {data}')
else:
    print(f'Error: {r.text}')
