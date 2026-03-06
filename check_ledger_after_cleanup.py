import requests
import json

# Login as the user directly
login_response = requests.post(
    "https://tradingnexus.pro/api/v2/auth/login",
    json={"mobile": "9326890165", "password": "admin123"}
)
print(f"Login status: {login_response.status_code}")
if login_response.status_code != 200:
    print("Login failed:")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get wallet balance
wallet_response = requests.get(
    "https://tradingnexus.pro/api/v2/user/wallet",
    headers=headers
)
print(f"\n=== WALLET BALANCE ===")
print(f"Status: {wallet_response.status_code}")
wallet_data = wallet_response.json()
print(json.dumps(wallet_data, indent=2))

# Get ledger
ledger_response = requests.get(
    "https://tradingnexus.pro/api/v2/ledger",
    headers=headers
)
print(f"\n=== LEDGER ENTRIES ===")
print(f"Status: {ledger_response.status_code}")
ledger_data = ledger_response.json()
if isinstance(ledger_data, list):
    print(f"Total entries: {len(ledger_data)}")
    for idx, entry in enumerate(ledger_data[:15], 1):  # Show first 15
        print(f"\n{idx}. {entry.get('description', 'N/A')}")
        print(f"   Created: {entry.get('created_at', 'N/A')[:19]}")
        debit = entry.get('debit') or 0
        credit = entry.get('credit') or 0
        balance = entry.get('balance_after', 0)
        if debit:
            print(f"   Debit: -₹{debit:,.2f}")
        if credit:
            print(f"   Credit: +₹{credit:,.2f}")
        print(f"   Balance: ₹{balance:,.2f}")
else:
    print(json.dumps(ledger_data, indent=2))


