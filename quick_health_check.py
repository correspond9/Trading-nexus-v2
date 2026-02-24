#!/usr/bin/env python3
"""
Quick verification script - Check if backend is accessible
Run this after any deployment to verify API is working
"""
import requests
import sys

print("=" * 80)
print("  QUICK API HEALTH CHECK")
print("=" * 80)
print()

endpoints = {
    'Production Domain': 'http://api.tradingnexus.pro/health',
    'VPS IP': 'http://72.62.228.112/health',
}

all_ok = True

for name, url in endpoints.items():
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            print(f"✅ {name:20} - HTTP {r.status_code} - OK")
        else:
            print(f"❌ {name:20} - HTTP {r.status_code} - FAILED")
            all_ok = False
    except Exception as e:
        print(f"❌ {name:20} - Connection Error")
        all_ok = False

print()
if all_ok:
    print("✅ ALL ENDPOINTS OK - API is accessible!")
    print()
    print("Your API is live at:")
    print("  • http://api.tradingnexus.pro/api/v2/...")
    print("  • http://72.62.228.112/api/v2/...")
    sys.exit(0)
else:
    print("❌ SOME ENDPOINTS FAILED")
    print()
    print("If backend is not accessible, run the network fix:")
    print("  python fix_network_ssh.py")
    print()
    print("Or manually SSH and run:")
    print("  ssh root@72.62.228.112")
    print("  BACKEND=$(docker ps --format '{{.Names}}' | grep p488ok8.*backend)")
    print("  docker network connect coolify $BACKEND")
    sys.exit(1)
