import requests
import json

COOLIFY_URL = 'http://72.62.228.112:8000'
API_TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'x8gg0og8440wkgc8ow0ococs'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print('=' * 70)
print('COOLIFY API VERIFICATION - LIVE VPS CONFIGURATION')
print('=' * 70)

print('\n[1] Fetching live application configuration...')
try:
    resp = requests.get(
        f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}',
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        app_data = resp.json()
        
        print(f'✓ API Connection: SUCCESS')
        print(f'  Application Name: {app_data.get("name", "N/A")}')
        print(f'  Application UUID: {app_data.get("uuid", "N/A")}')
        print(f'  Status: {app_data.get("status", "N/A")}')
        
        print(f'\n  Pre-Deployment Command: {app_data.get("pre_deployment_command", "NULL")}')
        print(f'  Post-Deployment Command: {app_data.get("post_deployment_command", "NULL")}')
        print(f'  Pre-Deployment Container: {app_data.get("pre_deployment_command_container", "NULL")}')
        print(f'  Post-Deployment Container: {app_data.get("post_deployment_command_container", "NULL")}')
        
        if app_data.get('post_deployment_command') or app_data.get('pre_deployment_command'):
            print('\n  ⚠️  CUSTOM DEPLOYMENT COMMANDS DETECTED!')
        else:
            print('\n  ✓ NO CUSTOM PRE/POST DEPLOYMENT COMMANDS CONFIGURED')
            
    else:
        print(f'✗ API Error: {resp.status_code}')
        print(f'  Response: {resp.text[:200]}')
except Exception as e:
    print(f'✗ Connection Error: {str(e)}')

print('\n' + '=' * 70)
print('VERIFICATION COMPLETE')
print('=' * 70)
