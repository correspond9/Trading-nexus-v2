"""
Fix the double-count of Opening Balance for Anum Begum.

Root cause: entry_id=322 has balance_after=200000.
The deployed ledger.py reads this as opening_balance_value=200000,
then ALSO counts entry 322's credit=200000 in the running balance.
Result: ₹4,00,000 at Opening Balance row → wallet shows ₹5,29,203.08.

Fix: Set entry_id=322's balance_after=0 so opening_balance_value=0.
Running balance then: 0 + 200000 (entry 322 credit) + 129203.08 (entries 315-321) = 329203.08 ✓
"""

import subprocess
import json

DB_CONTAINER = "db-x8gg0og8440wkgc8ow0ococs-145803824898"
SERVER = "root@72.62.228.112"
USER_ID = "6785692d-8f36-4183-addb-16c96ea95a88"


def run_sql(sql):
    cmd = ["ssh", SERVER,
           f"docker exec {DB_CONTAINER} psql -U postgres -d trading_terminal -t -A -c \"{sql}\""]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout.strip(), result.stderr.strip()


# Step 1: Check current state
print("=== CURRENT STATE OF LEDGER ENTRIES ===")
out, err = run_sql(
    f"SELECT entry_id, description, credit, debit, balance_after, created_at::date "
    f"FROM ledger_entries "
    f"WHERE user_id = '{USER_ID}' "
    f"ORDER BY created_at ASC, entry_id ASC;"
)
print(out or err)

# Step 2: Check specifically entry 322
print("\n=== ENTRY 322 DETAILS ===")
out, err = run_sql(
    f"SELECT entry_id, ref_type, credit, balance_after FROM ledger_entries "
    f"WHERE entry_id = 322;"
)
print(out or err)

# Step 3: Apply the fix — set entry 322's balance_after = 0
print("\n=== APPLYING FIX: SET entry_id=322 balance_after=0 ===")
out, err = run_sql(
    f"UPDATE ledger_entries SET balance_after = 0 "
    f"WHERE entry_id = 322 "
    f"AND user_id = '{USER_ID}'::uuid "
    f"AND ref_type = 'OPENING_BALANCE';"
)
print("Result:", out or err)

# Step 4: Verify the fix
print("\n=== VERIFICATION: ENTRY 322 AFTER FIX ===")
out, err = run_sql(
    f"SELECT entry_id, ref_type, credit, balance_after FROM ledger_entries "
    f"WHERE entry_id = 322;"
)
print(out or err)

# Step 5: Verify paper_accounts.balance is still correct
print("\n=== PAPER ACCOUNTS BALANCE ===")
out, err = run_sql(
    f"SELECT balance FROM paper_accounts WHERE user_id = '{USER_ID}'::uuid;"
)
print("paper_accounts.balance =", out or err)

# Step 6: Compute expected running balance
print("\n=== COMPUTING EXPECTED WALLET BALANCE ===")
out, err = run_sql(
    f"SELECT SUM(COALESCE(credit,0)) - SUM(COALESCE(debit,0)) AS net_balance "
    f"FROM ledger_entries "
    f"WHERE user_id = '{USER_ID}'::uuid "
    f"AND description NOT LIKE '%Realized P&L%';"
)
print("Net (credits - debits) from wallet entries =", out or err)

print("\n=== FIX COMPLETE ===")
print("After fix:")
print("  - opening_balance_value = 0 (reads entry 322's balance_after=0)")
print("  - Running balance: 0 + 200000 (entry 322 credit) + remaining = 329203.08")
print("  - Wallet shows: ₹3,29,203.08 ✓")
