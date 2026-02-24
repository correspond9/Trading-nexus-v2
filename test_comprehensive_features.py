#!/usr/bin/env python3
"""
Comprehensive test suite for:
1. Trade History - records all executed trades of all users
2. P&L Page - records realized profit and losses of all users
3. Ledger Page - records PAYINS, PAYOUTS, PROFITS (credits), LOSSES (debits) for all users

Test Strategy:
- Create test positions for multiple users
- Execute trades (close positions)
- Verify entries in Trade History, P&L, and Ledger
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "https://tradingnexus.pro/api/v2"
ADMIN_MOBILE = "9999999999"
ADMIN_PASSWORD = "123456"

# Test users to create
TEST_USERS = [
    {"mobile": "8001111111", "name": "TestUser1", "initial_balance": 100000},
    {"mobile": "8002222222", "name": "TestUser2", "initial_balance": 50000},
]

PRINT_COLORS = {
    'header': '\033[95m',
    'blue': '\033[94m',
    'cyan': '\033[96m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'red': '\033[91m',
    'end': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m',
}

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{PRINT_COLORS['bold']}{PRINT_COLORS['cyan']}{'='*70}")
    print(f"  {title.upper()}")
    print(f"{'='*70}{PRINT_COLORS['end']}\n")

def print_success(msg):
    """Print success message"""
    print(f"{PRINT_COLORS['green']}✓ {msg}{PRINT_COLORS['end']}")

def print_error(msg):
    """Print error message"""
    print(f"{PRINT_COLORS['red']}✗ {msg}{PRINT_COLORS['end']}")

def print_info(msg):
    """Print info message"""
    print(f"{PRINT_COLORS['cyan']}  {msg}{PRINT_COLORS['end']}")

def get_admin_token():
    """Login as admin and get token"""
    print_section("1. Admin Authentication")
    
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD},
        verify=False,
        timeout=10
    )
    
    if resp.status_code != 200:
        print_error(f"Login failed: {resp.status_code} - {resp.text}")
        return None
    
    token = resp.json().get('token')
    print_success(f"Admin login successful: {token[:30]}...")
    return token

def create_test_positions(token, user_mobile):
    """Create multiple test positions for a user"""
    print_section(f"Creating Test Positions for User {user_mobile}")
    
    headers = {"X-AUTH": token, "Content-Type": "application/json"}
    
    # Multiple instruments to test
    positions = [
        {"symbol": "Reliance Industries", "qty": 10, "price": 2500, "time_offset": -60},
        {"symbol": "TCS", "qty": 5, "price": 3500, "time_offset": -30},
        {"symbol": "HDFC Bank", "qty": 20, "price": 1500, "time_offset": 0},
    ]
    
    trade_date = datetime.now().strftime("%d-%m-%Y")
    created_positions = []
    
    for pos in positions:
        # Calculate time within market hours (09:15 - 15:30)
        base_time = datetime.strptime("09:15", "%H:%M")
        offset_minutes = pos.pop("time_offset")
        trade_time = (base_time + timedelta(minutes=offset_minutes)).strftime("%H:%M")
        
        payload = {
            "user_id": user_mobile,
            "symbol": pos["symbol"],
            "qty": pos["qty"],
            "price": pos["price"],
            "trade_date": trade_date,
            "trade_time": trade_time,
            "instrument_type": "EQ",
            "exchange": "NSE",
            "product_type": "MIS"
        }
        
        resp = requests.post(
            f"{BASE_URL}/admin/backdate-position",
            json=payload,
            headers=headers,
            verify=False,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print_success(f"Created: {pos['qty']} {pos['symbol']} @ {pos['price']}")
                created_positions.append(data.get('position'))
            else:
                print_error(f"Failed to create: {data.get('detail')}")
        else:
            print_error(f"API error: {resp.status_code}")
    
    return created_positions

def get_user_positions(token, user_mobile):
    """Get all open positions for a user"""
    headers = {"X-AUTH": token}
    
    resp = requests.get(
        f"{BASE_URL}/portfolio/positions/{user_mobile}",
        headers=headers,
        verify=False,
        timeout=10
    )
    
    if resp.status_code == 200:
        return resp.json()
    else:
        print_error(f"Failed to get positions: {resp.status_code}")
        return []

def close_positions(token, user_mobile, positions):
    """Close multiple positions for a user"""
    print_section(f"Closing Positions for User {user_mobile}")
    
    headers = {"X-AUTH": token, "Content-Type": "application/json"}
    closed_positions = []
    
    exit_date = datetime.now().strftime("%d-%m-%Y")
    
    for idx, pos in enumerate(positions):
        # Vary exit times
        exit_times = ["10:30", "11:45", "14:00"]
        exit_time = exit_times[idx % len(exit_times)]
        
        # Use random exit price near original
        exit_price = float(pos.get('avg_price', pos.get('price', 1000))) * (1 + (idx % 3) * 0.02)
        
        payload = {
            "user_id": user_mobile,
            "position_id": pos.get('position_id', pos.get('id')),
            "exit_price": exit_price,
            "exit_date": exit_date,
            "exit_time": exit_time
        }
        
        resp = requests.post(
            f"{BASE_URL}/admin/force-exit",
            json=payload,
            headers=headers,
            verify=False,
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success'):
                print_success(f"Closed: {pos.get('symbol')} @ {exit_price:.2f}")
                closed_positions.append(data)
            else:
                print_error(f"Failed to close: {data.get('detail')}")
        else:
            print_error(f"API error: {resp.status_code}")
    
    return closed_positions

def get_trade_history(token, user_mobile=None):
    """Get trade history"""
    print_section("Trade History Report")
    
    headers = {"X-AUTH": token}
    
    # Get all trades
    endpoint = f"{BASE_URL}/trade-history"
    if user_mobile:
        endpoint += f"?user_id={user_mobile}"
    
    resp = requests.get(endpoint, headers=headers, verify=False, timeout=10)
    
    if resp.status_code != 200:
        print_error(f"Failed to get trade history: {resp.status_code}")
        return None
    
    data = resp.json()
    
    if isinstance(data, dict) and 'data' in data:
        trades = data['data']
    else:
        trades = data
    
    if not trades:
        print_error("No trades found in history")
        return trades
    
    print_success(f"Found {len(trades)} trades in history")
    
    # Display sample trades
    for trade in trades[:5]:
        symbol = trade.get('symbol', 'N/A')
        side = trade.get('side', 'N/A')
        qty = trade.get('quantity', 0)
        price = trade.get('fill_price', 0)
        print_info(f"{side:5} {qty:5} {symbol:20} @ {price:8.2f}")
    
    if len(trades) > 5:
        print_info(f"... and {len(trades) - 5} more trades")
    
    return trades

def get_pandl_report(token, user_mobile=None):
    """Get P&L report"""
    print_section("P&L Report")
    
    headers = {"X-AUTH": token}
    
    endpoint = f"{BASE_URL}/pandl"
    if user_mobile:
        endpoint += f"?user_id={user_mobile}"
    
    resp = requests.get(endpoint, headers=headers, verify=False, timeout=10)
    
    if resp.status_code != 200:
        print_error(f"Failed to get P&L: {resp.status_code}")
        return None
    
    data = resp.json()
    
    if isinstance(data, dict) and 'data' in data:
        pnl_items = data['data']
    else:
        pnl_items = data
    
    if not pnl_items:
        print_error("No P&L data found")
        return pnl_items
    
    print_success(f"Found {len(pnl_items)} P&L items")
    
    total_pnl = 0
    for item in pnl_items[:10]:
        realized = item.get('realized_pnl', 0)
        unrealized = item.get('unrealized_pnl', 0)
        symbol = item.get('symbol', 'N/A')
        total = realized + unrealized
        total_pnl += realized
        
        print_info(f"{symbol:20} Realized: {realized:10.2f}  Unrealized: {unrealized:10.2f}")
    
    print_success(f"Total Realized P&L: {total_pnl:.2f}")
    
    return pnl_items

def get_ledger(token, user_mobile):
    """Get Ledger entries"""
    print_section(f"Ledger for User {user_mobile}")
    
    headers = {"X-AUTH": token}
    
    resp = requests.get(
        f"{BASE_URL}/ledger/{user_mobile}",
        headers=headers,
        verify=False,
        timeout=10
    )
    
    if resp.status_code != 200:
        print_error(f"Failed to get ledger: {resp.status_code}")
        return None
    
    data = resp.json()
    
    if isinstance(data, dict) and 'data' in data:
        ledger_items = data['data']
    elif isinstance(data, dict) and 'ledger' in data:
        ledger_items = data['ledger']
    else:
        ledger_items = data
    
    if not ledger_items:
        print_error("No ledger entries found")
        return ledger_items
    
    print_success(f"Found {len(ledger_items)} ledger entries")
    
    # Display entries
    categories = {}
    for item in ledger_items:
        # Try different field names
        entry_type = item.get('type') or item.get('entry_type') or item.get('category') or 'UNKNOWN'
        amount = item.get('amount') or item.get('credit') or item.get('debit') or 0
        
        if entry_type not in categories:
            categories[entry_type] = []
        categories[entry_type].append(amount)
    
    # Show summary
    for category, amounts in categories.items():
        total = sum(amounts)
        count = len(amounts)
        print_info(f"{category:15} x{count:2d} → Total: {total:10.2f}")
    
    return ledger_items

def validate_features(token):
    """Run comprehensive feature validation"""
    print_section("Feature Validation")
    
    validation_results = {
        "trade_history": False,
        "pandl": False,
        "ledger": False,
    }
    
    try:
        # Check Trade History
        trades = get_trade_history(token)
        if trades and len(trades) > 0:
            validation_results["trade_history"] = True
            print_success("Trade History: ✓ Working")
        else:
            print_error("Trade History: ✗ No trades recorded")
        
        time.sleep(1)
        
        # Check P&L
        pnl = get_pandl_report(token)
        if pnl and len(pnl) > 0:
            validation_results["pandl"] = True
            print_success("P&L Report: ✓ Working")
        else:
            print_error("P&L Report: ✗ No P&L data")
        
        time.sleep(1)
        
        # Check Ledger for a test user
        ledger = get_ledger(token, TEST_USERS[0]["mobile"])
        if ledger and len(ledger) > 0:
            validation_results["ledger"] = True
            print_success("Ledger: ✓ Working")
        else:
            print_error("Ledger: ✗ No ledger entries")
    
    except Exception as e:
        print_error(f"Validation error: {e}")
    
    # Summary
    print_section("Validation Summary")
    all_pass = all(validation_results.values())
    
    for feature, passed in validation_results.items():
        status = f"{PRINT_COLORS['green']}PASS{PRINT_COLORS['end']}" if passed else f"{PRINT_COLORS['red']}FAIL{PRINT_COLORS['end']}"
        print(f"  {feature:20} [{status}]")
    
    if all_pass:
        print_success("\n✓ All features validated successfully!")
    else:
        print_error("\n✗ Some features failed validation")
    
    return validation_results

def main():
    """Main test execution"""
    print(f"\n{PRINT_COLORS['bold']}{PRINT_COLORS['header']}")
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║         COMPREHENSIVE FEATURE VALIDATION TEST SUITE                     ║")
    print("║  Trade History | P&L | Ledger Validation for Multiple User Scenarios   ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    print(f"{PRINT_COLORS['end']}\n")
    
    # Step 1: Get admin auth
    token = get_admin_token()
    if not token:
        print_error("Cannot proceed without admin token")
        return
    
    # Step 2: Create positions and close them for test validation
    all_positions = {}
    for user_info in TEST_USERS:
        mobile = user_info["mobile"]
        positions = create_test_positions(token, mobile)
        if positions:
            all_positions[mobile] = positions
        time.sleep(2)
    
    # Step 3: Close positions to generate trades
    for user_mobile, positions in all_positions.items():
        close_positions(token, user_mobile, positions)
        time.sleep(2)
    
    # Step 4: Wait a moment for database to update
    print_section("Waiting for Database Updates")
    print_info("Waiting 3 seconds for data to be written...")
    time.sleep(3)
    
    # Step 5: Validate features
    results = validate_features(token)
    
    # Final summary
    print_section("Test Execution Complete")
    
    if all(results.values()):
        print(f"{PRINT_COLORS['green']}{PRINT_COLORS['bold']}")
        print("  ✓✓✓ ALL TESTS PASSED ✓✓✓")
        print(f"{PRINT_COLORS['end']}")
    else:
        print(f"{PRINT_COLORS['yellow']}")
        print("  ⚠ SOME FEATURES NEED ATTENTION")
        print(f"{PRINT_COLORS['end']}")
    
    # Recommendations
    print_section("Recommendations")
    print_info("If any feature failed, check:")
    print_info("1. Trade History: Verify trades are being inserted into paper_orders table")
    print_info("2. P&L: Verify realized_pnl is calculated correctly when positions close")
    print_info("3. Ledger: Verify ledger entries are created for payins/payouts/pnl")
    print()

if __name__ == '__main__':
    main()
