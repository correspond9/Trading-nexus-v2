import requests
import json
import time

COOLIFY_URL = 'http://72.62.228.112:8000'
API_TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'x8gg0og8440wkgc8ow0ococs'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print('=' * 70)
print('TRIGGERING CLEAN DEPLOYMENT VIA COOLIFY')
print('=' * 70)

print('\n[1] Requesting new deployment...')
try:
    resp = requests.post(
        f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}/deployments',
        headers=headers,
        json={},
        timeout=15
    )
    
    if resp.status_code in [200, 201, 202]:
        data = resp.json()
        deployment_uuid = data.get('uuid') or data.get('deployment_uuid')
        print(f'✓ Deployment triggered: {deployment_uuid}')
        
        # Monitor deployment
        print('\n[2] Monitoring deployment status...')
        for i in range(30):
            time.sleep(2)
            try:
                check_resp = requests.get(
                    f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}/deployments?limit=1',
                    headers=headers,
                    timeout=10
                )
                if check_resp.status_code == 200:
                    deployments = check_resp.json()
                    if deployments and len(deployments) > 0:
                        status = deployments[0].get('status', 'unknown')
                        print(f'  [{i+1}/30] Status: {status}')
                        
                        if status in ['finished', 'failed']:
                            if status == 'finished':
                                print(f'\n✓ DEPLOYMENT COMPLETE: Application cleaned and redeployed')
                            else:
                                print(f'\n✗ DEPLOYMENT FAILED: Check Coolify logs')
                            break
            except:
                pass
        
    else:
        print(f'✗ Error: {resp.status_code}')
        print(f'  Response: {resp.text[:300]}')
        
except Exception as e:
    print(f'✗ Connection error: {str(e)}')

print('\n' + '=' * 70)
print('Verification: Run script_verify_scripts_removed.py to confirm')
print('=' * 70)
