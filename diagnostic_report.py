import requests

API = "https://tradingnexus.pro/api/v2"

# Login
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("=== Diagnostic Report ===\n")

# 1. Check instrument master
print("1. Instrument Master Status:")
status_response = requests.get(f"{API}/admin/scrip-master/status", headers=headers)
if status_response.status_code == 200:
    status = status_response.json()
    print(f"   Total instruments: {status.get('total', 0)}")
    print(f"   Subscribed: {status.get('subscribed', 0)}")
    print(f"   Last refreshed: {status.get('refreshed_at', 'Never')}")
    
    if status.get('counts'):
        print("\n   Breakdown:")
        for c in status['counts'][:5]:
            print(f"      Tier {c.get('tier')}: {c.get('instrument_type')} = {c.get('cnt')}")
else:
    print(f"   ❌ Error: {status_response.status_code}")

# 2. Test search
print("\n2. Search Test:")
search_response = requests.get(f"{API}/instruments/search?q=RELIANCE&limit=3")
if search_response.status_code == 200:
    results = search_response.json()
    print(f"   Found {len(results)} results for 'RELIANCE'")
    for i, r in enumerate(results[:3], 1):
        print(f"      {i}. symbol='{r.get('symbol')}' | underlying='{r.get('underlying')}' | type={r.get('instrument_type')}")
else:
    print(f"   ❌ Error: {search_response.status_code}")

# 3. Try the problematic Lenskart search
print("\n3. Lenskart Search Test:")
search_response = requests.get(f"{API}/instruments/search?q=LENSKART&limit=3")
if search_response.status_code == 200:
    results = search_response.json()
    print(f"   Found {len(results)} results for 'LENSKART'")
    for i, r in enumerate(results[:3], 1):
        print(f"      {i}. symbol='{r.get('symbol')}' | underlying='{r.get('underlying')}' | token={r.get('instrument_token')}")
else:
    print(f"   ❌ Error: {search_response.status_code}")

print("\n" + "=" * 70)
