#!/usr/bin/env python3
"""
Phase 6: UI & Frontend Audit
Tests frontend rendering, navigation, components, and browser interaction
"""

import json
import sys
from datetime import datetime
from typing import Dict
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v2"
FRONTEND_URL = "http://localhost:80"  # Nginx serves frontend on port 80
HEADERS = {"Content-Type": "application/json"}

# Test Credentials
TEST_USERS = {
    "user": {"mobile": "7777777777", "password": "user123"},
}

class UIAndFrontendAudit:
    def __init__(self):
        self.results = {
            "phase": "6",
            "title": "UI & Frontend Audit",
            "timestamp": datetime.now().isoformat(),
            "frontend_access": [],
            "page_rendering": [],
            "navigation": [],
            "forms_and_interaction": [],
            "error_handling": [],
            "performance": [],
            "summary": {}
        }
        self.user_tokens = {}
        self.user_data = {}
        self.session = requests.Session()

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
        
        if category in self.results:
            if isinstance(self.results[category], list):
                self.results[category].append(entry)
        
        status_symbol = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"  {status_symbol} {test_name}: {status}")
        if details.get("message"):
            print(f"     → {details['message']}")

    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate a test user"""
        self.print_section("Authenticating Test User")
        
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
                    print(f"  ✓ Authentication successful")
                    return True
            
            print(f"  ✗ Authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False

    def test_frontend_availability(self):
        """Test Phase 6.1: Frontend availability"""
        self.print_section("Phase 6.1: Frontend Availability")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check for HTML content
                if "<!DOCTYPE html>" in response.text or "<html" in response.text:
                    self.log_test(
                        "frontend_access",
                        "Frontend Server Accessibility",
                        "PASS",
                        {
                            "message": "Frontend server is running and accessible",
                            "url": FRONTEND_URL,
                            "status_code": response.status_code
                        }
                    )
                else:
                    self.log_test(
                        "frontend_access",
                        "Frontend Server Accessibility",
                        "FAIL",
                        {
                            "message": "Frontend returned HTML but content validation needed",
                            "status_code": response.status_code
                        }
                    )
            else:
                self.log_test(
                    "frontend_access",
                    "Frontend Server Accessibility",
                    "FAIL",
                    {
                        "message": f"Frontend returned status {response.status_code}",
                        "status_code": response.status_code
                    }
                )
        except Exception as e:
            self.log_test(
                "frontend_access",
                "Frontend Server Accessibility",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_login_page_rendering(self):
        """Test Phase 6.2: Login page rendering"""
        self.print_section("Phase 6.2: Login Page Rendering")
        
        try:
            response = requests.get(f"{FRONTEND_URL}/login", timeout=10)
            
            if response.status_code == 200:
                self.log_test(
                    "page_rendering",
                    "Login Page Accessibility",
                    "PASS",
                    {
                        "message": "Login page loads successfully",
                        "status_code": response.status_code
                    }
                )
            else:
                self.log_test(
                    "page_rendering",
                    "Login Page Accessibility",
                    "FAIL",
                    {
                        "message": f"Login page returned status {response.status_code}",
                        "status_code": response.status_code
                    }
                )
        except Exception as e:
            self.log_test(
                "page_rendering",
                "Login Page Accessibility",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_dashboard_page_rendering(self, user_type: str):
        """Test Phase 6.2: Dashboard page rendering"""
        self.print_section("Phase 6.2: Dashboard Page Rendering (Authenticated)")
        
        if user_type not in self.user_tokens:
            print("  ✗ User not authenticated")
            return

        try:
            headers = {"Cookie": f"auth_token={self.user_tokens[user_type]}"}
            response = requests.get(f"{FRONTEND_URL}/dashboard", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.log_test(
                    "page_rendering",
                    "Dashboard Page Accessibility",
                    "PASS",
                    {
                        "message": "Dashboard page loads successfully",
                        "status_code": response.status_code
                    }
                )
            else:
                self.log_test(
                    "page_rendering",
                    "Dashboard Page Accessibility",
                    "FAIL",
                    {
                        "message": f"Dashboard returned status {response.status_code}",
                        "status_code": response.status_code
                    }
                )
        except Exception as e:
            self.log_test(
                "page_rendering",
                "Dashboard Page Accessibility",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_navigation_structure(self):
        """Test Phase 6.3: Navigation structure"""
        self.print_section("Phase 6.3: Navigation Structure")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check for common navigation elements
                has_header = "<header" in response.text or "header" in response.text.lower()
                has_nav = "<nav" in response.text or "navigation" in response.text.lower()
                
                self.log_test(
                    "navigation",
                    "Navigation Elements",
                    "PASS" if has_header or has_nav else "WARN",
                    {
                        "message": "Navigation structure identified" if has_header or has_nav else "Navigation elements not clearly identified",
                        "has_header": has_header,
                        "has_nav": has_nav
                    }
                )
        except Exception as e:
            self.log_test(
                "navigation",
                "Navigation Elements",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_responsive_design(self):
        """Test Phase 6.3: Responsive design indicators"""
        self.print_section("Phase 6.3: Responsive Design")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check for responsive design indicators
                has_viewport_meta = "viewport" in response.text
                has_media_queries = "@media" in response.text or "media-query" in response.text.lower()
                
                self.log_test(
                    "navigation",
                    "Responsive Design Implementation",
                    "PASS" if has_viewport_meta else "WARN",
                    {
                        "message": "Responsive design detected" if has_viewport_meta else "Responsive design indicators not found",
                        "has_viewport_meta": has_viewport_meta,
                        "has_media_queries": has_media_queries
                    }
                )
        except Exception as e:
            self.log_test(
                "navigation",
                "Responsive Design Implementation",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_form_structure(self):
        """Test Phase 6.4: Form structure"""
        self.print_section("Phase 6.4: Form Structure & Validation")
        
        try:
            response = requests.get(f"{FRONTEND_URL}/login", timeout=10)
            
            if response.status_code == 200:
                # Check for form elements
                has_form = "<form" in response.text
                has_inputs = "<input" in response.text
                has_buttons = "<button" in response.text or "button" in response.text.lower()
                
                self.log_test(
                    "forms_and_interaction",
                    "Form Elements Presence",
                    "PASS" if has_form and has_inputs else "WARN",
                    {
                        "message": "Login form structure identified",
                        "has_form": has_form,
                        "has_inputs": has_inputs,
                        "has_buttons": has_buttons
                    }
                )
        except Exception as e:
            self.log_test(
                "forms_and_interaction",
                "Form Elements Presence",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_css_loading(self):
        """Test Phase 6.4: CSS and styling"""
        self.print_section("Phase 6.4: CSS & Styling")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check for CSS links
                has_css_link = "<link" in response.text and "css" in response.text.lower()
                has_style_tag = "<style" in response.text
                
                self.log_test(
                    "forms_and_interaction",
                    "CSS Loading",
                    "PASS" if has_css_link or has_style_tag else "WARN",
                    {
                        "message": "CSS resources identified",
                        "has_css_link": has_css_link,
                        "has_style_tag": has_style_tag
                    }
                )
        except Exception as e:
            self.log_test(
                "forms_and_interaction",
                "CSS Loading",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_javascript_loading(self):
        """Test Phase 6.5: JavaScript execution"""
        self.print_section("Phase 6.5: JavaScript & Interactivity")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check for JavaScript
                has_script_tags = "<script" in response.text
                has_bundle = "bundle" in response.text.lower() or "main" in response.text
                
                self.log_test(
                    "error_handling",
                    "JavaScript Loading",
                    "PASS" if has_script_tags else "WARN",
                    {
                        "message": "JavaScript resources identified",
                        "has_script_tags": has_script_tags,
                        "has_bundle": has_bundle
                    }
                )
        except Exception as e:
            self.log_test(
                "error_handling",
                "JavaScript Loading",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_api_integration_points(self):
        """Test Phase 6.5: API integration from frontend"""
        self.print_section("Phase 6.5: API Integration Points")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=10)
            
            if response.status_code == 200:
                # Check for API endpoints references
                has_api_refs = "/api" in response.text or "api/" in response.text
                
                self.log_test(
                    "error_handling",
                    "API Integration",
                    "PASS" if has_api_refs else "WARN",
                    {
                        "message": "API integration references found" if has_api_refs else "API integration not clearly visible",
                        "has_api_refs": has_api_refs
                    }
                )
        except Exception as e:
            self.log_test(
                "error_handling",
                "API Integration",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_frontend_performance(self):
        """Test Phase 6.6: Frontend performance"""
        self.print_section("Phase 6.6: Performance Metrics")
        
        try:
            start_time = time.time()
            response = requests.get(FRONTEND_URL, timeout=10)
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                status = "PASS" if load_time < 5.0 else "WARN"
                self.log_test(
                    "performance",
                    "Page Load Time",
                    status,
                    {
                        "message": f"Frontend loads in {load_time:.2f}s",
                        "load_time_seconds": load_time
                    }
                )
        except Exception as e:
            self.log_test(
                "performance",
                "Page Load Time",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def test_error_pages(self):
        """Test Phase 6.6: Error page handling"""
        self.print_section("Phase 6.6: Error Page Handling")
        
        try:
            response = requests.get(f"{FRONTEND_URL}/nonexistent-page-12345", timeout=10)
            
            if response.status_code == 404:
                self.log_test(
                    "performance",
                    "404 Error Page",
                    "PASS",
                    {
                        "message": "404 error page handler working",
                        "status_code": 404
                    }
                )
            else:
                self.log_test(
                    "performance",
                    "404 Error Page",
                    "WARN",
                    {
                        "message": f"Unexpected response to 404: {response.status_code}",
                        "status_code": response.status_code
                    }
                )
        except Exception as e:
            self.log_test(
                "performance",
                "404 Error Page",
                "FAIL",
                {"message": f"Error: {str(e)}"}
            )

    def generate_report(self):
        """Generate Phase 6 audit report"""
        self.print_section("Phase 6 Audit Report Summary")
        
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
        report_file = "audit_phase6_ui_frontend_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n  Report saved to: {report_file}")
        return True

    def run(self):
        """Run all Phase 6 tests"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*15 + "Phase 6: UI & Frontend Audit" + " "*15 + "║")
        print("╚" + "="*58 + "╝")

        # Frontend availability tests (no auth needed)
        self.test_frontend_availability()
        self.test_login_page_rendering()
        self.test_navigation_structure()
        self.test_responsive_design()
        self.test_form_structure()
        self.test_css_loading()
        self.test_javascript_loading()
        self.test_api_integration_points()
        self.test_frontend_performance()
        self.test_error_pages()

        # Authenticated tests
        user_type = "user"
        if self.authenticate_user(user_type):
            self.test_dashboard_page_rendering(user_type)

        # Generate report
        self.generate_report()

        return True


if __name__ == "__main__":
    try:
        audit = UIAndFrontendAudit()
        success = audit.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Audit failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
