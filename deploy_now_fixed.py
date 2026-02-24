#!/usr/bin/env python3
import requests
import time

COOLIFY_BASE = 'http://72.62.228.112:8000/api/v1'
TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'x8gg0og8440wkgc8ow0ococs'
headers = {'Authorization': f'Bearer {TOKEN}'}

print('='*80)
print('TRADING NEXUS - COOLIFY DEPLOYMENT')
print('='*80)
print()
print(f'Coolify: http://72.62.228.112:8000')
print(f'Project: My first project')
print(f'Application UUID: {APP_UUID}')
print()

# Step 1: Check current status
print('[Step 1/3] Checking current application status...')
try:
    r = requests.get(f'{COOLIFY_BASE}/applications/{APP_UUID}', headers=headers, timeout=10)
    r.raise_for_status()
    app_data = r.json().get('data', r.json())
    current_status = app_data.get('status', 'unknown')
    print(f'  Current status: {current_status}')
except Exception as e:
    print(f'  Status check failed: {e}')
    current_status = 'unknown'

print()

# Step 2: Trigger deployment
print('[Step 2/3] Triggering deployment...')
try:
    r = requests.post(f'{COOLIFY_BASE}/applications/{APP_UUID}/restart', headers=headers, timeout=10)
    if r.status_code == 200:
        print(f'  Deployment triggered successfully')
    else:
        print(f'  WARNING: Status {r.status_code}')
except Exception as e:
    print(f'  ERROR: {e}')
    exit(1)

print()

# Step 3: Monitor deployment
print('[Step 3/3] Monitoring deployment (max 30 minutes)...')
print()

start_time = time.time()
last_status = None

for i in range(180):
    try:
        r = requests.get(f'{COOLIFY_BASE}/applications/{APP_UUID}', headers=headers, timeout=10)
        r.raise_for_status()
        app_data = r.json().get('data', r.json())
        status = app_data.get('status', 'unknown')
        is_online = app_data.get('is_online', False)
        
        elapsed = int(time.time() - start_time)
        if i % 2 == 0 or status != last_status:
            print(f'  [{elapsed:>4}s] Status: {status:18} | Online: {str(is_online):5}')
            last_status = status
        
        # Success!
        if status.lower() == 'running' and is_online:
            print()
            print('='*80)
            print('SUCCESS! DEPLOYMENT COMPLETE')
            print('='*80)
            print()
            print('Application is now RUNNING')
            print()
            print('Next validation steps:')
            print('  1. Test health endpoint:')
            print('     curl http://72.62.228.112:8000/health')
            print()
            print('  2. Check database migrations:')
            print('     Migration 025: Brokerage plans (ON CONFLICT - safe)')
            print('     Migration 024: DISABLED (.disabled extension)')
            print()
            print('  3. Access Coolify Dashboard:')
            print('     http://72.62.228.112:8000')
            print()
            exit(0)
        
        # Failure
        if any(x in status.lower() for x in ['error', 'exited', 'failed']):
            print()
            print('='*80)
            print(f'DEPLOYMENT FAILED - Status: {status}')
            print('='*80)
            exit(1)
            
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f'  [{elapsed:>4}s] Check error: {str(e)[:50]}')
    
    time.sleep(10)

print()
print('Monitoring completed.')
print('Check Coolify dashboard: http://72.62.228.112:8000')
