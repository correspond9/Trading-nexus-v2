import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
CONTAINER = "backend-x8gg0og8440wkgc8ow0ococs-072411615629"

checks = [
    "grep -n \"calculate_pending_orders_margin\" /app/app/routers/margin.py || true",
    "grep -n \"pending_orders_margin\" /app/app/routers/orders.py || true",
    "grep -n \"Available Margin = Allotted Margin - Used Margin (positions + pending orders)\" /app/app/routers/margin.py || true",
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=10)

try:
    for cmd in checks:
        remote = f"docker exec {CONTAINER} sh -lc '{cmd}'"
        stdin, stdout, stderr = ssh.exec_command(remote)
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        print("---")
        print(cmd)
        print(out if out else "(no output)")
        if err:
            print("ERR:", err)
finally:
    ssh.close()
