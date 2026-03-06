import requests
import json

# Login as admin
login_response = requests.post(
    "https://tradingnexus.pro/api/v2/auth/login",
    json={"mobile": "9999999999", "password": "admin123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

user_id = "6785692d-8f36-4183-addb-16c96ea95a88"

# 1. Get positions
print("=== ALL POSITIONS ===")
pos_response = requests.get(f"https://tradingnexus.pro/api/v2/admin/users/{user_id}/positions", headers=headers)
print(f"Status: {pos_response.status_code}")
pos_data = pos_response.json()
if isinstance(pos_data, list):
    for p in pos_data:
        print(f"  {p.get('symbol')} | qty={p.get('qty')} | avg_price={p.get('avg_price')} | status={p.get('status')} | product={p.get('product_type')} | opened={p.get('opened_at','')[:10]} | pos_id={p.get('position_id','')[:8]}")
else:
    print(json.dumps(pos_data, indent=2))

print()

# 2. Get ledger
print("=== LEDGER ENTRIES ===")
ledger_response = requests.get(f"https://tradingnexus.pro/api/v2/admin/users/{user_id}/ledger", headers=headers)
print(f"Status: {ledger_response.status_code}")
led_data = ledger_response.json()
if isinstance(led_data, list):
    print(f"Total: {len(led_data)}")
    for e in led_data:
        debit = e.get('debit') or 0
        credit = e.get('credit') or 0
        bal = e.get('balance_after', 0)
        desc = e.get('description', '')
        dt = e.get('created_at', '')[:10]
        sign = f"-{debit}" if debit else f"+{credit}"
        print(f"  [{dt}] {sign} | bal={bal} | {desc[:60]}")
else:
    print(json.dumps(led_data, indent=2))

print()

# 3. Get wallet balance
print("=== USER DETAILS ===")
user_response = requests.get(f"https://tradingnexus.pro/api/v2/admin/users/{user_id}", headers=headers)
print(f"Status: {user_response.status_code}")
u = user_response.json()
if isinstance(u, dict):
    print(f"  Name: {u.get('name')}")
    print(f"  Mobile: {u.get('mobile')}")
    print(f"  Created: {u.get('created_at','')[:10]}")
    print(f"  Wallet: {u.get('wallet_balance')}")
    for k, v in u.items():
        if 'balance' in k.lower() or 'fund' in k.lower():
            print(f"  {k}: {v}")
else:
    print(json.dumps(u, indent=2))
