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
headers = {"Authorization": f"Bearer {token}"}

# affected user from prior tests
uid = "098c818d-39e1-40a6-97f0-66472a011442"
resp = requests.get(f"{BASE}/margin?user_id={uid}", headers=headers, verify=False, timeout=30)
print("margin_status", resp.status_code)
print(resp.text)
