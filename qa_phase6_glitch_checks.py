"""
Phase 6 - Glitch/Runtime Stability Checks
----------------------------------------
Runs focused runtime checks against live API:
- Auth + profile access
- Stream status endpoint
- Concurrent search burst
- Concurrent quote burst
- Error-rate summary
"""

from __future__ import annotations

import concurrent.futures
import json
import time
from collections import Counter
from datetime import datetime
from typing import Any

import requests

BASE_URL = "http://localhost:8000/api/v2"
TIMEOUT = 10
USER = {"mobile": "7777777777", "password": "user123"}


def login() -> str:
    r = requests.post(f"{BASE_URL}/auth/login", json=USER, timeout=TIMEOUT)
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        raise RuntimeError("No access token returned")
    return token


def req(method: str, path: str, headers: dict[str, str], **kwargs: Any) -> tuple[int, float, str]:
    t0 = time.perf_counter()
    try:
        r = requests.request(method, f"{BASE_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
        dt = (time.perf_counter() - t0) * 1000.0
        detail = ""
        if r.status_code >= 400:
            detail = r.text[:200]
        return r.status_code, dt, detail
    except Exception as exc:
        dt = (time.perf_counter() - t0) * 1000.0
        return 0, dt, str(exc)


def main() -> int:
    started = datetime.now().isoformat()
    token = login()
    headers = {"X-AUTH": token}

    checks: list[dict[str, Any]] = []

    # Baseline API calls
    for path in ["/auth/me", "/market/stream-status", "/portfolio/positions", "/trading/orders"]:
        code, ms, detail = req("GET", path, headers)
        checks.append({"type": "baseline", "path": path, "status": code, "latency_ms": round(ms, 2), "detail": detail})

    # Concurrent search burst
    search_queries = ["NIFTY", "BANK", "RELIANCE", "ITC", "DCB", "TATA", "INFY", "SBIN", "AXIS", "GOLD"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = [
            ex.submit(
                req,
                "GET",
                "/instruments/search",
                headers,
                params={"query": q, "exchange": "NSE_EQ"},
            )
            for q in search_queries
        ]
        for q, f in zip(search_queries, futs):
            code, ms, detail = f.result()
            checks.append({"type": "search_burst", "query": q, "status": code, "latency_ms": round(ms, 2), "detail": detail})

    # Concurrent quote burst
    symbols = ["ITC", "DCB Bank", "NIFTY 26 MAY 30700 CALL", "BANKBARODA 26 MAY 180 CALL", "NIFTY 07 APR 19200 CALL"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = [
            ex.submit(
                req,
                "GET",
                "/market/quote",
                headers,
                params={"symbol": s, "exchange_segment": "NSE_FNO" if "CALL" in s else "NSE_EQ"},
            )
            for s in symbols
        ]
        for s, f in zip(symbols, futs):
            code, ms, detail = f.result()
            checks.append({"type": "quote_burst", "symbol": s, "status": code, "latency_ms": round(ms, 2), "detail": detail})

    status_counts = Counter(item["status"] for item in checks)
    failures = [c for c in checks if c["status"] == 0 or c["status"] >= 500]
    client_errors = [c for c in checks if 400 <= c["status"] < 500]

    summary = {
        "started_at": started,
        "finished_at": datetime.now().isoformat(),
        "total_checks": len(checks),
        "status_counts": dict(status_counts),
        "server_failures": len(failures),
        "client_errors": len(client_errors),
        "max_latency_ms": max(c["latency_ms"] for c in checks) if checks else 0,
        "checks": checks,
    }

    with open("QA_PHASE6_GLITCH_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps({k: summary[k] for k in ["total_checks", "status_counts", "server_failures", "client_errors", "max_latency_ms"]}, indent=2))
    return 0 if len(failures) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
