#!/usr/bin/env python3
"""
Diagnose INDEX instruments in production database
"""
import paramiko
from io import StringIO

VPS_IP = "72.62.228.112"
SSH_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

DIAG_CODE = '''
import asyncio
from app.database import get_pool, init_db, close_db

async def diagnose():
    await init_db()
    pool = get_pool()
    
    print("\\n=== SEARCHING FOR INDEX/NIFTY INSTRUMENTS ===\\n")
    
    # Check all instrument types
    print("1. All instrument types in database:")
    types = await pool.fetch("SELECT DISTINCT instrument_type, COUNT(*) as cnt FROM instrument_master GROUP BY instrument_type ORDER BY cnt DESC LIMIT 20")
    for t in types:
        print(f"   {t['instrument_type']:15s}: {t['cnt']:>6,} instruments")
    
    # Search for NIFTY by symbol
    print("\\n2. Searching for NIFTY in symbol field:")
    nifty_symbol = await pool.fetch("SELECT instrument_token, symbol, underlying, instrument_type, tier, ws_slot FROM instrument_master WHERE symbol ILIKE '%NIFTY%' AND instrument_type NOT IN ('OPTIDX', 'FUTIDX') LIMIT 10")
    if nifty_symbol:
        for r in nifty_symbol:
            print(f"   Token: {r['instrument_token']:10} | Symbol: {r['symbol']:30s} | Type: {r['instrument_type']:10s} | Tier: {r['tier'] or ' '}")
    else:
        print("   No matches")
    
    # Search for NIFTY by underlying
    print("\\n3. Searching for NIFTY in underlying field:")
    nifty_underlying = await pool.fetch("SELECT DISTINCT underlying, instrument_type, COUNT(*) as cnt FROM instrument_master WHERE underlying ILIKE '%NIFTY%' GROUP BY underlying, instrument_type LIMIT 15")
    for r in nifty_underlying:
        print(f"   {r['underlying']:20s} | Type: {r['instrument_type']:10s} | Count: {r['cnt']:>5,}")
    
    # Check market_data table for index prices
    print("\\n4. Checking market_data for index prices:")
    md = await pool.fetch("""
        SELECT md.instrument_token, im.symbol, im.instrument_type, md.ltp, md.close, md.updated_at
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE im.symbol IN ('NIFTY', 'BANKNIFTY', 'SENSEX', 'NIFTY 50', 'NIFTY BANK', 'FINNIFTY', 'MIDCPNIFTY')
        OR im.underlying IN ('NIFTY', 'BANKNIFTY', 'SENSEX')
        LIMIT 10
    """)
    if md:
        for r in md:
            print(f"   {r['symbol']:30s} | Type: {r['instrument_type']:10s} | LTP: {r['ltp']} | Updated: {r['updated_at']}")
    else:
        print("   No market data found for indices")
    
    # Check for FUTIDX
    print("\\n5. Checking NIFTY FUTIDX (to see if they exist):")
    futidx = await pool.fetch("SELECT instrument_token, symbol, underlying, tier, ws_slot FROM instrument_master WHERE underlying = 'NIFTY' AND instrument_type = 'FUTIDX' LIMIT 5")
    for r in futidx:
        print(f"   Token: {r['instrument_token']:10} | Symbol: {r['symbol']:30s} | Tier: {r['tier'] or ' '} | WS: {r['ws_slot']}")
    
    await close_db()

asyncio.run(diagnose())
'''

print("=" * 70)
print("DIAGNOSING INDEX INSTRUMENTS")
print("=" * 70)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("\nConnecting to VPS...")
    key_file = StringIO(SSH_KEY)
    private_key = paramiko.Ed25519Key.from_private_key(key_file)
    ssh.connect(VPS_IP, username='root', pkey=private_key, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command('docker ps --filter name=backend --format "{{.Names}}"')
    container_name = stdout.read().decode().strip()
    
    if not container_name:
        stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}}" | grep -i trading')
        containers = stdout.read().decode().strip().split('\n')
        for c in containers:
            if 'backend' in c.lower():
                container_name = c
                break
    
    print(f"Container: {container_name}\n")
    
    escaped_code = DIAG_CODE.replace('"', '\\"').replace('$', '\\$')
    command = f'docker exec {container_name} python -c "{escaped_code}"'
    
    stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
    
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    print(output)
    if errors and 'Runtime' not in errors:
        print("\nStderr:", errors[:500])
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()

print("\n" + "=" * 70)
