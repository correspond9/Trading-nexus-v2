import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"


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
    names = run_cmd(ssh, "docker ps --format '{{.Names}}'").splitlines()
    backend = ""
    for n in names:
        if n.startswith("backend-") and APP_PREFIX in n:
            backend = n.strip()
            break
    if not backend:
        raise RuntimeError("Backend container not found")

    print(f"Backend: {backend}\n")
    print(run_cmd(ssh, f"docker exec {backend} sh -lc \"grep -n 'EXIT' /app/app/routers/orders.py\""))
    print(run_cmd(ssh, f"docker exec {backend} sh -lc \"grep -n 'No open position found to EXIT' /app/app/routers/orders.py\""))
    print(run_cmd(ssh, f"docker exec {backend} sh -lc \"grep -n 'should_queue = ord_type in' /app/app/routers/orders.py\""))

finally:
    ssh.close()
