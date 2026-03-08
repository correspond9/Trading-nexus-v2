"""
QA Test Script - Phase 2 & 3: Complete Testing with Correct Endpoints
====================================================================
Tests all user roles with CORRECTED API paths + Market closed validation
"""
import httpx
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v2"

# Test credentials
USERS = {
    "SUPER_ADMIN": {"mobile": "9999999999", "password": "admin123"},
    "ADMIN": {"mobile": "8888888888", "password": "admin123"},
    "SUPER_USER": {"mobile": "6666666666", "password": "super123"},
    "USER": {"mobile": "7777777777", "password": "user123"},
}

# Endpoints with CORRECTED paths based on router analysis
ENDPOINTS_TO_TEST = [
    # Authentication
    {"method": "GET", "url": "/auth/me", "feature": "Get own profile"},
    
    # Market Data - CORRECTED prefix /market
    {"method": "GET", "url": "/market/stream-status", "feature": "View stream status"},
    
    # Watchlist
    {"method": "GET", "url": "/watchlist/{user_id}", "feature": "View own watchlist"},
    
    # Search - CORRECTED no /search prefix
    {"method": "GET", "url": "/instruments/search?q=NIFTY", "feature": "Search instruments"},
    
    # Orders - CORRECTED prefix /trading/orders
    {"method": "GET", "url": "/trading/orders", "feature": "View own pending orders"},
    {"method": "GET", "url": "/trading/orders/executed", "feature": "View own executed orders"},
    
    # Positions - CORRECTED prefix /portfolio/positions
    {"method": "GET", "url": "/portfolio/positions", "feature": "View own positions"},
    {"method": "GET", "url": "/portfolio/positions/pnl/summary", "feature": "View own P&L summary"},
    
    # Margin
    {"method": "GET", "url": "/margin/account", "feature": "View margin account"},
    
    # Ledger
    {"method": "GET", "url": "/ledger", "feature": "View ledger"},
    
    # Admin features
    {"method": "GET", "url": "/admin/users", "feature": "View all users"},
    {"method": "GET", "url": "/payouts", "feature": "View payouts"},
    {"method": "GET", "url": "/admin/positions/userwise", "feature": "View all user positions"},
    {"method": "GET", "url": "/admin/credentials", "feature": "View Dhan credentials"},
    {"method": "GET", "url": "/admin/dhan/status", "feature": "View Dhan connection status"},
    {"method": "GET", "url": "/admin/schedulers", "feature": "View schedulers"},
    {"method": "GET", "url": "/admin/vps-monitor/status", "feature": "View VPS monitor"},
]


async def login(client: httpx.AsyncClient, mobile: str, password: str) -> Dict[str, Any]:
    """Login and return session info"""
    try:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"mobile": mobile, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            client.headers.update({"X-AUTH": data["access_token"]})
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.text, "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e), "status": 0}


async def test_endpoint(
    client: httpx.AsyncClient, 
    method: str, 
    url: str, 
    user_id: str
) -> Dict[str, Any]:
    """Test an endpoint and return result"""
    url = url.replace("{user_id}", user_id)
    
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{url}")
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{url}")
        
        return {
            "status_code": response.status_code,
            "accessible": 200 <= response.status_code < 300,
            "response": response.text[:200] if len(response.text) > 200 else response.text
        }
    except Exception as e:
        return {
            "status_code": 0,
            "accessible": False,
            "error": str(e)
        }


