#!/usr/bin/env python3
"""Check deployment status and Git commit"""
import requests
import json

api_url = 'http://72.62.228.112:8000/api/v1'
token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
uuid = 'x8gg0og8440wkgc8ow0ococs'
headers = {'Authorization': f'Bearer {token}'}

print('='*70)
print('CHECKING DEPLOYMENT STATUS')
print('='*70)
print()

print('1. Application Details:')
resp = requests.get(f'{api_url}/applications/{uuid}', headers=headers, timeout=10)
data = resp.json()
app = data[0] if isinstance(data, list) else data

print(f'   Status: {app.get("status")}')
print(f'   Git Branch: {app.get("git_branch")}')
print(f'   Git Commit: {app.get("git_commit_sha")}')
print(f'   Build Pack: {app.get("build_pack")}')
print(f'   Docker Compose Location: {app.get("docker_compose_location")}')
print(f'   Last Online: {app.get("last_online_at")}')
print()

# Get docker compose to check image tags
print('2. Docker Images in Use:')
docker_compose = app.get('docker_compose', '')
if 'image:' in docker_compose:
    lines = docker_compose.split('\n')
    for line in lines:
        if 'image:' in line and 'backend' in line:
            print(f'   Backend: {line.strip()}')
        elif 'image:' in line and 'frontend' in line:
            print(f'   Frontend: {line.strip()}')
print()

print('3. Expected Git Commit:')
print('   Latest push: ade642e (Fix critical bugs)')
print()

match = 'ade642e' in str(app.get("git_commit_sha", ""))
if match:
    print('   ✓ Deployment is using the latest code!')
else:
    print('   ✗ Deployment is NOT using the latest code!')
    print('   Need to trigger a fresh rebuild without cache.')

print()
print('='*70)
