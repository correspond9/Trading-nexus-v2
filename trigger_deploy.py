import requests

headers = {'Authorization': 'Bearer 2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7', 'Content-Type': 'application/json'}
apps = requests.get('http://72.62.228.112/api/v1/applications', headers=headers).json()

print("Available apps:")
for app in apps:
    print(f"  - {app.get('name','?')} | {app.get('uuid','?')}")

for app in apps:
    name = str(app.get('name', '')).lower()
    if 'frontend' in name:
        uid = app.get('uuid', '')
        r = requests.post(f'http://72.62.228.112/api/v1/applications/{uid}/start', headers=headers)
        print(f"\nTriggered deploy for {app.get('name', uid)}: HTTP {r.status_code}")
        print(r.text[:200])
        break
