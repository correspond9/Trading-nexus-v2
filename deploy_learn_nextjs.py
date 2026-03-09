#!/usr/bin/env python3
"""
Deploy learn-trading-nexus to Coolify as a new resource
"""
import requests
import json
import sys
import time

COOLIFY_URL = "http://72.62.228.112:8000"
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 70)
print("DEPLOYING learn-trading-nexus TO COOLIFY")
print("=" * 70)
print()

# ============================================================
# STEP 1: Get all projects to find "My first project"
# ============================================================
print("[STEP 1] Finding 'My first project'...")
print("-" * 70)
try:
    projects_response = requests.get(
        f'{COOLIFY_URL}/api/v1/projects',
        headers=headers,
        timeout=10
    )
    projects_response.raise_for_status()
    projects_data = projects_response.json()
    
    # Handle both list and dict responses
    if isinstance(projects_data, list):
        projects = projects_data
    else:
        projects = projects_data.get('projects', [])
    
    print(f"✓ Found {len(projects)} project(s)")
    
    # Find "My first project"
    target_project = None
    for project in projects:
        print(f"  - {project.get('name')} (UUID: {project.get('uuid')})")
        if project.get('name') == 'My first project':
            target_project = project
    
    if not target_project:
        print("\n✗ ERROR: 'My first project' not found!")
        print("Available projects:", [p.get('name') for p in projects])
        sys.exit(1)
    
    project_uuid = target_project.get('uuid')
    print(f"\n✓ Target project found: {target_project.get('name')}")
    print(f"  UUID: {project_uuid}")
    
except requests.exceptions.RequestException as e:
    print(f"✗ Failed to fetch projects: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Get environments in the project
# ============================================================
print("\n[STEP 2] Finding 'production' environment...")
print("-" * 70)
try:
    envs_response = requests.get(
        f'{COOLIFY_URL}/api/v1/projects/{project_uuid}/environments',
        headers=headers,
        timeout=10
    )
    envs_response.raise_for_status()
    envs_data = envs_response.json()
    
    # Handle both list and dict responses
    if isinstance(envs_data, list):
        environments = envs_data
    else:
        environments = envs_data.get('environments', [])
    
    print(f"✓ Found {len(environments)} environment(s)")
    
    target_env = None
    for env in environments:
        print(f"  - {env.get('name')} (UUID: {env.get('uuid')})")
        if env.get('name') == 'production':
            target_env = env
    
    if not target_env:
        print("\n✗ ERROR: 'production' environment not found!")
        print("Available environments:", [e.get('name') for e in environments])
        sys.exit(1)
    
    env_uuid = target_env.get('uuid')
    print(f"\n✓ Target environment found: {target_env.get('name')}")
    print(f"  UUID: {env_uuid}")
    
except requests.exceptions.RequestException as e:
    print(f"✗ Failed to fetch environments: {e}")
    sys.exit(1)

# ============================================================
# STEP 3: Get servers in the environment
# ============================================================
print("\n[STEP 3] Finding available servers...")
print("-" * 70)
try:
    servers_response = requests.get(
        f'{COOLIFY_URL}/api/v1/servers',
        headers=headers,
        timeout=10
    )
    servers_response.raise_for_status()
    servers_data = servers_response.json()
    
    # Handle both list and dict responses
    if isinstance(servers_data, list):
        servers = servers_data
    else:
        servers = servers_data.get('servers', [])
    
    print(f"✓ Found {len(servers)} server(s)")
    
    if not servers:
        print("✗ No servers available!")
        sys.exit(1)
    
    # Use the first server (localhost)
    target_server = servers[0]
    server_uuid = target_server.get('uuid')
    
    for server in servers:
        print(f"  - {server.get('name')} (UUID: {server.get('uuid')})")
        if server.get('name') == 'localhost':
            target_server = server
            server_uuid = server.get('uuid')
    
    print(f"\n✓ Target server: {target_server.get('name')}")
    print(f"  UUID: {server_uuid}")
    
except requests.exceptions.RequestException as e:
    print(f"✗ Failed to fetch servers: {e}")
    sys.exit(1)

# ============================================================
# STEP 4: Create Application Resource
# ============================================================
print("\n[STEP 4] Creating application resource...")
print("-" * 70)
try:
    # Create the application
    app_payload = {
        "name": "learn-trading-nexus",
        "description": "Trading Nexus Learn Platform - Next.js Frontend",
        "type": "docker-compose",
        "docker_compose_raw": """
version: '3'
services:
  learn-app:
    image: learn-trading-nexus:latest
    container_name: learn-trading-nexus
    restart: always
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=https://tradingnexus.pro/api/v2
      - NEXT_PUBLIC_PORTAL_API_TOKEN=portal-signups-token
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
networks:
  default:
    external: true
    name: traefik
""",
        "environment_id": env_uuid,
        "server_id": server_uuid,
        "build_pack": "dockerfile",
        "ports_exposes": "3000",
        "ports_mappings": "3001:3000"
    }
    
    # First, let's try to create an application via docker-compose endpoint
    create_response = requests.post(
        f'{COOLIFY_URL}/api/v1/projects/{project_uuid}/environments/{env_uuid}/applications',
        headers=headers,
        json=app_payload,
        timeout=30
    )
    
    print(f"Response Status: {create_response.status_code}")
    response_data = create_response.json()
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if create_response.status_code in [200, 201]:
        print("✓ Application resource created successfully!")
        if 'uuid' in response_data:
            app_uuid = response_data['uuid']
            print(f"  Application UUID: {app_uuid}")
    else:
        print(f"✗ Failed to create application: {create_response.status_code}")
        if 'message' in response_data:
            print(f"  Message: {response_data['message']}")
        if 'error' in response_data:
            print(f"  Error: {response_data['error']}")

except requests.exceptions.RequestException as e:
    print(f"✗ Failed to create application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================
# STEP 5: Configure domain
# ============================================================
print("\n[STEP 5] Configuring domain...")
print("-" * 70)
print("Note: You need to configure the domain 'learn.tradingnexus.pro' in Coolify UI")
print("  - Go to the new application resource")
print("  - Add domain: learn.tradingnexus.pro")
print("  - Make sure SSL/TLS is enabled")
print("  - Save the configuration")

print("\n" + "=" * 70)
print("DEPLOYMENT CONFIGURATION COMPLETE")
print("=" * 70)
print("\nNext Steps:")
print("1. The new 'learn-trading-nexus' resource has been created")
print("2. Configure the domain in Coolify UI (learn.tradingnexus.pro)")
print("3. Build and deploy the application")
print("4. Verify the application is running at https://learn.tradingnexus.pro")
print()
