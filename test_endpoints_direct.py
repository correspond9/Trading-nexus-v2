#!/usr/bin/env python3
"""Test the margin calculate and order endpoints directly"""
import requests
import json

BASE_URL = "https://api.tradingnexus.pro/api/v2"

print('='*70)
print('TESTING BACKEND ENDPOINTS')
print('='*70)
print()

# Test 1: Margin calculation for Reliance (equity)
print('1. Testing /margin/calculate for Rel iance (NSE_EQ)')
print()

margin_payload = {
    "instrument_token": 2885,  # Reliance token
    "side": "BUY",
    "quantity": 1,
    "product_type": "MIS",
    "price": 1431.30
}

try:
    response = requests.post(
        f"{BASE_URL}/margin/calculate",
        json=margin_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f'   Status Code: {response.status_code}')
    print(f'   Response:')
    try:
        data = response.json()
        print(f'   {json.dumps(data, indent=2)}')
    except:
        print(f'   {response.text[:500]}')
    print()
    
except Exception as e:
    print(f'   Error: {e}')
    print()

# Test 2: Place order for Reliance
print('2. Testing /trading/orders for Reliance (BUY)')
print()

order_payload = {
    "instrument_token": 2885,
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 1,
    "product_type": "MIS"
}

try:
    response = requests.post(
        f"{BASE_URL}/trading/orders",
        json=order_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f'   Status Code: {response.status_code}')
    print(f'   Response:')
    try:
        data = response.json()
        print(f'   {json.dumps(data, indent=2)}')
    except:
        print(f'   {response.text[:500]}')
    print()
    
except Exception as e:
    print(f'   Error: {e}')
    print()

print('='*70)
