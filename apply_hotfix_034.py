import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB = "db-x8gg0og8440wkgc8ow0ococs-072411628978"
DB_NAME = "trading_terminal"

LOCAL_SQL = r"d:\4.PROJECTS\FRESH\trading-nexus\migrations\034_fix_pending_margin_status_compatibility.sql"
REMOTE_SQL = "/tmp/034_fix_pending_margin_status_compatibility.sql"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=15)

try:
    sftp = ssh.open_sftp()
    sftp.put(LOCAL_SQL, REMOTE_SQL)
    sftp.close()

    apply_cmd = f"cat {REMOTE_SQL} | docker exec -i {DB} psql -U postgres -d {DB_NAME}"
    stdin, stdout, stderr = ssh.exec_command(apply_cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    err = stderr.read().decode("utf-8", errors="replace")
    if err.strip():
        print(err)

    verify_cmd = (
        f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \""
        "SELECT pg_get_functiondef('calculate_pending_orders_margin(uuid)'::regprocedure);"
        "\""
    )
    stdin, stdout, stderr = ssh.exec_command(verify_cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    verr = stderr.read().decode("utf-8", errors="replace")
    if verr.strip():
        print(verr)

    ssh.exec_command(f"rm -f {REMOTE_SQL}")
finally:
    ssh.close()
