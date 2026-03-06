import subprocess

DB = "db-x8gg0og8440wkgc8ow0ococs-145803824898"
UID = "6785692d-8f36-4183-addb-16c96ea95a88"

def q(sql, desc=""):
    cmd = ["ssh", "root@72.62.228.112",
           f'docker exec {DB} psql -U postgres -d trading_terminal -c "{sql}"']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if desc:
        print(f"\n=== {desc} ===")
    print(result.stdout.strip())
    if "ERROR" in result.stderr:
        print("ERROR:", result.stderr.strip())

# 1. Current paper_accounts balance
q(f"SELECT user_id, display_name, balance, margin_allotted FROM paper_accounts WHERE user_id = '{UID}'",
  "Current paper_accounts")

# 2. Check for triggers on ledger_entries
q("SELECT trigger_name, event_manipulation, action_statement FROM information_schema.triggers WHERE event_object_table = 'ledger_entries'",
  "Triggers on ledger_entries")

# 3. Check for triggers on paper_accounts
q("SELECT trigger_name, event_manipulation, action_statement FROM information_schema.triggers WHERE event_object_table = 'paper_accounts'",
  "Triggers on paper_accounts")

# 4. Sum check: credit - debit from ALL ledger entries
q(f"SELECT COALESCE(SUM(credit),0) - COALESCE(SUM(debit),0) AS computed_balance FROM ledger_entries WHERE user_id = '{UID}'",
  "Computed balance from ledger_entries (credit - debit)")

# 5. All ledger entries with current values
q(f"SELECT entry_id, created_at::date, description, debit, credit, balance_after, ref_type FROM ledger_entries WHERE user_id = '{UID}' ORDER BY created_at",
  "All ledger entries")
