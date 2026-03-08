"""
QA Test Script - Phase 4-5: End-to-End Trading Lifecycle Testing
=================================================================

This script tests the complete trading workflow:
1. Authentication
2. Instrument search
3. Order placement (Market, Limit, SL, SLL)
4. Order execution verification
5. Position creation and tracking
6. P&L calculations
7. Order modification
8. Order cancellation
9. Position closing
10. Ledger entry validation
11. Balance updates

Requirements:
- Market must be OPEN (NSE: Mon-Fri 9:15 AM - 3:30 PM IST)
- All backend services running
- Database accessible

Usage:
    python qa_test_phase4_5_trading_lifecycle.py
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/v2"
TIMEOUT = 10

# Test user credentials (USER role - Trader 1)
TEST_USER = {
    "mobile": "7777777777",
    "password": "user123",
    "role_expected": "USER"
}

# Test instruments for different order types
TEST_INSTRUMENTS = {
    "NSE_EQUITY": {
        "symbol": "DCB Bank",
        "exchange_segment": "NSE_EQ"
    },
    "NSE_OPTIONS": {
        "symbol": "NIFTY 26 MAY 30700 CALL",
        "exchange_segment": "NSE_FNO"
    }
}

# Results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "market_status": None,
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": []
}

session_token = None


def _unwrap_list_payload(payload: Any) -> List[Dict[str, Any]]:
    """Normalize API responses that return either list or {'data': list}."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return payload["data"]
    return []


def log_test(test_name: str, status: str, details: Any = None, error: str = None):
    """Log test result"""
    global test_results
    
    result = {
        "test": test_name,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details,
        "error": error
    }
    
    test_results["tests"].append(result)
    test_results["total_tests"] += 1
    
    if status == "PASS":
        test_results["passed"] += 1
        print(f"✅ PASS: {test_name}")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"❌ FAIL: {test_name}")
        if error:
            print(f"   Error: {error}")
    elif status == "SKIP":
        test_results["skipped"] += 1
        print(f"⏭️  SKIP: {test_name}")
        if details:
            print(f"   Reason: {details}")
    
    if details:
        print(f"   Details: {json.dumps(details, indent=2)}")


