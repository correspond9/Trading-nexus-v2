import time
import requests
import paramiko

API = "http://72.62.228.112:8000/api/v1"
TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
APP_UUID = "x8gg0og8440wkgc8ow0ococs"
EXPECTED_COMMIT = "78cb69d"
HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
PREFIX = "backend-x8gg0og8440wkgc8ow0ococs-"

headers = {"Authorization": f"Bearer {TOKEN}"}

def desired_backend_container_name():
    r = requests.get(f"{API}/applications/{APP_UUID}", headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    compose = data.get("docker_compose", "")
    desired = None
    image = None
    for line in compose.splitlines():
        s = line.strip()
        if s.startswith("container_name:") and PREFIX in s:
            desired = s.split("container_name:", 1)[1].strip()
        if s.startswith("image:") and "_backend:" in s:
            image = s
    return desired, image

def running_backend_container_name(ssh):
    cmd = "docker ps --filter name=backend-x8gg0og8440wkgc8ow0ococs- --format '{{.Names}}' | head -n 1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode("utf-8", errors="replace").strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)

try:
    for i in range(30):
        desired, image = desired_backend_container_name()
        running = running_backend_container_name(ssh)
        print(f"[{i+1}/30] desired={desired} running={running} image={image}")

        # Success if running container matches desired and image tag contains current commit
        if desired and running and desired == running and image and EXPECTED_COMMIT in image:
            print("DEPLOYMENT_ACTIVE=YES")
            break

        time.sleep(10)
    else:
        print("DEPLOYMENT_ACTIVE=NO")
finally:
    ssh.close()
