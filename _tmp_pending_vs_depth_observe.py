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

    sql = r'''
WITH pending AS (
    SELECT
        po.order_id,
        po.user_id,
        po.symbol,
        po.instrument_token,
        po.side,
        po.order_type,
        po.status::text AS status,
        po.quantity,
        COALESCE(po.filled_qty,0) AS filled_qty,
        GREATEST(po.quantity - COALESCE(po.filled_qty,0), 0) AS remaining_qty,
        po.limit_price,
        po.placed_at,
        md.ltp,
        CASE
            WHEN md.bid_depth IS NOT NULL
             AND jsonb_typeof(md.bid_depth)='array'
             AND jsonb_array_length(md.bid_depth) > 0
            THEN NULLIF(md.bid_depth->0->>'price','')::numeric
            ELSE NULL
        END AS best_bid,
        CASE
            WHEN md.bid_depth IS NOT NULL
             AND jsonb_typeof(md.bid_depth)='array'
             AND jsonb_array_length(md.bid_depth) > 0
            THEN COALESCE(NULLIF(md.bid_depth->0->>'qty','')::numeric,0)
            ELSE 0
        END AS best_bid_qty,
        CASE
            WHEN md.ask_depth IS NOT NULL
             AND jsonb_typeof(md.ask_depth)='array'
             AND jsonb_array_length(md.ask_depth) > 0
            THEN NULLIF(md.ask_depth->0->>'price','')::numeric
            ELSE NULL
        END AS best_ask,
        CASE
            WHEN md.ask_depth IS NOT NULL
             AND jsonb_typeof(md.ask_depth)='array'
             AND jsonb_array_length(md.ask_depth) > 0
            THEN COALESCE(NULLIF(md.ask_depth->0->>'qty','')::numeric,0)
            ELSE 0
        END AS best_ask_qty
    FROM paper_orders po
    LEFT JOIN market_data md ON md.instrument_token = po.instrument_token
    WHERE po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
      AND UPPER(COALESCE(po.order_type::text,'')) = 'LIMIT'
      AND GREATEST(po.quantity - COALESCE(po.filled_qty,0), 0) > 0
), classified AS (
    SELECT
      p.*,
      CASE
        WHEN p.side='BUY'  AND p.best_ask IS NOT NULL AND p.best_ask_qty>0 AND p.limit_price >= p.best_ask THEN true
        WHEN p.side='SELL' AND p.best_bid IS NOT NULL AND p.best_bid_qty>0 AND p.limit_price <= p.best_bid THEN true
        ELSE false
      END AS marketable_by_top_book_now,
      CASE
        WHEN p.side='BUY'  AND p.ltp IS NOT NULL AND p.limit_price >= p.ltp THEN true
        WHEN p.side='SELL' AND p.ltp IS NOT NULL AND p.limit_price <= p.ltp THEN true
        ELSE false
      END AS crossed_ltp_now
    FROM pending p
)
SELECT
  order_id, user_id, symbol, instrument_token, side, status,
  quantity, filled_qty, remaining_qty, limit_price, ltp, best_bid, best_bid_qty, best_ask, best_ask_qty,
  marketable_by_top_book_now, crossed_ltp_now, placed_at
FROM classified
ORDER BY marketable_by_top_book_now DESC, crossed_ltp_now DESC, placed_at ASC
LIMIT 120;
'''

    print("=== Pending LIMIT orders vs live LTP/top-book ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{sql}\""))

    summary_sql = r'''
WITH pending AS (
    SELECT
        po.order_id,
        po.side,
        po.limit_price,
        md.ltp,
        CASE
            WHEN md.bid_depth IS NOT NULL
             AND jsonb_typeof(md.bid_depth)='array'
             AND jsonb_array_length(md.bid_depth) > 0
            THEN NULLIF(md.bid_depth->0->>'price','')::numeric
            ELSE NULL
        END AS best_bid,
        CASE
            WHEN md.bid_depth IS NOT NULL
             AND jsonb_typeof(md.bid_depth)='array'
             AND jsonb_array_length(md.bid_depth) > 0
            THEN COALESCE(NULLIF(md.bid_depth->0->>'qty','')::numeric,0)
            ELSE 0
        END AS best_bid_qty,
        CASE
            WHEN md.ask_depth IS NOT NULL
             AND jsonb_typeof(md.ask_depth)='array'
             AND jsonb_array_length(md.ask_depth) > 0
            THEN NULLIF(md.ask_depth->0->>'price','')::numeric
            ELSE NULL
        END AS best_ask,
        CASE
            WHEN md.ask_depth IS NOT NULL
             AND jsonb_typeof(md.ask_depth)='array'
             AND jsonb_array_length(md.ask_depth) > 0
            THEN COALESCE(NULLIF(md.ask_depth->0->>'qty','')::numeric,0)
            ELSE 0
        END AS best_ask_qty
    FROM paper_orders po
    LEFT JOIN market_data md ON md.instrument_token = po.instrument_token
    WHERE po.status::text IN ('PENDING','OPEN','PARTIAL','PARTIAL_FILL','PARTIALLY_FILLED')
      AND UPPER(COALESCE(po.order_type::text,'')) = 'LIMIT'
      AND GREATEST(po.quantity - COALESCE(po.filled_qty,0), 0) > 0
), classified AS (
    SELECT
      p.*,
      CASE
        WHEN p.side='BUY'  AND p.best_ask IS NOT NULL AND p.best_ask_qty>0 AND p.limit_price >= p.best_ask THEN 1
        WHEN p.side='SELL' AND p.best_bid IS NOT NULL AND p.best_bid_qty>0 AND p.limit_price <= p.best_bid THEN 1
        ELSE 0
      END AS marketable_by_top_book_now,
      CASE
        WHEN p.side='BUY'  AND p.ltp IS NOT NULL AND p.limit_price >= p.ltp THEN 1
        WHEN p.side='SELL' AND p.ltp IS NOT NULL AND p.limit_price <= p.ltp THEN 1
        ELSE 0
      END AS crossed_ltp_now
    FROM pending p
)
SELECT
  COUNT(*) AS total_pending_limit,
  SUM(marketable_by_top_book_now) AS pending_but_marketable_now,
  SUM(crossed_ltp_now) AS pending_with_limit_crossing_ltp
FROM classified;
'''

    print("=== Summary ===")
    print(run_cmd(ssh, f"docker exec {db_container} psql -U postgres -d {DB_NAME} -P pager=off -c \"{summary_sql}\""))

finally:
    ssh.close()
