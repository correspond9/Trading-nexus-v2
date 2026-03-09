import paramiko
from io import StringIO

KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""


def run(ssh, cmd: str) -> str:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode(errors="ignore")
    err = stderr.read().decode(errors="ignore")
    return out + ("\nSTDERR:\n" + err if err else "")


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key = paramiko.Ed25519Key.from_private_key(StringIO(KEY))
ssh.connect("72.62.228.112", username="root", pkey=key, timeout=20)

container = run(ssh, "docker ps --format '{{.Names}}' | grep '^db-' | head -1").strip().splitlines()[0]
print(f"DB container: {container}\n")

queries = [
    ("ACCOUNT ROW", """
    SELECT user_id, full_name, email, role, balance, margin_allotted
    FROM paper_accounts
    WHERE full_name ILIKE '%Aneega%' OR email ILIKE '%aneega%' OR role IS NOT NULL
    ORDER BY full_name
    LIMIT 20;
    """),
    ("TARGET USER BY EXTERNAL ID 2544 (if stored)", """
    SELECT *
    FROM paper_accounts
    WHERE external_user_id::text = '2544';
    """),
    ("OPEN POSITIONS FOR USER 2544 MAPPED BY NAME", """
    SELECT pa.full_name, pa.user_id, pp.symbol, pp.exchange_segment, pp.product_type,
           pp.quantity, pp.avg_price, md.ltp,
           calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type) AS required_margin
    FROM paper_positions pp
    JOIN paper_accounts pa ON pa.user_id = pp.user_id
    LEFT JOIN market_data md ON md.instrument_token = pp.instrument_token
    WHERE pa.full_name ILIKE '%Aneega%'
      AND pp.status='OPEN'
      AND pp.quantity != 0;
    """),
    ("USED/AVAILABLE MARGIN FOR ANEEGA", """
    SELECT
      pa.full_name,
      pa.user_id,
      pa.margin_allotted,
      COALESCE(SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
        FILTER (WHERE pp.status='OPEN' AND pp.quantity != 0), 0) AS used_margin,
      pa.margin_allotted - COALESCE(SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
        FILTER (WHERE pp.status='OPEN' AND pp.quantity != 0), 0) AS available_margin
    FROM paper_accounts pa
    LEFT JOIN paper_positions pp ON pp.user_id = pa.user_id
    WHERE pa.full_name ILIKE '%Aneega%'
    GROUP BY pa.full_name, pa.user_id, pa.margin_allotted;
    """),
    ("LATEST ORDERS FOR ANEEGA", """
    SELECT po.order_id, po.symbol, po.side, po.order_type, po.quantity, po.filled_qty, po.remaining_qty,
           po.price, po.status, po.product_type, po.created_at
    FROM paper_orders po
    JOIN paper_accounts pa ON pa.user_id = po.user_id
    WHERE pa.full_name ILIKE '%Aneega%'
    ORDER BY po.created_at DESC
    LIMIT 20;
    """),
    ("LATEST TRADES FOR ANEEGA", """
    SELECT pt.order_id, pt.symbol, pt.side, COALESCE(pt.fill_qty, pt.quantity) AS fill_qty, pt.fill_price, pt.traded_at
    FROM paper_trades pt
    JOIN paper_accounts pa ON pa.user_id = pt.user_id
    WHERE pa.full_name ILIKE '%Aneega%'
    ORDER BY pt.traded_at DESC
    LIMIT 20;
    """),
]

for title, sql in queries:
    print("=" * 90)
    print(title)
    print("=" * 90)
    esc = sql.replace("'", "'\"'\"'")
    cmd = f"docker exec {container} psql -U postgres -d trading_terminal -c '{esc}'"
    print(run(ssh, cmd))

ssh.close()
