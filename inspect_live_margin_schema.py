import paramiko
from io import StringIO

KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""


def run(ssh, cmd: str) -> str:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors="ignore")
    err = stderr.read().decode(errors="ignore")
    return out + ("\nSTDERR:\n" + err if err else "")


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.Ed25519Key.from_private_key(StringIO(KEY))
ssh.connect("72.62.228.112", username="root", pkey=key, timeout=20)

container = run(ssh, "docker ps --format '{{.Names}}' | grep '^db-' | head -1").strip().splitlines()[0]
print(f"DB container: {container}\n")

cmds = [
    "docker exec {} psql -U postgres -d trading_terminal -c '\\d paper_accounts'".format(container),
    "docker exec {} psql -U postgres -d trading_terminal -c '\\d paper_orders'".format(container),
    "docker exec {} psql -U postgres -d trading_terminal -c '\\d paper_positions'".format(container),
    "docker exec {} psql -U postgres -d trading_terminal -c '\\d users'".format(container),
    "docker exec {} psql -U postgres -d trading_terminal -c \"SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;\"".format(container),
]

for c in cmds:
    print('='*100)
    print(c)
    print('='*100)
    print(run(ssh, c))

ssh.close()
