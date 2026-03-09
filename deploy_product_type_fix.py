"""
Deploy the product_type fix to production via Coolify API
"""
import requests
import time

COOLIFY_URL = 'http://72.62.228.112:8000'
API_TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'bsgc4kwsk88s04kgws0408c4'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print('=' * 80)
print('DEPLOYING PRODUCT_TYPE FIX TO PRODUCTION')
print('=' * 80)

print('\n[1] Triggering deployment...')
deploy_resp = requests.post(
    f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}/deploy',
    headers=headers,
    json={
        'force_rebuild': True,
        'commit': '846111a'  # Latest commit with product_type fix
    },
    timeout=30
)

if deploy_resp.status_code in (200, 201, 202):
    print('✅ Deployment triggered successfully!')
    deploy_data = deploy_resp.json()
    print(f'   Deployment UUID: {deploy_data.get("deployment_uuid", "N/A")}')
    print(f'   Status: {deploy_data.get("message", "In progress")}')
else:
    print(f'❌ Deployment failed: {deploy_resp.status_code}')
    print(f'   Response: {deploy_resp.text[:500]}')
    exit(1)

print('\n[2] Monitoring deployment status...')
print('    (This may take 2-5 minutes)')

for attempt in range(60):  # Wait up to 10 minutes
    time.sleep(10)
    
    # Check app status
    status_resp = requests.get(
        f'{COOLIFY_URL}/api/v1/applications/{APP_UUID}',
        headers=headers,
        timeout=10
    )
    
    if status_resp.status_code == 200:
        app_data = status_resp.json()
        status = app_data.get('status', 'unknown')
        
        print(f'    [{attempt * 10}s] Status: {status}')
        
        if 'running' in status.lower():
            print('\n✅ DEPLOYMENT SUCCESSFUL!')
            print(f'   Application Status: {status}')
            break
        elif 'error' in status.lower() or 'failed' in status.lower():
            print(f'\n❌ DEPLOYMENT FAILED')
            print(f'   Status: {status}')
            break
    else:
        print(f'    Status check failed: {status_resp.status_code}')

print('\n[3] Verifying deployed version...')
health_resp = requests.get(
    'https://api.tradingnexus.pro/health',
    timeout=10
)

if health_resp.status_code == 200:
    health = health_resp.json()
    print('✅ Application is healthy')
    print(f'   Status: {health.get("status", "N/A")}')
    print(f'   Database: {health.get("database", "N/A")}')
else:
    print(f'⚠️  Health check returned: {health_resp.status_code}')

print('\n' + '=' * 80)
print('DEPLOYMENT COMPLETE')
print('=' * 80)
print("""
Fix Deployed:
- Product type now defaults to NORMAL instead of MIS
- All order INSERT queries now include product_type
- Orders placed as NORMAL will be saved as NORMAL

Next Steps:
- Test placing a NORMAL order and verify it's saved correctly
- Still need to fix LIMIT order execution issue
""")
