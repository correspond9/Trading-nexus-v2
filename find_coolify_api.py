#!/usr/bin/env python3
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"

# Common Coolify ports
ports = [3000, 5000, 5173, 8080, 8081, 9000]
host = "72.62.228.112"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("Scanning for Coolify API on common ports...")
print()

for port in ports:
    base_url = f"http://{host}:{port}"
    
    # Try projects endpoint
    try:
        url = f"{base_url}/api/v1/projects"
        response = requests.get(url, headers=headers, timeout=3)
        print(f"✓ Port {port}: {response.status_code} - {base_url}")
        if response.status_code == 200:
            print(f"  SUCCESS! Response: {response.text[:200]}")
            break
    except requests.exceptions.Timeout:
        print(f"  Port {port}: TIMEOUT")
    except requests.exceptions.ConnectionError:
        print(f"  Port {port}: Connection refused")
    except Exception as e:
        pass

print("\nIf Coolify API is not found, please provide the full Coolify dashboard URL")
