import requests

API = "https://tradingnexus.pro/api/v2"

print("Testing backdate position with case-insensitive lookup\n")

# Login
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Test data exactly as entered in browser
test_data = {
    "user_id": "1003",
    "symbol": "Lenskart Solutions",  # Exact case from dropdown selection
    "qty": 580,
    "price": 380.70,
    "trade_date": "20-02-2026",  # DD-MM-YYYY format
    "instrument_type": "EQ",
    "exchange": "NSE"
}

print("Request data:")
for k, v in test_data.items():
    print(f"  {k}: {v}")
print()

response = requests.post(f"{API}/admin/backdate-position", json=test_data, headers=headers)
result = response.json()

print(f"Response Status: {response.status_code}")
print(f"Response Body: {result}")

if response.status_code == 200 and result.get("success"):
    print("\n✅ SUCCESS!")
else:
    print(f"\n❌ ERROR: {result.get('detail', 'Unknown error')}")
