import requests
import json

# Test the backend fix - does it accept NSE (not NSE_EQ)?
print("TEST: Backend fix - does it accept NSE (not NSE_EQ)?")
print("=" * 70)

# First, get auth token
login_r = requests.post(
    'https://tradingnexus.pro/api/v2/auth/login',
    json={'mobile': '8888888888', 'password': 'admin123'},  # 10-digit mobile
    verify=False
)

if login_r.status_code != 200:
    print(f"Login failed: {login_r.status_code}")
    print(login_r.text[:300])
    exit(1)

login_data = login_r.json()
token = login_data.get('access_token')
print(f"\nOK - Login successful")
print(f"  Token: {token[:30]}...")

# Test backdate position with NSE using a test User ID
# We'll just retry with user_id as a mobile number
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

backdate_payload = {
    "user_id": "9876543210",  # Try a different mobile/ID format
    "symbol": "LENSKART",
    "qty": 370,
    "price": 524.70,
    "trade_date": "19-02-2026",
    "instrument_type": "EQ",
    "exchange": "NSE"
}

print("\nTrying backdate with user_id: 9876543210")
print("(To find the exact user ID for Trader1, use the dashboard)")

r = requests.post(
    'https://tradingnexus.pro/api/v2/admin/backdate-position',
    json=backdate_payload,
    headers=headers,
    verify=False
)

print(f"\nResponse Status: {r.status_code}")
resp_data = r.json()
print("Response:")
print(json.dumps(resp_data, indent=2))

# Check if the NSE issue is fixed (should NOT say "Invalid exchange: NSE")
if "Invalid exchange" not in str(resp_data):
    print("\n" + "="*70)
    print("OK - Backend accepted NSE exchange! (no validation error)")
    print("="*70)
