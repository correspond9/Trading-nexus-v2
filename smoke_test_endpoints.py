import requests
import json

base_url = "https://tradingnexus.pro/api/v2"
headers = {
    'X-AUTH': '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466',
    'X-USER': 'x8gg0og8440wkgc8ow0ococs',
    'Content-Type': 'application/json'
}

print("=" * 70)
print("SMOKE TEST: Trading Nexus API Endpoints")
print("=" * 70)

# Test 1: Health
print("\n1. GET /health")
try:
    r = requests.get(f"{base_url}/health", timeout=5)
    print(f"   Status: {r.status_code}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

# Test 2: Auth me
print("\n2. GET /auth/me")
try:
    r = requests.get(f"{base_url}/auth/me", headers=headers, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✓ User: {r.json().get('data', {}).get('username', 'N/A')}")
    else:
        print(f"   Error: {r.text[:100]}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

# Test 3: Margin Calculate
print("\n3. POST /margin/calculate (Equity)")
payload = {
    "symbol": "RELIANCE",
    "token": 2885,
    "exchange": "NSE",
    "quantity": 1,
    "price": 1430.0,
    "product_type": "MIS",
    "side": "BUY",
    "user_id": "x8gg0og8440wkgc8ow0ococs"
}
try:
    r = requests.post(f"{base_url}/margin/calculate", json=payload, headers=headers, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get('data', {})
        print(f"   ✓ Required Margin: ₹{data.get('required_margin', 0)}")
    else:
        print(f"   Error: {r.text[:150]}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

# Test 4: Margin Account
print("\n4. GET /margin/account")
try:
    r = requests.get(f"{base_url}/margin/account?user_id=x8gg0og8440wkgc8ow0ococs", headers=headers, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get('data', {})
        print(f"   ✓ Available Margin: ₹{data.get('available_margin', 0)}")
    else:
        print(f"   Error: {r.text[:150]}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

# Test 5: Get Watchlist
print("\n5. GET /watchlist/1")
try:
    r = requests.get(f"{base_url}/watchlist/1", headers=headers, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        items = r.json().get('data', {}).get('items', [])
        print(f"   ✓ Items in watchlist: {len(items)}")
    else:
        print(f"   Error: {r.text[:150]}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

# Test 6: Place Order
print("\n6. POST /trading/orders")
order_payload = {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "token": 2885,
    "order_type": "MARKET",
    "product_type": "MIS",
    "side": "BUY",
    "quantity": 1,
    "price": 1430.0,
    "user_id": "x8gg0og8440wkgc8ow0ococs"
}
try:
    r = requests.post(f"{base_url}/trading/orders", json=order_payload, headers=headers, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code in [200, 201]:
        print(f"   ✓ Order placed successfully")
    else:
        print(f"   Error: {r.text[:150]}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

# Test 7: Get Orders
print("\n7. GET /trading/orders")
try:
    r = requests.get(f"{base_url}/trading/orders?user_id=x8gg0og8440wkgc8ow0ococs", headers=headers, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        orders = r.json().get('data', {}).get('orders', [])
        print(f"   ✓ Orders retrieved: {len(orders)}")
    else:
        print(f"   Error: {r.text[:150]}")
except Exception as e:
    print(f"   Error: {str(e)[:60]}")

print("\n" + "=" * 70)
