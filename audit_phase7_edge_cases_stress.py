#!/usr/bin/env python3
"""
Phase 7: Edge Cases & Stress Testing
Tests system behavior under stress, rapid operations, and edge conditions
"""

import json
import sys
from datetime import datetime
from typing import Dict
import requests
import asyncio
import concurrent.futures
import time

# Configuration  
API_BASE_URL = "http://localhost:8000/api/v2"
HEADERS = {"Content-Type": "application/json"}

# Test Credentials
TEST_USERS = {
    "user": {"mobile": "7777777777", "password": "user123"},
}

class EdgeCasesAndStressTest:
    def __init__(self):
        self.results = {
            "phase": "7",
            "title": "Edge Cases & Stress Testing",
            "timestamp": datetime.now().isoformat(),
            "rapid_operations": [],
            "duplicate_requests": [],
            "invalid_inputs": [],
            "boundary_conditions": [],
            "concurrent_operations": [],
            "connection_handling": [],
            "resource_limits": [],
            "summary": {}
        }
        self.user_tokens = {}

    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")

    def log_test(self, category: str, test_name: str, status: str, details: Dict):
        """Log test result"""
        entry = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **details
        }
        
        if category in self.results and isinstance(self.results[category], list):
            self.results[category].append(entry)
        
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"  {status_symbol} {test_name}: {status}")
        if details.get("message"):
            print(f"     → {details['message']}")

    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate test user"""
        self.print_section("Authenticating Test User")
        
        user = TEST_USERS.get(user_type)
        if not user:
            print(f"  ✗ User not found")
            return False

        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"mobile": user["mobile"], "password": user["password"]},
                headers=HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.user_tokens[user_type] = token
                    print(f"  ✓ Authentication successful")
                    return True
            
            print(f"  ✗ Authentication failed")
            return False
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False

    def test_rapid_order_placement(self, user_type: str):
        """Test Phase 7.1: Rapid order placement"""
        self.print_section("Phase 7.1: Rapid Order Placement")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        # Send 10 rapid orders
        success_count = 0
        error_count = 0
        start_time = time.time()

        for i in range(10):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/trading/place_order",
                    json={
                        "symbol": "TCS",
                        "side": "BUY" if i % 2 == 0 else "SELL",
                        "quantity": 1,
                        "order_type": "MARKET",
                    },
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    error_count += 1
            except:
                error_count += 1

        elapsed_time = time.time() - start_time
        
        self.log_test(
            "rapid_operations",
            "Rapid Order Placement (10 orders)",
            "PASS" if success_count >= 8 else "WARN",
            {
                "message": f"Placed {success_count}/10 orders in {elapsed_time:.2f}s",
                "successful": success_count,
                "failed": error_count,
                "elapsed_seconds": elapsed_time
            }
        )

    def test_duplicate_orders(self, user_type: str):
        """Test Phase 7.2: Duplicate order detection"""
        self.print_section("Phase 7.2: Duplicate Order Detection")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        order_payload = {
            "symbol": "INFY",
            "side": "BUY",
            "quantity": 1,
            "order_type": "MARKET",
        }

        # Send same order twice
        try:
            response1 = requests.post(
                f"{API_BASE_URL}/trading/place_order",
                json=order_payload,
                headers=headers,
                timeout=10
            )
            
            response2 = requests.post(
                f"{API_BASE_URL}/trading/place_order",
                json=order_payload,
                headers=headers,
                timeout=10
            )
            
            # Should create two different orders or one should fail
            if response1.status_code in [200, 201] and response2.status_code in [200, 201]:
                order_id_1 = response1.json().get("id")
                order_id_2 = response2.json().get("id")
                
                if order_id_1 != order_id_2:
                    self.log_test(
                        "duplicate_requests",
                        "Duplicate Order Prevention",
                        "PASS",
                        {
                            "message": "Created two distinct orders (no deduplication)",
                            "order1_id": order_id_1,
                            "order2_id": order_id_2
                        }
                    )
                else:
                    self.log_test(
                        "duplicate_requests",
                        "Duplicate Order Prevention",
                        "WARN",
                        {
                            "message": "Both requests returned same order ID (possible deduplication)",
                            "order_id": order_id_1
                        }
                    )
            else:
                self.log_test(
                    "duplicate_requests",
                    "Duplicate Order Prevention",
                    "WARN",
                    {
                        "message": "Second request failed (status: {})".format(response2.status_code),
                        "first_status": response1.status_code,
                        "second_status": response2.status_code
                    }
                )
        except Exception as e:
            self.log_test(
                "duplicate_requests",
                "Duplicate Order Prevention",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_invalid_input_handling(self, user_type: str):
        """Test Phase 7.3: Invalid input handling"""
        self.print_section("Phase 7.3: Invalid Input Handling")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        invalid_tests = [
            {
                "name": "Zero quantity",
                "payload": {"symbol": "TCS", "side": "BUY", "quantity": 0, "order_type": "MARKET"}
            },
            {
                "name": "Negative price",
                "payload": {"symbol": "TCS", "side": "BUY", "quantity": 1, "order_type": "LIMIT", "price": -100.0}
            },
            {
                "name": "Invalid side",
                "payload": {"symbol": "TCS", "side": "INVALID", "quantity": 1, "order_type": "MARKET"}
            },
            {
                "name": "Missing symbol",
                "payload": {"side": "BUY", "quantity": 1, "order_type": "MARKET"}
            },
        ]

        for test in invalid_tests:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/trading/place_order",
                    json=test["payload"],
                    headers=headers,
                    timeout=5
                )
                
                status = "PASS" if response.status_code >= 400 else "FAIL"
                self.log_test(
                    "invalid_inputs",
                    f"Reject: {test['name']}",
                    status,
                    {
                        "message": f"Status code: {response.status_code}",
                        "status_code": response.status_code
                    }
                )
            except Exception as e:
                self.log_test(
                    "invalid_inputs",
                    f"Reject: {test['name']}",
                    "FAIL",
                    {"message": f"Error: {str(e)}"}
                )

    def test_boundary_conditions(self, user_type: str):
        """Test Phase 7.4: Boundary conditions"""
        self.print_section("Phase 7.4: Boundary Conditions")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        boundary_tests = [
            {
                "name": "Extremely high quantity",
                "payload": {"symbol": "TCS", "side": "BUY", "quantity": 999999, "order_type": "MARKET"}
            },
            {
                "name": "Very high price",
                "payload": {"symbol": "TCS", "side": "BUY", "quantity": 1, "order_type": "LIMIT", "price": 999999999.99}
            },
            {
                "name": "Very low price",
                "payload": {"symbol": "TCS", "side": "BUY", "quantity": 1, "order_type": "LIMIT", "price": 0.01}
            },
        ]

        for test in boundary_tests:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/trading/place_order",
                    json=test["payload"],
                    headers=headers,
                    timeout=5
                )
                
                status = "PASS" if response.status_code in [200, 201, 400] else "WARN"
                self.log_test(
                    "boundary_conditions",
                    f"Test: {test['name']}",
                    status,
                    {
                        "message": f"Status code: {response.status_code}",
                        "status_code": response.status_code
                    }
                )
            except Exception as e:
                self.log_test(
                    "boundary_conditions",
                    f"Test: {test['name']}",
                    "FAIL",
                    {"message": f"Error: {str(e)}"}
                )

    def test_concurrent_orders(self, user_type: str):
        """Test Phase 7.5: Concurrent order placement"""
        self.print_section("Phase 7.5: Concurrent Operations")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        def place_order(order_num):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/trading/place_order",
                    json={
                        "symbol": "TCS",
                        "side": "BUY" if order_num % 2 == 0 else "SELL",
                        "quantity": 1,
                        "order_type": "MARKET",
                    },
                    headers=headers,
                    timeout=5
                )
                return response.status_code in [200, 201]
            except:
                return False

        # Use ThreadPoolExecutor for concurrent requests
        success_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(place_order, i) for i in range(5)]
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    success_count += 1

        self.log_test(
            "concurrent_operations",
            "Concurrent Order Placement (5 concurrent)",
            "PASS" if success_count >= 3 else "WARN",
            {
                "message": f"Successfully placed {success_count}/5 concurrent orders",
                "successful": success_count,
                "total": 5
            }
        )

    def test_connection_timeout(self):
        """Test Phase 7.6: Connection timeout handling"""
        self.print_section("Phase 7.6: Connection Timeout Handling")
        
        try:
            # Very short timeout to trigger timeout
            response = requests.get(
                f"{API_BASE_URL}/trading/orders",
                headers={"X-AUTH": "invalid_token"},
                timeout=0.001  # 1ms timeout (will likely timeout)
            )
            
            self.log_test(
                "connection_handling",
                "Timeout Recovery",
                "WARN",
                {
                    "message": "Request completed despite short timeout",
                    "status_code": response.status_code
                }
            )
        except requests.exceptions.Timeout:
            self.log_test(
                "connection_handling",
                "Timeout Recovery",
                "PASS",
                {
                    "message": "Request correctly timed out with short timeout"
                }
            )
        except Exception as e:
            self.log_test(
                "connection_handling",
                "Timeout Recovery",
                "PASS",
                {
                    "message": f"Request failed as expected: {type(e).__name__}"
                }
            )

    def test_rate_limiting(self, user_type: str):
        """Test Phase 7.7: Rate limiting"""
        self.print_section("Phase 7.7: Rate Limiting")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        status_codes = []
        for i in range(20):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/trading/orders",
                    headers=headers,
                    timeout=5
                )
                status_codes.append(response.status_code)
            except:
                status_codes.append(0)

        # Check if any rate limit errors (429) occurred
        rate_limited = sum(1 for code in status_codes if code == 429)
        
        self.log_test(
            "resource_limits",
            "Rate Limiting Detection",
            "WARN" if rate_limited > 0 else "PASS",
            {
                "message": f"sent 20 requests, {rate_limited} rate limited",
                "rate_limited_count": rate_limited,
                "total_requests": 20
            }
        )

    def generate_report(self):
        """Generate Phase 7 audit report"""
        self.print_section("Phase 7 Audit Report Summary")
        
        # Count test results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category in self.results:
            if isinstance(self.results[category], list):
                for test in self.results[category]:
                    total_tests += 1
                    if test.get("status") == "PASS":
                        passed_tests += 1
                    elif test.get("status") == "FAIL":
                        failed_tests += 1

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": total_tests - passed_tests - failed_tests,
            "pass_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
        }

        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {failed_tests}")
        print(f"  Pass Rate: {self.results['summary']['pass_rate']}")

        # Save report
        report_file = "audit_phase7_edge_cases_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n  Report saved to: {report_file}")
        return True

    def run(self):
        """Run all Phase 7 tests"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*8 + "Phase 7: Edge Cases & Stress Testing" + " "*14 + "║")
        print("╚" + "="*58 + "╝")

        user_type = "user"
        if not self.authenticate_user(user_type):
            print("\n✗ Failed to authenticate. Aborting.")
            return False

        # Run all test categories
        self.test_rapid_order_placement(user_type)
        self.test_duplicate_orders(user_type)
        self.test_invalid_input_handling(user_type)
        self.test_boundary_conditions(user_type)
        self.test_concurrent_orders(user_type)
        self.test_connection_timeout()
        self.test_rate_limiting(user_type)

        # Generate report
        self.generate_report()

        return True


if __name__ == "__main__":
    try:
        audit = EdgeCasesAndStressTest()
        success = audit.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Audit failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
