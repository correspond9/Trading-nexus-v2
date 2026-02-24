import requests

API = "https://tradingnexus.pro/api/v2"

# Login as super admin
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get user 1003's positions
print("Fetching positions for user 1003...\n")
positions_response = requests.get(
    f"{API}/portfolio/positions",
    params={"user_id": "1003"},  # User ID
    headers=headers
)

if positions_response.status_code == 200:
    positions = positions_response.json()
    print(f"Found {len(positions)} positions:")
    for p in positions:
        print(f"\nPosition ID: {p.get('position_id')}")
        print(f"Symbol: {p.get('symbol')}")
        print(f"Quantity: {p.get('quantity')}")
        print(f"Avg Price: {p.get('avg_price')}")
        print(f"Status: {p.get('status')}")
        print(f"LTP: {p.get('ltp')}")
else:
    print(f"Error: {positions_response.status_code}")
    print(positions_response.json())
