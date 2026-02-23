import asyncio
import asyncpg

async def check_db():
    # Connect to the remote database
    conn = await asyncpg.connect(
        host="72.62.228.112",
        port=5432,
        user="postgres",
        password="dhanishpostgres",
        database="trading_terminal"
    )
    
    try:
        # Check if users exist
        users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"Total users in database: {users_count}")
        
        # Get all users
        users = await conn.fetch("SELECT id, mobile, role, first_name FROM users ORDER BY mobile")
        print("\nUsers:")
        for user in users:
            print(f"  - {user['mobile']} ({user['role']}) - {user['first_name']}")
        
        # Check paper_accounts
        accounts_count = await conn.fetchval("SELECT COUNT(*) FROM paper_accounts")
        print(f"\nTotal paper_accounts: {accounts_count}")
        
        # Check if any paper_accounts have the default users
        accounts = await conn.fetch("SELECT user_id, display_name, balance, margin_allotted FROM paper_accounts")
        print("\nPaper Accounts:")
        for acc in accounts:
            print(f"  - User ID: {acc['user_id']}, Name: {acc['display_name']}, Balance: {acc['balance']}, Margin: {acc['margin_allotted']}")
        
        # Try the actual query from the endpoint
        print("\nTrying actual endpoint query:")
        rows = await conn.fetch("""
            SELECT u.user_no, u.id, u.first_name, u.last_name, u.email,
                   u.mobile, u.role, u.status, u.is_active, u.created_at,
                   u.address, u.country, u.state, u.city,
                   u.aadhar_number, u.pan_number, u.upi, u.bank_account,
                   u.brokerage_plan,
                   (u.aadhar_doc IS NOT NULL)           AS has_aadhar_doc,
                   (u.cancelled_cheque_doc IS NOT NULL) AS has_cheque_doc,
                   (u.pan_card_doc IS NOT NULL)         AS has_pan_doc,
                   COALESCE(pa.balance, 0)              AS wallet_balance,
                   COALESCE(pa.margin_allotted, 0)      AS margin_allotted
            FROM users u
            LEFT JOIN paper_accounts pa ON pa.user_id = u.id
            ORDER BY u.user_no
        """)
        
        print(f"Query returned {len(rows)} rows")
        for r in rows:
            print(f"  - {r['mobile']} ({r['role']}): wallet={r['wallet_balance']}, margin={r['margin_allotted']}")
            # Try to convert to float like the endpoint does
            try:
                wb = float(r.get("wallet_balance") or 0)
                ma = float(r.get("margin_allotted") or 0)
                print(f"    Conversion successful: wb={wb}, ma={ma}")
            except Exception as e:
                print(f"    ERROR converting to float: {e}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_db())
