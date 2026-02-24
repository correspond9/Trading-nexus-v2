#!/usr/bin/env python3
"""
Use Coolify API to fix the application configuration
Remove the problematic routing settings that are preventing API access
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
COOLIFY_URL = "http://72.62.228.112:8080"  # Based on earlier findings
API_TOKEN = os.environ.get("COOLIFY_TOKEN", "")  # User should set this
APP_ID = "14"  # From our earlier grep output
APP_UUID = "p488ok8g8swo4ockks040ccg"

def test_api_connection():
    """Test if we can connect to Coolify API"""
    print("Testing Coolify API connection...")
    
    try:
        # Try to get API status
        headers = {"Authorization": f"Bearer {API_TOKEN}"} if API_TOKEN else {}
        response = requests.get(
            f"{COOLIFY_URL}/api/v1/applications",
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 401, 403]:
            print(f"✅ Connected to Coolify API")
            if response.status_code == 401:
                print("⚠️  Authentication failed - check API token")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def get_application_details():
    """Get current application configuration"""
    print(f"\nFetching application {APP_ID}...")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{COOLIFY_URL}/api/v1/applications/{APP_ID}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            app_data = response.json()
            print(f"✅ Retrieved application configuration")
            
            # Print relevant routing details
            if 'fqdn' in app_data:
                print(f"  FQDN: {app_data.get('fqdn', 'N/A')}")
            if 'ports' in app_data:
                print(f"  Ports: {app_data.get('ports', 'N/A')}")
            if 'name' in app_data:
                print(f"  Name: {app_data.get('name', 'N/A')}")
            
            return app_data
        else:
            print(f"❌ Failed to get app details: {response.status_code}")
            print(response.text[:500])
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_application_routing():
    """Update application routing configuration"""
    print(f"\nUpdating application routing...")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Configuration to send
    update_payload = {
        "_redirect_http_to_https": True,
        "docker_compose_domain_set_explicitly": False,
        "generate_docker_compose": True,
        # Remove problematic port expose settings
        "ports": "8000/http"
    }
    
    try:
        response = requests.put(
            f"{COOLIFY_URL}/api/v1/applications/{APP_ID}",
            headers=headers,
            json=update_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Application updated")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(response.text[:500])
            return False
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False

def trigger_deployment():
    """Trigger a redeployment with the new configuration"""
    print(f"\nTriggering redeployment...")
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{COOLIFY_URL}/api/v1/applications/{APP_ID}/deploy",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Redeployment triggered")
            return True
        elif response.status_code == 202:
            print(f"✅ Redeployment queued")
            return True
        else:
            print(f"❌ Deployment trigger failed: {response.status_code}")
            print(response.text[:500])
            return False
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("COOLIFY API - APPLICATION CONFIGURATION FIX")
    print("="*70 + "\n")
    
    if not API_TOKEN:
        print("⚠️  COOLIFY_TOKEN environment variable not set")
        print("\nTo use this fix:")
        print("1. Get your Coolify API token from:")
        print("   http://72.62.228.112:8080 → Settings → API → Generate Token")
        print("2. Set the environment variable:")
        print("   export COOLIFY_TOKEN='your-token-here'")
        print("3. Run this script again")
        sys.exit(1)
    
    # Step 1: Test connection
    if not test_api_connection():
        print("\n⚠️  Cannot connect to Coolify API at {COOLIFY_URL}")
        print("\nTroubleshooting:")
        print("1. Verify Coolify is running: docker ps | grep coolify")
        print("2. Check Coolify port: netstat -tlnp | grep 8080")
        print("3. Verify token: echo $COOLIFY_TOKEN")
        sys.exit(1)
    
    # Step 2: Get current config
    app_config = get_application_details()
    if not app_config:
        sys.exit(1)
    
    # Step 3: Update configuration
    if not update_application_routing():
        sys.exit(1)
    
    # Step 4: Trigger redeployment
    if not trigger_deployment():
        print("\n⚠️  Deployment trigger failed, but configuration may have been updated")
        print("Try manually deploying from Coolify UI")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("FIX COMPLETE")
    print("="*70)
    print("""
Coolify is now redeploying the application with fixed configuration.

Expected timeline:
  1. Docker images rebuild (~5-10 minutes)
  2. Containers restart (~30 seconds)
  3. Application initializes (~30-60 seconds)
  4. API becomes available

Monitor progress:
  1. Check Coolify dashboard: http://72.62.228.112:8080
  2. View deployment logs in application details
  3. Test endpoint: curl http://api.tradingnexus.pro/api/v2/instruments/search?q=RELIANCE

Expected result:
  ✅ Search endpoint returns JSON array of instruments
  ✅ Frontend dropdown works when typing stock symbol
  ✅ Backdate position form can auto-complete instruments
""")

if __name__ == "__main__":
    main()
