#!/usr/bin/env python3
"""
Trigger DhanHQ stream startup after credentials are saved.
This makes the backend reinitialize and subscribe to Tier-B instruments.
"""
import requests
import time
import json

API_BASE = "https://api.tradingnexus.pro/api/v2"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"  # SUPER_ADMIN token
HEADERS = {"X-AUTH": TOKEN}

def main():
    print("\n" + "=" * 80)
    print("DHAN STREAM INITIALIZATION")
    print("=" * 80 + "\n")

    # Step 1: Check current status
    print("[1] Checking current DhanHQ status...")
    try:
        resp = requests.get(f"{API_BASE}/admin/dhan/status", headers=HEADERS, timeout=10)
        status = resp.json()
        print(f"    Status: {json.dumps(status, indent=2)}")
        
        if status.get("has_credentials"):
            print("    ✓ Credentials are saved")
        else:
            print("    ❌ NO CREDENTIALS FOUND!")
            print("    Please save DhanHQ Client ID and Access Token in Admin settings first.")
            return False
            
        if status.get("connected"):
            print("    ✓ WebSocket slots are connected")
            total_tokens = sum(s.get("tokens", 0) for s in status.get("slots", []))
            print(f"    Tokens subscribed: {total_tokens}")
            
            if total_tokens == 0:
                print("    ⚠ No tokens subscribed - need to reconnect to trigger subscription")
        else:
            print("    ❌ WebSocket slots NOT connected")

    except Exception as e:
        print(f"    ❌ Error checking status: {e}")
        return False

    # Step 2: Disconnect and reconnect
    print("\n[2] Disconnecting existing streams...")
    try:
        resp = requests.post(f"{API_BASE}/admin/dhan/disconnect", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            print(f"    ✓ Disconnected")
        time.sleep(2)
    except Exception as e:
        print(f"    ⚠ Warning disconnecting: {e}")

    print("\n[2] Triggering connect to load Tier-B subscriptions...")
    try:
        resp = requests.post(f"{API_BASE}/admin/dhan/connect", headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            print(f"    ✓ Connect triggered: {result.get('message')}")
            if result.get("errors"):
                print(f"    ⚠ Errors: {result.get('errors')}")
        else:
            print(f"    ❌ Connect failed: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"    ❌ Error triggering connect: {e}")
        return False

    # Step 3: Wait for subscriptions to load
    print("\n[3] Waiting for Tier-B subscriptions to load (may take 10-30 seconds)...")
    for i in range(12):
        time.sleep(5)
        try:
            resp = requests.get(f"{API_BASE}/admin/dhan/status", headers=HEADERS, timeout=10)
            status = resp.json()
            total_tokens = sum(s.get("tokens", 0) for s in status.get("slots", []))
            print(f"    [{i*5}s] Subscribed tokens: {total_tokens}")
            
            if total_tokens > 0:
                print(f"    ✓ SUCCESS! {total_tokens} Tier-B instruments subscribed")
                
                # Print breakdown
                print("\n    Slot breakdown:")
                for slot in status.get("slots", []):
                    print(f"      WS-{slot['slot']}: {slot.get('tokens', 0)}/{slot.get('capacity', 5000)} tokens")
                
                return True
        except Exception as e:
            print(f"    [{i*5}s] Still waiting... ({e})")

    print("    ⚠ Timeout: Subscriptions did not load in time")
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
