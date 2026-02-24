#!/usr/bin/env python3
"""
Check actual deployment status and why it's still unhealthy
"""
import requests

api_token = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
api_url = "http://72.62.228.112:8000/api/v1"
app_uuid = "zccs8wko40occg44888kwooc"

headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}

print("="*70)
print("CHECKING ACTUAL APPLICATION STATUS")
print("="*70)

try:
    response = requests.get(f"{api_url}/applications/{app_uuid}", headers=headers, timeout=10)
    app = response.json()
    
    status = app.get('status', 'unknown')
    
    print(f"\nStatus: {status}")
    print(f"Exact status string: '{status}'")
    print(f"Status is running: {'running' in status.lower()}")
    print(f"Status is exited: {'exited' in status.lower()}")
    print(f"Status is unhealthy: {'unhealthy' in status.lower()}")
    
    print(f"\nOther info:")
    print(f"  Last online: {app.get('last_online_at')}")
    print(f"  Restart count: {app.get('restart_count')}")
    print(f"  Server status: {app.get('server_status')}")
    print(f"  Health check enabled: {app.get('health_check_enabled')}")
    
except Exception as e:
    print(f"Error: {e}")

print(f"\n" + "="*70)
print("This means the containers are NOT running yet.")
print("Check the Coolify logs to see what error occurred.")
print("="*70)
