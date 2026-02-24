#!/usr/bin/env python3
import requests
import json

API_BASE = "http://72.62.228.112:8000/api/v1"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
APP_UUID = "zccs8wko40occg44888kwooc"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("Attempting to fetch backend container logs from Coolify API")
print("=" * 80)

# Try to get application details first
print("\n1. Getting application details...")
try:
    resp = requests.get(f"{API_BASE}/applications/{APP_UUID}", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        app_data = resp.json()
        print(f"Application Status: {app_data.get('status')}")
        print(f"Git Commit: {app_data.get('git_commit')}")
except Exception as e:
    print(f"Error: {e}")

# Try different log endpoints
endpoints = [
    f"/applications/{APP_UUID}/logs",
    f"/applications/{APP_UUID}/logs?all=true",
    f"/applications/{APP_UUID}/logs?lines=500",
    f"/applications/{APP_UUID}/logs?container=backend",
]

for endpoint in endpoints:
    print(f"\n2. Trying: GET {endpoint}")
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Response: {resp.text[:500]}")
        else:
            logs = resp.text
            print(f"Got logs ({len(logs)} bytes):")
            print(logs[:2000])
    except Exception as e:
        print(f"Error: {e}")

# Try to list resources and get logs that way
print(f"\n3. Trying to list all resources in application...")
try:
    resp = requests.get(f"{API_BASE}/applications/{APP_UUID}/resources", headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        resources = resp.json()
        print(f"Resources: {json.dumps(resources, indent=2)[:1000]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("If no logs obtained via API, the Coolify dashboard must be accessed manually.")
print("Container name from deployment logs: backend-zccs8wko40occg44888kwooc-204020364466")
print("=" * 80)
