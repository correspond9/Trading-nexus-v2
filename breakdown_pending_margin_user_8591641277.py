import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB = "db-x8gg0og8440wkgc8ow0ococs-072411628978"
DB_NAME = "trading_terminal"
MOBILE = "8591641277"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=15)

queries = [
    (
        "User + margin snapshot",
        f"""
        WITH usr AS (
            SELECT id, mobile FROM users WHERE mobile = '{MOBILE}'
        )
        SELECT
            usr.mobile,
            usr.id as user_id,
            pa.margin_allotted,
            COALESCE(calculate_pending_orders_margin(pa.user_id), 0) AS pending_reserved_margin,
            pa.margin_allotted - COALESCE(calculate_pending_orders_margin(pa.user_id), 0) AS available_if_no_open_positions
        FROM usr
        JOIN paper_accounts pa ON pa.user_id = usr.id;
        """,
    ),
    (
        "Pending/Open/Partial orders",
        f"""
        WITH usr AS (
            SELECT id FROM users WHERE mobile = '{MOBILE}'
        )
        SELECT
            po.order_id,
            po.symbol,
            po.side,
            po.order_type,
            po.product_type,
            po.status,
            po.quantity,
            COALESCE(po.filled_qty, 0) AS filled_qty,
            GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) AS unfilled_qty,
            COALESCE(po.limit_price, po.fill_price) AS margin_price,
            po.instrument_token,
            po.placed_at,
            po.updated_at
        FROM paper_orders po
        WHERE po.user_id = (SELECT id FROM usr)
          AND po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
        ORDER BY po.updated_at DESC NULLS LAST, po.placed_at DESC;
        """,
    ),
    (
        "Per-order estimated reserved margin (as function would reserve)",
        f"""
        WITH usr AS (
            SELECT id FROM users WHERE mobile = '{MOBILE}'
        ), pending_orders AS (
            SELECT
                po.order_id,
                po.symbol,
                po.side,
                po.status,
                po.exchange_segment,
                po.product_type,
                po.instrument_token,
                GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) AS unfilled_qty,
                COALESCE(po.limit_price, po.fill_price) AS margin_price
            FROM paper_orders po
            WHERE po.user_id = (SELECT id FROM usr)
              AND po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
        )
        SELECT
            p.order_id,
            p.symbol,
            p.side,
            p.status,
            p.unfilled_qty,
            p.margin_price,
            CASE
              WHEN p.unfilled_qty > 0 AND p.margin_price IS NOT NULL AND p.margin_price > 0 THEN
                calculate_position_margin(
                    p.instrument_token,
                    p.symbol,
                    p.exchange_segment,
                    p.unfilled_qty,
                    p.product_type
                )
              ELSE 0
            END AS reserved_margin_estimate
        FROM pending_orders p
        ORDER BY reserved_margin_estimate DESC NULLS LAST;
        """,
    ),
]

try:
    for title, q in queries:
        print("\n" + "=" * 30 + f" {title} " + "=" * 30)
        cmd = f"docker exec {DB} psql -U postgres -d {DB_NAME} -c \"{q}\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        print(out)
        if err.strip():
            print("ERR:")
            print(err)
finally:
    ssh.close()
