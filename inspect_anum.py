import subprocess
import json

DB = "db-x8gg0og8440wkgc8ow0ococs-145803824898"

def run_sql(query, description=""):
    cmd = f'docker exec {DB} psql -U postgres -d trading_terminal -c "{query}"'
    result = subprocess.run(
        ["ssh", "root@72.62.228.112", cmd],
        capture_output=True, text=True
    )
    if description:
        print(f"\n=== {description} ===")
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.stdout

# 1. Table structures
run_sql(r"\d paper_positions", "paper_positions TABLE STRUCTURE")

# 2. Check paper_trades
run_sql(r"\dt paper_trades*", "CHECK paper_trades")

# 3. Current positions with all P&L fields
run_sql(
    "SELECT position_id, symbol, quantity, avg_price, status, realized_pnl, trade_expense, platform_cost, opened_at::date, closed_at::date FROM paper_positions WHERE user_id = '6785692d-8f36-4183-addb-16c96ea95a88' ORDER BY opened_at",
    "ALL POSITIONS WITH P&L"
)

# 3b. Paper trades table structure
run_sql(r"\d paper_trades", "paper_trades STRUCTURE")

# 3c. Trades for existing SUNDARAM position
run_sql(
    "SELECT * FROM paper_trades WHERE position_id = '2acd403c-aaee-47dc-9bc2-bc9251bbeee4' LIMIT 5",
    "TRADES FOR EXISTING SUNDARAM"
)

# 3d. Trades for PCJEWELLER (to understand expected structure with proper data)
run_sql(
    "SELECT * FROM paper_trades WHERE position_id = 'b9a60484-48af-44a1-a29e-660c0249f62c' LIMIT 5",
    "TRADES FOR PCJEWELLER (reference)"
)

# 4. User creation time
run_sql(
    "SELECT id, name, mobile, created_at FROM users WHERE id = '6785692d-8f36-4183-addb-16c96ea95a88'",
    "USER CREATION"
)

# 5. Ledger entries
run_sql(
    "SELECT entry_id, created_at::date, description, debit, credit, balance_after FROM ledger_entries WHERE user_id = '6785692d-8f36-4183-addb-16c96ea95a88' ORDER BY created_at",
    "CURRENT LEDGER"
)
