#!/usr/bin/env python3
"""
Direct endpoint testing for Trading Nexus backend
Tests all critical trading, user management, and reporting endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v2"

def get_token(mobile, password):
    """Get authentication token"""
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={"mobile": mobile, "password": password})
        if r.status_code == 200:
            return r.json()["access_token"]
        return None
    except:
        return None

def test_endpoint(method, endpoint, role, token=None, data=None, params=None):
    """Test an endpoint and return status + response"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            r = requests.get(url, headers=headers, params=params, timeout=3)
        elif method.upper() == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=3)
        elif method.upper() == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=3)
        else:
            return None, "Invalid method"
        
        return r.status_code, r.json() if r.text else {}
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)[:100]

def print_result(endpoint, status, details=""):
    """Print test result with formatting"""
    if status is None:
        symbol = "[ERROR]"
    elif status == 200:
        symbol = "[PASS]"
    elif status == 404:
        symbol = "[NOTFOUND]"
    elif status >= 400:
        symbol = "[FAIL]"
    else:
        symbol = "[OK]"
    
    print(f"{symbol} {endpoint:<50} Status: {status if status else 'ERROR':<4} {details}")

# ============================================================
# GET TOKENS FOR ALL ROLES
# ============================================================

print("\n" + "="*80)
print("TRADING NEXUS ENDPOINT VERIFICATION")
print("="*80 + "\n")

print("Authenticating users...")
tokens = {
    "SUPER_ADMIN": get_token("9999999999", "admin123"),
    "ADMIN": get_token("8888888888", "admin123"),
    "SUPER_USER": get_token("6666666666", "super123"),
    "USER": get_token("7777777777", "user123"),
}

for role, token in tokens.items():
    status = "[OK]" if token else "[FAIL]"
    print(f"  {status} {role:<20} {token[:16] if token else 'FAILED'}...")

# ============================================================
# TEST ENDPOINTS BY CATEGORY
# ============================================================

print("\n" + "-"*80)
print("AUTHENTICATION ENDPOINTS")
print("-"*80)

status, resp = test_endpoint("GET", "/auth/me", "ADMIN", tokens["ADMIN"])
print_result("/auth/me", status, f"User: {resp.get('name', 'N/A')}")

print("\n" + "-"*80)
print("ADMIN MANAGEMENT ENDPOINTS")
print("-"*80)

status, resp = test_endpoint("GET", "/admin/users", "ADMIN", tokens["ADMIN"])
user_count = len(resp.get("data", [])) if isinstance(resp.get("data"), list) else "?"
print_result("/admin/users", status, f"Users: {user_count}")

status, resp = test_endpoint("GET", "/admin/dhan/status", "ADMIN", tokens["ADMIN"])
print_result("/admin/dhan/status", status)

status, resp = test_endpoint("GET", "/admin/notifications", "ADMIN", tokens["ADMIN"])
print_result("/admin/notifications", status)

print("\n" + "-"*80)
print("TRADING - ORDERS")
print("-"*80)

status, resp = test_endpoint("GET", "/trading/orders/", "USER", tokens["USER"])
order_count = len(resp.get("data", [])) if isinstance(resp.get("data"), list) else "?"
print_result("/trading/orders/", status, f"Orders: {order_count}")

status, resp = test_endpoint("GET", "/trading/orders/?current_session_only=true", "USER", tokens["USER"])
print_result("/trading/orders/?current_session_only=true", status)

status, resp = test_endpoint("GET", "/trading/orders/?limit=100", "USER", tokens["USER"])
print_result("/trading/orders/?limit=100", status)

print("\n" + "-"*80)
print("TRADING - POSITIONS")
print("-"*80)

status, resp = test_endpoint("GET", "/portfolio/positions/", "USER", tokens["USER"])
pos_count = len(resp.get("data", [])) if isinstance(resp.get("data"), list) else "?"
print_result("/portfolio/positions/", status, f"Positions: {pos_count}")

status, resp = test_endpoint("GET", "/portfolio/positions/?type=open", "USER", tokens["USER"])
print_result("/portfolio/positions/?type=open", status)

