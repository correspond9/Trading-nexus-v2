import requests

API = "https://tradingnexus.pro/api/v2"

# Get login token (you'll need valid credentials)
print("=== Testing Instrument Search ===\n")

# Test 1: Search for LENSKART (correct spelling)
print("1. Searching for 'LENSKART' (correct spelling):")
response = requests.get(f"{API}/instruments/search?q=LENSKART&limit=5")
if response.status_code == 200:
    results = response.json()
    print(f"   Found {len(results)} results:")
    for r in results:
        print(f"   - Symbol: {r.get('symbol')}, Exchange: {r.get('exchange_segment')}, Type: {r.get('instrument_type')}")
else:
    print(f"   Error: {response.status_code}")

print()

# Test 2: Search for LENSCART (with C - user's typo)
print("2. Searching for 'LENSCART' (user's typo with C):")
response = requests.get(f"{API}/instruments/search?q=LENSCART&limit=5")
if response.status_code == 200:
    results = response.json()
    print(f"   Found {len(results)} results")
    if len(results) == 0:
        print("   ❌ No results - typo prevents finding the instrument!")
else:
    print(f"   Error: {response.status_code}")

print()

# Test 3: Search for just "LENS"
print("3. Searching for 'LENS' (partial):")
response = requests.get(f"{API}/instruments/search?q=LENS&limit=5")
if response.status_code == 200:
    results = response.json()
    print(f"   Found {len(results)} results:")
    for r in results:
        print(f"   - Symbol: {r.get('symbol')}, Exchange: {r.get('exchange_segment')}")
else:
    print(f"   Error: {response.status_code}")
