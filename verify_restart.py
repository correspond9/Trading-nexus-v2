import requests
import time
import sys

token = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'
headers = {'X-AUTH': token}

print("\n" + "=" * 80)
print("VERIFYING BACKEND RESTART & WEBSOCKET SUBSCRIPTIONS")
print("=" * 80 + "\n")

# Check 1: Backend Online
print("[1] Checking if backend is online...")
for i in range(10):
    try:
        resp = requests.get('https://api.tradingnexus.pro/api/v2/health', timeout=10)
        if resp.status_code == 200:
            print(f"    ✓ Backend responded after attempt {i+1}")
            time.sleep(3)
            break
    except:
        if i < 9:
            print(f"    Attempt {i+1}/10 - waiting...")
            time.sleep(3)
        else:
            print(f"    ❌ Backend not responding after 10 attempts")
            sys.exit(1)

# Check 2: DhanHQ Subscriptions
print("\n[2] Checking DhanHQ subscription status...")
try:
    resp = requests.get('https://api.tradingnexus.pro/api/v2/admin/dhan/status', 
                       headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"    ❌ API returned {resp.status_code}")
        print(f"    Response: {resp.text}")
        sys.exit(1)
    
    status = resp.json()
    total_tokens = sum(s.get('tokens', 0) for s in status.get('slots', []))
    
    print(f"    Credentials saved: {status.get('has_credentials')}")
    print(f"    WebSocket connected: {status.get('connected')}")
    print(f"    Total tokens subscribed: {total_tokens:,}")
    
    if total_tokens > 0:
        print("\n    ✅ SUCCESS! Tier-B subscriptions LOADED!")
        print("\n    Slot breakdown:")
        for slot in status.get('slots', []):
            tokens = slot.get('tokens', 0)
            capacity = slot.get('capacity', 5000)
            pct = (tokens / capacity * 100) if capacity > 0 else 0
            print(f"      WS-{slot['slot']}: {tokens:6,} / {capacity:,} ({pct:5.1f}%)")
        
        print("\n    ✓ WebSocket data is now ACTIVE!")
        print("    ✓ Open the Trading Dashboard to see live market prices")
    else:
        print("\n    ⚠ Subscriptions still loading (0 tokens)")
        print("    This may take 30-60 seconds after startup")
        print("    Please check again in a moment...")
        
except Exception as e:
    print(f"    ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 80 + "\n")
