import requests
import json

api_token = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
headers = {'Authorization': f'Bearer {api_token}'}
base_url = 'http://72.62.228.112:8000/api/v1'

print('=== DETAILED APPLICATION ANALYSIS ===\n')

try:
    # Get all applications
    r = requests.get(f'{base_url}/applications', headers=headers, timeout=10)
    if r.status_code == 200:
        apps = r.json()
        if isinstance(apps, list) and len(apps) > 0:
            app = apps[0]
            app_id = app.get('id')
            
            print(f'Application: {app.get("name")}')
            print(f'ID: {app_id}')
            print(f'Status: {app.get("status")}')
            print(f'Updated: {app.get("updated_at")}')
            
            # Get detailed application config
            r2 = requests.get(f'{base_url}/applications/{app_id}', headers=headers, timeout=10)
            if r2.status_code == 200:
                app_details = r2.json()
                
                print(f'\n--- CONFIGURATION ---')
                print(f'Build Pack: {app_details.get("build_pack")}')
                print(f'Repository: {app_details.get("repository_url")}')
                print(f'Branch: {app_details.get("git_branch")}')
                
                # Check custom start command
                if app_details.get('custom_start_command'):
                    print(f'Custom Start Command: {app_details.get("custom_start_command")}')
                
                # Check for docker compose details
                if app_details.get('docker_compose_file'):
                    print(f'Docker Compose File: {app_details.get("docker_compose_file")[:200]}...')
                
                # Get environment variables - these might show what's running
                env_vars = app_details.get('environment_variables', [])
                if env_vars:
                    print(f'\n--- ENVIRONMENT VARIABLES ({len(env_vars)} total) ---')
                    # Show all of them to understand the setup
                    for var in env_vars:
                        key = var.get('key', '')
                        val = str(var.get('value', ''))[:80]
                        print(f'{key}: {val}')
                else:
                    print('No environment variables set')
                
                # Check container details
                print(f'\n--- DOCKER DETAILS ---')
                print(f'Image: {app_details.get("image")}')
                print(f'Container Image: {app_details.get("docker_image_custom_start_cmd")}')
                
except Exception as e:
    print(f'Error: {e}')

# Now check what the actual deployment log says about what started
print('\n=== DEPLOYMENT LOG ANALYSIS ===\n')
try:
    dep_uuid = 'jgwg88c000ckok8ggscc4c08'
    r = requests.get(f'{base_url}/deployments/{dep_uuid}', headers=headers, timeout=10)
    if r.status_code == 200:
        dep = r.json()
        logs = dep.get('logs', [])
        
        print(f'Deployment Status: {dep.get("status")}')
        print(f'Created: {dep.get("created_at")} (UTC - 5:30 for IST)')
        print(f'Updated: {dep.get("updated_at")}')
        print(f'\nLast 50 log entries:\n')
        
        if isinstance(logs, list):
            for log_entry in logs[-50:]:
                if isinstance(log_entry, dict):
                    output = log_entry.get('output', '')[:120]
                    ts = log_entry.get('timestamp', '')
                    print(f'[{ts}] {output}')
                else:
                    print(f'{str(log_entry)[:120]}')
        else:
            # If it's a JSON string
            try:
                log_list = json.loads(str(logs))
                for entry in log_list[-50:]:
                    print(entry)
            except:
                print(str(logs)[-2000:])
except Exception as e:
    print(f'Error: {e}')
