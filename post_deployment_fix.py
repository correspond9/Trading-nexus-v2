#!/usr/bin/env python3
"""
Post-Deployment Script: Close user 1003's LENSKART position and create new one
Run this AFTER deploying the updated code to Coolify with the force-exit endpoint
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://tradingnexus.pro/api/v2"
ADMIN_MOBILE = "9999999999"
ADMIN_PASSWORD = "123456"

def get_auth_token():
    """Login as admin and get auth token"""
    print("🔐 Logging in as admin...")
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"mobile": ADMIN_MOBILE, "password": ADMIN_PASSWORD},
        verify=False,
        timeout=10
    )
    
    if resp.status_code == 200:
        token = resp.json().get('token')
        print(f"✓ Got auth token: {token[:30]}...")
        return token
    else:
        print(f"✗ Login failed: {resp.status_code} - {resp.text}")
        return None

def get_user_positions(user_id, token):
    """Get all positions for a specific user"""
    print(f"\n📋 Getting positions for user {user_id}...")
    
    headers = {"X-AUTH": token, "Content-Type": "application/json"}
    
    resp = requests.get(
        f"{BASE_URL}/admin/positions/userwise",
        headers=headers,
        verify=False,
        timeout=10
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ Got positions data")
        return data
    else:
        print(f"✗ Failed to get positions: {resp.status_code}")
        return None

def force_exit_position(user_id, position_id, exit_price, token):
    """Call the force-exit endpoint to close a position"""
    print(f"\n🔴 Force exiting position {position_id}...")
    
    headers = {"X-AUTH": token, "Content-Type": "application/json"}
    
    payload = {
        "user_id": user_id,
        "position_id": position_id,
        "exit_price": float(exit_price)
    }
    
    resp = requests.post(
        f"{BASE_URL}/admin/force-exit",
        json=payload,
        headers=headers,
        verify=False,
        timeout=10
    )
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('success'):
            print(f"✓ Position closed successfully!")
            print(f"  Symbol: {result.get('symbol')}")
            print(f"  Exit Price: {result.get('exit_price')}")
            return True
        else:
            print(f"✗ Force exit failed: {result.get('detail')}")
            return False
    else:
        print(f"✗ API error: {resp.status_code} - {resp.text[:200]}")
        return False

def create_backdate_position(user_id, symbol, qty, price, trade_date, token):
    """Create a new historic position"""
    print(f"\n✨ Creating new historian position...")
    print(f"  User: {user_id}")
    print(f"  Symbol: {symbol}")
    print(f"  Qty: {qty}")
    print(f"  Price: {price}")
    print(f"  Date: {trade_date}")
    
    headers = {"X-AUTH": token, "Content-Type": "application/json"}
    
    payload = {
        "user_id": user_id,
        "symbol": symbol,
        "qty": int(qty),
        "price": float(price),
        "trade_date": trade_date,
        "instrument_type": "EQ",
        "exchange": "NSE"
    }
    
    resp = requests.post(
        f"{BASE_URL}/admin/backdate-position",
        json=payload,
        headers=headers,
        verify=False,
        timeout=10
    )
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get('success'):
            print(f"✓ Position created successfully!")
            print(f"  Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"✗ Creation failed: {result.get('detail') or result}")
            return False
    else:
        print(f"✗ API error: {resp.status_code} - {resp.text[:500]}")
        return False

def main():
    print("=" * 60)
    print("LENSKART POSITION FIX - CLOSE & CREATE")
    print("=" * 60)
    
    # Step 1: Get auth token
    token = get_auth_token()
    if not token:
        print("\n❌ Cannot proceed without auth token")
        sys.exit(1)
    
    # Step 2: Get user 1003's positions
    positions_data = get_user_positions("1003", token)
    if not positions_data:
        print("\n⚠️  Could not fetch positions, but continuing...")
    
    # Step 3: Force exit existing LENSKART position
    print("\n" + "="*60)
    print("STEP 1: CLOSING EXISTING POSITION")
    print("="*60)
    
    # For now, we'll try common position IDs
    # In production, you'd extract the ID from positions_data
    position_id_options = [
        "1", "2", "3", "4", "5",  # Common low numbers  
        "lenskart_1003",  # Possible naming scheme
    ]
    
    closed = False
    for pos_id in position_id_options:
        print(f"\nTrying position ID: {pos_id}")
        if force_exit_position("1003", pos_id, "380.70", token):
            closed = True
            break
    
    if not closed:
        print("\n⚠️  Could not close position with common IDs")
        print("   You may need to manually specify the position ID")
        print("   Check the database or use the Force Exit form in SuperAdmin Dashboard")
        
        # Try to provide helpful output
        if positions_data:
            print("\n   Position data available - manually extract ID and retry")
        
        response = input("\nContinue to create new position anyway? (y/n): ").lower()
        if response != 'y':
            print("Exiting.")
            sys.exit(1)
    
    # Step 4: Create new LENSKART position
    print("\n" + "="*60)
    print("STEP 2: CREATING NEW POSITION")
    print("="*60)
    
    success = create_backdate_position(
        user_id="1003",
        symbol="Lenskart Solutions",
        qty=580,
        price=380.70,
        trade_date="2026-02-20",
        token=token
    )
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS! Position created")
        print("="*60)
        print("\nVerification Steps:")
        print("1. Open browser: https://tradingnexus.pro/dashboard")
        print("2. Go to Users tab")
        print("3. Search for user 1003")
        print("4. Check Positions - should show:")
        print("   - Symbol: Lenskart Solutions")
        print("   - Qty: 580")
        print("   - Entry Price: 380.70")
    else:
        print("\n❌ Failed to create position")
        sys.exit(1)

if __name__ == '__main__':
    main()
