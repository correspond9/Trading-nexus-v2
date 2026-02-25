#!/usr/bin/env python3
"""
Investigate why frontend assets aren't updating:
1. Check what JavaScript is currently served
2. Check if it contains the fixes (String(user?.id))
3. Check the frontend container's build artifacts
4. Verify Coolify deployment status
"""

import requests
import json
from datetime import datetime

base_url = "http://tradingnexus.pro"
api_url = "http://api.tradingnexus.pro/api/v2"

print("="*70)
print("FRONTEND ASSET INVESTIGATION")
print("="*70)

# Step 1: Get the index.html to find asset names
print("\n1. Checking what assets are loaded in index.html...")
try:
    r = requests.get(f"{base_url}/", timeout=5)
    if r.status_code == 200:
        # Find all .js files mentioned in HTML
        import re
        js_files = re.findall(r'src="([^"]*\.js)"', r.text)
        print(f"   ✓ Found {len(js_files)} JavaScript files")
        for js_file in js_files:
            print(f"     - {js_file}")
    else:
        print(f"   ✗ Status {r.status_code}")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:80]}")

# Step 2: Check if the main bundle contains the fix
print("\n2. Looking for 'String(user' in served JavaScript...")
js_urls = [
    f"{base_url}/index.js",
    f"{base_url}/assets/index.js",
]

# Try to find the actual js file from index.html
try:
    r = requests.get(f"{base_url}/", timeout=5)
    import re
    matches = re.findall(r'src="(/assets/[^"]*\.js)"', r.text)
    if matches:
        actual_js_url = f"{base_url}{matches[0]}"
        print(f"   Checking: {actual_js_url}")
        r = requests.get(actual_js_url, timeout=10)
        
        # Check file size
        print(f"   File size: {len(r.text)} bytes")
        
        # Check for the fix markers
        has_string_user = "String(user" in r.text
        has_user_id_string = 'user_id:""+String' in r.text or "user_id:String" in r.text
        has_ltp_passing = "ltp:ltp" in r.text or "ltp:" in r.text
        
        print(f"   Contains 'String(user': {has_string_user}")
        print(f"   Contains user_id string conversion: {has_user_id_string}")
        print(f"   Contains 'ltp:ltp' passing: {has_ltp_passing}")
        
        if has_string_user and has_user_id_string and has_ltp_passing:
            print("   ✓ FIXES ARE PRESENT IN SERVED CODE!")
        else:
            print("   ✗ FIXES ARE NOT IN SERVED CODE (or minified differently)")
            
        # Look for specific commit hash or version info
        if "44c3283" in r.text:
            print("   ✓ Found commit 44c3283 reference")
        else:
            print("   ⚠ No visible commit reference (normal for production builds)")
            
except Exception as e:
    print(f"   ✗ Error: {str(e)[:100]}")

# Step 3: Check if frontend container is running
print("\n3. Checking frontend container status...")
try:
    # Try to access build metadata or headers
    r = requests.head(f"{base_url}/", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Server: {r.headers.get('Server', 'Unknown')}")
    print(f"   Last-Modified: {r.headers.get('Last-Modified', 'Unknown')}")
    print(f"   Cache-Control: {r.headers.get('Cache-Control', 'Unknown')}")
    print(f"   ETag: {r.headers.get('ETag', 'Unknown')}")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:80]}")

# Step 4: Check Coolify API for deployment status
print("\n4. Checking Coolify deployment status...")
coolify_url = "http://72.62.228.112:8000"
try:
    # Try to get app status from Coolify
    # This would need API token, so likely to fail
    # But we can at least check if Coolify is up
    r = requests.get(f"{coolify_url}/status", timeout=5)
    print(f"   Coolify status: {r.status_code}")
except Exception as e:
    print(f"   Coolify check: {str(e)[:80]}")

# Step 5: Compare with backend to see deployment info
print("\n5. Checking backend deployment info...")
try:
    r = requests.get(f"{api_url}/health", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   Backend status: OK")
        print(f"   Backend response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"   ✗ Error: {str(e)[:80]}")

print("\n" + "="*70)
print("SUMMARY:")
print("="*70)
print("""
To determine why frontend isn't updating:

1. If fixes ARE in served code:
   - Issue is browser cache
   - Solution: Hard refresh (Ctrl+Shift+R) or open in private/incognito
   - Or clear site data (Settings → Privacy → Cookies and site data)

2. If fixes are NOT in served code:
   - Issue is frontend container not rebuilt
   - Check if Coolify actually re-ran the build
   - May need to force deployment or restart container
   - Check: docker ps | grep frontend
   - Check: docker logs <frontend_container_id>

3. If getting 500 errors on API:
   - Authentication is broken (token format issue)
   - This is separate from frontend asset issue
""")
