#!/usr/bin/env python3
"""
Try to fetch deployment logs from Coolify
"""
import requests
import json

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
api_url = "http://72.62.228.112:8000/api/v1"
app_uuid = "zccs8wko40occg44888kwooc"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("Attempting to retrieve deployment logs...\n")

# Try different log-fetching approaches
approaches = [
    (f"{api_url}/applications/{app_uuid}/logs", "GET", None),
    (f"{api_url}/applications/{app_uuid}/logs?limit=100", "GET", None),
    (f"{api_url}/applications/{app_uuid}/logs?tail=100", "GET", None),
]

for url, method, data in approaches:
    try:
        print(f"Trying: GET {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ SUCCESS!")
            try:
                logs = response.json()
                if isinstance(logs, list):
                    print(f"Found {len(logs)} log entries:\n")
                    for entry in logs[-20:]:  # Show last 20
                        print(f"  {entry}")
                else:
                    print(logs)
            except:
                print(response.text[:500])
            break
        elif response.status_code == 400:
            print("Status 400 - API endpoint may need different parameters")
            print(f"Response: {response.text[:200]}\n")
        else:
            print(f"Response: {response.text[:200]}\n")
            
    except Exception as e:
        print(f"Error: {e}\n")

print("\n" + "="*70)
print("⚠️  If logs are not available via API, check Coolify dashboard:")
print("="*70)
print("\nGo to: http://72.62.228.112:8000/")
print("Then: Projects → trade-nexuss → production → trade-nexus-v2 → Logs tab")
print("\nLook for error messages starting with:")
print("  'Deployment failed:' or 'Error:' or exception stacktraces")
print("="*70)
