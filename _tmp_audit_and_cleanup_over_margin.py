import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"
DB_NAME = "trading_terminal"


def run_cmd(ssh, cmd: str) -> str:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if err.strip():
        out += "\n[stderr]\n" + err
    return out


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY_PATH), timeout=20)

try:
    db_container = run_cmd(
        ssh,
        f"docker ps --filter name=db-{APP_PREFIX} --format '{{{{.Names}}}}' | sed -n '1p'",
    ).strip().splitlines()[0]
    print(f"DB container: {db_container}\n")

    print("=== Verify pending-margin function in production ===")
    fn_sql = "SELECT pg_get_functiondef('calculate_pending_orders_margin(uuid)'::regprocedure);"
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -At -c \"{fn_sql}\""))

    print("=== Pre-cleanup users over effective pending capacity ===")
    audit_sql = r'''
WITH user_capacity AS (
    SELECT
        pa.user_id,
        COALESCE(pa.margin_allotted, 0)::numeric AS margin_allotted,
        COALESCE((
            SELECT SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment,
                    pp.quantity,
                    pp.product_type
                )
            )
            FROM paper_positions pp
            WHERE pp.user_id = pa.user_id
              AND pp.status = 'OPEN'
              AND pp.quantity != 0
        ), 0)::numeric AS positions_margin
    FROM paper_accounts pa
), pending_orders AS (
    SELECT
        po.order_id,
        po.user_id,
        po.symbol,
        po.side,
        po.status::text AS status,
        po.exchange_segment,
        po.product_type,
        po.instrument_token,
        po.placed_at,
        GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) AS unfilled_qty,
        COALESCE(
            calculate_position_margin(
                po.instrument_token,
                po.symbol,
                po.exchange_segment,
                GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0),
                po.product_type
            ),
            0
        )::numeric AS order_margin
    FROM paper_orders po
    WHERE po.status::text IN ('PENDING', 'OPEN', 'PARTIAL', 'PARTIAL_FILL', 'PARTIALLY_FILLED')
      AND GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) > 0
), ranked AS (
    SELECT
        p.*,
        c.margin_allotted,
        c.positions_margin,
        GREATEST(c.margin_allotted - c.positions_margin, 0)::numeric AS pending_capacity,
        SUM(p.order_margin) OVER (
            PARTITION BY p.user_id
            ORDER BY p.placed_at ASC NULLS LAST, p.order_id ASC
        ) AS cumulative_pending_margin
    FROM pending_orders p
    JOIN user_capacity c ON c.user_id = p.user_id
), overflow AS (
    SELECT *
    FROM ranked
    WHERE cumulative_pending_margin > pending_capacity
)
SELECT
    u.mobile,
    o.user_id,
    COUNT(*) AS overflow_orders,
    ROUND(MAX(o.pending_capacity)::numeric, 2) AS pending_capacity,
    ROUND(MAX(o.cumulative_pending_margin)::numeric, 2) AS top_cumulative_pending
FROM overflow o
JOIN users u ON u.id = o.user_id
GROUP BY u.mobile, o.user_id
ORDER BY overflow_orders DESC, u.mobile;
'''
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -c \"{audit_sql}\""))

    print("=== One-time silent reject of overflow pending orders ===")
    cleanup_sql = r'''
WITH user_capacity AS (
    SELECT
        pa.user_id,
        COALESCE(pa.margin_allotted, 0)::numeric AS margin_allotted,
        COALESCE((
            SELECT SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment,
                    pp.quantity,
                    pp.product_type
                )
            )
            FROM paper_positions pp
            WHERE pp.user_id = pa.user_id
              AND pp.status = 'OPEN'
              AND pp.quantity != 0
        ), 0)::numeric AS positions_margin
    FROM paper_accounts pa
), pending_orders AS (
    SELECT
        po.order_id,
        po.user_id,
        po.placed_at,
        GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) AS unfilled_qty,
        COALESCE(
            calculate_position_margin(
                po.instrument_token,
                po.symbol,
                po.exchange_segment,
                GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0),
                po.product_type
            ),
            0
        )::numeric AS order_margin
    FROM paper_orders po
    WHERE po.status::text IN ('PENDING', 'OPEN', 'PARTIAL', 'PARTIAL_FILL', 'PARTIALLY_FILLED')
      AND GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) > 0
), ranked AS (
    SELECT
        p.*,
        GREATEST(c.margin_allotted - c.positions_margin, 0)::numeric AS pending_capacity,
        SUM(p.order_margin) OVER (
            PARTITION BY p.user_id
            ORDER BY p.placed_at ASC NULLS LAST, p.order_id ASC
        ) AS cumulative_pending_margin
    FROM pending_orders p
    JOIN user_capacity c ON c.user_id = p.user_id
), to_reject AS (
    SELECT order_id
    FROM ranked
    WHERE cumulative_pending_margin > pending_capacity
), upd AS (
    UPDATE paper_orders po
    SET
        status = 'REJECTED',
        remaining_qty = 0,
        updated_at = NOW()
    WHERE po.order_id IN (SELECT order_id FROM to_reject)
    RETURNING po.user_id, po.order_id
)
SELECT COUNT(*) AS rejected_orders, COUNT(DISTINCT user_id) AS affected_users
FROM upd;
'''
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -c \"{cleanup_sql}\""))

    print("=== Post-cleanup verification ===")
    post_sql = r'''
WITH user_capacity AS (
    SELECT
        pa.user_id,
        COALESCE(pa.margin_allotted, 0)::numeric AS margin_allotted,
        COALESCE((
            SELECT SUM(
                calculate_position_margin(
                    pp.instrument_token,
                    pp.symbol,
                    pp.exchange_segment,
                    pp.quantity,
                    pp.product_type
                )
            )
            FROM paper_positions pp
            WHERE pp.user_id = pa.user_id
              AND pp.status = 'OPEN'
              AND pp.quantity != 0
        ), 0)::numeric AS positions_margin
    FROM paper_accounts pa
), pending_orders AS (
    SELECT
        po.user_id,
        COALESCE(
            calculate_position_margin(
                po.instrument_token,
                po.symbol,
                po.exchange_segment,
                GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0),
                po.product_type
            ),
            0
        )::numeric AS order_margin
    FROM paper_orders po
    WHERE po.status::text IN ('PENDING', 'OPEN', 'PARTIAL', 'PARTIAL_FILL', 'PARTIALLY_FILLED')
      AND GREATEST(po.quantity - COALESCE(po.filled_qty, 0), 0) > 0
), agg AS (
    SELECT user_id, SUM(order_margin) AS pending_margin
    FROM pending_orders
    GROUP BY user_id
)
SELECT
    u.mobile,
    c.user_id,
    ROUND(GREATEST(c.margin_allotted - c.positions_margin, 0)::numeric, 2) AS pending_capacity,
    ROUND(COALESCE(a.pending_margin, 0)::numeric, 2) AS pending_margin_now
FROM user_capacity c
JOIN users u ON u.id = c.user_id
LEFT JOIN agg a ON a.user_id = c.user_id
WHERE COALESCE(a.pending_margin, 0) > GREATEST(c.margin_allotted - c.positions_margin, 0) + 0.0001
ORDER BY u.mobile;
'''
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -c \"{post_sql}\""))

finally:
    ssh.close()
