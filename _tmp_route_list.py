import re
from io import StringIO
import paramiko
from pathlib import Path

src=Path('d:/4.PROJECTS/FRESH/trading-nexus/check_coolify.py').read_text(encoding='utf-8')
m=re.search(r'key_content = """(.*?)"""',src,re.S)
if not m:
    raise SystemExit('key not found')
key_content=m.group(1)
ssh=paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key=paramiko.Ed25519Key.from_private_key(StringIO(key_content))
ssh.connect('72.62.228.112',username='root',pkey=key,timeout=20)
for cmd in [
    "docker ps --format '{{.Names}} {{.Image}}' | grep -i coolify",
    "docker exec coolify php artisan route:list --path=api/v1 | sed -n '1,220p'"
]:
    print('\nCMD:',cmd)
    i,o,e=ssh.exec_command(cmd)
    print(o.read().decode('utf-8','ignore'))
    err=e.read().decode('utf-8','ignore').strip()
    if err: print('ERR:',err)
ssh.close()
