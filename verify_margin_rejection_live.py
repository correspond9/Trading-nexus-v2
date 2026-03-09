import requests

requests.packages.urllib3.disable_warnings()
BASE = "https://tradingnexus.pro/api/v2"

login = requests.post(
    f"{BASE}/auth/login",
    json={"mobile": "8888888888", "password": "admin123"},
    verify=False,
    timeout=20,
)
print("login", login.status_code)
if login.status_code != 200:
    print(login.text)
    raise SystemExit(1)

token = login.json().get("access_token")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

body = {
    "user_id": "098c818d-39e1-40a6-97f0-66472a011442",
    "instrument_token": 16249,
    "symbol": "CCAVENUE",
    "exchange_segment": "NSE_EQ",
    "side": "BUY",
    "order_type": "LIMIT",
    "product_type": "NORMAL",
    "quantity": 500000,
    "limit_price": 15.08,
}

resp = requests.post(
    f"{BASE}/trading/orders",
    headers=headers,
    json=body,
    verify=False,
    timeout=30,
)
print("order_status", resp.status_code)
print(resp.text)
