#!/usr/bin/env python3
"""Run migration 031 on production DB via SSH and verify required columns."""

import pathlib
import subprocess
import sys

VPS = "root@72.62.228.112"
APP_PREFIX = "db-x8gg0og8440wkgc8ow0ococs-"
MIGRATION_FILE = pathlib.Path("migrations/031_paper_positions_missing_columns.sql")


def run_ssh(command: str, input_text: str | None = None, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ssh", VPS, command],
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def main() -> int:
    print("=" * 72)
    print("Migration 031 Runner")
    print("=" * 72)

    if not MIGRATION_FILE.exists():
        print(f"ERROR: missing file {MIGRATION_FILE}")
        return 1

    sql = MIGRATION_FILE.read_text(encoding="utf-8")
    print(f"Loaded SQL: {MIGRATION_FILE} ({len(sql)} bytes)")

    print("\n[1/4] Finding DB container...")
    list_res = run_ssh("docker ps --format '{{.Names}}'", timeout=30)
    if list_res.returncode != 0:
        print("ERROR: could not list docker containers")
        print(list_res.stderr.strip())
        return 1

    containers = [line.strip() for line in list_res.stdout.splitlines() if line.strip()]
    db_matches = [name for name in containers if name.startswith(APP_PREFIX)]
    if not db_matches:
        print("ERROR: DB container not found")
        print("Available containers:")
        for name in containers:
            print(f"- {name}")
        return 1

    db_container = db_matches[0]
    print(f"Found DB container: {db_container}")

    print("\n[2/5] Detecting DB name...")
    db_name_res = run_ssh(f"docker exec {db_container} sh -lc 'echo ${{POSTGRES_DB:-postgres}}'", timeout=30)
    if db_name_res.returncode != 0:
        print("ERROR: could not detect DB name")
        print(db_name_res.stderr.strip())
        return 1
    db_name = db_name_res.stdout.strip() or "postgres"
    print(f"Using database: {db_name}")

    print("\n[3/5] Uploading migration SQL to VPS...")
    upload_res = run_ssh("cat > /tmp/migration_031.sql", input_text=sql, timeout=30)
    if upload_res.returncode != 0:
        print("ERROR: upload failed")
        print(upload_res.stderr.strip())
        return 1
    print("Upload complete: /tmp/migration_031.sql")

    print("\n[4/5] Executing migration...")
    exec_cmd = (
        f"cat /tmp/migration_031.sql | docker exec -i {db_container} "
        f"psql -U postgres -d {db_name} -v ON_ERROR_STOP=1"
    )
    exec_res = run_ssh(exec_cmd, timeout=90)
    # Idempotent DDL may emit notices to stderr; only fail on non-zero exit code.
    if exec_res.returncode != 0:
        print("ERROR: migration execution failed")
        if exec_res.stdout.strip():
            print(exec_res.stdout.strip())
        print(exec_res.stderr.strip())
        return 1
    if exec_res.stdout.strip():
        print(exec_res.stdout.strip())
    print("Migration SQL executed")

    print("\n[5/5] Verifying columns...")
    verify_sql = (
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='paper_positions' "
        "AND column_name IN ('status','realized_pnl','closed_at') "
        "ORDER BY column_name;"
    )
    verify_cmd = (
        f"docker exec -i {db_container} "
        f"psql -U postgres -d {db_name} -tA -c \"{verify_sql}\""
    )
    verify_res = run_ssh(verify_cmd, timeout=30)
    if verify_res.returncode != 0:
        print("ERROR: verification query failed")
        print(verify_res.stderr.strip())
        return 1

    found = [line.strip() for line in verify_res.stdout.splitlines() if line.strip()]
    expected = ["closed_at", "realized_pnl", "status"]
    print("Found columns:", ", ".join(found) if found else "none")

    if sorted(found) != expected:
        print("ERROR: expected columns are not all present")
        return 1

    print("\nSUCCESS: migration 031 is applied and verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
