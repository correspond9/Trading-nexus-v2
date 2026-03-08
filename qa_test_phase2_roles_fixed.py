"""
QA Test Script - Phase 2: User Role Testing (FIXED)
====================================================
Tests all user roles and builds a role-feature access matrix.
"""
import httpx
import asyncio
import json
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000/api/v2"

# Test credentials - CORRECTED to use mobile field
USERS = {
    "SUPER_ADMIN": {"mobile": "9999999999", "password": "admin123"},
    "ADMIN": {"mobile": "8888888888", "password": "admin123"},
    "SUPER_USER": {"mobile": "6666666666", "password": "super123"},
    "USER": {"mobile": "7777777777", "password": "user123"},
}

# Endpoints to test for each role
ENDPOINTS_TO_TEST = [
    # Authentication
    {"method": "GET", "url": "/auth/me", "feature": "Get own profile"},
    
    # Market Data (should be accessible to all)
    {"method": "GET", "url": "/market-data/stream-status", "feature": "View stream status"},
    
    # Watchlist (user_id will be replaced with actual user ID from login)
    {"method": "GET", "url": "/watchlist/{user_id}", "feature": "View own watchlist"},
    
    # Search (should be accessible to all)
    {"method": "GET", "url": "/search/instruments/search?q=NIFTY", "feature": "Search instruments"},
    
    # Orders (should be accessible to all for own orders)
    {"method": "GET", "url": "/orders", "feature": "View own pending orders"},
    {"method": "GET", "url": "/orders/executed", "feature": "View own executed orders"},
    
    # Positions (should be accessible to all for own positions)
    {"method": "GET", "url": "/positions", "feature": "View own positions"},
    {"method": "GET", "url": "/positions/pnl/summary", "feature": "View own P&L summary"},
    
    # Margin calculation (should be accessible to all)
    {"method": "GET", "url": "/margin/account", "feature": "View margin account"},
    
    # Ledger (admin only - check if endpoint exists)
    {"method": "GET", "url": "/ledger", "feature": "View ledger"},
    
    # Users management (admin only)
    {"method": "GET", "url": "/admin/users", "feature": "View all users"},
    
    # Payouts (admin only)
    {"method": "GET", "url": "/payouts", "feature": "View payouts"},
    
    # All positions userwise (admin only)
    {"method": "GET", "url": "/admin/positions/userwise", "feature": "View all user positions"},
    
    # Super admin features
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
            # Set the auth token header for subsequent requests
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
    # Replace {user_id} placeholder
    url = url.replace("{user_id}", user_id)
    
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{url}")
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{url}")
        
        return {
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "accessible": 200 <= response.status_code < 300,
            "response": response.text[:200] if len(response.text) > 200 else response.text
        }
    except Exception as e:
        return {
            "status_code": 0,
            "success": False,
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
            print(f"❌ Login FAILED: {login_result.get('error', 'Unknown error')}")
            print(f"   Status Code: {login_result.get('status', 'N/A')}")
            return {
                "role": role,
                "mobile": credentials["mobile"],
                "login_success": False,
                "login_error": login_result.get("error"),
                "endpoints": []
            }
        
        print(f"✅ Login SUCCESS")
        user_data = login_result['data'].get('user', {})
        print(f"   ID: {user_data.get('id')}")
        print(f"   Name: {user_data.get('name')}")
        print(f"   Role: {user_data.get('role')}")
        print(f"   Mobile: {user_data.get('mobile')}")
        
        # Test all endpoints
        print(f"\n2. Testing endpoint access...")
        results = []
        
        for endpoint_config in ENDPOINTS_TO_TEST:
            endpoint_url = endpoint_config["url"]
            method = endpoint_config["method"]
            feature = endpoint_config["feature"]
            
            result = await test_endpoint(
                client, 
                method, 
                endpoint_url, 
                user_data.get('id', 'unknown')
            )
            
            status_icon = "✅" if result["accessible"] else "❌"
            status_code = result['status_code']
            
            # Truncate URL for display
            display_url = endpoint_url if len(endpoint_url) < 50 else endpoint_url[:47] + "..."
            
            print(f"   {status_icon} [{status_code:3}] {method:4} {display_url:50} - {feature}")
            
            results.append({
                "feature": feature,
                "endpoint": f"{method} {endpoint_url}",
                "accessible": result["accessible"],
                "status_code": result["status_code"],
                "response_preview": result.get("response", "")[:100]
            })
        
        return {
            "role": role,
            "mobile": credentials["mobile"],
            "login_success": True,
            "user_data": user_data,
            "endpoints": results
        }


async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("TRADING NEXUS - USER ROLE TESTING")
    print("Phase 2: Role-Based Access Matrix")
    print("="*80)
    
    all_results = []
    
    # Test each role
    for role, credentials in USERS.items():
        result = await test_role(role, credentials)
        all_results.append(result)
        await asyncio.sleep(0.5)  # Brief delay between role tests
    
    # Generate summary
    print(f"\n\n{'='*80}")
    print("ROLE-FEATURE ACCESS MATRIX SUMMARY")
    print(f"{'='*80}\n")
    
    # Build matrix
    features = [ep["feature"] for ep in ENDPOINTS_TO_TEST]
    
    print(f"{'Feature':<50} {'SUPER_ADMIN':<15} {'ADMIN':<15} {'SUPER_USER':<15} {'USER':<15}")
    print("-" * 110)
    
    for feature in features:
        row = f"{feature:<50}"
        for result in all_results:
            if result["login_success"]:
                endpoint_result = next(
                    (ep for ep in result["endpoints"] if ep["feature"] == feature),
                    None
                )
                if endpoint_result:
                    access = "✅ YES" if endpoint_result["accessible"] else "❌ NO"
                    row += f"{access:<15}"
                else:
                    row += f"{'? N/A':<15}"
            else:
                row += f"{'❌ LOGIN FAIL':<15}"
        print(row)
    
    # Save detailed results to JSON
    with open("QA_ROLE_TEST_RESULTS.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✅ Detailed results saved to: QA_ROLE_TEST_RESULTS.json")
    
    # Generate markdown report
    generate_markdown_report(all_results)
    
    return all_results


def generate_markdown_report(results: List[Dict[str, Any]]):
    """Generate a markdown report of role testing"""
    
    report = """# USER ROLE TEST RESULTS
**Date:** March 8, 2026  
**Phase:** 2 - Role-Based Access Testing

---

## Login Test Results

| Role | Mobile | Login Status | Actual Role | User Name |
|------|--------|--------------|-------------|-----------|
"""
    
    for result in results:
        role = result["role"]
        mobile = result["mobile"]
        login_status = "✅ SUCCESS" if result["login_success"] else "❌ FAILED"
        actual_role = result.get("user_data", {}).get("role", "N/A") if result["login_success"] else "N/A"
        user_name = result.get("user_data", {}).get("name", "N/A") if result["login_success"] else "N/A"
        report += f"| {role} | {mobile} | {login_status} | {actual_role} | {user_name} |\n"
    
    report += "\n---\n\n## Role-Feature Access Matrix\n\n"
    report += "| Feature | SUPER_ADMIN | ADMIN | SUPER_USER | USER |\n"
    report += "|---------|-------------|-------|------------|------|\n"
    
    # Get all unique features
    features = []
    for result in results:
        if result["login_success"]:
            for ep in result["endpoints"]:
                if ep["feature"] not in features:
                    features.append(ep["feature"])
    
    # Build matrix
    for feature in features:
        row = f"| {feature} |"
        for result in results:
            if result["login_success"]:
                endpoint_result = next(
                    (ep for ep in result["endpoints"] if ep["feature"] == feature),
                    None
                )
                if endpoint_result:
                    access = "✅" if endpoint_result["accessible"] else "❌"
                    row += f" {access} |"
                else:
                    row += " ? |"
            else:
                row += " ❌ |"
        report += row + "\n"
    
    report += "\n---\n\n## Detailed Results by Role\n\n"
    
    for result in results:
        report += f"### {result['role']}\n\n"
        
        if not result["login_success"]:
            report += f"**Login Failed:** {result.get('login_error', 'Unknown error')}\n\n"
            continue
        
        user_data = result.get("user_data", {})
        report += f"- **User ID:** {user_data.get('id')}\n"
        report += f"- **Name:** {user_data.get('name', 'N/A')}\n"
        report += f"- **Mobile:** {user_data.get('mobile')}\n"
        report += f"- **Role:** {user_data.get('role')}\n\n"
        
        report += "**Endpoint Access:**\n\n"
        report += "| Endpoint | Status | Accessible |\n"
        report += "|----------|--------|------------|\n"
        
        for ep in result["endpoints"]:
            status_icon = "✅" if ep["accessible"] else "❌"
            report += f"| `{ep['endpoint']}` | {ep['status_code']} | {status_icon} |\n"
        
        report += "\n"
    
    with open("QA_ROLE_TEST_REPORT.md", "w") as f:
        f.write(report)
    
    print(f"✅ Markdown report saved to: QA_ROLE_TEST_REPORT.md")


if __name__ == "__main__":
    asyncio.run(main())
