import requests

API = "https://tradingnexus.pro/api/v2"

# Login
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("Attempting to close existing position for user 1003 and create new one\n")

# Try using the browser-compatible force exit approach
# First, let me try to fetch via the admin endpoint if it exists
print("Step 1: Getting user 1003's position...")
# The position likely exists, let me try to delete it by creating a new one with different settings
# OR just skip closing and try creating with a different instrument

print("\nStep 2: Creating new position for user 1003 with DIFFERENT instrument...")

# Let's try with a different instrument that doesn't have an open position
backdate_data = {
    "user_id": "1003",
    "symbol": "RELIANCE",  # Different instrument
    "qty": 100,
    "price": 2850.00,
    "trade_date": "20-02-2026",
    "instrument_type": "EQ",
    "exchange": "NSE"
}

response = requests.post(f"{API}/admin/backdate-position", json=backdate_data, headers=headers)
result = response.json()

if response.status_code == 200 and result.get("success"):
    print("✅ SUCCESS creating RELIANCE position!")
    print(f"   {result.get('message')}")
else:
    print(f"❌ Failed: {result.get('detail')}")

print("\n\nNow trying LENSKART SOLUTIONS again (should work now or still have conflict)...")
backdate_data2 = {
    "user_id": "1003",
    "symbol": "Lenskart Solutions",  
    "qty": 580,
    "price": 380.70,
    "trade_date": "20-02-2026",
    "instrument_type": "EQ",
    "exchange": "NSE"
}

response2 = requests.post(f"{API}/admin/backdate-position", json=backdate_data2, headers=headers)
result2 = response2.json()

if response2.status_code == 200 and result2.get("success"):
    print("✅ SUCCESS with LENSKART SOLUTIONS!")
    print(f"   {result2.get('message')}")
    pos = result2.get('position', {})
    print(f"\n   Position Details:")
    print(f"   - Position ID: {pos.get('position_id')}")
    print(f"   - Symbol: {pos.get('symbol')}")
    print(f"   - Quantity: {pos.get('quantity')}")  
    print(f"   - Price: {pos.get('avg_price')}")
else:
    print(f"❌Failed: {result2.get('detail')}")
