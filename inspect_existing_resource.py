#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112:8000/api/v1"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

# UUID of the existing resource
EXISTING_RESOURCE_UUID = "iwkk4g08gcw4wgc0ocw048k4"

print("Examining existing resource structure...")
print()

# Get existing resource details
try:
    url = f"{base_url}/resources/{EXISTING_RESOURCE_UUID}"
    response = requests.get(url, headers=headers, timeout=5)
    
    if response.status_code == 200:
        resource = response.json()
        print("✓ Resource found!")
        print()
        print("Full resource structure:")
        print(json.dumps(resource, indent=2))
    else:
        print(f"✗ Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error: {e}")
