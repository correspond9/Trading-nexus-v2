import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY_PATH = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"
DB_NAME = "trading_terminal"
TARGET_ORDER_ID = "47dc2a0f-0b08-47f0-b08c-edd1829041d3"


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
    containers = run_cmd(
        ssh,
        f"docker ps --filter name={APP_PREFIX} --format '{{{{.Names}}}}'",
    ).strip().splitlines()
    db_container = [c for c in containers if c.startswith("db-")][0]
    backend_container = [c for c in containers if c.startswith("backend-")][0]

    print(f"DB container: {db_container}")
    print(f"Backend container: {backend_container}\n")

    sql = rf'''
WITH target AS (
  SELECT u.id, u.user_no, u.name, u.mobile
  FROM users u
  WHERE LOWER(u.name) LIKE LOWER('%aneeqa%')
  ORDER BY u.created_at DESC
  LIMIT 1
),
acc AS (
  SELECT pa.user_id, COALESCE(pa.margin_allotted,0) AS margin_allotted
  FROM paper_accounts pa
  JOIN target t ON t.id = pa.user_id
),
pos AS (
  SELECT COALESCE(SUM(calculate_position_margin(pp.instrument_token, pp.symbol, pp.exchange_segment, pp.quantity, pp.product_type)),0) AS positions_margin
  FROM paper_positions pp
  JOIN target t ON t.id = pp.user_id
  WHERE pp.status='OPEN' AND pp.quantity <> 0
),
pend AS (
  SELECT COALESCE(calculate_pending_orders_margin((SELECT id FROM target)),0) AS pending_margin
),
ord AS (
  SELECT
    po.order_id,
    po.user_id,
    po.placed_at,
    po.symbol,
    po.side,
    po.order_type,
    po.product_type,
    po.exchange_segment,
    po.instrument_token,
    po.quantity,
    COALESCE(po.filled_qty,0) AS filled_qty,
    (po.quantity - COALESCE(po.filled_qty,0)) AS calc_remaining_qty,
    po.limit_price,
    po.fill_price
  FROM paper_orders po
  JOIN target t ON t.id = po.user_id
  WHERE po.order_id = '{TARGET_ORDER_ID}'::uuid
),
ord_component AS (
  SELECT
    calculate_position_margin(o.instrument_token, o.symbol, o.exchange_segment, o.calc_remaining_qty, o.product_type) AS this_order_pending_component
  FROM ord o
)
SELECT
  t.id AS user_id,
  t.user_no,
  t.name,
  t.mobile,
  a.margin_allotted::numeric(18,2) AS margin_allotted,
  p.positions_margin::numeric(18,2) AS positions_margin,
  pe.pending_margin::numeric(18,2) AS pending_reserved_margin,
  (a.margin_allotted - (p.positions_margin + pe.pending_margin))::numeric(18,2) AS available_now,
  o.order_id,
  o.placed_at,
  o.symbol,
  o.side,
  o.order_type,
  o.product_type,
  o.exchange_segment,
  o.quantity,
  o.filled_qty,
  o.calc_remaining_qty AS remaining_qty,
  o.limit_price,
  (o.quantity * COALESCE(o.limit_price, o.fill_price, 0))::numeric(18,2) AS required_if_cash_equity_rule,
  oc.this_order_pending_component::numeric(18,2) AS this_order_pending_component,
  (a.margin_allotted - (p.positions_margin + pe.pending_margin) + oc.this_order_pending_component)::numeric(18,2) AS approx_available_before_this_order
FROM target t
JOIN acc a ON a.user_id = t.id
CROSS JOIN pos p
CROSS JOIN pend pe
JOIN ord o ON true
CROSS JOIN ord_component oc;
'''

    print("=== Core forensic snapshot ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{sql}\""))

    sql_positions = r'''
WITH target AS (
  SELECT id
  FROM users
  WHERE LOWER(name) LIKE LOWER('%aneeqa%')
  ORDER BY created_at DESC
  LIMIT 1
)
SELECT position_id, symbol, exchange_segment, quantity, avg_price, product_type, status,
       calculate_position_margin(instrument_token, symbol, exchange_segment, quantity, product_type)::numeric(18,2) AS position_margin_component
FROM paper_positions
WHERE user_id=(SELECT id FROM target)
  AND status='OPEN'
ORDER BY symbol;
'''
    print("=== Open positions with margin components ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{sql_positions}\""))

    sql_pending = r'''
WITH target AS (
  SELECT id
  FROM users
  WHERE LOWER(name) LIKE LOWER('%aneeqa%')
  ORDER BY created_at DESC
  LIMIT 1
)
SELECT order_id, placed_at, symbol, side, order_type, product_type, quantity, COALESCE(filled_qty,0) AS filled_qty,
       (quantity-COALESCE(filled_qty,0)) AS remaining_qty, status, limit_price,
       calculate_position_margin(instrument_token, symbol, exchange_segment, (quantity-COALESCE(filled_qty,0)), product_type)::numeric(18,2) AS pending_margin_component
FROM paper_orders
WHERE user_id=(SELECT id FROM target)
  AND status IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
  AND (quantity-COALESCE(filled_qty,0)) > 0
ORDER BY placed_at DESC;
'''
    print("=== Pending/open orders with margin components ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{sql_pending}\""))

    print("=== Backend logs mentioning the order id ===")
    print(run_cmd(ssh, f"docker logs {backend_container} --since 72h 2>&1 | grep -n '{TARGET_ORDER_ID}' | tail -n 20"))

    print("=== Backend access logs for trading order endpoint (last 72h) ===")
    print(run_cmd(ssh, f"docker logs {backend_container} --since 72h 2>&1 | grep -n 'POST /api/v2/trading/orders' | tail -n 40"))

finally:
    ssh.close()
