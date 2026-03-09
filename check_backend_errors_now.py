import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
PREFIX = "x8gg0og8440wkgc8ow0ococs"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)

try:
    find_cmd = f"docker ps -a --filter name=backend-{PREFIX} --format '{{{{.Names}}}}|{{{{.Status}}}}' | head -n 5"
    stdin, stdout, stderr = ssh.exec_command(find_cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    print("BACKEND CONTAINERS:")
    print(out)

    running = None
    for line in out.splitlines():
        if "|Up" in line:
            running = line.split("|", 1)[0].strip()
            break

    if not running:
        print("No running backend container found")
        raise SystemExit(1)

    print("Using:", running)
    log_cmd = f"docker logs --tail 300 {running} 2>&1"
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    logs = stdout.read().decode("utf-8", errors="replace")
    print("\nLAST LOGS:\n")
    print(logs)
finally:
    ssh.close()
