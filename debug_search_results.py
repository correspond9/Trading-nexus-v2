#!/usr/bin/env python
"""Debug script to see what search returns for specific queries."""

import requests
import json

BASE_URL = "http://72.62.228.112:8000"

# Login
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"phone": "8888888888", "password": "admin123"}
)
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test searches
test_queries = [
    "Reliance",
    "HDFC",
    "Tata Motors",
    "Infosys",
    "TCS"
]

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Search: '{query}'")
    print('='*80)
    
    resp = requests.get(
        f"{BASE_URL}/instruments/search",
        params={"q": query},
        headers=headers
    )
    
    results = resp.json()
    print(f"Total results: {len(results)}")
    
    # Group by instrument type
    by_type = {}
    for r in results:
        inst_type = r.get("instrument_type", "UNKNOWN")
        if inst_type not in by_type:
            by_type[inst_type] = []
        by_type[inst_type].append(r)
    
    for inst_type, items in by_type.items():
        print(f"\n  [{inst_type}] - {len(items)} results:")
        for item in items[:3]:  # Show first 3 of each type
            print(f"    - {item.get('symbol')} | {item.get('exchange_segment')} | underlying: {item.get('underlying')}")
        if len(items) > 3:
            print(f"    ... and {len(items) - 3} more")
