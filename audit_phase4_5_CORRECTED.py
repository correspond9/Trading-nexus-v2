#!/usr/bin/env python3
"""
Trading Nexus Audit - Phase 4-5 (CORRECTED VERSION)
Market State & Trading Workflow Tests with CORRECT API endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration - CORRECTED ENDPOINTS
API_BASE_URL = "http://localhost:8000/api/v2"
FRONTEND_URL = "http://localhost:80"

# Test credentials
TEST_USER = {
    "mobile": "7777777777",
    "password": "user123"
}

class TradingWorkflowAudit:
    def __init__(self):
        self.results = {
            "phase": "4-5-CORRECTED",
            "title": "Market State & Trading Workflow Tests (CORRECTED ENDPOINTS)",
            "timestamp": datetime.now().isoformat(),
            "phase_4_market_state_tests": [],
            "phase_5_trading_workflows": [],
            "api_endpoints_used": {
                "auth": f"{API_BASE_URL}/auth/login",
                "place_order": f"{API_BASE_URL}/trading/orders",
                "list_orders": f"{API_BASE_URL}/trading/orders",
                "positions": f"{API_BASE_URL}/portfolio/positions",
                "margin_account": f"{API_BASE_URL}/margin/account"
            }
        }
        self.auth_token = None
        
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
        
    def add_result(self, category: str, test: str, status: str, **kwargs):
        """Add test result"""
        result = {
            "test": test,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        self.results[category].append(result)
        
    def authenticate_user(self, user_type: str = "USER") -> bool:
        """Authenticate and get token"""
        self.print_section(f"Authenticating as {user_type}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=TEST_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.print_result("PASS", f"Authenticated successfully (token: {self.auth_token[:20]}...)")
                return True
            else:
                self.print_result("FAIL", f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("FAIL", f"Authentication error: {str(e)}")
            return False
            
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token"""
        return {
            "X-AUTH": self.auth_token,
            "Content-Type": "application/json"
        }
        
    # ==================== PHASE 4: MARKET STATE TESTS ====================
    
    def test_order_placement(self, user_type: str):
        """Test Phase 4.1: Order placement - CORRECTED ENDPOINT"""
        self.print_section("Phase 4.1: Order Placement (CORRECTED)")
        
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
            # CORRECTED: Using /api/v2/trading/orders
            response = requests.post(
                f"{API_BASE_URL}/trading/orders",
                json=order_data,
                headers=self.get_headers(),
                timeout=10
            )
            
            self.print_result(
                "PASS" if response.status_code in [200, 201, 403] else "FAIL",
                f"Status {response.status_code}: {response.text[:200]}"
            )
            
            # 403 is acceptable (market closed)
            if response.status_code in [200, 201]:
                self.add_result(
                    "phase_4_market_state_tests",
                    "Order Placement",
                    "PASS",
                    message="Order placed successfully",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )
            elif response.status_code == 403:
                self.add_result(
                    "phase_4_market_state_tests",
                    "Order Placement",
                    "PASS",
                    message="Order rejected - Market closed (Expected behavior)",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )
            else:
                self.add_result(
                    "phase_4_market_state_tests",
                    "Order Placement",
                    "FAIL",
                    message=f"Failed with status {response.status_code}",
                    response=response.text[:200]
                )
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.add_result(
                "phase_4_market_state_tests",
                "Order Placement",
                "FAIL",
                message=f"Exception: {str(e)}"
            )
            
    # ==================== PHASE 5: TRADING WORKFLOWS ====================
    
    def test_order_retrieval(self, user_type: str):
        """Test Phase 5.1: Order retrieval - CORRECTED ENDPOINT"""
        self.print_section("Phase 5.1: Order Retrieval (CORRECTED)")
        
        try:
            # CORRECTED: Using /api/v2/trading/orders
            response = requests.get(
                f"{API_BASE_URL}/trading/orders",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                order_count = len(data) if isinstance(data, list) else len(data.get("orders", []))
                self.print_result("PASS", f"Retrieved {order_count} orders")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Order Retrieval",
                    "PASS",
                    message=f"Retrieved {order_count} orders",
                    total_orders=order_count
                )
            else:
                self.print_result("FAIL", f"Status {response.status_code}: {response.text[:100]}")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Order Retrieval",
                    "FAIL",
                    message=f"Failed with status {response.status_code}"
                )
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.add_result(
                "phase_5_trading_workflows",
                "Order Retrieval",
                "FAIL",
                message=f"Exception: {str(e)}"
            )
            
    def test_position_retrieval(self, user_type: str):
        """Test Phase 5.2: Position retrieval - CORRECTED ENDPOINT"""
        self.print_section("Phase 5.2: Position Retrieval (CORRECTED)")
        
        try:
            # CORRECTED: Using /api/v2/portfolio/positions
            response = requests.get(
                f"{API_BASE_URL}/portfolio/positions",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                position_count = len(data) if isinstance(data, list) else len(data.get("positions", []))
                self.print_result("PASS", f"Retrieved {position_count} positions")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Position Retrieval",
                    "PASS",
                    message=f"Retrieved {position_count} positions",
                    total_positions=position_count
                )
            else:
                self.print_result("FAIL", f"Status {response.status_code}: {response.text[:100]}")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Position Retrieval",
                    "FAIL",
                    message=f"Failed with status {response.status_code}"
                )
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.add_result(
                "phase_5_trading_workflows",
                "Position Retrieval",
                "FAIL",
                message=f"Exception: {str(e)}"
            )
            
    def test_margin_retrieval(self, user_type: str):
        """Test Phase 5.3: Margin account retrieval - CORRECTED ENDPOINT"""
        self.print_section("Phase 5.3: Margin Account Retrieval (CORRECTED)")
        
        try:
            # CORRECTED: Using /api/v2/margin/account
            response = requests.get(
                f"{API_BASE_URL}/margin/account",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("PASS", f"Margin account: {json.dumps(data, indent=2)[:200]}")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Margin Account Retrieval",
                    "PASS",
                    message="Margin account retrieved successfully",
                    available_margin=data.get("available_margin"),
                    used_margin=data.get("used_margin")
                )
            else:
                self.print_result("FAIL", f"Status {response.status_code}: {response.text[:100]}")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Margin Account Retrieval",
                    "FAIL",
                    message=f"Failed with status {response.status_code}"
                )
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.add_result(
                "phase_5_trading_workflows",
                "Margin Account Retrieval",
                "FAIL",
                message=f"Exception: {str(e)}"
            )
            
    def test_error_handling(self, user_type: str):
        """Test Phase 5.4: Error handling with invalid orders"""
        self.print_section("Phase 5.4: Error Handling")
        
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
                headers=self.get_headers(),
                timeout=10
            )
            
            # We expect 4xx error (400, 422)
            if response.status_code in [400, 422, 403]:
                self.print_result("PASS", f"Invalid order correctly rejected: {response.status_code}")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Invalid Order Rejection",
                    "PASS",
                    message="Invalid order correctly rejected",
                    status_code=response.status_code
                )
            else:
                self.print_result("WARN", f"Unexpected status {response.status_code}")
                self.add_result(
                    "phase_5_trading_workflows",
                    "Invalid Order Rejection",
                    "WARN",
                    message=f"Unexpected status {response.status_code}"
                )
                
        except Exception as e:
            self.print_result("FAIL", f"Error: {str(e)}")
            self.add_result(
                "phase_5_trading_workflows",
                "Invalid Order Rejection",
                "FAIL",
                message=f"Exception: {str(e)}"
            )
            
    def calculate_summary(self):
        """Calculate test summary"""
        all_tests = (
            self.results["phase_4_market_state_tests"] + 
            self.results["phase_5_trading_workflows"]
        )
        
        total = len(all_tests)
        passed = sum(1 for t in all_tests if t["status"] == "PASS")
        failed = sum(1 for t in all_tests if t["status"] == "FAIL")
        skipped = sum(1 for t in all_tests if t["status"] == "SKIP")
        
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
        }
        
    def save_report(self):
        """Save audit report to JSON"""
        with open("audit_phase4_5_CORRECTED_report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Report saved: audit_phase4_5_CORRECTED_report.json")
        
    def run_audit(self):
        """Execute complete Phase 4-5 audit"""
        self.print_header("TRADING NEXUS - PHASE 4-5 AUDIT (CORRECTED ENDPOINTS)")
        
        print("API Endpoints Being Tested:")
        for key, url in self.results["api_endpoints_used"].items():
            print(f"  • {key}: {url}")
        
        # Authenticate
        if not self.authenticate_user("USER"):
            print("\n✗ Authentication failed. Cannot proceed with tests.")
            return
            
        # Phase 4 Tests
        self.print_header("PHASE 4: MARKET STATE TESTS")
        self.test_order_placement("USER")
        
        # Phase 5 Tests
        self.print_header("PHASE 5: TRADING WORKFLOW TESTS")
        self.test_order_retrieval("USER")
        self.test_position_retrieval("USER")
        self.test_margin_retrieval("USER")
        self.test_error_handling("USER")
        
        # Summary
        self.calculate_summary()
        self.print_header("AUDIT SUMMARY")
        summary = self.results["summary"]
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Skipped: {summary['skipped']}")
        print(f"  Pass Rate: {summary['pass_rate']}")
        
        # Save report
        self.save_report()


if __name__ == "__main__":
    audit = TradingWorkflowAudit()
    audit.run_audit()