status, resp = test_endpoint("GET", "/portfolio/positions/?user_id=all", "ADMIN", tokens["ADMIN"])
print_result("/portfolio/positions/?user_id=all (ADMIN)", status)

print("\n" + "-"*80)
print("OPTIONS - OPTION CHAIN")
print("-"*80)

status, resp = test_endpoint("GET", "/options/", "USER", tokens["USER"])
print_result("/options/", status)

status, resp = test_endpoint("GET", "/options/?symbol=NIFTY", "USER", tokens["USER"])
print_result("/options/?symbol=NIFTY", status)

status, resp = test_endpoint("GET", "/options/?symbol=BANKNIFTY&expiry=24FEB25", "USER", tokens["USER"])
print_result("/options/?symbol=BANKNIFTY&expiry=24FEB25", status)

print("\n" + "-"*80)
print("MARKET DATA")
print("-"*80)

status, resp = test_endpoint("GET", "/market/hours/NSE", "USER", tokens["USER"])
print_result("/market/hours/NSE", status)

status, resp = test_endpoint("GET", "/market/hours/BSE", "USER", tokens["USER"])
print_result("/market/hours/BSE", status)

status, resp = test_endpoint("GET", "/market/hours/MCX", "USER", tokens["USER"])
print_result("/market/hours/MCX", status)

status, resp = test_endpoint("GET", "/market/underlying-ltp/NIFTY", "USER", tokens["USER"])
print_result("/market/underlying-ltp/NIFTY", status)

status, resp = test_endpoint("GET", "/market/underlying-ltp/BANKNIFTY", "USER", tokens["USER"])
print_result("/market/underlying-ltp/BANKNIFTY", status)

print("\n" + "-"*80)
print("MARGIN SYSTEM")
print("-"*80)

status, resp = test_endpoint("GET", "/margin/nse", "SUPER_USER", tokens["SUPER_USER"])
print_result("/margin/nse", status)

status, resp = test_endpoint("GET", "/margin/bse", "SUPER_USER", tokens["SUPER_USER"])
print_result("/margin/bse", status)

status, resp = test_endpoint("GET", "/margin/mcx", "SUPER_USER", tokens["SUPER_USER"])
print_result("/margin/mcx", status)

status, resp = test_endpoint("GET", "/margin/block", "SUPER_USER", tokens["SUPER_USER"])
print_result("/margin/block", status)

print("\n" + "-"*80)
print("LEDGER & PAYOUTS")
print("-"*80)

status, resp = test_endpoint("GET", "/ledger/", "USER", tokens["USER"])
ledger_count = len(resp.get("data", [])) if isinstance(resp.get("data"), list) else "?"
print_result("/ledger/", status, f"Entries: {ledger_count}")

status, resp = test_endpoint("GET", "/payouts/", "USER", tokens["USER"])
payout_count = len(resp.get("data", [])) if isinstance(resp.get("data"), list) else "?"
print_result("/payouts/ (USER)", status, f"Payouts: {payout_count}")

status, resp = test_endpoint("GET", "/payouts/", "ADMIN", tokens["ADMIN"])
payout_count = len(resp.get("data", [])) if isinstance(resp.get("data"), list) else "?"
print_result("/payouts/ (ADMIN)", status, f"Payouts: {payout_count}")

print("\n" + "-"*80)
print("WATCHLIST & SEARCH")
print("-"*80)

status, resp = test_endpoint("GET", "/watchlist/", "USER", tokens["USER"])
print_result("/watchlist/", status)

status, resp = test_endpoint("GET", "/search/scrips?q=NIFTY", "USER", tokens["USER"])
print_result("/search/scrips?q=NIFTY", status)

print("\n" + "-"*80)
print("BASKETS")
print("-"*80)

status, resp = test_endpoint("GET", "/trading/basket-orders/", "USER", tokens["USER"])
print_result("/trading/basket-orders/", status)

print("\n" + "-"*80)
print("HEALTH CHECK")
print("-"*80)

status, resp = test_endpoint("GET", "/health", "", None)
print_result("/health", status)

print("\n" + "="*80)
print("ENDPOINT VERIFICATION COMPLETE")
print("="*80 + "\n")
