import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB = "db-x8gg0og8440wkgc8ow0ococs-072411628978"
DB_NAME = "trading_terminal"
USER_ID = "098c818d-39e1-40a6-97f0-66472a011442"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=15)

queries = [
    f"SELECT calculate_pending_orders_margin('{USER_ID}'::uuid);",
    f"SELECT id, status, side, quantity, filled_quantity, symbol, exchange_segment, product_type, price, limit_price, instrument_token FROM paper_orders WHERE user_id='{USER_ID}'::uuid AND status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED') ORDER BY created_at DESC LIMIT 20;",
]

try:
    for q in queries:
        cmd = f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"{q}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        print('\n--- QUERY ---')
        print(q)
        print(out)
        if err.strip():
            print('ERR:')
            print(err)
finally:
    ssh.close()
