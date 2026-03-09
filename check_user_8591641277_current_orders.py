import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"
DB_NAME = "trading_terminal"
MOBILE = "8591641277"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)

try:
    find_cmd = f"docker ps --filter name=db-{APP_PREFIX} --format '{{{{.Names}}}}' | head -n 1"
    stdin, stdout, stderr = ssh.exec_command(find_cmd)
    db = stdout.read().decode("utf-8", errors="replace").strip()
    print(f"DB container: {db}")

    q = f"""
    WITH usr AS (
        SELECT id FROM users WHERE mobile = '{MOBILE}'
    )
    SELECT
      po.order_id,
      po.symbol,
      po.side,
      po.status,
      po.quantity,
      COALESCE(po.filled_qty,0) AS filled_qty,
      (po.quantity - COALESCE(po.filled_qty,0)) AS unfilled_qty,
      COALESCE(po.limit_price, po.fill_price) AS price,
      po.placed_at
    FROM paper_orders po
    WHERE po.user_id = (SELECT id FROM usr)
      AND po.archived_at IS NULL
      AND po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
    ORDER BY po.placed_at DESC;
    """
    cmd = f"docker exec {db} psql -U postgres -d {DB_NAME} -c \"{q}\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    err = stderr.read().decode("utf-8", errors="replace")
    if err.strip():
        print(err)
finally:
    ssh.close()
