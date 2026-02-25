#!/usr/bin/env python3
"""Get backend container logs via Coolify API"""
import requests

api_url = 'http://72.62.228.112:8000/api/v1'
token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
uuid = 'x8gg0og8440wkgc8ow0ococs'
headers = {'Authorization': f'Bearer {token}'}

print('Fetching backend container logs...')
print()

try:
    # First, get application details to find container name
    resp = requests.get(f'{api_url}/applications/{uuid}', headers=headers, timeout=10)
    app = resp.json()
    if isinstance(app, list):
        app = app[0]
    
    container_name = app.get('docker_compose', '').split('container_name: backend-')[1].split('\n')[0].strip() if 'container_name: backend-' in app.get('docker_compose', '') else None
    
    if container_name:
        print(f'Container: {container_name}')
    print()
    
    # Try to get logs
    log_resp = requests.get(
        f'{api_url}/applications/{uuid}/logs',
        headers=headers,
        timeout=20
    )
    
    if log_resp.status_code == 200:
        logs = log_resp.text
        # Filter for recent errors
        lines = logs.split('\n')
        error_lines = [l for l in lines[-200:] if 'error' in l.lower() or 'exception' in l.lower() or 'failed' in l.lower() or '500' in l or '422' in l]
        
        if error_lines:
            print('Recent errors from logs:')
            print('-' * 70)
            for line in error_lines[-20:]:
                print(line)
        else:
            print('No obvious errors found in recent logs.')
            print('Last 10 log lines:')
            print('-' * 70)
            for line in lines[-10:]:
                print(line)
    else:
        print(f'Could not fetch logs: {log_resp.status_code}')
        print(f'Response: {log_resp.text[:500]}')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
