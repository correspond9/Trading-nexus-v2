#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112:8000/api/v1"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("Investigating Coolify API structure for applications...")
print()

PROJECT_UUID = "vwwc8c0kgssscc8so8ocwckw"
ENV_UUID = "b0og88kc444w8o84ckoo0g8c"

# Try to get the environment details
print("[1] Get project details:")
try:
    url = f"{base_url}/projects/{PROJECT_UUID}"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        project = response.json()
        print(f"✓ Project found")
        print(json.dumps(project, indent=2)[:500])
    else:
        print(f"✗ Status: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("[2] Get environment details:")
try:
    url = f"{base_url}/projects/{PROJECT_UUID}/environments/{ENV_UUID}"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        env = response.json()
        print(f"✓ Environment found")
        print(json.dumps(env, indent=2)[:500])
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"  Response: {response.text[:300]}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("[3] List all resources (to understand existing structure):")
try:
    url = f"{base_url}/resources"
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        resources = response.json()
        print(f"✓ Resources found: {len(resources)}")
        for res in resources:
            print(f"\n  Resource: {res.get('name')}")
            print(f"    UUID: {res.get('uuid')}")
            print(f"    Type: {res.get('type')}")
            if 'git_repository' in res:
                print(f"    Git Repo: {res.get('git_repository')}")
    else:
        print(f"✗ Status: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("[4] Try POST to resources endpoint (to create new resource):")
try:
    url = f"{base_url}/resources"
    payload = {
        "name": "trading-nexus",
        "type": "application",
        "project_id": PROJECT_UUID,
        "environment_id": ENV_UUID,
    }
    print(f"Payload: {json.dumps(payload, indent=2)}")
    response = requests.post(url, headers=headers, json=payload, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"✗ Error: {e}")
