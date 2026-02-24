#!/usr/bin/env python3
"""
Check application status via Coolify API
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

print("="*70)
print("TRADING-NEXUS-V2 STATUS CHECK")
print("="*70)

try:
    response = requests.get(f"{api_url}/applications/{app_uuid}", headers=headers, timeout=10)
    app = response.json()
    
    print(f"\nApplication: {app.get('name')}")
    print(f"Status: {app.get('status')}")
    print(f"Last Online: {app.get('last_online_at')}")
    print(f"Restart Count: {app.get('restart_count')}")
    print(f"Health Check Enabled: {app.get('health_check_enabled')}")
    print(f"Docker Compose: {app.get('docker_compose')}")
    
    # Try to get logs
    print(f"\n" + "-"*70)
    print("RECENT LOGS:")
    print("-"*70)
    
    logs_response = requests.get(
        f"{api_url}/applications/{app_uuid}/logs",
        headers=headers,
        timeout=10
    )
    
    if logs_response.status_code == 200:
        logs = logs_response.json()
        if isinstance(logs, list):
            for log_entry in logs[-10:]:  # Show last 10
                print(f"  {log_entry}")
        else:
            print(logs)
    elif logs_response.status_code == 400:
        print("  (No logs available yet or logs endpoint returns 400)")
    else:
        print(f"  Status: {logs_response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print(f"\n" + "="*70)
print("VIEW FULL DASHBOARD:")
print("  → http://72.62.228.112:8000/")
print("  → Projects → trade-nexuss → production → trade-nexus-v2")
print("  → Click 'Logs' tab for full deployment logs")
print("="*70)
