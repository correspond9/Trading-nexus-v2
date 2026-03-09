#!/usr/bin/env python3
"""
TRADING NEXUS — PHASE 3: ROLE-BASED ACCESS TESTING

This phase systematically tests that each role can only access their entitled features:
- SUPER_ADMIN: Full system access (credentials, users,trading operations, admin operations)
- ADMIN: User management, account management, trading oversight
- SUPER_USER: Trading with elevated privileges (can trade for self)
- USER: Basic trading (can only manage own account)
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v2"

# Test credentials from migrations
CREDS = {
    "SUPER_ADMIN": ("9999999999", "admin123"),
    "ADMIN": ("8888888888", "admin123"),
    "USER": ("7777777777", "user123"),
    "SUPER_USER": ("6666666666", "super123"),
}

class RoleBasedTester:
    def __init__(self):
        self.tokens = {}
        self.results = {}
    
    async def login_all_roles(self):
        """Login all 4 roles and cache tokens."""
        async with httpx.AsyncClient(timeout=10) as client:
            for role, (mobile, password) in CREDS.items():
                resp = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={"mobile": mobile, "password": password}
                )
                if resp.status_code == 200:
                    self.tokens[role] = resp.json()["access_token"]
                    print(f"✓ Logged in as {role}")
    
    def get_headers(self, role: str):
        """Get auth headers for a role."""
        return {"X-AUTH": self.tokens.get(role, "")}
    
    async def test_endpoint(self, role: str, method: str, endpoint: str, expected_code: int = 200):
        """Test a single endpoint for a role."""
        headers = self.get_headers(role)
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                if method == "GET":
                    resp = await client.get(f"{BASE_URL}{endpoint}", headers=headers)
                elif method == "POST":
                    resp = await client.post(f"{BASE_URL}{endpoint}", json={}, headers=headers)
                else:
                    return None
                
                success = resp.status_code == expected_code
                return {
                    "status": "PASS" if success else "FAIL",
                    "code": resp.status_code,
                    "expected": expected_code
                }
            except Exception as exc:
                return {"status": "ERROR", "message": str(exc)}
    
    async def test_super_admin(self):
        """SUPER_ADMIN should have access to everything."""
        print("\n" + "="*80)
        print("TESTING SUPER_ADMIN ROLE")
        print("="*80)
        
        tests = [
            ("GET", "/auth/me", 200, "View own profile"),
            ("GET", "/admin/credentials", 200, "View DhanHQ credentials"),
            ("GET", "/admin/users", 200, "List all users"),
            ("GET", "/ledger", 200, "View own ledger"),
            ("GET", "/trading/orders", 200, "View orders"),
            ("GET", "/margin/account", 200, "View margin account"),
        ]
        
        for method, endpoint, expected, description in tests:
            result = await self.test_endpoint("SUPER_ADMIN", method, endpoint, expected)
            status = "✓" if result and result["status"] == "PASS" else "✗"
            print(f"{status} {description:40} {endpoint}")
            if result:
                self.results.setdefault("SUPER_ADMIN", []).append({
                    "test": description,
                    "result": result["status"],
                    "code": result.get("code")
                })
    
    async def test_admin(self):
        """ADMIN should have user management and trading oversight."""
        print("\n" + "="*80)
        print("TESTING ADMIN ROLE")
        print("="*80)
        
        tests = [
            ("GET", "/auth/me", 200, "View own profile"),
            ("GET", "/admin/users", 200, "List all users"),
            ("GET", "/admin/credentials", 403, "SHOULD NOT access credentials (403)"),
            ("GET", "/ledger", 200, "View own ledger"),
            ("GET", "/trading/orders", 200, "View orders"),
            ("GET", "/margin/account", 200, "View margin account"),
        ]
        
        for method, endpoint, expected, description in tests:
            result = await self.test_endpoint("ADMIN", method, endpoint, expected)
            status = "✓" if result and result["status"] == "PASS" else "✗"
            print(f"{status} {description:40} {endpoint}")
            if result:
                self.results.setdefault("ADMIN", []).append({
                    "test": description,
                    "result": result["status"],
                    "code": result.get("code")
                })
    
    async def test_super_user(self):
        """SUPER_USER should have basic access + no admin features."""
        print("\n" + "="*80)
        print("TESTING SUPER_USER ROLE")
        print("="*80)
        
        tests = [
            ("GET", "/auth/me", 200, "View own profile"),
            ("GET", "/admin/users", 403, "SHOULD NOT access user management (403)"),
            ("GET", "/ledger", 200, "View own ledger"),
            ("GET", "/trading/orders", 200, "View orders"),
            ("GET", "/margin/account", 200, "View margin account"),
        ]
        
        for method, endpoint, expected, description in tests:
            result = await self.test_endpoint("SUPER_USER", method, endpoint, expected)
            status = "✓" if result and result["status"] == "PASS" else "✗"
            print(f"{status} {description:40} {endpoint}")
            if result:
                self.results.setdefault("SUPER_USER", []).append({
                    "test": description,
                    "result": result["status"],
                    "code": result.get("code")
                })
    
    async def test_user(self):
        """USER should only access their own data, no admin features."""
        print("\n" + "="*80)
        print("TESTING USER ROLE")
        print("="*80)
        
        tests = [
            ("GET", "/auth/me", 200, "View own profile"),
            ("GET", "/admin/users", 403, "SHOULD NOT access user management (403)"),
            ("GET", "/admin/credentials", 403, "SHOULD NOT access credentials (403)"),
            ("GET", "/ledger", 200, "View own ledger"),
            ("GET", "/trading/orders", 200, "View orders"),
            ("GET", "/margin/account", 200, "View margin account"),
        ]
        
        for method, endpoint, expected, description in tests:
            result = await self.test_endpoint("USER", method, endpoint, expected)
            status = "✓" if result and result["status"] == "PASS" else "✗"
            print(f"{status} {description:40} {endpoint}")
            if result:
                self.results.setdefault("USER", []).append({
                    "test": description,
                    "result": result["status"],
                    "code": result.get("code")
                })
    
    async def test_permission_boundaries(self):
        """Test specific permission boundaries."""
        print("\n" + "="*80)
        print("TESTING PERMISSION BOUNDARIES")
        print("="*80)
        
        print("\nTest: Non-admin USER trying to view other user's ledger")
        headers_user = self.get_headers("USER")
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/ledger?user_id=00000000-0000-0000-0000-000000000001",
                headers=headers_user
            )
            status = "✓" if resp.status_code == 403 else "✗"
            print(f"{status} USER cannot view other ledgers (expected 403, got {resp.status_code})")
        
        print("\nTest: ADMIN/SUPER_ADMIN can view other users' ledgers")
        headers_admin = self.get_headers("ADMIN")
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BASE_URL}/ledger?user_id=00000000-0000-0000-0000-000000000003",
                headers=headers_admin
            )
            status = "✓" if resp.status_code == 200 else "✗"
            print(f"{status} ADMIN can view other ledgers (expected 200, got {resp.status_code})")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("ROLE-BASED ACCESS CONTROL SUMMARY")
        print("="*80)
        
        total_tests = 0
        passed_tests = 0
        
        for role, tests in self.results.items():
            print(f"\n{role}:")
            for test in tests:
                total_tests += 1
                if test["result"] == "PASS":
                    passed_tests += 1
                    status = "✓"
                else:
                    status = "✗"
                print(f"  {status} {test['test']}")
        
        print(f"\n\nTotal: {passed_tests}/{total_tests} tests passed")
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Pass rate: {pass_rate:.1f}%")

async def main():
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " TRADING NEXUS — PHASE 3: ROLE-BASED ACCESS TESTING ".center(78) + "║")
    print("╚" + "="*78 + "╝")
    print(f"\nStart time: {datetime.now().isoformat()}")
    
    tester = RoleBasedTester()
    
    print("\nStep 1: Authenticating all roles...")
    await tester.login_all_roles()
    
    print("\nStep 2: Testing role permissions...")
    await tester.test_super_admin()
    await tester.test_admin()
    await tester.test_super_user()
    await tester.test_user()
    
    print("\nStep 3: Testing permission boundaries...")
    await tester.test_permission_boundaries()
    
    tester.print_summary()
    
    print(f"\n\nEnd time: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    asyncio.run(main())
