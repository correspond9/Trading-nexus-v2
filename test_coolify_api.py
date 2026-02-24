#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112"

print("Testing Coolify API connectivity...")

# Try different endpoints
endpoints = [
    "/api/v1/projects",
    "/api/v2/projects", 
    "/health",
    "/",
]

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

for endpoint in endpoints:
    try:
        url = base_url + endpoint
        print(f"\nTrying: {url}")
        response = requests.get(url, headers=headers, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.text and len(response.text) > 0:
            print(f"  Response: {response.text[:300]}")
    except Exception as e:
        print(f"  Error: {str(e)}")
