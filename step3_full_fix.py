#!/usr/bin/env python3
"""
Full fix for Anum Begum (6785692d-8f36-4183-addb-16c96ea95a88):
1. Insert KRITIKA closed position (realized_pnl=624, expense=94.88, net=529.12)
2. Insert SUNDARAM 2nd closed position (realized_pnl=9400, expense=596.79, net=8803.21)
3. Insert opening balance ledger entry (200000 at account creation time)
4. Update all existing ledger entries' balance_after (+200000 each)
5. Update paper_accounts.balance to 329203.08
"""

import subprocess

DB = "db-x8gg0og8440wkgc8ow0ococs-145803824898"
UID = "6785692d-8f36-4183-addb-16c96ea95a88"

def run_ssh_sql(sql, desc=""):
    # Escape double quotes inside the SQL for the shell
    escaped_sql = sql.replace('"', '\\"')
    cmd = ["ssh", "root@72.62.228.112",
           f'docker exec {DB} psql -U postgres -d trading_terminal -c "{escaped_sql}"']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if desc:
        print(f"\n=== {desc} ===")
    print(result.stdout.strip())
    if result.stderr and "ERROR" in result.stderr:
        print("ERROR:", result.stderr.strip())
    return result.returncode == 0

# ──────────────────────────────────────────────────────────────────────
# STEP 1: Insert KRITIKA closed position
# wipe_audit data: avg_price=5.42, realized_pnl=624.00, trade_expense=94.88
# closed_at from wipe_audit: 2026-03-04 09:22:00.411311+00
# instrument_token: 9288 (Kritika Wires / NSE_EQ)
# ──────────────────────────────────────────────────────────────────────
KRITIKA_SQL = f"""
INSERT INTO paper_positions 
  (user_id, instrument_token, symbol, exchange_segment, quantity, avg_price,
   status, realized_pnl, product_type, trade_expense, total_charges,
   charges_calculated, charges_calculated_at, opened_at, closed_at)
VALUES
  ('{UID}', 9288, 'KRITIKA', 'NSE_EQ', 0, 5.4200,
   'CLOSED', 624.00, 'NORMAL', 94.88, 94.88,
   true, '2026-03-04 09:22:00.411311+00',
   '2026-03-04 09:00:00+00', '2026-03-04 09:22:00.411311+00')
RETURNING position_id, symbol, realized_pnl, trade_expense;
""".strip()

run_ssh_sql(KRITIKA_SQL, "INSERT KRITIKA closed position")

# ──────────────────────────────────────────────────────────────────────
# STEP 2: Insert SUNDARAM 2nd closed position
# realized_pnl=9400.00, trade_expense=596.79, net=8803.21
# avg_price=1.31 (buy price of 2nd batch), closed ~08:01:45 on 04 Mar
# instrument_token: 18931 (Sundaram Multi Pap / NSE_EQ)
# ──────────────────────────────────────────────────────────────────────
SUNDARAM2_SQL = f"""
INSERT INTO paper_positions 
  (user_id, instrument_token, symbol, exchange_segment, quantity, avg_price,
   status, realized_pnl, product_type, trade_expense, total_charges,
   charges_calculated, charges_calculated_at, opened_at, closed_at)
VALUES
  ('{UID}', 18931, 'SUNDARAM', 'NSE_EQ', 0, 1.3100,
   'CLOSED', 9400.00, 'NORMAL', 596.79, 596.79,
   true, '2026-03-04 08:01:45.103721+00',
   '2026-03-04 07:30:00+00', '2026-03-04 08:01:45.103721+00')
RETURNING position_id, symbol, realized_pnl, trade_expense;
""".strip()

run_ssh_sql(SUNDARAM2_SQL, "INSERT SUNDARAM 2nd closed position")

# ──────────────────────────────────────────────────────────────────────
# STEP 3: Add opening balance ledger entry (₹200,000)
# Account created at 2026-02-24 11:11:34 — insert opening balance just before first entry
# ──────────────────────────────────────────────────────────────────────
OB_SQL = f"""
INSERT INTO ledger_entries 
  (user_id, created_at, description, debit, credit, balance_after, ref_type)
VALUES
  ('{UID}', '2026-02-24 11:11:34+00', 'Opening Balance', NULL, 200000.00, 200000.00, 'OPENING_BALANCE')
RETURNING entry_id, description, credit, balance_after;
""".strip()

run_ssh_sql(OB_SQL, "INSERT opening balance ₹200,000")

# ──────────────────────────────────────────────────────────────────────
# STEP 4: Update all 7 existing ledger entries — add 200000 to balance_after
# entry_ids: 315, 316, 317, 318, 319, 320, 321
# ──────────────────────────────────────────────────────────────────────
UPDATE_SQL = f"""
UPDATE ledger_entries
SET balance_after = balance_after + 200000.00
WHERE user_id = '{UID}'
  AND entry_id IN (315, 316, 317, 318, 319, 320, 321)
RETURNING entry_id, description, balance_after;
""".strip()

run_ssh_sql(UPDATE_SQL, "UPDATE existing ledger balance_after values (+200000)")

# ──────────────────────────────────────────────────────────────────────
# STEP 5: Update paper_accounts.balance to 329203.08
# ──────────────────────────────────────────────────────────────────────
ACCT_SQL = f"""
UPDATE paper_accounts
SET balance = 329203.08
WHERE user_id = '{UID}'
RETURNING user_id, display_name, balance;
""".strip()

run_ssh_sql(ACCT_SQL, "UPDATE paper_accounts balance to 329203.08")

print("\n✅ All steps completed successfully!")
