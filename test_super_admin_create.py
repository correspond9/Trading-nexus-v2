import requests

API = "https://tradingnexus.pro/api/v2"

print("=" * 70)
print("  SUPER_ADMIN Creating Position for User 1003")
print("=" * 70)

# Step 1: Login as SUPER_ADMIN
print("\n1. Logging in as SUPER_ADMIN (9999999999)...")
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.json())
    exit(1)

token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
role = login_response.json().get("role", "unknown")
print(f"✅ Logged in as {role}\n")

# Step 2: Create position via backdate API
print("2. Creating position for User ID 1003...")
print("   - User: 1003 (Super User, mobile 6666666666)")
print("   - Instrument: LENSKART SOLUTIONS (or any case variant)")
print("   - Quantity: 580")
print("   - Price: 380.70")
print("   - Date: 20-02-2026\n")

backdate_data = {
    "user_id": "1003",  # User ID or mobile
    "symbol": "LENSKART SOLUTIONS",  # All caps - should work with case-insensitive backend
    "qty": 580,
    "price": 380.70,
    "trade_date": "20-02-2026",
    "instrument_type": "EQ",
    "exchange": "NSE"
}

response = requests.post(
    f"{API}/admin/backdate-position",
    json=backdate_data,
    headers=headers
)

print(f"Response Status: {response.status_code}\n")
result = response.json()

if response.status_code == 200 and result.get("success"):
    print("✅ SUCCESS! Position created successfully!\n")
    pos = result.get("position", {})
    print("Position Details:")
    print(f"  Position ID: {pos.get('position_id')}")
    print(f"  User ID: {pos.get('user_id')}")
    print(f"  Symbol: {pos.get('symbol')}")
    print(f"  Quantity: {pos.get('quantity')}")
    print(f"  Avg Price: {pos.get('avg_price')}")
    print(f"  Opened At: {pos.get('opened_at')}")
    print(f"  Status: {pos.get('status')}")
else:
    print("❌ FAILED!")
    print(f"Error: {result.get('detail', 'Unknown error')}")

print("\n" + "=" * 70)
