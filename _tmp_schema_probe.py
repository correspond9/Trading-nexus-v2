import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"
DB_NAME = "trading_terminal"


def run_cmd(ssh, cmd: str) -> str:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if err.strip():
        out += "\n[stderr]\n" + err
    return out


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=20)

try:
    all_containers = run_cmd(
        ssh,
        f"docker ps --filter name={APP_PREFIX} --format '{{{{.Names}}}}'",
    ).strip()
    print("=== containers ===")
    print(all_containers)

    db_container = [c for c in all_containers.splitlines() if c.startswith("db-")][0]
    print(f"\nDB container: {db_container}\n")

    sql_fn = r'''
SELECT proname, pg_get_function_identity_arguments(p.oid) args
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace=n.oid
WHERE n.nspname='public'
  AND proname IN ('calculate_position_margin','calculate_pending_orders_margin')
ORDER BY proname;
'''
    print("=== function signatures ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{sql_fn}\""))

    sql_cols = r'''
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name='paper_positions'
ORDER BY ordinal_position;
'''
    print("=== paper_positions columns ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{sql_cols}\""))

finally:
    ssh.close()
