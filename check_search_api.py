import requests

API = "https://tradingnexus.pro/api/v2"

print("=== Checking What Search API Returns ===\n")

response = requests.get(f"{API}/instruments/search?q=LENSKART&limit=1")
if response.status_code == 200:
    results = response.json()
    if len(results) > 0:
        print("Fields returned by search API:")
        for key, value in results[0].items():
            print(f"  {key}: {value}")
else:
    print(f"Error: {response.status_code}")
