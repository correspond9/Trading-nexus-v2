import requests
import json
import warnings

warnings.filterwarnings('ignore')

# Test as SUPER_ADMIN
token = "super_admin_token_here"  # We'll need to handle auth properly

# First, let's test without auth to see what the endpoint returns
url = "https://tradingnexus.pro/api/v2/trading/orders/historic/orders"
params = {
    "from_date": "2026-03-01",
    "to_date": "2026-03-03"
}

try:
    response = requests.get(url, params=params, verify=False)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"\nResponse Body:")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2)[:500] + "...")
        print(f"\nTotal records: {len(data.get('data', []))}")
        if data.get('data'):
            print(f"First record keys: {list(data['data'][0].keys())}")
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
