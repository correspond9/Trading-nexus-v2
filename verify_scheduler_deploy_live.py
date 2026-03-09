import paramiko
import time

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)

try:
    # wait a bit for restart to rotate containers
    time.sleep(15)

    cmd = f"docker ps --filter name=backend-{APP_PREFIX} --format '{{{{.Names}}}}' | head -n 1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    backend = stdout.read().decode("utf-8", errors="replace").strip()
    print("backend_container", backend)

    check = (
        "grep -n \"cancel all active orders from previous trading days\" /app/app/positions/eod_archiver.py || true; "
        "grep -n \"cancelled_stale_orders\" /app/app/positions/eod_archiver.py || true"
    )
    verify_cmd = f"docker exec {backend} sh -lc '{check}'"
    stdin, stdout, stderr = ssh.exec_command(verify_cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    err = stderr.read().decode("utf-8", errors="replace")
    if err.strip():
        print(err)
finally:
    ssh.close()
