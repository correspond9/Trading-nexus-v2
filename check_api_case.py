import requests

API = "https://tradingnexus.pro/api/v2"

print("=== Checking Search API Response Format ===\n")

response = requests.get(f"{API}/instruments/search?q=LENSKART&limit=3")
if response.status_code == 200:
    results = response.json()
    print("Search results for 'LENSKART':")
    for i, r in enumerate(results, 1):
        symbol = r.get('symbol', '')
        print(f"{i}. symbol field: '{symbol}'")
        print(f"   Display name converted to: {symbol.upper()}")
        print()
