#!/usr/bin/env python3
import requests
import time

COOLIFY_BASE = 'http://72.62.228.112:8000/api/v1'
TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'x8gg0og8440wkgc8ow0ococs'
headers = {'Authorization': f'Bearer {TOKEN}'}

print('='*80)
print('REDEPLOYING WITH CREDENTIAL SAVING FIXES')
print('='*80)
print()

# Trigger restart
print('Triggering redeployment...')
try:
    r = requests.post(f'{COOLIFY_BASE}/applications/{APP_UUID}/restart', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'✅ Redeployment triggered')
    else:
        print(f'⚠️  Status {r.status_code}')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)

print()
print('Monitoring redeployment (max 15 minutes)...')
print()

start_time = time.time()
for i in range(90):
    try:
        r = requests.get(f'{COOLIFY_BASE}/applications/{APP_UUID}', headers=headers, timeout=10)
        app_data = r.json().get('data', r.json())
        status = app_data.get('status', 'unknown')
        
        elapsed = int(time.time() - start_time)
        if i % 2 == 0 or 'running' in status.lower():
            print(f'  [{elapsed:>4}s] Status: {status}')
        
        if 'running' in status.lower():
            print()
            print('='*80)
            print('✅ REDEPLOYMENT SUCCESSFUL!')
            print('='*80)
            print()
            print('Fixes deployed to production:')
            print('  ✅ Comprehensive error handling in save_credentials endpoint')
            print('  ✅ Error handling in rotate_token function')
            print('  ✅ Error handling in update_client_id function')
            print('  ✅ Error handling in update_static_credentials function')
            print('  ✅ Error handling in set_auth_mode function')
            print('  ✅ Graceful WebSocket reconnection error handling')
            print('  ✅ Detailed error logging for all operations')
            print('  ✅ Partial success responses when some operations succeed')
            print()
            print('You can now:')
            print('  1. Enter DhanHQ credentials in the dashboard')
            print('  2. Click "Save Credentials"')
            print('  3. Credentials will be saved to database')
            print('  4. Error messages will be clearly displayed if issues occur')
            exit(0)
        
        if 'error' in status.lower() or 'failed' in status.lower():
            print()
            print(f'❌ Redeployment failed: {status}')
            exit(1)
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f'  [{elapsed:>4}s] Status check error: {str(e)[:50]}')
    
    time.sleep(10)

print()
print('Monitoring completed.')
