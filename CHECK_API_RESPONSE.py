#!/usr/bin/env python3
"""
Check if the Watchlist API is returning the new tier/has_position fields
"""

import requests
import json
import sys

# Replace with your user ID
USER_ID = input("Enter your user ID (from URL or app): ").strip()

if not USER_ID:
    print("Error: User ID required")
    sys.exit(1)

API_URL = "http://72.62.228.112:8000"

print("\n" + "=" * 70)
print("  CHECKING WATCHLIST API RESPONSE")
print("=" * 70 + "\n")

print(f"Connecting to: {API_URL}/watchlist/{USER_ID}\n")

try:
    response = requests.get(
        f"{API_URL}/watchlist/{USER_ID}",
        headers={"X-USER": USER_ID},
        timeout=5
    )
    response.raise_for_status()
    data = response.json()
    
    print("✅ API Response Received!\n")
    print(json.dumps(data, indent=2))
    
    # Check for required fields
    print("\n" + "-" * 70)
    print("  FIELD VALIDATION")
    print("-" * 70 + "\n")
    
    if "data" in data and len(data["data"]) > 0:
        item = data["data"][0]
        
        fields_to_check = [
            ("tier", "Tier classification"),
            ("has_position", "Position status"),
            ("added_at", "Added timestamp"),
            ("symbol", "Symbol"),
            ("token", "Token"),
        ]
        
        all_good = True
        for field, desc in fields_to_check:
            has_field = field in item
            status = "✅" if has_field else "❌"
            print(f"{status} {field:15} ({desc:25}): {item.get(field, 'MISSING')}")
            if not has_field:
                all_good = False
        
        if all_good:
            print("\n✅ All required fields present! UI should show badges.")
        else:
            print("\n❌ Missing fields. Badges won't show.")
            print("   → Backend deployment may not have completed properly")
            print("   → Try redeploying from Coolify dashboard")
    else:
        print("⚠️  No items in watchlist to check")
        print("   Add an item to watchlist first")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Error connecting to API: {e}")
    print("\nPossible issues:")
    print("  1. VPS not running")
    print("  2. API URL incorrect")
    print("  3. Application not started")
    sys.exit(1)
