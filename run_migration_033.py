#!/usr/bin/env python3
"""Run migration 033 directly on live VPS DB."""

import paramiko
from io import StringIO

KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""


def run(ssh, cmd: str) -> tuple[str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors="ignore"), stderr.read().decode(errors="ignore")


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.Ed25519Key.from_private_key(StringIO(KEY))
ssh.connect("72.62.228.112", username="root", pkey=key, timeout=20)

out, err = run(ssh, "docker ps --format \"{{.Names}}\" | grep '^db-' | head -1")
container = out.strip()
if not container:
    print("ERROR: Could not find db container")
    print(err)
    ssh.close()
    raise SystemExit(1)

print(f"Using DB container: {container}")

with open("migrations/033_paper_trades_compat_columns.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# Escape single quotes for shell-safe psql -c execution
sql_escaped = sql.replace("'", "'\"'\"'")

cmd = (
    f"docker exec {container} psql -U postgres -d trading_terminal -v ON_ERROR_STOP=1 "
    f"-c '{sql_escaped}'"
)
out, err = run(ssh, cmd)
print("--- Migration output ---")
print(out.strip())
if err.strip():
    print("--- Migration stderr ---")
    print(err.strip())

verify_cmd = (
    f"docker exec {container} psql -U postgres -d trading_terminal "
    f"-c '\\d paper_trades'"
)
out, err = run(ssh, verify_cmd)
print("--- paper_trades schema after migration ---")
print(out.strip())
if err.strip():
    print(err.strip())

ssh.close()
print("Migration 033 completed")
