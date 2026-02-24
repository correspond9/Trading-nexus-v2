import requests

API = "https://tradingnexus.pro/api/v2"

# Login
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Get status with more details
status_response = requests.get(f"{API}/admin/scrip-master/status", headers=headers)
status = status_response.json()

print("=== Instrument Master Status ===")
print(f"Total instruments: {status.get('total', 0)}")
print(f"Subscribed: {status.get('subscribed', 0)}")
print(f"Last refreshed: {status.get('refreshed_at', 'Never')}")

if status.get('counts'):
    print("\nBreakdown by tier and type:")
    for c in status['counts']:
        print(f"  Tier {c['tier']}: {c['instrument_type']} = {c['cnt']}")
