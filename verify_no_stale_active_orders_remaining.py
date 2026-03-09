import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB = "db-x8gg0og8440wkgc8ow0ococs-081958030996"
DB_NAME = "trading_terminal"

sql = """
SELECT COUNT(*) AS stale_active_orders
FROM paper_orders
WHERE archived_at IS NULL
  AND DATE(placed_at AT TIME ZONE 'Asia/Kolkata') < CURRENT_DATE
  AND status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED');
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)
try:
    print(f"Using DB container: {DB}")
    cmd = f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"{sql}\""
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print("STDOUT:")
    print(out if out.strip() else "(empty)")
    print("STDERR:")
    print(err if err.strip() else "(empty)")
finally:
    ssh.close()
