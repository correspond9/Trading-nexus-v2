import requests

API = "https://tradingnexus.pro/api/v2"

print("Testing with exact case from database: 'Lenskart Solutions'\n")

# Login  
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})
token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Try with exact database case
backdate_data = {
    "user_id": "1003",
    "symbol": "Lenskart Solutions",  # Exact case from database
    "qty": 580,
    "price": 380.70,
    "trade_date": "20-02-2026",
    "instrument_type": "EQ",
    "exchange": "NSE"
}

response = requests.post(f"{API}/admin/backdate-position", json=backdate_data, headers=headers)
result = response.json()

if response.status_code == 200 and result.get("success"):
    print("✅ SUCCESS with database case!")
    pos = result.get("position", {})
    print(f"Position created: {pos.get('quantity')} {pos.get('symbol')} @ {pos.get('avg_price')} on {pos.get('opened_at')}")
else:
    print(f"❌ Still failed: {result.get('detail')}")
