import re
from io import StringIO
import paramiko
from pathlib import Path
src=Path('d:/4.PROJECTS/FRESH/trading-nexus/check_coolify.py').read_text(encoding='utf-8')
key=re.search(r'key_content = """(.*?)"""',src,re.S).group(1)
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('72.62.228.112',username='root',pkey=paramiko.Ed25519Key.from_private_key(StringIO(key)),timeout=20)
cmds=[
"docker exec coolify sh -lc \"grep -R --line-number 'function dockerCompose' /var/www/html/app/Http/Controllers/Api 2>/dev/null\"",
"docker exec coolify sh -lc \"grep -R --line-number 'applications/dockercompose' /var/www/html/routes /var/www/html/app 2>/dev/null\"",
"docker exec coolify sh -lc \"sed -n '1,260p' /var/www/html/app/Http/Controllers/Api/ApplicationController.php\"",
"docker exec coolify sh -lc \"sed -n '1,340p' /var/www/html/app/Http/Controllers/Api/ApplicationsController.php\""
]
for c in cmds:
 print('\nCMD',c)
 i,o,e=ssh.exec_command(c)
 out=o.read().decode('utf-8','ignore')
 err=e.read().decode('utf-8','ignore')
 print(out[:12000])
 if err.strip(): print('ERR',err[:1000])
ssh.close()
