import re
from io import StringIO
import paramiko
from pathlib import Path
src=Path('d:/4.PROJECTS/FRESH/trading-nexus/check_coolify.py').read_text(encoding='utf-8')
key=re.search(r'key_content = """(.*?)"""',src,re.S).group(1)
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('72.62.228.112',username='root',pkey=paramiko.Ed25519Key.from_private_key(StringIO(key)),timeout=20)
for rng in [('1180,1420'),('1420,1700'),('1880,2080')]:
 cmd=f"docker exec coolify sh -lc \"nl -ba /var/www/html/app/Http/Controllers/Api/ApplicationsController.php | sed -n '{rng}p'\""
 print('\n=== RANGE',rng,'===')
 i,o,e=ssh.exec_command(cmd)
 print(o.read().decode('utf-8','ignore'))
 err=e.read().decode('utf-8','ignore').strip()
 if err: print('ERR',err)
ssh.close()
