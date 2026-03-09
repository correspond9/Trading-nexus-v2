"""
Deploy Pending Orders Margin Feature via Coolify API
=====================================================
Triggers deployment of the margin reservation feature
"""
import asyncio
import aiohttp
import os

APP_UUID = 'x8gg0og8440wkgc8ow0ococs'
COOLIFY_URL = 'http://72.62.228.112'
COOLIFY_TOKEN = '2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7'

async def trigger_deployment():
    """Trigger deployment via Coolify API"""
    headers = {
        "Authorization": f"Bearer {COOLIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("=" * 80)
    print("DEPLOYING: Pending Orders Margin Reservation Feature")
    print("=" * 80)
    
    print(f"\nApp UUID: {APP_UUID}")
    print(f"Coolify URL: {COOLIFY_URL}")
    
    async with aiohttp.ClientSession() as session:
        # Trigger deployment
        print("\n🚀 Triggering deployment...")
        try:
            async with session.post(
                f"{COOLIFY_URL}/api/v1/applications/{APP_UUID}/deploy",
                headers=headers,
                json={},
                ssl=False
            ) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    deployment_id = data.get('id', 'unknown')
                    print(f"✅ Deployment triggered successfully!")
                    print(f"   Deployment ID: {deployment_id}")
                    
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
                    print("   Check Coolify dashboard for status:")
                    print(f"   https://coolify.io/project/your-project-id/application/{APP_UUID}")
                    
                    return True
                else:
                    error = await resp.text()
                    print(f"❌ Deployment failed: {resp.status}")
                    print(f"   Error: {error}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error triggering deployment: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(trigger_deployment())
    
    if success:
        print("\n" + "=" * 80)
        print("✅ DEPLOYMENT TRIGGERED SUCCESSFULLY")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Monitor deployment in Coolify dashboard")
        print("2. Once deployed, test with a user who has pending orders")
        print("3. Verify margin calculation includes pending orders")
    else:
        print("\n❌ DEPLOYMENT FAILED - Check error messages above")
