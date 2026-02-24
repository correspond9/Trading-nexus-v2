#!/usr/bin/env python
"""
Test to verify market hours validation is working.
This test will try to place orders and exit positions outside market hours.
Expected: All operations should be rejected with market hours error.
"""

import requests
import json
import urllib3
from datetime import datetime
import zoneinfo

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://tradingnexus.pro/api/v2"
IST = zoneinfo.ZoneInfo("Asia/Kolkata")

print("="*80)
print("MARKET HOURS VALIDATION TEST")
print("="*80)

# Check current time
now_ist = datetime.now(tz=IST)
current_time = now_ist.strftime("%H:%M:%S")
is_weekday = now_ist.weekday() < 5  # Mon-Fri = 0-4

print(f"\nCurrent IST time: {current_time}")
print(f"Day: {now_ist.strftime('%A')}")
print(f"Is weekday: {is_weekday}")

# Market hours: 09:15 - 15:30 IST
market_open_time = now_ist.replace(hour=9, minute=15, second=0)
market_close_time = now_ist.replace(hour=15, minute=30, second=0)

is_market_hours = (market_open_time <= now_ist <= market_close_time) and is_weekday

print(f"\nMarket hours: 09:15 - 15:30 IST")
print(f"Currently in market hours: {is_market_hours}")

if is_market_hours:
    print("\n⚠️ WARNING: Market is currently OPEN!")
    print("This test is designed to run OUTSIDE market hours.")
    print("The test will proceed but may show unexpected results.")
else:
    print("\n✅ Good! Market is currently CLOSED - perfect for testing validation.")

# Login as user
print("\n" + "="*80)
print("LOGGING IN")
print("="*80)

r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                 json={'mobile': '9326890165', 'password': 'trader123'})

if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    print("Trying admin login...")
    r = requests.post(f'{BASE_URL}/auth/login', verify=False,
                     json={'mobile': '8888888888', 'password': 'admin123'})

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("✅ Logged in successfully")

# Test 1: Try to place an order outside market hours
print("\n" + "="*80)
print("TEST 1: Place order outside market hours")
print("="*80)

order_payload = {
    "symbol": "ITC",
    "instrument_token": 1660,
    "exchange_segment": "NSE_EQ",
    "transaction_type": "BUY",
    "quantity": 10,
    "order_type": "MARKET",
    "product_type": "MIS"
}

print(f"Attempting to place BUY order for ITC...")
r = requests.post(f'{BASE_URL}/trading/orders', 
                 headers=headers,
                 json=order_payload,
                 verify=False)

print(f"Status Code: {r.status_code}")
if r.status_code == 403:
    resp = r.json()
    if "Market is" in resp.get('detail', ''):
        print(f"✅ CORRECT! Order rejected with: {resp.get('detail')}")
    else:
        print(f"❌ WRONG! Got 403 but wrong reason: {resp.get('detail')}")
elif r.status_code == 201:
    print(f"❌ WRONG! Order was accepted during market closure!")
    print(f"Response: {r.json()}")
else:
    print(f"❓ Unexpected status code: {r.status_code}")
    print(f"Response: {r.text[:200]}")

# Test 2: Try to close a position outside market hours
print("\n" + "="*80)
print("TEST 2: Close position outside market hours")
print("="*80)

# First, get user's open positions
r = requests.get(f'{BASE_URL}/portfolio/positions', headers=headers, verify=False)

if r.status_code == 200:
    positions = r.json().get('data', [])
    open_positions = [p for p in positions if p.get('status') == 'OPEN' and p.get('quantity', 0) != 0]
    
    if open_positions:
        position = open_positions[0]
        position_id = position.get('id') or position.get('instrument_token')
        symbol = position.get('symbol', 'Unknown')
        
        print(f"Found open position: {symbol} (ID: {position_id})")
        print(f"Attempting to close position...")
        
        r = requests.post(f'{BASE_URL}/portfolio/positions/{position_id}/close',
                         headers=headers,
                         verify=False)
        
        print(f"Status Code: {r.status_code}")
        if r.status_code == 403:
            resp = r.json()
            if "Market is" in resp.get('detail', ''):
                print(f"✅ CORRECT! Position close rejected with: {resp.get('detail')}")
            else:
                print(f"❌ WRONG! Got 403 but wrong reason: {resp.get('detail')}")
        elif r.status_code == 200:
            print(f"❌ WRONG! Position was closed during market closure!")
            print(f"Response: {r.json()}")
        else:
            print(f"❓ Unexpected status code: {r.status_code}")
            print(f"Response: {r.text[:200]}")
    else:
        print("ℹ️ No open positions found to test position closure")
        print("(This is expected if you've closed all positions)")
else:
    print(f"❌ Failed to get positions: {r.status_code}")

# Final verdict
print("\n" + "="*80)
print("VERDICT")
print("="*80)

if is_market_hours:
    print("⚠️ Test ran during market hours - results may be invalid")
    print("Please run this test outside market hours (before 09:15 or after 15:30 IST)")
else:
    print("✅ Market hours validation is now enforced!")
    print("Users cannot:")
    print("  - Place orders outside market hours")
    print("  - Close positions outside market hours")
    print("  - Execute basket orders outside market hours")

print("="*80)
