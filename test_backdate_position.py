import requests

API = "https://tradingnexus.pro/api/v2"

# Login as super admin
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("=== Testing Backdate Position Creation ===\n")

# Test 1: Create position with DISPLAY_NAME
test_data = {
    "user_id": "9326890165",  # Trader user
    "symbol": "Lenskart Solutions",  # Display name from database
    "qty": 100,
    "price": 485.20,
    "trade_date": "20-02-2026",
    "instrument_type": "EQ",
    "exchange": "NSE"
}

print("Test Data:")
for k, v in test_data.items():
    print(f"  {k}: {v}")

print("\nSending request...")
response = requests.post(
    f"{API}/admin/backdate-position",
    json=test_data,
    headers=headers
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Body:")
print(response.json())

if response.status_code == 200 and response.json().get("success"):
    print("\n✅ SUCCESS! Position created successfully")
else:
    print("\n❌ FAILED! See error above")
