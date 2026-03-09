import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
BACKEND = "backend-x8gg0og8440wkgc8ow0ococs-072411615629"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=15)

cmd = f"docker logs --tail 2000 {BACKEND} 2>&1 | grep -n -E 'CRITICAL ORDER PLACEMENT ERROR|Exception type:|InFailedSQLTransaction|invalid input value for enum|calculate_pending_orders_margin'"

try:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    print(out)
    if err.strip():
        print("ERR:")
        print(err)
finally:
    ssh.close()
