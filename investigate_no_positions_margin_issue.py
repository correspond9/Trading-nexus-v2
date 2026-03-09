import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB = "db-x8gg0og8440wkgc8ow0ococs-072411628978"
DB_NAME = "trading_terminal"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=15)

queries = [
    (
        "Users with no OPEN positions but pending margin reserved",
        """
        SELECT
            u.mobile,
            u.id as user_id,
            COALESCE(pa.margin_allotted, 0) AS allotted,
            COALESCE(calculate_pending_orders_margin(pa.user_id), 0) AS pending_reserved,
            COALESCE((
                SELECT SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
                FROM paper_positions pp
                WHERE pp.user_id = pa.user_id AND pp.status='OPEN' AND pp.quantity != 0
            ), 0) AS open_positions_margin,
            (
                SELECT COUNT(*)
                FROM paper_positions pp
                WHERE pp.user_id = pa.user_id AND pp.status='OPEN' AND pp.quantity != 0
            ) AS open_positions_count,
            (
                SELECT COUNT(*)
                FROM paper_orders po
                WHERE po.user_id = pa.user_id AND po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
            ) AS pending_orders_count
        FROM paper_accounts pa
        JOIN users u ON u.id = pa.user_id
        WHERE (
            SELECT COUNT(*)
            FROM paper_positions pp
            WHERE pp.user_id = pa.user_id AND pp.status='OPEN' AND pp.quantity != 0
        ) = 0
          AND COALESCE(calculate_pending_orders_margin(pa.user_id), 0) > 0
        ORDER BY pending_reserved DESC
        LIMIT 20;
        """,
    ),
    (
        "Detailed pending orders for mobile 9326890165",
        """
        WITH usr AS (
            SELECT id FROM users WHERE mobile = '9326890165'
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
            (po.quantity - COALESCE(po.filled_qty, 0)) AS unfilled_qty,
            po.limit_price,
            po.fill_price,
            po.placed_at,
            po.updated_at
        FROM paper_orders po
        WHERE po.user_id = (SELECT id FROM usr)
          AND po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
        ORDER BY po.updated_at DESC NULLS LAST, po.placed_at DESC
        LIMIT 50;
        """,
    ),
    (
        "Open positions for mobile 9326890165",
        """
        WITH usr AS (
            SELECT id FROM users WHERE mobile = '9326890165'
        )
        SELECT
            pp.symbol,
            pp.quantity,
            pp.status,
            pp.average_price,
            pp.last_price,
            pp.updated_at
        FROM paper_positions pp
        WHERE pp.user_id = (SELECT id FROM usr)
          AND pp.status = 'OPEN'
          AND pp.quantity != 0
        ORDER BY pp.updated_at DESC NULLS LAST;
        """,
    ),
    (
        "Margin snapshot for mobile 9326890165",
        """
        WITH usr AS (
            SELECT id FROM users WHERE mobile = '9326890165'
        )
        SELECT
            u.mobile,
            pa.margin_allotted,
            COALESCE((
                SELECT SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
                FROM paper_positions pp
                WHERE pp.user_id = pa.user_id AND pp.status='OPEN' AND pp.quantity != 0
            ), 0) AS open_used_margin,
            COALESCE(calculate_pending_orders_margin(pa.user_id), 0) AS pending_reserved_margin,
            (
                COALESCE((
                    SELECT SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
                    FROM paper_positions pp
                    WHERE pp.user_id = pa.user_id AND pp.status='OPEN' AND pp.quantity != 0
                ), 0)
                + COALESCE(calculate_pending_orders_margin(pa.user_id), 0)
            ) AS total_used,
            pa.margin_allotted - (
                COALESCE((
                    SELECT SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type))
                    FROM paper_positions pp
                    WHERE pp.user_id = pa.user_id AND pp.status='OPEN' AND pp.quantity != 0
                ), 0)
                + COALESCE(calculate_pending_orders_margin(pa.user_id), 0)
            ) AS available_margin
        FROM paper_accounts pa
        JOIN users u ON u.id = pa.user_id
        WHERE pa.user_id = (SELECT id FROM usr);
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
