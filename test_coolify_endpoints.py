#!/usr/bin/env python3
import requests

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
base_url = "http://72.62.228.112:8000"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("Testing Coolify API endpoints...")
print()

# Try different API endpoints
endpoints = [
    "/api/v1/projects",  
    "/api/v4/projects",
    "/api/projects",
    "/api/v1/resources",
    "/api/v4/resources",
    "/api/resources",
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
            print(f"  Response: {str(data)[:200]}...")
            break
        elif response.status_code == 401:
            print(f"  ✗ Unauthorized (token invalid or invalid format)")
        elif response.status_code == 404:
            print(f"  ✗ Not found")
        else:
            print(f"  ? Unexpected status")
        print()
        
    except requests.exceptions.JSONDecodeError:
        print(f"GET {endpoint}")
        print(f"  Status: {response.status_code}")
        print(f"  Error: Response is not JSON")
        print()
    except Exception as e:
        print(f"GET {endpoint}")
        print(f"  Error: {str(e)[:100]}")
        print()
