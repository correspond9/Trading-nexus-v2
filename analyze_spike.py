import requests
import json
import subprocess

api_token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
headers = {'Authorization': f'Bearer {api_token}'}
base_url = 'http://72.62.228.112:8000/api/v1'

print('=== ANALYZING RESOURCE SPIKE CAUSE ===\n')

# First, check what git commits happened around the spike time
print('1. CHECKING GIT HISTORY FOR CHANGES AROUND SPIKE TIME...')
try:
    result = subprocess.run(['git', 'log', '--oneline', '--all', '-20'], 
                          capture_output=True, text=True, cwd='.')
    print('Recent commits:')
    print(result.stdout)
except Exception as e:
    print(f'Could not get git log: {e}')

# Check deployment history
print('\n2. CHECKING DEPLOYMENT TIMESTAMPS...')
try:
    r = requests.get(f'{base_url}/deployments?limit=20', headers=headers, timeout=10)
    if r.status_code == 200:
        deps = r.json()
        if isinstance(deps, list):
            print(f'Recent deployments ({len(deps)} found):')
            for dep in deps[:10]:
                print(f"  - {dep.get('id')}: {dep.get('status')} | Created: {dep.get('created_at')} | Updated: {dep.get('updated_at')}")
        else:
            print(json.dumps(deps, indent=2)[:500])
    else:
        print(f'Error {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

# Get application details to see config
print('\n3. CHECKING APPLICATION CONFIGURATION...')
try:
    r = requests.get(f'{base_url}/applications', headers=headers, timeout=10)
    if r.status_code == 200:
        apps = r.json()
        if isinstance(apps, list) and len(apps) > 0:
            app = apps[0]
            print(f"App: {app.get('name')}")
            print(f"Status: {app.get('status')}")
            print(f"Ports: {app.get('ports')}")
            print(f"Docker Image: {app.get('image')}")
            print(f"Build Pack: {app.get('build_pack')}")
            print(f"Base Image: {app.get('base_image')}")
            
            # Check environment variables for resource-intensive operations
            env_vars = app.get('environment_variables', [])
            if env_vars:
                print(f"\nEnvironment variables ({len(env_vars)}): (showing key ones)")
                for var in env_vars:
                    key = str(var.get('key', '')).upper() 
                    if any(x in key for x in ['WORKER', 'THREAD', 'POOL', 'DEBUG', 'LOG', 'CACHE', 'BATCH']):
                        print(f"  - {var.get('key')}: {var.get('value')[:50]}")
except Exception as e:
    print(f'Error: {e}')

print('\n4. CHECKING FOR BACKGROUND JOBS OR PROCESSES IN LOGS...')
# Check the deployment logs for any background job starts
try:
    dep_uuid = 'jgwg88c000ckok8ggscc4c08'
    r = requests.get(f'{base_url}/deployments/{dep_uuid}', headers=headers, timeout=10)
    if r.status_code == 200:
        dep = r.json()
        logs = dep.get('logs', '')
        logs_str = json.dumps(logs) if isinstance(logs, list) else str(logs)
        
        # Look for keywords that might indicate resource-heavy operations
        keywords = ['worker', 'background', 'cron', 'schedule', 'batch', 'migration', 'indexing', 'cache', 'rebuild']
        print('Deployment log analysis:')
        for keyword in keywords:
            if keyword.lower() in logs_str.lower():
                print(f"  ✓ Found '{keyword}' - potential resource-intensive operation")
except Exception as e:
    print(f'Error: {e}')
