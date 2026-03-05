#!/usr/bin/env python3
"""
Coolify API - Admin Wipe Wrong Orders
======================================
Executes admin_wipe_wrong_orders.py directly on the server via Coolify API
"""
import requests
import json
import time
import sys

# Coolify Configuration
COOLIFY_URL = "http://72.62.228.112"
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
APP_UUID = "x8gg0og8440wkgc8ow0ococs"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

def execute_via_coolify():
    """Execute admin wipe script via Coolify API"""
    
    print("\n" + "=" * 80)
    print("COOLIFY API - EXECUTE ADMIN WIPE")
    print("=" * 80)
    print(f"\nApp UUID: {APP_UUID}")
    print(f"Coolify URL: {COOLIFY_URL}")
    
    # Method 1: Try exec endpoint
    print("\n[1/2] Attempting to execute via Coolify API...")
    
    cmd = "cd /app && python admin_wipe_wrong_orders.py"
    
    endpoints_to_try = [
        f"{COOLIFY_URL}/api/v1/applications/{APP_UUID}/exec",
        f"{COOLIFY_URL}/api/v1/applications/{APP_UUID}/terminal",
        f"{COOLIFY_URL}/api/applications/{APP_UUID}/exec",
    ]
    
    for endpoint in endpoints_to_try:
        try:
            print(f"\nTrying endpoint: {endpoint}")
            
            response = requests.post(
                endpoint,
                headers=headers,
                json={"command": cmd},
                timeout=60
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code in [200, 201, 202]:
                print("\n✅ Command executed successfully!")
                
                # Try to get output
                if response.status_code == 200:
                    data = response.json()
                    if 'output' in data:
                        print("\n" + "=" * 80)
                        print("OUTPUT:")
                        print("=" * 80)
                        print(data['output'])
                        return True
                    elif 'result' in data:
                        print("\n" + "=" * 80)
                        print("OUTPUT:")
                        print("=" * 80)
                        print(data['result'])
                        return True
                
                return True
                
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
            continue
    
    # Method 2: Use Docker Compose approach
    print("\n[2/2] Using alternative method via Coolify...")
    
    try:
        # Try to trigger a deployment that includes running the script
        response = requests.post(
            f"{COOLIFY_URL}/api/v1/applications/{APP_UUID}/deployments",
            headers=headers,
            json={
                "pre_deployment_command": "cd /app && python admin_wipe_wrong_orders.py",
            },
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code in [200, 201]:
            print("\n⚠️  Script queued for next deployment")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    print("⚠️  COOLIFY API LIMITATION DETECTED")
    print("=" * 80)
    print("""
The Coolify API endpoints don't support direct command execution 
from external clients in this configuration.

WORKAROUND: Use SSH command instead:

ssh -i <your-key> root@<server-ip> << 'EOF'
cd /app
python admin_wipe_wrong_orders.py
EOF

Or connect via Coolify Terminal and run:
docker exec trading-nexus-app python admin_wipe_wrong_orders.py
""")
    
    return False

if __name__ == '__main__':
    try:
        success = execute_via_coolify()
        
        if not success:
            print("\n💡 Alternative option:")
            print("   The script has been committed to GitHub (f74c0bc)")
            print("   You can execute it directly on your server when ready")
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
