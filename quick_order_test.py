"""Quick test to verify order placement endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v2"

# Login
print("Logging in...")
login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={"mobile": "6666666666", "password": "super123"}
)
print(f"Login status: {login_resp.status_code}")
if login_resp.status_code == 200:
    token = login_resp.json()["access_token"]
    print(f"Token obtained: {token[:30]}...")
    
    # Try placing an order
    print("\nPlacing order...")
    order_data = {
        "symbol": "FEDERALBNK",
        "exchange_segment": "NSE_EQ",
        "transaction_type": "BUY",
        "quantity": 1,
        "order_type": "MARKET",
        "product_type": "MIS",
        "price": 0,
        "trigger_price": 0,
        "disclosed_quantity": 0,
        "validity": "DAY"
    }
    
    order_resp = requests.post(
        f"{BASE_URL}/trading/orders",
        json=order_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Order status: {order_resp.status_code}")
    print(f"Response: {json.dumps(order_resp.json(), indent=2)}")
else:
    print(f"Login failed: {login_resp.text}")
