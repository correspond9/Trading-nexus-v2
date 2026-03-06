import subprocess

DB = "db-x8gg0og8440wkgc8ow0ococs-145803824898"
UID = "6785692d-8f36-4183-addb-16c96ea95a88"

def q(sql, desc=""):
    # Use single quotes inside for SQL, wrap with double for shell
    cmd = ["ssh", "root@72.62.228.112",
           f'docker exec {DB} psql -U postgres -d trading_terminal -c "{sql}"']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if desc:
        print(f"\n{'='*60}")
        print(f"  {desc}")
        print('='*60)
    print(result.stdout.strip())

q(f"SELECT symbol, quantity, avg_price, status, realized_pnl, trade_expense, (realized_pnl - trade_expense) AS net_pnl, opened_at::date, closed_at::date FROM paper_positions WHERE user_id = '{UID}' AND status = 'CLOSED' ORDER BY closed_at",
  "CLOSED POSITIONS (P&L Report should match)")

q(f"SELECT symbol, quantity, avg_price, status FROM paper_positions WHERE user_id = '{UID}' AND status = 'OPEN'",
  "OPEN POSITIONS (Portfolio)")

q(f"SELECT entry_id, created_at::date, description, debit, credit, balance_after FROM ledger_entries WHERE user_id = '{UID}' ORDER BY created_at",
  "LEDGER ENTRIES (8 entries total)")

q(f"SELECT display_name, balance FROM paper_accounts WHERE user_id = '{UID}'",
  "WALLET BALANCE")
