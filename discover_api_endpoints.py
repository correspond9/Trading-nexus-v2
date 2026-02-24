#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112:8000/api/v1"
app_uuid = "zccs8wko40occg44888kwooc"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("Discovering available Coolify API endpoints for applications...\n")

# Get full application object to see structure
try:
    response = requests.get(f"{base_url}/applications/{app_uuid}", headers=headers, timeout=10)
    app = response.json()
    
    print("Full application object structure:")
    print(json.dumps(app, indent=2)[:2000])
    print("\n... (truncated)\n")
    
    # Show all keys available
    print("Available fields in application object:")
    for key in sorted(app.keys()):
        value_type = type(app[key]).__name__
        print(f"  - {key}: {value_type}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*70)
print("Available API endpoints for this application:\n")

endpoints = [
    f"/applications/{app_uuid}",
    f"/applications/{app_uuid}/logs",
    f"/applications/{app_uuid}/compose",
    f"/applications/{app_uuid}/environment-variables",
    f"/applications/{app_uuid}/secrets",
    f"/applications/{app_uuid}/deploy",
    f"/applications/{app_uuid}/start",
    f"/applications/{app_uuid}/stop",
    f"/applications/{app_uuid}/restart",
    f"/applications/{app_uuid}/rollback",
]

for endpoint in endpoints:
    try:
        response = requests.get(base_url + endpoint, headers=headers, timeout=5)
        status = f"✓ {response.status_code}"
        print(f"{endpoint:<50s} {status}")
    except:
        print(f"{endpoint:<50s} ✗ Error")
