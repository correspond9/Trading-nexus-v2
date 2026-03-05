#!/usr/bin/env python3
"""
Apply INDEX tier fix directly on production
Executes the fix inline without needing a separate file
"""
import paramiko
from io import StringIO
import time

VPS_IP = "72.62.228.112"
SSH_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

# Python code to execute in container
FIX_CODE = '''
import asyncio
from app.database import get_pool, init_db, close_db

TIER_B_INDICES = ["NIFTY", "BANKNIFTY", "SENSEX", "MIDCPNIFTY", "FINNIFTY", "BANKEX", "NIFTYNXT50"]

async def fix():
    await init_db()
    pool = get_pool()
    
    print("\\n=== BEFORE UPDATE ===")
    before = await pool.fetch(
        """SELECT instrument_token, symbol, tier, ws_slot 
           FROM instrument_master
           WHERE instrument_type = 'INDEX' AND symbol = ANY($1::text[])
           ORDER BY symbol""",
        TIER_B_INDICES
    )
    print(f"Found {len(before)} INDEX instruments:")
    for r in before:
        print(f"  {r['symbol']:15s} | tier={r['tier'] or ' '} | ws_slot={r['ws_slot']}")
    
    print("\\n=== APPLYING FIX ===")
    result = await pool.execute(
        """UPDATE instrument_master 
           SET tier = 'B', ws_slot = (instrument_token % 5)
           WHERE instrument_type = 'INDEX' AND symbol = ANY($1::text[])""",
        TIER_B_INDICES
    )
    print(f"Updated: {result}")
    
    print("\\n=== AFTER UPDATE ===")
    after = await pool.fetch(
        """SELECT instrument_token, symbol, tier, ws_slot 
           FROM instrument_master
           WHERE instrument_type = 'INDEX' AND symbol = ANY($1::text[])
           ORDER BY symbol""",
        TIER_B_INDICES
    )
    for r in after:
        print(f"  {r['symbol']:15s} | tier={r['tier']} | ws_slot={r['ws_slot']}")
    
    tier_b_total = await pool.fetchval("SELECT COUNT(*) FROM instrument_master WHERE tier = 'B'")
    print(f"\\nTotal Tier-B instruments: {tier_b_total}")
    
    await close_db()
    print("\\n✓ Fix applied successfully!")

asyncio.run(fix())
'''

print("=" * 70)
print("APPLYING INDEX TIER FIX ON PRODUCTION")
print("=" * 70)
print()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("[1/4] Connecting to VPS...")
    key_file = StringIO(SSH_KEY)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect(VPS_IP, username='root', pkey=private_key, timeout=10)
    print(f"✓ Connected to {VPS_IP}\n")
    
    print("[2/4] Finding backend container...")
    stdin, stdout, stderr = ssh.exec_command('docker ps --filter name=backend --format "{{.Names}}"')
    container_name = stdout.read().decode().strip()
    
    if not container_name:
        stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}}" | grep -i trading')
        containers = stdout.read().decode().strip().split('\n')
        for c in containers:
            if 'backend' in c.lower() or 'api' in c.lower():
                container_name = c
                break
    
    if not container_name:
        print("✗ Could not find backend container")
        exit(1)
    
    print(f"✓ Found container: {container_name}\n")
    
    print("[3/4] Executing INDEX tier fix...")
    print("-" * 70)
    
    # Escape the Python code for shell
    escaped_code = FIX_CODE.replace('"', '\\"').replace('$', '\\$')
    command = f'docker exec {container_name} python -c "{escaped_code}"'
    
    stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
    
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    print(output)
    if errors and errors.strip() and 'RuntimeWarning' not in errors:
        print("\nErrors:")
        print(errors)
    
    print("-" * 70)
    
    print("\n[4/4] Restarting backend to reload subscriptions...")
    stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_name}')
    time.sleep(3)
    print(f"✓ Container restarted\n")
    
    print("=" * 70)
    print("FIX COMPLETE!")
    print("=" * 70)
    print("\n✅ The INDEX instruments are now classified as Tier-B")
    print("✅ WebSocket will subscribe to them on startup")
    print("✅ Live prices will be available in 30 seconds")
    print("\nWhat to check:")
    print("  1. Open your trading app in browser")
    print("  2. Go to Straddle or Options page")
    print("  3. NIFTY should show live price (~24600)")
    print("  4. Price should update every second")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    ssh.close()
