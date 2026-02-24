#!/usr/bin/env python3
"""
COMPREHENSIVE BACKDATE POSITION TEST - 3 TEST CASES
Tests the complete flow via browser API calls exactly as the browser would
"""

import requests
import warnings
import json
import time

warnings.filterwarnings('ignore')

BASE_URL = 'https://tradingnexus.pro/api/v2'
ADMIN_MOBILE = '8888888888'
ADMIN_PASSWORD = 'admin123'
TRADER1_ID = '00000000-0000-0000-0000-000000000003'

print('='*80)
print('COMPREHENSIVE BACKDATE POSITION TEST - 3 TEST CASES'.center(80))
print('='*80)

# Login as admin
print('\n[SETUP] Logging in as admin...')
r = requests.post(f'{BASE_URL}/auth/login',
                 verify=False,
                 json={'mobile': ADMIN_MOBILE, 'password': ADMIN_PASSWORD})
assert r.status_code == 200, f"Login failed: {r.status_code}"
token = r.json()['access_token']
print(f'✅ Login successful (token: {token[:30]}...)')

headers = {'Authorization': f'Bearer {token}'}

def test_backdate_position(test_num, search_query, expected_symbol_part, qty, price, trade_date):
    """Test complete backdate position flow"""
    print(f'\n{"="*80}')
    print(f'TEST {test_num}: {search_query}'.center(80))
    print('='*80)
    
    # Step 1: Search for instrument (like frontend does)
    print(f'\n[STEP 1] Searching for "{search_query}"...')
    r = requests.get(f'{BASE_URL}/instruments/search?q={search_query}&limit=8', verify=False)
    assert r.status_code == 200, f"Search failed: {r.status_code}"
    results = r.json()
    assert len(results) > 0, f"No search results for '{search_query}'"
    print(f'✅ Found {len(results)} results')
    
    # Get first equity result
    equity_results = [r for r in results if r.get('instrument_type') == 'EQUITY']
    assert len(equity_results) > 0, f"No EQUITY results found for '{search_query}'"
    
    selected = equity_results[0]
    print(f'\n[STEP 2] Selected instrument from dropdown:')
    print(f'   Symbol: "{selected.get("symbol")}"')
    print(f'   Display Name: "{selected.get("display_name")}"')
    print(f'   Exchange Segment: "{selected.get("exchange_segment")}"')
    print(f'   Instrument Type: "{selected.get("instrument_type")}"')
    
    # Verify it contains expected text
    assert expected_symbol_part.lower() in selected.get('symbol', '').lower(), \
        f"Expected '{expected_symbol_part}' in symbol '{selected.get('symbol')}'"
    
    # Step 3: Extract exchange and prepare payload (like frontend does)
    exchange_segment = selected.get('exchange_segment', 'NSE_EQ')
    base_exchange = exchange_segment.split('_')[0] if exchange_segment else 'NSE'
    inst_type = selected.get('instrument_type', 'EQUITY')
    
    # Map inst_type for backend
    if inst_type == 'EQUITY':
        backend_inst_type = 'EQ'
    elif inst_type.startswith('OPT'):
        backend_inst_type = 'OPTIDX' if 'IDX' in inst_type else 'OPTSTK'
    elif inst_type.startsWith('FUT'):
        backend_inst_type = 'FUTIDX' if 'IDX' in inst_type else 'FUTSTK'
    else:
        backend_inst_type = 'EQ'
    
    payload = {
        'user_id': TRADER1_ID,
        'symbol': selected.get('symbol'),  # Use exact symbol from search
        'qty': qty,
        'price': price,
        'trade_date': trade_date,
        'instrument_type': backend_inst_type,
        'exchange': base_exchange
    }
    
    print(f'\n[STEP 3] Creating backdate position with payload:')
    print(json.dumps(payload, indent=2))
    
    # Step 4: Submit to backend
    print(f'\n[STEP 4] Submitting to backend...')
    r = requests.post(f'{BASE_URL}/admin/backdate-position',
                     verify=False,
                     headers=headers,
                     json=payload)
    
    print(f'   Status Code: {r.status_code}')
    resp = r.json()
    
    if resp.get('success'):
        print(f'✅ SUCCESS!')
        print(f'   Message: {resp.get("message")}')
        if resp.get('position'):
            pos = resp['position']
            print(f'   Position ID: {pos.get("position_id")}')
            print(f'   Symbol: {pos.get("symbol")}')
            print(f'   Quantity: {pos.get("quantity")}')
            print(f'   Avg Price: {pos.get("avg_price")}')
        return True
    else:
        print(f'❌ FAILED!')
        print(f'   Error: {resp.get("detail")}')
        return False

# Run 3 test cases
print('\n\n' + '='*80)
print('RUNNING 3 TEST CASES'.center(80))
print('='*80)

results = []

# Test 1: ITC (single word, known EQUITY)
results.append(test_backdate_position(
    test_num=1,
    search_query='ITC',
    expected_symbol_part='ITC',
    qty=100,
    price=450.00,
    trade_date='20-02-2026'
))

time.sleep(1)

# Test 2: HDFC AMC (multi-word EQUITY)
results.append(test_backdate_position(
    test_num=2,
    search_query='HDFC',
    expected_symbol_part='HDFC',
    qty=50,
    price=2800.00,
    trade_date='21-02-2026'
))

time.sleep(1)

# Test 3: Info Edge (multi-word EQUITY with space)
results.append(test_backdate_position(
    test_num=3,
    search_query='Info',
    expected_symbol_part='Info',
    qty=75,
    price=1600.00,
    trade_date='22-02-2026'
))

# Final Summary
print('\n\n' + '='*80)
print('FINAL SUMMARY'.center(80))
print('='*80)

for i, result in enumerate(results, 1):
    status = '✅ PASSED' if result else '❌ FAILED'
    print(f'Test {i}: {status}')

total_passed = sum(results)
total_tests = len(results)

print(f'\nPassed: {total_passed}/{total_tests}')

if total_passed == total_tests:
    print('\n🎉 ALL TESTS PASSED! Backdate Position feature is working correctly!')
else:
    print(f'\n⚠️ {total_tests - total_passed} test(s) failed. Review errors above.')

print('='*80)
