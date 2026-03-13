import paramiko
from pathlib import Path

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"

LOCAL_ORDERS = Path(r"d:\4.PROJECTS\FRESH\trading-nexus\app\routers\orders.py")
LOCAL_MONITOR = Path(r"d:\4.PROJECTS\FRESH\trading-nexus\app\execution_simulator\partial_fill_monitor.py")


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

    print(f"Backend container: {backend}")

    sftp = ssh.open_sftp()
    sftp.put(str(LOCAL_ORDERS), "/tmp/orders.py")
    sftp.put(str(LOCAL_MONITOR), "/tmp/partial_fill_monitor.py")
    sftp.close()

    print(run_cmd(ssh, f"docker cp /tmp/orders.py {backend}:/app/app/routers/orders.py"))
    print(run_cmd(ssh, f"docker cp /tmp/partial_fill_monitor.py {backend}:/app/app/execution_simulator/partial_fill_monitor.py"))

    print(run_cmd(ssh, f"docker exec {backend} python -m py_compile /app/app/routers/orders.py /app/app/execution_simulator/partial_fill_monitor.py"))

    print(run_cmd(ssh, f"docker restart {backend}"))

    print(run_cmd(ssh, "rm -f /tmp/orders.py /tmp/partial_fill_monitor.py"))

finally:
    ssh.close()
