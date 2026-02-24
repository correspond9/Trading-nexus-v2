#!/usr/bin/env python3
"""
Coolify API Client for Trading-Nexus V2 Deployment
"""
import requests
import json
import sys

COOLIFY_URL = "http://72.62.228.112"
API_TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
GIT_REPO = "https://github.com/correspond9/Trading-nexus-v2.git"
GIT_BRANCH = "main"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 60)
print("TRADING-NEXUS V2 - COOLIFY DEPLOYMENT")
print("=" * 60)
print()

# ============================================================
# STEP 1: Get all projects
# ============================================================
print("[STEP 1] Fetching Coolify Projects...")
print("-" * 60)
try:
    projects_response = requests.get(
        f'{COOLIFY_URL}/api/v1/projects',
        headers=headers,
        timeout=10
    )
    projects_response.raise_for_status()
    projects_data = projects_response.json()
    
    if 'projects' in projects_data:
        projects = projects_data['projects']
        print(f"✓ Found {len(projects)} projects:\n")
        for project in projects:
            print(f"  Name: {project.get('name', 'N/A')}")
            print(f"  ID:   {project.get('uuid', 'N/A')}")
            print()
    else:
        print(f"Response: {json.dumps(projects_data, indent=2)}")
        
except requests.exceptions.RequestException as e:
    print(f"✗ Failed to fetch projects: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Get all resources
# ============================================================
print("[STEP 2] Fetching Coolify Resources...")
print("-" * 60)
try:
    resources_response = requests.get(
        f'{COOLIFY_URL}/api/v1/resources',
        headers=headers,
        timeout=10
    )
    resources_response.raise_for_status()
    resources_data = resources_response.json()
    
    if 'resources' in resources_data:
        resources = resources_data['resources']
        print(f"✓ Found {len(resources)} resources:\n")
        for resource in resources:
            print(f"  Name: {resource.get('name', 'N/A')}")
            print(f"  ID:   {resource.get('uuid', 'N/A')}")
            print(f"  Type: {resource.get('type', 'N/A')}")
            print()
    else:
        print(f"Response: {json.dumps(resources_data, indent=2)}")
        
except requests.exceptions.RequestException as e:
    print(f"✗ Failed to fetch resources: {e}")
    sys.exit(1)

# ============================================================
# STEP 3: Get environments
# ============================================================
print("[STEP 3] Fetching Coolify Environments...")
print("-" * 60)
if projects:
    first_project = projects[0]
    project_id = first_project.get('uuid')
    
    try:
        envs_response = requests.get(
            f'{COOLIFY_URL}/api/v1/projects/{project_id}/environments',
            headers=headers,
            timeout=10
        )
        envs_response.raise_for_status()
        envs_data = envs_response.json()
        
        if 'environments' in envs_data:
            environments = envs_data['environments']
            print(f"✓ Found {len(environments)} environments in project '{first_project.get('name')}':\n")
            for env in environments:
                print(f"  Name: {env.get('name', 'N/A')}")
                print(f"  ID:   {env.get('uuid', 'N/A')}")
                print()
        else:
            print(f"Response: {json.dumps(envs_data, indent=2)}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to fetch environments: {e}")

print("\n" + "=" * 60)
print("✓ Coolify configuration retrieved successfully")
print("=" * 60)
