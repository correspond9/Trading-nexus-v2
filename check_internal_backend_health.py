import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
PREFIX = "x8gg0og8440wkgc8ow0ococs"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)

try:
    find_cmd = f"docker ps --filter name=backend-{PREFIX} --format '{{{{.Names}}}}' | head -n 1"
    stdin, stdout, stderr = ssh.exec_command(find_cmd)
    backend = stdout.read().decode("utf-8", errors="replace").strip()
    print("backend", backend)

    for cmd in [
        f"docker exec {backend} sh -lc 'python -c \"import urllib.request;print(urllib.request.urlopen(\\\"http://127.0.0.1:8000/health\\\", timeout=5).read().decode())\"'",
        f"docker exec {backend} sh -lc 'python -c \"import urllib.request;print(urllib.request.urlopen(\\\"http://127.0.0.1:8000/api/v2/health\\\", timeout=5).read().decode())\"'",
    ]:
        print("CMD:", cmd)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode("utf-8", errors="replace"))
        err = stderr.read().decode("utf-8", errors="replace")
        if err.strip():
            print("ERR:", err)
finally:
    ssh.close()
