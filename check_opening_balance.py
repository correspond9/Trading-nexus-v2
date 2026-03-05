"""
Check if opening balance exists for the user shown in screenshot
"""
import asyncio
from app.database import init_db, get_pool

async def check_user_opening_balance():
    await init_db()
    pool = get_pool()
    
    # Based on screenshot, find user with mobile 9326890165
    user = await pool.fetchrow(
        "SELECT id, name, mobile FROM users WHERE mobile LIKE '%9326890165%'"
    )
    
    if not user:
        print("User not found")
        return
    
    print(f"User: {user['name']} ({user['mobile']}) - ID: {user['id']}")
    print("\n=== Opening Balance Entry ===")
    
    opening_entry = await pool.fetchrow(
        """
        SELECT * FROM ledger_entries 
        WHERE user_id = $1 AND ref_type = 'OPENING_BALANCE'
        """,
        user['id']
    )
    
    if opening_entry:
        print(f"Found: {dict(opening_entry)}")
    else:
        print("NO OPENING BALANCE ENTRY FOUND!")
    
    print("\n=== All Ledger Entries ===")
    all_entries = await pool.fetch(
        """
        SELECT created_at, description, debit, credit, balance_after, ref_type
        FROM ledger_entries 
        WHERE user_id = $1 
        ORDER BY created_at ASC
        LIMIT 10
        """,
        user['id']
    )
    
    for entry in all_entries:
        print(f"{entry['created_at']} | {entry['description'][:50]:50} | Credit: {entry['credit']} | Balance: {entry['balance_after']} | Type: {entry['ref_type']}")
    
    print("\n=== Paper Account ===")
    paper_account = await pool.fetchrow(
        "SELECT balance, display_name FROM paper_accounts WHERE user_id = $1",
        user['id']
    )
    if paper_account:
        print(f"Paper account balance: {paper_account['balance']}")
    else:
        print("No paper account found")

if __name__ == "__main__":
    asyncio.run(check_user_opening_balance())
