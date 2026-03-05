#!/usr/bin/env python3
"""Hotfix production backend for position-exit row selection bug."""

from __future__ import annotations

import pathlib
import subprocess
import sys
from datetime import datetime

VPS = "root@72.62.228.112"
APP_PREFIX = "x8gg0og8440wkgc8ow0ococs"
LOCAL_POSITIONS = pathlib.Path("app/routers/positions.py")
LOCAL_ADMIN = pathlib.Path("app/routers/admin.py")


def run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ssh(command: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return run(["ssh", VPS, command], timeout=timeout)


def must(ok: bool, message: str, stdout: str = "", stderr: str = "") -> None:
    if ok:
        print(f"OK: {message}")
        return
    print(f"ERROR: {message}")
    if stdout.strip():
        print(stdout.strip())
    if stderr.strip():
        print(stderr.strip())
    sys.exit(1)


def main() -> int:
    print("=" * 72)
    print("Production Hotfix: Position Exit")
    print("=" * 72)

    if not LOCAL_POSITIONS.exists() or not LOCAL_ADMIN.exists():
        print("ERROR: local router files not found")
        return 1

    # Detect backend container dynamically.
    ps = ssh("docker ps --format '{{.Names}}'", timeout=30)
    must(ps.returncode == 0, "list docker containers", ps.stdout, ps.stderr)

    containers = [line.strip() for line in ps.stdout.splitlines() if line.strip()]
    backend = next((c for c in containers if c.startswith(f"backend-{APP_PREFIX}-")), None)
    must(bool(backend), "find backend container", ps.stdout, "")
    print(f"Backend container: {backend}")

    # Upload patched files to VPS /tmp.
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    remote_pos = f"/tmp/positions.py.{ts}"
    remote_admin = f"/tmp/admin.py.{ts}"

    scp1 = run(["scp", str(LOCAL_POSITIONS), f"{VPS}:{remote_pos}"], timeout=30)
    must(scp1.returncode == 0, "upload positions.py", scp1.stdout, scp1.stderr)

    scp2 = run(["scp", str(LOCAL_ADMIN), f"{VPS}:{remote_admin}"], timeout=30)
    must(scp2.returncode == 0, "upload admin.py", scp2.stdout, scp2.stderr)

    # Backup and replace inside container.
    backup_and_copy = ssh(
        " ; ".join(
            [
                f"docker exec {backend} sh -lc 'cp /app/app/routers/positions.py /app/app/routers/positions.py.bak_{ts}'",
                f"docker exec {backend} sh -lc 'cp /app/app/routers/admin.py /app/app/routers/admin.py.bak_{ts}'",
                f"docker cp {remote_pos} {backend}:/app/app/routers/positions.py",
                f"docker cp {remote_admin} {backend}:/app/app/routers/admin.py",
            ]
        ),
        timeout=60,
    )
    must(backup_and_copy.returncode == 0, "backup and replace backend router files", backup_and_copy.stdout, backup_and_copy.stderr)

    # Syntax check in container before restart.
    syntax = ssh(
        f"docker exec {backend} python -m py_compile /app/app/routers/positions.py /app/app/routers/admin.py",
        timeout=30,
    )
    must(syntax.returncode == 0, "python syntax check", syntax.stdout, syntax.stderr)

    # Restart backend container to load changed python modules.
    restart = ssh(f"docker restart {backend}", timeout=60)
    must(restart.returncode == 0, "restart backend container", restart.stdout, restart.stderr)

    # Quick health check from inside VPS.
    health = ssh("curl -sS http://127.0.0.1:8000/api/v2/health", timeout=30)
    must(health.returncode == 0, "backend health endpoint reachable", health.stdout, health.stderr)
    print("Health response:")
    print(health.stdout.strip()[:400])

    print("\nSUCCESS: Production hotfix applied. Please retry exit on P.Userwise now.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
