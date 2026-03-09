import paramiko
from io import StringIO

KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""


def run(ssh, cmd: str):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode(errors='ignore'), stderr.read().decode(errors='ignore')


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.Ed25519Key.from_private_key(StringIO(KEY))
ssh.connect('72.62.228.112', username='root', pkey=key, timeout=20)

out, _ = run(ssh, "docker ps --format '{{.Names}}' | grep '^db-' | head -1")
container = out.strip()
print('DB:', container)

queries = {
    'USER_MAPPING': """
SELECT id, user_no, first_name, last_name, name, role
FROM users
WHERE user_no = 2544;
""",
    'ACCOUNT_ROW': """
SELECT pa.user_id, pa.display_name, pa.balance, pa.margin_allotted, pa.used_margin
FROM paper_accounts pa
JOIN users u ON u.id = pa.user_id
WHERE u.user_no = 2544;
""",
    'OPEN_POSITIONS': """
SELECT pp.position_id, pp.instrument_token, pp.symbol, pp.exchange_segment, pp.product_type,
       pp.quantity, pp.avg_price, md.ltp,
       calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type) AS required_margin
FROM paper_positions pp
JOIN users u ON u.id = pp.user_id
LEFT JOIN market_data md ON md.instrument_token = pp.instrument_token
WHERE u.user_no = 2544 AND pp.status='OPEN' AND pp.quantity != 0
ORDER BY pp.symbol;
""",
    'MARGIN_SUMMARY': """
SELECT u.user_no, pa.display_name, pa.margin_allotted,
       COALESCE(SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
         FILTER (WHERE pp.status='OPEN' AND pp.quantity != 0),0) AS used_calc,
       pa.margin_allotted - COALESCE(SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
         FILTER (WHERE pp.status='OPEN' AND pp.quantity != 0),0) AS available_calc
FROM paper_accounts pa
JOIN users u ON u.id = pa.user_id
LEFT JOIN paper_positions pp ON pp.user_id = pa.user_id
WHERE u.user_no = 2544
GROUP BY u.user_no, pa.display_name, pa.margin_allotted;
""",
    'RECENT_ORDERS': """
SELECT po.order_id, po.symbol, po.side, po.order_type, po.product_type,
       po.quantity, po.filled_qty, po.remaining_qty, po.limit_price, po.fill_price,
       po.status, po.placed_at
FROM paper_orders po
JOIN users u ON u.id = po.user_id
WHERE u.user_no = 2544
ORDER BY po.placed_at DESC
LIMIT 20;
"""
}

for title, sql in queries.items():
    print('\n' + '='*100)
    print(title)
    print('='*100)
    esc = sql.replace("'", "'\"'\"'")
    out, err = run(ssh, f"docker exec {container} psql -U postgres -d trading_terminal -c '{esc}'")
    print(out)
    if err:
        print('STDERR:', err)

ssh.close()
