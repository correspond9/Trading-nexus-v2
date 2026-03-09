import paramiko
from io import StringIO

KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.Ed25519Key.from_private_key(StringIO(KEY))
ssh.connect("72.62.228.112", username="root", pkey=key, timeout=20)

stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}' | grep '^backend-'")
backend = stdout.read().decode().strip()
print(f"Backend container: {backend}")

ssh.close()
