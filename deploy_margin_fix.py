"""
Deploy Pending Orders Margin Feature via Coolify API
=====================================================
"""
import requests
import json

APP_UUID = 'x8gg0og8440wkgc8ow0ococs'
COOLIFY_URL = 'http://72.62.228.112:8000/api/v1'
API_TOKEN = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 80)
print("DEPLOYING: Pending Orders Margin Reservation Feature")
print("=" * 80)

print(f"\nApp UUID: {APP_UUID}")
print(f"Coolify URL: {COOLIFY_URL}")

print("\n🚀 Triggering deployment...")
try:
    deploy_response = requests.post(
        f'{COOLIFY_URL}/applications/{APP_UUID}/deploy',
        headers=headers,
        json={},
        timeout=30
    )
    
    deploy_response.raise_for_status()
    result = deploy_response.json()
    
    print("\n✅ Deployment triggered successfully!")
    print(json.dumps(result, indent=2))
    
    print("\n📝 Summary of Changes:")
    print("   • Database migration 033 applied ✓")
    print("   • Added calculate_pending_orders_margin() function")
    print("   • Updated margin.py to include pending orders")
    print("   • Updated orders.py to check pending orders margin")
    
    print("\n💡 What This Fixes:")
    print("   - Prevents over-leveraging from multiple pending orders")
    print("   - Reserves margin for fresh orders (not exits)")
    print("   - Available margin now = Allotted - (Positions + Pending)")
    
    print("\n⏳ Deployment in progress...")
    print("   Monitor the deployment status in Coolify dashboard")
    
    print("\n" + "=" * 80)
    print("✅ DEPLOYMENT TRIGGERED SUCCESSFULLY")
    print("=" * 80)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ Failed to trigger deployment:")
    print(f"   {str(e)}")
    if hasattr(e.response, 'text'):
        print(f"   Response: {e.response.text}")
