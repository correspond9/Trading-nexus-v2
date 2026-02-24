#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112:8000/api/v1"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("=" * 70)
print("COOLIFY INFRASTRUCTURE ANALYSIS")
print("=" * 70)

# Get projects
print("\n[1] PROJECTS:")
print("-" * 70)
try:
    response = requests.get(f"{base_url}/projects", headers=headers, timeout=5)
    projects = response.json()
    for project in projects:
        print(f"\nProject: {project['name']}")
        print(f"  UUID: {project['uuid']}")
        print(f"  ID: {project['id']}")
        print(f"  Description: {project['description']}")
        
        # Get environments for this project
        project_uuid = project['uuid']
        env_response = requests.get(f"{base_url}/projects/{project_uuid}/environments", headers=headers, timeout=5)
        environments = env_response.json()
        
        print(f"  Environments ({len(environments)}):")
        for env in environments:
            print(f"    - {env['name']} (UUID: {env['uuid']})")
            
            # Get resources for this environment
            env_uuid = env['uuid']
            res_response = requests.get(
                f"{base_url}/projects/{project_uuid}/environments/{env_uuid}/applications",
                headers=headers, timeout=5
            )
            try:
                resources = res_response.json()
                if isinstance(resources, list):
                    print(f"      Applications: {len(resources)}")
                    for res in resources[:3]:  # Show first 3
                        print(f"        * {res.get('name', 'Unknown')} (UUID: {res.get('uuid', 'N/A')})")
            except:
                pass
                
except Exception as e:
    print(f"Error: {e}")

# Get all resources
print("\n\n[2] ALL RESOURCES:")
print("-" * 70)
try:
    response = requests.get(f"{base_url}/resources", headers=headers, timeout=5)
    resources = response.json()
    for resource in resources:
        print(f"\nResource: {resource['name']}")
        print(f"  UUID: {resource['uuid']}")
        print(f"  Type: {resource.get('type', 'Unknown')}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("✓ Analysis complete. Use the UUIDs above for deployment configuration.")
print("=" * 70)
