import re
from io import StringIO
import paramiko
from pathlib import Path
src=Path('d:/4.PROJECTS/FRESH/trading-nexus/check_coolify.py').read_text(encoding='utf-8')
key=re.search(r'key_content = """(.*?)"""',src,re.S).group(1)
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('72.62.228.112',username='root',pkey=paramiko.Ed25519Key.from_private_key(StringIO(key)),timeout=20)
cmds=[
"docker exec coolify sh -lc \"grep -n 'applications/dockercompose' /var/www/html/app/Http/Controllers/Api/ApplicationsController.php\"",
"docker exec coolify sh -lc \"grep -n 'Create (Docker Compose)' /var/www/html/app/Http/Controllers/Api/ApplicationsController.php\"",
"docker exec coolify sh -lc \"grep -n 'public function .*docker' /var/www/html/app/Http/Controllers/Api/ApplicationsController.php\"",
"docker exec coolify sh -lc \"grep -n 'function create_' /var/www/html/app/Http/Controllers/Api/ApplicationsController.php\"",
"docker exec coolify sh -lc \"grep -n 'dockercompose' /var/www/html/app/Http/Controllers/Api/ApplicationsController.php | sed -n '1,40p'\"",
"docker exec coolify sh -lc \"nl -ba /var/www/html/app/Http/Controllers/Api/ApplicationsController.php | sed -n '300,520p'\"",
"docker exec coolify sh -lc \"nl -ba /var/www/html/app/Http/Controllers/Api/ApplicationsController.php | sed -n '520,760p'\""
]
for c in cmds:
 print('\nCMD',c)
 i,o,e=ssh.exec_command(c)
 print(o.read().decode('utf-8','ignore')[:12000])
 err=e.read().decode('utf-8','ignore').strip()
 if err: print('ERR',err[:1200])
ssh.close()
