import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB = "db-x8gg0og8440wkgc8ow0ococs-072411628978"
DB_NAME = "trading_terminal"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=15)

q = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='paper_orders' ORDER BY ordinal_position;"
cmd = f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"{q}\""

try:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err.strip():
        print(err)
finally:
    ssh.close()
