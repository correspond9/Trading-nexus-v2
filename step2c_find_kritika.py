import subprocess

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

# Find KRITIKA
run_ssh_query(
    "SELECT instrument_token, symbol, exchange_segment, display_name FROM instrument_master WHERE symbol ILIKE '%KRITIKA%' LIMIT 10",
    "KRITIKA token"
)

# Find SUNDARAM (verify it's 18931)
run_ssh_query(
    "SELECT instrument_token, symbol, exchange_segment, display_name FROM instrument_master WHERE instrument_token = 18931",
    "SUNDARAM token=18931"
)
