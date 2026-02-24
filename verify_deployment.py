#!/usr/bin/env python3
"""
Verify the application is truly running and healthy
"""
import requests
import time

print("="*70)
print("VERIFYING TRADING-NEXUS-V2 DEPLOYMENT")
print("="*70)

base_url = "http://72.62.228.112:8000"

endpoints = [
    ("/api/v2/health", "Backend Health"),
    ("/api/v2/market/stream-status", "Market Stream Status"),
    ("/api/v2/admin/notifications?limit=5", "Admin Notifications (Data Check)"),
]

print(f"\nAttempting to reach trading-nexus-v2 on VPS...")
print(f"Base URL: {base_url}\n")

time.sleep(3)  # Give it a moment to start if needed

all_working = True
for endpoint, description in endpoints:
    try:
        url = base_url + endpoint
        print(f"Testing: {description}")
        print(f"  URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"  Status: ✅ {response.status_code}")
            try:
                data = response.json()
                # Show first 200 chars of response
                response_preview = str(data)[:200]
                print(f"  Response: {response_preview}")
            except:
                print(f"  Response: {response.text[:200]}")
        else:
            print(f"  Status: ⚠️  {response.status_code}")
            all_working = False
            
    except requests.exceptions.Timeout:
        print(f"  Status: ✗ TIMEOUT - Application may still be starting")
        all_working = False
    except requests.exceptions.ConnectionError:
        print(f"  Status: ✗ CONNECTION REFUSED - Application not responding")
        all_working = False
    except Exception as e:
        print(f"  Status: ✗ ERROR - {str(e)[:50]}")
        all_working = False
    
    print()

print("="*70)
if all_working:
    print("✅ ALL ENDPOINTS WORKING - DEPLOYMENT SUCCESSFUL!")
else:
    print("⚠️  Some endpoints not responding yet - Application may still be starting")
    print("\nGive it 1-2 minutes and check again, or view logs at:")
    print("  → http://72.62.228.112:8000/")
print("="*70)
