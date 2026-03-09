#!/usr/bin/env python3
"""Inspect live paper_trades schema on VPS."""

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
    if err.strip():
        return f"ERR:\n{err}\nOUT:\n{out}"
    return out


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.Ed25519Key.from_private_key(StringIO(KEY))
ssh.connect("72.62.228.112", username="root", pkey=key, timeout=15)

container = run(
    ssh,
    "docker ps --format \"{{.Names}}\" | grep '^db-' | head -1"
).strip()

if not container:
    print("Could not find db container")
    ssh.close()
    raise SystemExit(1)

print(f"DB container: {container}")
print("--- paper_trades schema ---")
print(run(ssh, f"docker exec {container} psql -U postgres -d trading_terminal -c '\\d paper_trades'"))

ssh.close()