async def test_role(role: str, credentials: Dict[str, str]):
    """Test a specific user role"""
    print(f"\n{'='*80}")
    print(f"TESTING ROLE: {role}")
    print(f"Mobile: {credentials['mobile']}")
    print(f"{'='*80}\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Login
        print("1. Attempting login...")
        login_result = await login(client, credentials["mobile"], credentials["password"])
        
        if not login_result["success"]:
            print(f"[FAIL] Login failed: {login_result.get('error', 'Unknown error')}")
            return {
                "role": role,
                "mobile": credentials["mobile"],
                "login_success": False,
                "login_error": login_result.get("error"),
                "endpoints": []
            }
        
        print("[PASS] Login succeeded")
        user_data = login_result['data'].get('user', {})
        print(f"   Name: {user_data.get('name')}")
        print(f"   Role: {user_data.get('role')}")
        
        # Test all endpoints
        print(f"\n2. Testing endpoint access...")
        results = []
        
        for endpoint_config in ENDPOINTS_TO_TEST:
            endpoint_url = endpoint_config["url"]
            method = endpoint_config["method"]
            feature = endpoint_config["feature"]
            
            result = await test_endpoint(client, method, endpoint_url, user_data.get('id', 'unknown'))
            
            status = "PASS" if result["accessible"] else "FAIL"
            status_code = result['status_code']
            display_url = endpoint_url if len(endpoint_url) < 45 else endpoint_url[:42] + "..."
            
            print(f"   [{status}] [{status_code:3}] {method:4} {display_url:45} - {feature}")
            
            results.append({
                "feature": feature,
                "endpoint": f"{method} {endpoint_url}",
                "accessible": result["accessible"],
                "status_code": result["status_code"],
                "response_preview": result.get("response", "")[:150]
            })
        
        return {
            "role": role,
            "mobile": credentials["mobile"],
            "login_success": True,
            "user_data": user_data,
            "endpoints": results
        }


async def test_market_closed_behavior():
    """Phase 3: Test market closed behavior"""
    print(f"\n{'='*80}")
    print("PHASE 3: MARKET CLOSED BEHAVIOR VALIDATION")
    print(f"Current time: {datetime.now()}")
    print(f"Expected: Market should be CLOSED (Sunday)")
    print(f"{'='*80}\n")
    
    # Login as a test user
    async with httpx.AsyncClient(timeout=10.0) as client:
        login_result = await login(client, "7777777777", "user123")
        if not login_result["success"]:
            print("[FAIL] Cannot test market closed behavior - login failed")
            return {"success": False, "error": "Login failed"}
        
        print("[INFO] Testing order placement during market closed hours...\n")
        
        # Try to place a simple buy order
        order_payload = {
            "instrument_token": "1",  # Dummy token
            "exchange_segment": "NSE_EQ",
            "transaction_type": "BUY",
            "quantity": 1,
            "order_type": "MARKET",
            "product_type": "INTRADAY",
            "price": 0
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/trading/orders",
                json=order_payload
            )
            
            print(f"Order placement response: {response.status_code}")
            print(f"Response body: {response.text[:300]}\n")
            
            if response.status_code == 400 or response.status_code == 403:
                response_data = response.json()
                if "market" in response_data.get("detail", "").lower() or \
                   "closed" in response_data.get("detail", "").lower():
                    print("[PASS] Order correctly rejected - market closed validation working")
                    return {
                        "success": True,
                        "validation_working": True,
                        "status_code": response.status_code,
                        "message": response_data.get("detail")
                    }
                else:
                    print(f"[WARN] Order rejected but not due to market hours: {response_data.get('detail')}")
                    return {
                        "success": True,
                        "validation_working": False,
                        "status_code": response.status_code,
                        "message": response_data.get("detail")
                    }
            elif response.status_code == 201:
                print("[FAIL] Order was ACCEPTED during market closed hours! Market validation not working!")
                return {
                    "success": True,
                    "validation_working": False,
                    "status_code": response.status_code,
                    "message": "Order accepted when market should be closed"
                }
            else:
                print(f"[UNKNOWN] Unexpected response: {response.status_code}")
                return {
                    "success": True,
                    "validation_working": "unknown",
                    "status_code": response.status_code,
                    "message": response.text[:200]
                }
                
        except Exception as e:
            print(f"[ERROR] Exception during test: {e}")
            return {"success": False, "error": str(e)}


async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("TRADING NEXUS - COMPREHENSIVE QA TESTING")
    print("Phase 2: Role Access (CORRECTED) + Phase 3: Market Closed Validation")
    print("="*80)
    
    all_results = []
    
    # Test each role
    for role, credentials in USERS.items():
        result = await test_role(role, credentials)
        all_results.append(result)
        await asyncio.sleep(0.5)
    
    # Phase 3: Market closed validation
    market_closed_result = await test_market_closed_behavior()
    
    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY - ROLE ACCESS MATRIX")
    print(f"{'='*80}\n")
    
    features = [ep["feature"] for ep in ENDPOINTS_TO_TEST]
    
    print(f"{'Feature':<50} {'SUPER_ADMIN':<15} {'ADMIN':<15} {'SUPER_USER':<15} {'USER':<15}")
    print("-" * 110)
    
    for feature in features:
        row = f"{feature:<50}"
        for result in all_results:
            if result["login_success"]:
                ep_result = next((ep for ep in result["endpoints"] if ep["feature"] == feature), None)
                access = "[PASS]" if ep_result and ep_result["accessible"] else "[FAIL]"
                row += f"{access:<15}"
            else:
                row += f"{'[LOGIN FAIL]':<15}"
        print(row)
    
    # Save results
    output_data = {
        "test_date": str(datetime.now()),
        "role_tests": all_results,
        "market_closed_test": market_closed_result
    }
    
    with open("QA_COMPREHENSIVE_TEST_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n[INFO] Results saved to: QA_COMPREHENSIVE_TEST_RESULTS.json")
    
    return output_data


if __name__ == "__main__":
    asyncio.run(main())
