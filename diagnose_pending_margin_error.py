import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
BACKEND = "backend-x8gg0og8440wkgc8ow0ococs-072411615629"
DB = "db-x8gg0og8440wkgc8ow0ococs-072411628978"
DB_NAME = "trading_terminal"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=15)

cmds = [
    ("backend logs", f"docker logs --tail 200 {BACKEND} 2>&1"),
    ("function def", f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"SELECT pg_get_functiondef('calculate_pending_orders_margin(uuid)'::regprocedure);\""),
    ("order status distribution", f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"SELECT status, COUNT(*) FROM paper_orders GROUP BY status ORDER BY 1;\""),
    ("sample pending orders", f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"SELECT id, user_id, symbol, side, quantity, filled_quantity, price, limit_price, instrument_token, exchange_segment, product_type, status FROM paper_orders WHERE status IN ('PENDING','OPEN','PARTIALLY_FILLED') LIMIT 20;\""),
]

try:
    for title, c in cmds:
        print("\n" + "=" * 30 + f" {title} " + "=" * 30)
        stdin, stdout, stderr = ssh.exec_command(c)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        print(out)
        if err.strip():
            print("ERR:")
            print(err)
finally:
    ssh.close()
