"""
Phase 7 - Edge Case and Stress Checks
-------------------------------------
Covers invalid payloads, boundary values, and short burst stress for order APIs.
"""

from __future__ import annotations

import concurrent.futures
import json
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


def post_order(headers: dict[str, str], payload: dict[str, Any]) -> tuple[int, str]:
    try:
        r = requests.post(f"{BASE_URL}/trading/orders", headers=headers, json=payload, timeout=TIMEOUT)
        return r.status_code, r.text[:240]
    except Exception as exc:
        return 0, str(exc)


def main() -> int:
    token = login()
    headers = {"X-AUTH": token, "Content-Type": "application/json"}

    edge_cases = [
        {
            "name": "missing_symbol",
            "payload": {"exchange_segment": "NSE_EQ", "side": "BUY", "quantity": 1, "order_type": "MARKET", "product_type": "MIS"},
            "expect_4xx": True,
        },
        {
            "name": "zero_quantity",
            "payload": {"symbol": "ITC", "exchange_segment": "NSE_EQ", "side": "BUY", "quantity": 0, "order_type": "MARKET", "product_type": "MIS"},
            "expect_4xx": True,
        },
        {
            "name": "negative_quantity",
            "payload": {"symbol": "ITC", "exchange_segment": "NSE_EQ", "side": "BUY", "quantity": -1, "order_type": "MARKET", "product_type": "MIS"},
            "expect_4xx": True,
        },
        {
            "name": "invalid_side",
            "payload": {"symbol": "ITC", "exchange_segment": "NSE_EQ", "side": "HOLD", "quantity": 1, "order_type": "MARKET", "product_type": "MIS"},
            "expect_4xx": True,
        },
        {
            "name": "invalid_exchange",
            "payload": {"symbol": "ITC", "exchange_segment": "BAD_EX", "side": "BUY", "quantity": 1, "order_type": "MARKET", "product_type": "MIS"},
            "expect_4xx": True,
        },
        {
            "name": "oversized_quantity",
            "payload": {"symbol": "ITC", "exchange_segment": "NSE_EQ", "side": "BUY", "quantity": 100000000, "order_type": "MARKET", "product_type": "MIS"},
            "expect_4xx": False,
        },
    ]

    results: list[dict[str, Any]] = []

    for case in edge_cases:
        code, detail = post_order(headers, case["payload"])
        ok = (400 <= code < 500) if case["expect_4xx"] else (code in (200, 201, 400, 403, 404, 422))
        results.append({"name": case["name"], "status": code, "ok": ok, "detail": detail})

    # Short stress burst: 20 concurrent small MARKET orders
    stress_payload = {
        "symbol": "NIFTY 26 MAY 30700 CALL",
        "exchange_segment": "NSE_FNO",
        "side": "BUY",
        "quantity": 1,
        "order_type": "MARKET",
        "product_type": "MIS",
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(post_order, headers, stress_payload) for _ in range(20)]
        stress = [f.result() for f in futs]

    stress_summary = {
        "total": len(stress),
        "status_counts": {},
    }
    for code, _ in stress:
        stress_summary["status_counts"][str(code)] = stress_summary["status_counts"].get(str(code), 0) + 1

    report = {
        "started_at": datetime.now().isoformat(),
        "edge_case_results": results,
        "stress_summary": stress_summary,
        "failed_edge_cases": [r for r in results if not r["ok"]],
    }

    with open("QA_PHASE7_EDGE_STRESS_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps({
        "edge_total": len(results),
        "edge_failed": len(report["failed_edge_cases"]),
        "stress_status_counts": stress_summary["status_counts"],
    }, indent=2))

    return 0 if len(report["failed_edge_cases"]) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
