import requests
import sys

API = "https://tradingnexus.pro/api/v2"

# Login as super admin
print("=== Refreshing Instrument Master from Dhan CDN ===\n")
print("Step 1: Logging in as super admin...")

login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

token = login_response.json().get("access_token")
print(f"✅ Logged in successfully\n")

# Trigger instrument refresh
print("Step 2: Triggering instrument master refresh from Dhan CDN...")
print("This will download fresh data and update the database...")
print("(This may take 30-60 seconds)\n")

headers = {"Authorization": f"Bearer {token}"}
refresh_response = requests.post(
    f"{API}/admin/scrip-master/refresh",
    headers=headers
)

if refresh_response.status_code == 200:
    result = refresh_response.json()
    print(f"✅ Instrument master refreshed successfully!")
    print(f"   Source: {result.get('source', 'cdn')}")
else:
    print(f"❌ Refresh failed: {refresh_response.status_code}")
    print(refresh_response.text)
    sys.exit(1)

# Get status
print("\nStep 3: Checking database status...")
status_response = requests.get(f"{API}/admin/scrip-master/status", headers=headers)

if status_response.status_code == 200:
    status = status_response.json()
    print(f"✅ Last refreshed: {status.get('refreshed_at', 'N/A')}")
    print(f"   Total instruments: {status.get('total', 0)}")
    print(f"   Subscribed: {status.get('subscribed', 0)}")
else:
    print(f"⚠️ Could not fetch status: {status_response.status_code}")

print("\n✅ Done! Database is now populated with latest Dhan instrument data.")
