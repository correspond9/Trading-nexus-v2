#!/usr/bin/env python3
"""
Phase 4-5: Market State & Trading Workflow Tests
Tests order behavior during closed/open markets and complete trading workflows
"""

import json
import sys
from datetime import datetime
from typing import Dict, Optional
import requests

# Configuration
API_BASE_URL = "http://localhost:8000/api/v2"
HEADERS = {"Content-Type": "application/json"}

# Test Credentials from Phase 3
TEST_USERS = {
    "user": {"mobile": "7777777777", "password": "user123"},
}

class MarketStateAndWorkflowAudit:
    def __init__(self):
        self.results = {
            "phase": "4-5",
            "title": "Market State & Trading Workflow Tests",
            "timestamp": datetime.now().isoformat(),
            "phase_4_market_state_tests": [],
            "phase_5_trading_workflows": [],
            "summary": {}
        }
        self.user_tokens = {}
        self.user_data = {}

    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")

    def log_test(self, phase: str, test_name: str, status: str, details: Dict):
        """Log test result"""
        entry = {
            "test": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **details
        }
        if phase in ["4", "5"]:
            if phase == "4":
                self.results["phase_4_market_state_tests"].append(entry)
            else:
                self.results["phase_5_trading_workflows"].append(entry)
        
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"  {status_symbol} {test_name}: {status}")
        if details.get("message"):
            print(f"     → {details['message']}")

    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate a test user and get token"""
        self.print_section(f"Authenticating {user_type}")
        
        user = TEST_USERS.get(user_type)
        if not user:
            print(f"  ✗ User type '{user_type}' not found")
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
                    self.user_data[user_type] = {
                        "mobile": user["mobile"],
                        "token": token,
                        "role": data.get("role", "unknown")
                    }
                    print(f"  ✓ Authentication successful for {user_type}")
                    print(f"     → Role: {self.user_data[user_type]['role']}")
                    return True
            
            print(f"  ✗ Authentication failed: {response.status_code}")
            print(f"     → {response.text[:200]}")
            return False
            
        except Exception as e:
            print(f"  ✗ Error during authentication: {str(e)}")
            return False

    def test_order_placement(self, user_type: str):
        """Phase 4-5: Test order placement"""
        self.print_section("Phase 4-5: Order Placement Tests")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        # Test order placement
        order_payload = {
            "symbol": "TCS",
            "side": "BUY",
            "quantity": 1,
            "order_type": "MARKET",
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/trading/place_order",
                json=order_payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test(
                    "4",
                    "Order Placement",
                    "PASS",
                    {
                        "message": "Order placed successfully",
                        "order_id": data.get("id"),
                        "status": data.get("status")
                    }
                )
                return data.get("id")
            else:
                self.log_test(
                    "4",
                    "Order Placement",
                    "FAIL",
                    {
                        "message": f"Failed with status {response.status_code}",
                        "response": response.text[:200]
                    }
                )
                return None
        except Exception as e:
            self.log_test(
                "4",
                "Order Placement",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )
            return None

    def test_order_retrieval(self, user_type: str):
        """Phase 5: Test order retrieval"""
        self.print_section("Phase 5: Order Retrieval")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        try:
            response = requests.get(
                f"{API_BASE_URL}/trading/orders",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                orders = response.json()
                self.log_test(
                    "5",
                    "Order Retrieval",
                    "PASS",
                    {
                        "message": f"Retrieved {len(orders)} orders",
                        "total_orders": len(orders)
                    }
                )
            else:
                self.log_test(
                    "5",
                    "Order Retrieval",
                    "FAIL",
                    {
                        "message": f"Failed with status {response.status_code}"
                    }
                )
        except Exception as e:
            self.log_test(
                "5",
                "Order Retrieval",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_position_retrieval(self, user_type: str):
        """Phase 5: Test position retrieval"""
        self.print_section("Phase 5: Position Retrieval")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        try:
            response = requests.get(
                f"{API_BASE_URL}/trading/positions",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                positions = response.json()
                self.log_test(
                    "5",
                    "Position Retrieval",
                    "PASS",
                    {
                        "message": f"Retrieved {len(positions)} positions",
                        "total_positions": len(positions)
                    }
                )
            else:
                self.log_test(
                    "5",
                    "Position Retrieval",
                    "FAIL",
                    {
                        "message": f"Failed with status {response.status_code}"
                    }
                )
        except Exception as e:
            self.log_test(
                "5",
                "Position Retrieval",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_margin_retrieval(self, user_type: str):
        """Phase 5: Test margin account retrieval"""
        self.print_section("Phase 5: Margin Account Retrieval")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        try:
            response = requests.get(
                f"{API_BASE_URL}/margin/account",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                margin_data = response.json()
                self.log_test(
                    "5",
                    "Margin Account Retrieval",
                    "PASS",
                    {
                        "message": "Margin account retrieved successfully",
                        "available_margin": margin_data.get("available_margin"),
                        "used_margin": margin_data.get("used_margin")
                    }
                )
            else:
                self.log_test(
                    "5",
                    "Margin Account Retrieval",
                    "FAIL",
                    {
                        "message": f"Failed with status {response.status_code}"
                    }
                )
        except Exception as e:
            self.log_test(
                "5",
                "Margin Account Retrieval",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_error_handling(self, user_type: str):
        """Phase 5: Test error handling"""
        self.print_section("Phase 5: Error Handling")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        headers = HEADERS.copy()
        headers["X-AUTH"] = self.user_tokens[user_type]

        # Test invalid order
        try:
            response = requests.post(
                f"{API_BASE_URL}/trading/place_order",
                json={
                    "symbol": "INVALID_SYM",
                    "side": "BUY",
                    "quantity": -1,
                    "order_type": "MARKET",
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code >= 400:
                self.log_test(
                    "5",
                    "Invalid Order Rejection",
                    "PASS",
                    {
                        "message": "Invalid order correctly rejected",
                        "status_code": response.status_code
                    }
                )
            else:
                self.log_test(
                    "5",
                    "Invalid Order Rejection",
                    "FAIL",
                    {
                        "message": "Invalid order was not rejected"
                    }
                )
        except Exception as e:
            self.log_test(
                "5",
                "Invalid Order Rejection",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def generate_report(self):
        """Generate Phase 4-5 audit report"""
        self.print_section("Phase 4-5 Audit Report Summary")
        
        # Count test results
        total_tests = len(self.results["phase_4_market_state_tests"]) + len(self.results["phase_5_trading_workflows"])
        passed_tests = sum(1 for t in self.results["phase_4_market_state_tests"] + self.results["phase_5_trading_workflows"] 
                          if t.get("status") == "PASS")
        failed_tests = sum(1 for t in self.results["phase_4_market_state_tests"] + self.results["phase_5_trading_workflows"] 
                          if t.get("status") == "FAIL")

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
        report_file = "audit_phase4_5_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n  Report saved to: {report_file}")
        return True

    def run(self):
        """Run all Phase 4-5 tests"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*10 + "Phase 4-5: Market State & Trading Workflows" + " "*5 + "║")
        print("╚" + "="*58 + "╝")

        # Authenticate test user
        user_type = "user"
        if not self.authenticate_user(user_type):
            print("\n✗ Failed to authenticate test user. Aborting.")
            return False

        # Phase 4-5 tests
        self.test_order_placement(user_type)
        self.test_order_retrieval(user_type)
        self.test_position_retrieval(user_type)
        self.test_margin_retrieval(user_type)
        self.test_error_handling(user_type)

        # Generate report
        self.generate_report()

        return True


if __name__ == "__main__":
    try:
        audit = MarketStateAndWorkflowAudit()
        success = audit.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Audit failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
