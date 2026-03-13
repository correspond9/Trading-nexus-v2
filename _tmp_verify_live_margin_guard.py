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


def first_matching_container(ssh, token: str, prefer_prefix: str = "") -> str:
    names = run_cmd(ssh, "docker ps --format '{{.Names}}'").splitlines()
    if prefer_prefix:
        for name in names:
            if token in name and name.startswith(prefer_prefix):
                return name.strip()
    for name in names:
        if token in name:
            return name.strip()
    return ""


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=20)

try:
    app_container = first_matching_container(ssh, f"{APP_PREFIX}", prefer_prefix="backend-")
    if not app_container:
        app_container = first_matching_container(ssh, APP_PREFIX)
    if not app_container:
        raise RuntimeError("No application container found for target prefix")

    print(f"APP container: {app_container}\n")

    print("=== Live orders.py checks ===")
    print(run_cmd(ssh, f"docker exec {app_container} sh -lc \"grep -n 'calculate_pending_orders_margin' /app/app/routers/orders.py\""))
    print(run_cmd(ssh, f"docker exec {app_container} sh -lc \"grep -n 'Insufficient margin\\.' /app/app/routers/orders.py\""))

finally:
    ssh.close()
