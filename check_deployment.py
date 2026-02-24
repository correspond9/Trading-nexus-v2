import requests

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
uuid = 'p488ok8g8swo4ockks040ccg'
base = 'http://72.62.228.112:8000/api/v1'
headers = {'Authorization': f'Bearer {token}'}

print('Checking deployed state...')
r = requests.get(f'{base}/applications/{uuid}', headers=headers)
data = r.json()

if isinstance(data, list):
    app = data[0]
else:
    app = data.get('data', data)

print(f'\nGit Commit: {app.get("git_commit_sha", "N/A")}')
print(f'Expected: 5d4c701')
print(f'Match: {"5d4c701" in app.get("git_commit_sha", "")}')

print(f'\nDocker Compose Location: {app.get("docker_compose_location")}')
print(f'Status: {app.get("status")}')
