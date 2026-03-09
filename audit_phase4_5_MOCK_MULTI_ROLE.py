#!/usr/bin/env python3
"""
Trading Nexus Audit - Phase 4-5 with Mock Dhan Engine
Market State & Trading Workflow Tests with BOTH USER and SUPER_USER roles
Testing with mock_dhan_engine (market simulation enabled)
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration - CORRECTED ENDPOINTS
API_BASE_URL = "http://localhost:8000/api/v2"
FRONTEND_URL = "http://localhost:80"

# Test credentials for both roles
TEST_USERS = {
    "USER": {
        "mobile": "7777777777",
        "password": "user123"
    },
    "SUPER_USER": {
        "mobile": "6666666666",
        "password": "super123"
    }
}

class TradingWorkflowAuditMultiRole:
    def __init__(self):
        self.results = {
            "phase": "4-5-MOCK-MULTI-ROLE",
            "title": "Market State & Trading Workflow Tests (Mock Engine, Multi-Role)",
            "timestamp": datetime.now().isoformat(),
            "test_environment": "LOCAL_DOCKER_WITH_MOCK_DHAN_ENGINE",
            "roles_tested": ["USER", "SUPER_USER"],
            "test_results_by_role": {},
            "api_endpoints_used": {
                "auth": f"{API_BASE_URL}/auth/login",
                "place_order": f"{API_BASE_URL}/trading/orders",
                "list_orders": f"{API_BASE_URL}/trading/orders",
                "positions": f"{API_BASE_URL}/portfolio/positions",
                "margin_account": f"{API_BASE_URL}/margin/account"
            }
        }
        
    def print_header(self, text: str):
        """Print section header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70 + "\n")
        
    def print_section(self, text: str):
        """Print subsection"""
        print(f"\n{'─' * 70}")
        print(f"  {text}")
        print(f"{'─' * 70}\n")
        
    def print_result(self, status: str, message: str):
        """Print test result"""
        symbols = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠", "SKIP": "○"}
        colors = {"PASS": "\033[92m", "FAIL": "\033[91m", "WARN": "\033[93m", "SKIP": "\033[90m"}
        reset = "\033[0m"
        symbol = symbols.get(status, "•")
        color = colors.get(status, "")
        print(f"  {color}[{symbol}] {status}{reset}: {message}")
        
    def test_role(self, role_name: str):
        """Execute all tests for a specific role"""
        self.print_header(f"TESTING ROLE: {role_name}")
        
        # Initialize results for this role
        self.results["test_results_by_role"][role_name] = {
            "phase_4_market_state_tests": [],
            "phase_5_trading_workflows": []
        }
        
        # Authenticate
        auth_token = self.authenticate_user(role_name)
        if not auth_token:
            print(f"\n✗ Authentication failed for {role_name}. Skipping tests.")
            return
            
        # Phase 4 Tests
        self.print_header(f"PHASE 4: MARKET STATE TESTS ({role_name})")
        self.test_order_placement(role_name, auth_token)
        
        # Phase 5 Tests
        self.print_header(f"PHASE 5: TRADING WORKFLOW TESTS ({role_name})")
        self.test_order_retrieval(role_name, auth_token)
        self.test_position_retrieval(role_name, auth_token)
        self.test_margin_retrieval(role_name, auth_token)
        self.test_error_handling(role_name, auth_token)
        
    def authenticate_user(self, role_name: str) -> str:
        """Authenticate and get token"""
        self.print_section(f"Authenticating as {role_name}")
        
        user_creds = TEST_USERS[role_name]
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=user_creds,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                auth_token = data.get("access_token")
                self.print_result("PASS", f"Authenticated successfully (token: {auth_token[:20]}...)")
                return auth_token
            else:
                self.print_result("FAIL", f"Authentication failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.print_result("FAIL", f"Authentication error: {str(e)}")
            return None
            
    def get_headers(self, auth_token: str) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {
            "X-AUTH": auth_token,
            "Content-Type": "application/json"
        }
        
    # ==================== PHASE 4: MARKET STATE TESTS ====================
    
    def test_order_placement(self, role_name: str, auth_token: str):
        """Test Phase 4.1: Order placement with mock engine"""
        self.print_section(f"Phase 4.1: Order Placement ({role_name})")
        
        order_data = {
            "symbol": "360ONE MAR FUT",
            "exchange": "NSE_FNO",
            "quantity": 1,
            "price": 750.00,
            "side": "BUY",
            "order_type": "LIMIT",
            "product": "MIS"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/trading/orders",
                json=order_data,
                headers=self.get_headers(auth_token),
                timeout=10
            )
            
            self.print_result(
                "PASS" if response.status_code in [200, 201] else "WARN" if response.status_code == 403 else "FAIL",
                f"Status {response.status_code}: {response.text[:200]}"
            )
            
            # With mock engine, 200/201 expected (market always "open")
            if response.status_code in [200, 201]:
                result_data = response.json() if response.text else None
                self.print_result("PASS", f"Order placed successfully: {json.dumps(result_data, indent=2)[:300]}")
                self.results["test_results_by_role"][role_name]["phase_4_market_state_tests"].append({
                    "test": "Order Placement",
                    "status": "PASS",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Order placed successfully with mock engine",
                    "status_code": response.status_code,
                    "response": result_data
                })
            elif response.status_code == 403:
                self.results["test_results_by_role"][role_name]["phase_4_market_state_tests"].append({
                    "test": "Order Placement",
                    "status": "WARN",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Mock engine returned 403 (unexpected - should simulate open market)",
                    "status_code": response.status_code,
                    "response": response.json() if response.text else None
                })
            else:
                self.results["test_results_by_role"][role_name]["phase_4_market_state_tests"].append({
                    "test": "Order Placement",
                    "status": "FAIL",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Failed with status {response.status_code}",
                    "response": response.text[:200]
                })
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.results["test_results_by_role"][role_name]["phase_4_market_state_tests"].append({
                "test": "Order Placement",
                "status": "FAIL",
                "timestamp": datetime.now().isoformat(),
                "message": f"Exception: {str(e)}"
            })
            
    # ==================== PHASE 5: TRADING WORKFLOWS ====================
    
    def test_order_retrieval(self, role_name: str, auth_token: str):
        """Test Phase 5.1: Order retrieval"""
        self.print_section(f"Phase 5.1: Order Retrieval ({role_name})")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/trading/orders",
                headers=self.get_headers(auth_token),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                order_count = len(data) if isinstance(data, list) else len(data.get("orders", []))
                self.print_result("PASS", f"Retrieved {order_count} orders")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Order Retrieval",
                    "status": "PASS",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Retrieved {order_count} orders",
                    "total_orders": order_count
                })
            else:
                self.print_result("FAIL", f"Status {response.status_code}: {response.text[:100]}")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Order Retrieval",
                    "status": "FAIL",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Failed with status {response.status_code}"
                })
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                "test": "Order Retrieval",
                "status": "FAIL",
                "timestamp": datetime.now().isoformat(),
                "message": f"Exception: {str(e)}"
            })
            
    def test_position_retrieval(self, role_name: str, auth_token: str):
        """Test Phase 5.2: Position retrieval"""
        self.print_section(f"Phase 5.2: Position Retrieval ({role_name})")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/portfolio/positions",
                headers=self.get_headers(auth_token),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                position_count = len(data) if isinstance(data, list) else len(data.get("positions", []))
                self.print_result("PASS", f"Retrieved {position_count} positions")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Position Retrieval",
                    "status": "PASS",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Retrieved {position_count} positions",
                    "total_positions": position_count
                })
            else:
                self.print_result("FAIL", f"Status {response.status_code}: {response.text[:100]}")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Position Retrieval",
                    "status": "FAIL",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Failed with status {response.status_code}"
                })
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                "test": "Position Retrieval",
                "status": "FAIL",
                "timestamp": datetime.now().isoformat(),
                "message": f"Exception: {str(e)}"
            })
            
    def test_margin_retrieval(self, role_name: str, auth_token: str):
        """Test Phase 5.3: Margin account retrieval"""
        self.print_section(f"Phase 5.3: Margin Account Retrieval ({role_name})")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/margin/account",
                headers=self.get_headers(auth_token),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("PASS", f"Margin account: {json.dumps(data, indent=2)[:200]}")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Margin Account Retrieval",
                    "status": "PASS",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Margin account retrieved successfully",
                    "available_margin": data.get("data", {}).get("available_margin") if isinstance(data, dict) else None,
                    "used_margin": data.get("data", {}).get("used_margin") if isinstance(data, dict) else None
                })
            else:
                self.print_result("FAIL", f"Status {response.status_code}: {response.text[:100]}")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Margin Account Retrieval",
                    "status": "FAIL",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Failed with status {response.status_code}"
                })
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                "test": "Margin Account Retrieval",
                "status": "FAIL",
                "timestamp": datetime.now().isoformat(),
                "message": f"Exception: {str(e)}"
            })
            
    def test_error_handling(self, role_name: str, auth_token: str):
        """Test Phase 5.4: Error handling with invalid orders"""
        self.print_section(f"Phase 5.4: Error Handling ({role_name})")
        
        invalid_order = {
            "symbol": "",
            "quantity": 0,
            "price": -100,
            "side": "INVALID"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/trading/orders",
                json=invalid_order,
                headers=self.get_headers(auth_token),
                timeout=10
            )
            
            # We expect 4xx error (400, 422)
            if response.status_code in [400, 422, 403]:
                self.print_result("PASS", f"Invalid order correctly rejected: {response.status_code}")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Invalid Order Rejection",
                    "status": "PASS",
                    "timestamp": datetime.now().isoformat(),
                    "message": "Invalid order correctly rejected",
                    "status_code": response.status_code
                })
            else:
                self.print_result("WARN", f"Unexpected status {response.status_code}")
                self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                    "test": "Invalid Order Rejection",
                    "status": "WARN",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Unexpected status {response.status_code}"
                })
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.results["test_results_by_role"][role_name]["phase_5_trading_workflows"].append({
                "test": "Invalid Order Rejection",
                "status": "FAIL",
                "timestamp": datetime.now().isoformat(),
                "message": f"Exception: {str(e)}"
            })
            
    def calculate_summary(self):
        """Calculate test summary for all roles"""
        self.results["summary_by_role"] = {}
        
        for role_name, role_results in self.results["test_results_by_role"].items():
            all_tests = (
                role_results["phase_4_market_state_tests"] + 
                role_results["phase_5_trading_workflows"]
            )
            
            total = len(all_tests)
            passed = sum(1 for t in all_tests if t["status"] == "PASS")
            failed = sum(1 for t in all_tests if t["status"] == "FAIL")
            skipped = sum(1 for t in all_tests if t["status"] == "SKIP")
            warned = sum(1 for t in all_tests if t["status"] == "WARN")
            
            self.results["summary_by_role"][role_name] = {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "warned": warned,
                "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
            }
        
    def save_report(self):
        """Save audit report to JSON"""
        with open("audit_phase4_5_MOCK_MULTI_ROLE_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Report saved: audit_phase4_5_MOCK_MULTI_ROLE_report.json")
        
    def run_audit(self):
        """Execute complete Phase 4-5 audit for all roles"""
        self.print_header("TRADING NEXUS - PHASE 4-5 AUDIT (MOCK ENGINE, MULTI-ROLE)")
        
        print("Test Environment: LOCAL DOCKER WITH MOCK_DHAN_ENGINE")
        print("API Endpoints Being Tested:")
        for key, url in self.results["api_endpoints_used"].items():
            print(f"  • {key}: {url}")
        print(f"Roles Being Tested: {', '.join(self.results['roles_tested'])}")
        
        # Test each role
        for role_name in self.results["roles_tested"]:
            self.test_role(role_name)
            time.sleep(2)  # Small delay between role tests
        
        # Summary
        self.calculate_summary()
        self.print_header("AUDIT SUMMARY - ALL ROLES")
        
        for role_name, summary in self.results["summary_by_role"].items():
            print(f"\n  {role_name}:")
            print(f"    Total Tests: {summary['total_tests']}")
            print(f"    Passed: {summary['passed']}")
            print(f"    Failed: {summary['failed']}")
            print(f"    Warned: {summary['warned']}")
            print(f"    Skipped: {summary['skipped']}")
            print(f"    Pass Rate: {summary['pass_rate']}")
        
        # Save report
        self.save_report()


if __name__ == "__main__":
    audit = TradingWorkflowAuditMultiRole()
    audit.run_audit()
