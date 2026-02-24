import requests
import time
import sys

API = "https://tradingnexus.pro/api/v2"

print("=" * 70)
print("  Monitoring Deployment & Instrument Master Refresh")
print("=" * 70)

# Login
print("\n1. Logging in as super admin...")
login_response = requests.post(f"{API}/auth/login", json={
    "mobile": "9999999999",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    sys.exit(1)

token = login_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in\n")

# Monitor for up to 5 minutes
print("2. Waiting for deployment to complete and instrument master to populate...")
print("   (Checking every 15 seconds for up to 5 minutes)\n")

for attempt in range(20):  # 20 * 15 = 300 seconds = 5 minutes
    try:
        status_response = requests.get(f"{API}/admin/scrip-master/status", headers=headers, timeout=10)
        
        if status_response.status_code == 200:
            status = status_response.json()
            total = status.get('total', 0)
            subscribed = status.get('subscribed', 0)
            refreshed_at = status.get('refreshed_at', 'Never')
            
            print(f"   [{attempt + 1:2d}/20] Total: {total:6d} | Subscribed: {subscribed:6d} | Last refresh: {refreshed_at}")
            
            if total > 0:
                print(f"\n✅ SUCCESS! Instrument master populated with {total} instruments")
                print(f"   Subscribed (Tier A/B): {subscribed}")
                
                # Verify DISPLAY_NAME is in symbol field
                print("\n3. Verifying DISPLAY_NAME is used in symbol field...")
                search_response = requests.get(f"{API}/instruments/search?q=RELIANCE&limit=1")
                if search_response.status_code == 200:
                    results = search_response.json()
                    if results:
                        symbol = results[0].get('symbol', '')
                        print(f"   Sample symbol field: '{symbol}'")
                        if len(symbol) > 15:  # Display names are longer than tickers
                            print("   ✅ Symbol field contains DISPLAY_NAME (user-friendly name)")
                        else:
                            print(f"   ⚠️  Symbol field might contain ticker: '{symbol}'")
                
                break
        else:
            print(f"   [{attempt + 1:2d}/20] API returned {status_response.status_code} - deployment might be in progress...")
    
    except requests.exceptions.RequestException as e:
        print(f"   [{attempt + 1:2d}/20] Backend not responding - deployment in progress...")
    
    if attempt < 19:
        time.sleep(15)
else:
    print("\n⚠️  Timeout: Deployment or refresh taking longer than expected")
    print("   Check Coolify logs for details")

print("\n" + "=" * 70)
print("  Done!")
print("=" * 70)
