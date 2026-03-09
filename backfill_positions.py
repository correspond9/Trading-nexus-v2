#!/usr/bin/env python3
"""
Backfill paper_positions from paper_trades.
This resolves the issue where old trades don't have corresponding positions.
"""

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

print(f"Using DB container: {container}\n")

# SQL to backfill positions from trades
sql = """
-- Backfill paper_positions from paper_trades
-- This creates OPEN positions for users based on their net trades

INSERT INTO paper_positions (
    user_id,
    instrument_token,
    exchange_segment,
    symbol,
    quantity,
    avg_price,
    status,
    opened_at
)
SELECT
    user_id,
    instrument_token,
    exchange_segment,
    symbol,
    -- Net quantity (BUY is positive, SELL is negative)
    SUM(CASE WHEN side = 'BUY' THEN COALESCE(fill_qty, quantity) ELSE -COALESCE(fill_qty, quantity) END) as net_qty,
    -- Weighted average price (approximation, ignoring FIFO for simplicity)
    AVG(fill_price) as avg_price,
    'OPEN' as status,
    MIN(traded_at) as opened_at
FROM paper_trades
GROUP BY user_id, instrument_token, exchange_segment, symbol
HAVING SUM(CASE WHEN side = 'BUY' THEN COALESCE(fill_qty, quantity) ELSE -COALESCE(fill_qty, quantity) END) != 0
ON CONFLICT DO NOTHING;

-- Show backfilled positions
SELECT 
    position_id,
    user_id,
    symbol,
    quantity,
    avg_price,
    status,
    opened_at
FROM paper_positions
ORDER BY opened_at DESC;
"""

print("Backfilling paper_positions from paper_trades...")
print("=" * 80)

# Escape for shell
sql_escaped = sql.replace("'", "'\"'\"'")
cmd = f"docker exec {container} psql -U postgres -d trading_terminal -c '{sql_escaped}'"

out, err = run(ssh, cmd)
print(out)
if err:
    print("STDERR:", err)

ssh.close()
print("\n✅ Backfill complete!")
print("\nNote: This uses average price as approximation.")
print("For exact P&L tracking, positions should be maintained in real-time during order execution.")
