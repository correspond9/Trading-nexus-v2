import subprocess
import json

DB = "db-x8gg0og8440wkgc8ow0ococs-145803824898"

def run_ssh_query(query, desc=""):
    cmd = ["ssh", "root@72.62.228.112", 
           f"docker exec {DB} psql -U postgres -d trading_terminal -c \"{query}\""]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if desc:
        print(f"\n=== {desc} ===")
    print(result.stdout)
    if "ERROR" in result.stderr:
        print("ERROR:", result.stderr)
    return result.stdout

# Find KRITIKA instrument token
run_ssh_query(
    "SELECT instrument_token, tradingsymbol, name, exchange, instrument_type FROM instrument_master WHERE tradingsymbol ILIKE '%KRITIKA%' OR name ILIKE '%KRITIKA%' LIMIT 10",
    "KRITIKA in instrument_master"
)

# Find SUNDARAM instrument token  
run_ssh_query(
    "SELECT instrument_token, tradingsymbol, name, exchange, instrument_type FROM instrument_master WHERE tradingsymbol ILIKE '%SUNDARAM%' LIMIT 10",
    "SUNDARAM in instrument_master"
)

# Also check what token the existing SUNDARAM position uses
run_ssh_query(
    "SELECT position_id, symbol, instrument_token, quantity, avg_price, realized_pnl, trade_expense, opened_at, closed_at FROM paper_positions WHERE user_id = '6785692d-8f36-4183-addb-16c96ea95a88' AND symbol ILIKE '%SUNDARAM%'",
    "Existing SUNDARAM position tokens"
)

# Check paper_accounts for this user
run_ssh_query(
    "SELECT * FROM paper_accounts WHERE user_id = '6785692d-8f36-4183-addb-16c96ea95a88'",
    "paper_accounts for user"
)
