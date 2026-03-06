import requests
import json

api_token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
headers = {'Authorization': f'Bearer {api_token}'}
base_url = 'http://72.62.228.112:8000/api/v1'

print('=== CHECKING DOCKER CONTAINER DETAILS ===\n')

# First get all services to find container names
try:
    r = requests.get(f'{base_url}/services', headers=headers, timeout=10)
    if r.status_code == 200:
        services = r.json()
        if isinstance(services, list):
            print(f'Found {len(services)} services:')
            for svc in services[:15]:
                print(f"\nService: {svc.get('name')}")
                print(f"  Type: {svc.get('type')}")
                print(f"  Status: {svc.get('status')}")
                print(f"  Updated: {svc.get('updated_at')}")
        else:
            print('Services:', json.dumps(services, indent=2)[:2000])
    else:
        print(f'Error {r.status_code}: {r.text[:300]}')
except Exception as e:
    print(f'Error getting services: {e}')

print('\n=== CHECKING FOR DATA SYNC/MIGRATION PROCESSES ===\n')

# Look for any webhooks or background jobs
try:
    r = requests.get(f'{base_url}/webhooks', headers=headers, timeout=10)
    if r.status_code == 200:
        webhooks = r.json()
        if isinstance(webhooks, list) and len(webhooks) > 0:
            print(f'Found {len(webhooks)} webhooks (could trigger background jobs)')
            for wh in webhooks[:5]:
                print(f"  - {wh.get('event')}: {wh.get('url')}")
        else:
            print('No webhooks or error response')
    else:
        print(f'Webhooks check returned {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

# Check if there's a database that might be indexing
print('\n=== CHECKING DATABASE CONFIG ===\n')
try:
    r = requests.get(f'{base_url}/databases', headers=headers, timeout=10)
    if r.status_code == 200:
        dbs = r.json()
        if isinstance(dbs, list):
            print(f'Databases: {len(dbs)} found')
            for db in dbs[:10]:
                print(f"\n  Database: {db.get('name')}")
                print(f"    Type: {db.get('type')}")
                print(f"    Status: {db.get('status')}")
                print(f"    Updated: {db.get('updated_at')}")
        else:
            print('Databases:', json.dumps(dbs, indent=2)[:1000])
    else:
        print(f'Error {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

# Check environment variables for background job configs
print('\n=== CHECKING ENV VARIABLES FOR PROCESS CONFIGS ===\n')
try:
    r = requests.get(f'{base_url}/applications', headers=headers, timeout=10)
    if r.status_code == 200:
        apps = r.json()
        if isinstance(apps, list) and len(apps) > 0:
            app = apps[0]
            app_id = app.get('id')
            
            # Get environment variables
            r2 = requests.get(f'{base_url}/applications/{app_id}', headers=headers, timeout=10)
            if r2.status_code == 200:
                app_details = r2.json()
                env_vars = app_details.get('environment_variables', [])
                
                suspicious_keys = ['WORKER', 'CELERY', 'QUEUE', 'CONCURRENCY', 'PROCESS', 'POOL', 'THREAD', 'DEBUG', 'LOG_LEVEL']
                print(f'Environment variables related to background processing:')
                found = False
                for var in env_vars:
                    key = str(var.get('key', '')).upper()
                    if any(x in key for x in suspicious_keys):
                        print(f"  • {var.get('key')} = {var.get('value')[:100]}")
                        found = True
                        
                if not found:
                    print('  (None found with suspicious names)')
except Exception as e:
    print(f'Error: {e}')
