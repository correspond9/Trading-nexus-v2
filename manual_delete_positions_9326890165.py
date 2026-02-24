#!/usr/bin/env python3
"""
MANUAL DELETE ALL POSITIONS FOR USER 9326890165
Run this to immediately delete all positions when the API endpoint fails
"""
import asyncio
import asyncpg
import sys

async def delete_all_positions_manual():
    """Delete all positions for user 9326890165 via direct database connection"""
    
    # Database connection details (update if different)
    DB_CONFIG = {
        'host': '72.62.228.112',
        'port': 5432,
        'database': 'trading_terminal',
        'user': 'trading_user',
        'password': 'NFTY_4x_5G!'  # Update if needed
    }
    
    USER_MOBILE = '9326890165'
    
    print(f"🔗 Connecting to database...")
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print(f"✓ Connected to PostgreSQL\n")
        
        # Step 1: Get user UUID
        user = await conn.fetchrow(
            "SELECT id, mobile, name FROM users WHERE mobile = $1",
            USER_MOBILE
        )
        
        if not user:
            print(f"❌ User {USER_MOBILE} not found!")
            await conn.close()
            sys.exit(1)
        
        user_id = user['id']
        user_name = user['name'] or 'Unknown'
        print(f"👤 Found user: {user_name} ({USER_MOBILE})")
        print(f"   UUID: {user_id}\n")
        
        # Step 2: Count before deletion
        pos_count = await conn.fetchval(
            "SELECT COUNT(*) FROM paper_positions WHERE user_id = $1", user_id
        )
        orders_count = await conn.fetchval(
            "SELECT COUNT(*) FROM paper_orders WHERE user_id = $1", user_id
        )
        trades_count = await conn.fetchval(
            "SELECT COUNT(*) FROM paper_trades WHERE user_id = $1", user_id
        )
        ledger_count = await conn.fetchval(
            "SELECT COUNT(*) FROM ledger_entries WHERE user_id = $1", user_id
        )
        
        print("📊 Current Records:")
        print(f"   Positions: {pos_count}")
        print(f"   Orders: {orders_count}")
        print(f"   Trades: {trades_count}")
        print(f"   Ledger Entries: {ledger_count}")
        print(f"   TOTAL: {pos_count + orders_count + trades_count + ledger_count}\n")
        
        if pos_count == 0 and orders_count == 0:
            print("✓ User already has no positions or orders!")
            await conn.close()
            return
        
        # Step 3: Confirm deletion
        confirm = input(f"⚠️  DELETE ALL {pos_count + orders_count + trades_count + ledger_count} records? Type 'YES' to confirm: ")
        if confirm != 'YES':
            print("❌ Deletion cancelled.")
            await conn.close()
            return
        
        print("\n🔥 Starting deletion...\n")
        
        # Step 4: Delete in correct order (respect foreign keys)
        # Order is important: ledger → trades → orders → positions
        
        deleted_ledger = await conn.execute(
            "DELETE FROM ledger_entries WHERE user_id = $1", user_id
        )
        print(f"✓ Deleted ledger entries: {deleted_ledger}")
        
        deleted_trades = await conn.execute(
            "DELETE FROM paper_trades WHERE user_id = $1", user_id
        )
        print(f"✓ Deleted paper trades: {deleted_trades}")
        
        deleted_orders = await conn.execute(
            "DELETE FROM paper_orders WHERE user_id = $1", user_id
        )
        print(f"✓ Deleted paper orders: {deleted_orders}")
        
        deleted_positions = await conn.execute(
            "DELETE FROM paper_positions WHERE user_id = $1", user_id
        )
        print(f"✓ Deleted paper positions: {deleted_positions}")
        
        # Step 5: Verify deletion
        remaining_pos = await conn.fetchval(
            "SELECT COUNT(*) FROM paper_positions WHERE user_id = $1", user_id
        )
        remaining_orders = await conn.fetchval(
            "SELECT COUNT(*) FROM paper_orders WHERE user_id = $1", user_id
        )
        
        print(f"\n✅ DELETION COMPLETE!")
        print(f"   Remaining positions: {remaining_pos}")
        print(f"   Remaining orders: {remaining_orders}")
        
        if remaining_pos == 0 and remaining_orders == 0:
            print(f"\n✓ All positions successfully deleted for {USER_MOBILE}")
        else:
            print(f"\n⚠️  Warning: Some records may still remain")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("="*80)
    print("MANUAL POSITION DELETION SCRIPT")
    print("User: 9326890165")
    print("="*80 + "\n")
    
    asyncio.run(delete_all_positions_manual())