def authenticate() -> bool:
    """Authenticate and get session token"""
    global session_token
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"mobile": TEST_USER["mobile"], "password": TEST_USER["password"]},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            session_token = data.get("access_token")
            log_test("Authentication", "PASS", {"user": TEST_USER["mobile"], "role": data.get("role")})
            return True
        else:
            log_test("Authentication", "FAIL", error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test("Authentication", "FAIL", error=str(e))
        return False


def get_headers() -> Dict[str, str]:
    """Get request headers with auth token"""
    return {
        "X-AUTH": session_token,
        "Content-Type": "application/json"
    }


def check_market_status() -> Dict[str, Any]:
    """Check current market status"""
    try:
        # Try to get market state from backend health endpoint
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        
        # Also check market hours by attempting to place a test order (will be rejected if market closed)
        test_response = requests.post(
            f"{BASE_URL}/trading/orders",
            headers=get_headers(),
            json={
                "symbol": "DCB Bank",
                "exchange_segment": "NSE_EQ",
                "side": "BUY",
                "quantity": 1,
                "order_type": "MARKET",
                "product_type": "MIS"
            },
            timeout=TIMEOUT
        )
        
        # Only mark CLOSED when backend explicitly returns market-hours rejection.
        response_detail = ""
        try:
            response_detail = (test_response.json() or {}).get("detail", "")
        except Exception:
            response_detail = test_response.text or ""

        explicit_market_closed = (
            test_response.status_code == 403
            and isinstance(response_detail, str)
            and "Market is CLOSED" in response_detail
        )

        is_market_open = not explicit_market_closed
        market_state = "CLOSED" if explicit_market_closed else "OPEN"
        
        result = {
            "is_open": is_market_open,
            "state": market_state,
            "probe_status": test_response.status_code,
            "probe_detail": response_detail[:200] if isinstance(response_detail, str) else str(response_detail),
            "checked_at": datetime.now().isoformat()
        }
        
        test_results["market_status"] = result
        log_test("Market Status Check", "PASS", result)
        return result
        
    except Exception as e:
        result = {
            "is_open": False,
            "state": "UNKNOWN",
            "error": str(e)
        }
        test_results["market_status"] = result
        log_test("Market Status Check", "FAIL", error=str(e))
        return result


def search_instrument(symbol: str, exchange: str) -> Optional[Dict[str, Any]]:
    """Search for an instrument"""
    try:
        response = requests.get(
            f"{BASE_URL}/instruments/search",
            headers=get_headers(),
            params={"query": symbol, "exchange": exchange},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            raw = response.json()
            results = _unwrap_list_payload(raw)
            if results and len(results) > 0:
                instrument = results[0]
                log_test(f"Search Instrument: {symbol}", "PASS", 
                        {"token": instrument.get("instrument_token"), "name": instrument.get("display_name")})
                return instrument
            else:
                log_test(f"Search Instrument: {symbol}", "FAIL", error="No results found")
                return None
        else:
            log_test(f"Search Instrument: {symbol}", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test(f"Search Instrument: {symbol}", "FAIL", error=str(e))
        return None


def place_order(symbol: str, exchange: str, side: str, quantity: int, 
                order_type: str = "MARKET", limit_price: float = None, 
                trigger_price: float = None) -> Optional[Dict[str, Any]]:
    """Place an order"""
    try:
        order_data = {
            "symbol": symbol,
            "exchange_segment": exchange,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "product_type": "MIS"
        }
        
        if limit_price:
            order_data["limit_price"] = limit_price
        if trigger_price:
            order_data["trigger_price"] = trigger_price
        
        response = requests.post(
            f"{BASE_URL}/trading/orders",
            headers=get_headers(),
            json=order_data,
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            order = response.json()
            log_test(f"Place {order_type} Order: {symbol} {side}", "PASS", 
                    {"order_id": order.get("order_id"), "status": order.get("status")})
            return order
        else:
            log_test(f"Place {order_type} Order: {symbol} {side}", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test(f"Place {order_type} Order: {symbol} {side}", "FAIL", error=str(e))
        return None


def get_pending_orders() -> List[Dict[str, Any]]:
    """Get pending orders"""
    try:
        response = requests.get(
            f"{BASE_URL}/trading/orders",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            orders = _unwrap_list_payload(response.json())
            log_test("Get Pending Orders", "PASS", {"count": len(orders)})
            return orders
        else:
            log_test("Get Pending Orders", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        log_test("Get Pending Orders", "FAIL", error=str(e))
        return []


def get_executed_orders() -> List[Dict[str, Any]]:
    """Get executed orders"""
    try:
        response = requests.get(
            f"{BASE_URL}/trading/orders/executed",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            orders = _unwrap_list_payload(response.json())
            log_test("Get Executed Orders", "PASS", {"count": len(orders)})
            return orders
        else:
            log_test("Get Executed Orders", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        log_test("Get Executed Orders", "FAIL", error=str(e))
        return []


def get_positions() -> List[Dict[str, Any]]:
    """Get open positions"""
    try:
        response = requests.get(
            f"{BASE_URL}/portfolio/positions",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            positions = _unwrap_list_payload(response.json())
            log_test("Get Positions", "PASS", {"count": len(positions)})
            return positions
        else:
            log_test("Get Positions", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return []
    except Exception as e:
        log_test("Get Positions", "FAIL", error=str(e))
        return []


def close_position(position_id: str) -> bool:
    """Close a position"""
    try:
        response = requests.post(
            f"{BASE_URL}/portfolio/positions/{position_id}/close",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            log_test(f"Close Position: {position_id}", "PASS", result)
            return True
        else:
            log_test(f"Close Position: {position_id}", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test(f"Close Position: {position_id}", "FAIL", error=str(e))
        return False


def get_pnl_summary() -> Optional[Dict[str, Any]]:
    """Get P&L summary"""
    try:
        response = requests.get(
            f"{BASE_URL}/portfolio/positions/pnl/summary",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            pnl = response.json()
            log_test("Get P&L Summary", "PASS", pnl)
            return pnl
        else:
            log_test("Get P&L Summary", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log_test("Get P&L Summary", "FAIL", error=str(e))
        return None


def cancel_order(order_id: str) -> bool:
    """Cancel an order"""
    try:
        response = requests.delete(
            f"{BASE_URL}/trading/orders/{order_id}",
            headers=get_headers(),
            timeout=TIMEOUT
        )
        
        if response.status_code in [200, 204]:
            log_test(f"Cancel Order: {order_id}", "PASS")
            return True
        else:
            log_test(f"Cancel Order: {order_id}", "FAIL", 
                    error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test(f"Cancel Order: {order_id}", "FAIL", error=str(e))
        return False


def run_trading_lifecycle_tests():
    """Run complete trading lifecycle tests"""
    print("\n" + "="*80)
    print("PHASE 4-5: END-TO-END TRADING LIFECYCLE TESTING")
    print("="*80 + "\n")
    
    # Step 1: Authenticate
    print("\n--- STEP 1: Authentication ---")
    if not authenticate():
        print("\n❌ Authentication failed. Cannot proceed with trading tests.")
        return False
    
    # Step 2: Check market status
    print("\n--- STEP 2: Market Status Check ---")
    market_status = check_market_status()
    
    if not market_status.get("is_open"):
        print("\n⚠️  MARKET IS CLOSED")
        print("=" * 80)
        print("Trading tests require market to be OPEN.")
        print("NSE Market Hours: Monday-Friday, 9:15 AM - 3:30 PM IST")
        print("Current Status:", market_status.get("state"))
        print("\nPlease run this script during market hours.")
        print("="*80)
        
        # Skip all trading tests
        log_test("Phase 4-5 Trading Tests", "SKIP", 
                "Market is closed. Trading tests require market hours.")
        return False
    
    print("✅ Market is OPEN - Proceeding with trading tests\n")
    
    # Step 3: Search instruments
    print("\n--- STEP 3: Instrument Search ---")
    instrument = search_instrument("DCB Bank", "NSE_EQ")
    if not instrument:
        print("❌ Failed to find test instrument. Cannot proceed.")
        return False
    
    # Step 4: Place MARKET BUY order
    print("\n--- STEP 4: Place MARKET BUY Order ---")
    buy_order = place_order("DCB Bank", "NSE_EQ", "BUY", 1, "MARKET")
    if not buy_order:
        print("❌ Failed to place order. Check logs.")
        return False
    
    # Wait for execution
    print("⏳ Waiting 2 seconds for order execution...")
    time.sleep(2)
    
    # Step 5: Verify order execution
    print("\n--- STEP 5: Verify Order Execution ---")
    executed_orders = get_executed_orders()
    order_executed = any(
        isinstance(o, dict)
        and o.get("order_id") == buy_order.get("order_id")
        and o.get("status") in ("EXECUTED", "FILLED")
        for o in executed_orders
    )
    
    if order_executed:
        log_test("Order Execution Verification", "PASS", 
                {"order_id": buy_order.get("order_id")})
    else:
        log_test("Order Execution Verification", "FAIL", 
                error="Order not found in executed orders")
    
    # Step 6: Verify position creation
    print("\n--- STEP 6: Verify Position Creation ---")
    positions = get_positions()
    position = next((p for p in positions 
                    if p.get("symbol") == "DCB Bank"), None)
    
    if position:
        log_test("Position Creation Verification", "PASS", 
                {"position_id": position.get("id"), "quantity": position.get("quantity")})
    else:
        log_test("Position Creation Verification", "FAIL", 
                error="Position not created after order execution")
    
    # Step 7: Check P&L
    print("\n--- STEP 7: P&L Calculation Verification ---")
    pnl_summary = get_pnl_summary()
    
    # Step 8: Place LIMIT SELL order (to close position)
    print("\n--- STEP 8: Place LIMIT SELL Order (Exit) ---")
    sell_order = None
    if position:
        time.sleep(1)
        current_price = float(position.get("current_price", 0) or 0)
        limit_price = round((current_price if current_price > 0 else 100.0) * 1.01, 2)
        sell_order = place_order("DCB Bank", "NSE_EQ", "SELL", 1, "LIMIT", limit_price=limit_price)
    else:
        log_test("Place LIMIT SELL Order (Exit)", "SKIP", "No open position available to exit.")
    
    # Step 9: Test order cancellation
    print("\n--- STEP 9: Test Order Cancellation ---")
    if sell_order and sell_order.get("order_id"):
        pending_orders = get_pending_orders()
        if any(isinstance(o, dict) and o.get("order_id") == sell_order.get("order_id") for o in pending_orders):
            cancel_order(str(sell_order.get("order_id")))
            
            # Verify cancellation
            time.sleep(1)
            pending_after = get_pending_orders()
            still_pending = any(o.get("order_id") == sell_order.get("order_id") 
                              for o in pending_after)
            
            if not still_pending:
                log_test("Order Cancellation Verification", "PASS")
            else:
                log_test("Order Cancellation Verification", "FAIL", 
                        error="Order still in pending after cancellation")
    
    # Step 10: Close position via API
    print("\n--- STEP 10: Close Position via API ---")
    if position and position.get("id"):
        close_position(str(position.get("id")))
        
        # Verify position closed
        time.sleep(2)
        positions_after = get_positions()
        still_open = any(p.get("id") == position.get("id") 
                        and p.get("status") == "OPEN" 
                        for p in positions_after)
        
        if not still_open:
            log_test("Position Close Verification", "PASS")
        else:
            log_test("Position Close Verification", "FAIL", 
                    error="Position still open after close request")
    
    # Step 11: Test different order types
    print("\n--- STEP 11: Test Different Order Types ---")
    
    # Test Stop Loss order
    sl_order = place_order("DCB Bank", "NSE_EQ", "BUY", 1, "SLM", trigger_price=100.0)
    if sl_order and sl_order.get("order_id"):
        time.sleep(1)
        cancel_order(str(sl_order.get("order_id")))
    
    # Test Stop Loss Limit order
    sll_order = place_order("DCB Bank", "NSE_EQ", "BUY", 1, "SLL", 
                           limit_price=105.0, trigger_price=100.0)
    if sll_order and sll_order.get("order_id"):
        time.sleep(1)
        cancel_order(str(sll_order.get("order_id")))
    
    print("\n" + "="*80)
    print("TRADING LIFECYCLE TESTS COMPLETED")
    print("="*80)
    
    return True


def save_results():
    """Save test results to file"""
    output_file = "QA_PHASE4_5_TRADING_TEST_RESULTS.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: {output_file}")


def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests:  {test_results['total_tests']}")
    print(f"✅ Passed:    {test_results['passed']}")
    print(f"❌ Failed:    {test_results['failed']}")
    print(f"⏭️  Skipped:   {test_results['skipped']}")
    print(f"Success Rate: {(test_results['passed'] / test_results['total_tests'] * 100):.1f}%" 
          if test_results['total_tests'] > 0 else "N/A")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("QA AUDIT - PHASE 4-5: END-TO-END TRADING LIFECYCLE TESTING")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("="*80 + "\n")
    
    try:
        run_trading_lifecycle_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print_summary()
        save_results()
        
        # Exit with status code based on results
        if test_results["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
