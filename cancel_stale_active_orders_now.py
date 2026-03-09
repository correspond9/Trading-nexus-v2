import paramiko

HOST = "72.62.228.112"
USER = "root"
KEY = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"
DB_NAME = "trading_terminal"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, pkey=paramiko.Ed25519Key.from_private_key_file(KEY), timeout=20)

try:
    find_db_cmd = f"docker ps --filter name=db-{APP_PREFIX} --format '{{{{.Names}}}}' | head -n 1"
    stdin, stdout, stderr = ssh.exec_command(find_db_cmd)
    db_container = stdout.read().decode("utf-8", errors="replace").strip()
    if not db_container:
        raise RuntimeError("Could not find DB container")

    print(f"Using DB container: {db_container}")

    sql = """
    WITH upd AS (
        UPDATE paper_orders
        SET status = 'CANCELLED',
            updated_at = NOW(),
            archived_at = COALESCE(archived_at, NOW())
        WHERE archived_at IS NULL
          AND DATE(placed_at AT TIME ZONE 'Asia/Kolkata') < CURRENT_DATE
          AND status::text IN ('PENDING', 'OPEN', 'PARTIAL', 'PARTIAL_FILL', 'PARTIALLY_FILLED')
        RETURNING user_id
    )
    SELECT COUNT(*) AS cancelled_orders, COUNT(DISTINCT user_id) AS affected_users FROM upd;
    """

    run_cmd = f"docker exec {db_container} psql -U postgres -d {DB_NAME} -c \"{sql}\""
    stdin, stdout, stderr = ssh.exec_command(run_cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    err = stderr.read().decode("utf-8", errors="replace")
    if err.strip():
        print(err)

    verify_sql = """
    SELECT
      u.mobile,
      pa.margin_allotted,
      COALESCE(calculate_pending_orders_margin(pa.user_id), 0) AS pending_reserved,
      pa.margin_allotted - COALESCE(calculate_pending_orders_margin(pa.user_id), 0) AS available_after_cleanup
    FROM paper_accounts pa
    JOIN users u ON u.id = pa.user_id
    WHERE u.mobile IN ('8591641277', '9326890165')
    ORDER BY u.mobile;
    """
    verify_cmd = f"docker exec {db_container} psql -U postgres -d {DB_NAME} -c \"{verify_sql}\""
    stdin, stdout, stderr = ssh.exec_command(verify_cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    verr = stderr.read().decode("utf-8", errors="replace")
    if verr.strip():
        print(verr)

finally:
    ssh.close()
