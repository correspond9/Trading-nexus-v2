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
print('REMOVING POST-DEPLOYMENT COMMAND FROM COOLIFY')
print('=' * 70)

# First, verify current state
print('\n[1] Current configuration:')
try:
    resp = requests.get(
        f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}',
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        app_data = resp.json()
        print(f'  Post-Deployment Command: {app_data.get("post_deployment_command", "NULL")}')
    else:
        print(f'  ✗ Error fetching config: {resp.status_code}')
except Exception as e:
    print(f'  ✗ Connection error: {str(e)}')

# Remove the post-deployment command
print('\n[2] Removing post-deployment command...')
try:
    payload = {
        'post_deployment_command': None,  # Set to null to remove
        'post_deployment_command_container': None
    }
    
    resp = requests.put(
        f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}',
        headers=headers,
        json=payload,
        timeout=10
    )
    
    if resp.status_code in [200, 201]:
        print(f'✓ Post-deployment command removed successfully')
        print(f'  Status: {resp.status_code}')
    else:
        print(f'✗ Error: {resp.status_code}')
        print(f'  Response: {resp.text[:300]}')
        
except Exception as e:
    print(f'✗ Connection error: {str(e)}')

# Verify removal
print('\n[3] Verification:')
try:
    resp = requests.get(
        f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}',
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        app_data = resp.json()
        post_cmd = app_data.get('post_deployment_command')
        if post_cmd is None:
            print(f'✓ CONFIRMED: Post-deployment command is now NULL')
        else:
            print(f'⚠️  Still present: {post_cmd}')
    else:
        print(f'✗ Error verifying: {resp.status_code}')
except Exception as e:
    print(f'✗ Connection error: {str(e)}')

print('\n' + '=' * 70)
