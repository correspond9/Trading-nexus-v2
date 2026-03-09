import requests

requests.packages.urllib3.disable_warnings()
BASE = "https://tradingnexus.pro/api/v2"
TARGET_USER_ID = "098c818d-39e1-40a6-97f0-66472a011442"

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
headers = {"Authorization": f"Bearer {token}"}

r1 = requests.get(f"{BASE}/admin/positions/userwise", headers=headers, verify=False, timeout=40)
print("userwise_status", r1.status_code)
if r1.status_code != 200:
    print(r1.text)
    raise SystemExit(1)

rows = r1.json().get("data", [])
target = next((x for x in rows if str(x.get("user_id")) == TARGET_USER_ID), None)
print("target_found", bool(target))
if target:
    print("mobile", target.get("mobile"))
    print("current_margin_usage", target.get("current_margin_usage"))
    print("pending_reserved_margin", target.get("pending_reserved_margin"))
    print("pending_orders_count", target.get("pending_orders_count"))

r2 = requests.get(f"{BASE}/admin/positions/userwise/{TARGET_USER_ID}/active-orders", headers=headers, verify=False, timeout=40)
print("active_orders_status", r2.status_code)
print(r2.text[:1200])
