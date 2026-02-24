#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112:8000/api/v1"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

resource_uuid = "zccs8wko40occg44888kwooc"

print("Investigating Coolify API paths for resource management...")
print(f"Resource UUID: {resource_uuid}\n")

# Try different endpoint patterns
endpoints = [
    f"/resources/{resource_uuid}",
    f"/resources/{resource_uuid}/configuration",
    f"/applications/{resource_uuid}",
    f"/applications/{resource_uuid}/configuration",
    f"/services/{resource_uuid}",
]

for endpoint in endpoints:
    try:
        url = base_url + endpoint
        response = requests.get(url, headers=headers, timeout=5)
        print(f"GET {endpoint}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ SUCCESS!")
            print(f"  Response keys: {list(data.keys())[:10]}")
            print(f"  Full response (first 500 chars):")
            print(f"  {json.dumps(data, indent=2)[:500]}")
        elif response.status_code == 404:
            print(f"  ✗ Not found")
        else:
            print(f"  Response: {response.text[:100]}")
        print()
        
    except Exception as e:
        print(f"GET {endpoint}")
        print(f"  Error: {str(e)[:50]}\n")

# Also check if we need to use the project/environment path
print("\n" + "="*70)
print("Getting project/environment info to construct correct paths...")

try:
    projects_response = requests.get(f"{base_url}/projects", headers=headers, timeout=5)
    projects = projects_response.json()
    
    for project in projects:
        if project['name'] == 'trade-nexuss':
            project_uuid = project['uuid']
            print(f"\nProject: {project['name']}")
            print(f"  UUID: {project_uuid}")
            
            # Get environments
            for env in project.get('environments', []):
                env_uuid = env['uuid']
                env_name = env['name']
                print(f"  Environment: {env_name}")
                print(f"    UUID: {env_uuid}")
                
                # Try to list applications in this environment
                app_endpoints = [
                    f"/projects/{project_uuid}/environments/{env_uuid}/applications",
                    f"/projects/{project_uuid}/environments/{env_uuid}/resources",
                ]
                
                for ep in app_endpoints:
                    try:
                        app_response = requests.get(base_url + ep, headers=headers, timeout=5)
                        if app_response.status_code == 200:
                            apps = app_response.json()
                            print(f"    Endpoint: {ep}")
                            print(f"      Found {len(apps) if isinstance(apps, list) else 1} applications")
                            if isinstance(apps, list):
                                for app in apps[:2]:
                                    print(f"        - {app.get('name')} (UUID: {app.get('uuid')})")
                    except:
                        pass
                        
except Exception as e:
    print(f"Error: {e}")
