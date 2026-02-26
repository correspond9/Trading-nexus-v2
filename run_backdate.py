import requests

API = "https://api.tradingnexus.pro/api/v2"
login = requests.post(f"{API}/auth/login", json={"mobile":"9999999999","password":"admin123"})
print('Login status', login.status_code)
try:
    token = login.json().get('access_token')
except Exception:
    print('Login response:', login.text)
    raise
if not token:
    print('No token returned; aborting')
    raise SystemExit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

payload = {
    "user_id": "9326890165",
    "symbol": "Lenskart Solutions",
    "qty": 100,
    "price": 485.20,
    "trade_date": "20-02-2026",
    "trade_time": "09:30",
    "instrument_type": "EQ",
    "exchange": "NSE",
    "product_type": "MIS"
}

r = requests.post(f"{API}/admin/backdate-position", json=payload, headers=headers)
print('Backdate status', r.status_code)
print('Backdate response:', r.text)
