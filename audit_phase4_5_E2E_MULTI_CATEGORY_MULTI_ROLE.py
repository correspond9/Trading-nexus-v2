#!/usr/bin/env python3
"""Phase 4-5 E2E audit using production-like instrument selection across categories."""

import json
from datetime import datetime

import requests

API_BASE_URL = "http://localhost:8000/api/v2"
MOCK_QUOTE_URL = "http://localhost:9000/v2/marketfeed/quote"

USERS = {
    "USER": {"mobile": "7777777777", "password": "user123"},
    "SUPER_USER": {"mobile": "6666666666", "password": "super123"},
}

# Representative instruments selected from instrument_master after refresh.
INSTRUMENTS = [
    {
        "category": "equity",
        "symbol": "Reliance Industries",
        "exchange_segment": "NSE_EQ",
        "order_type": "LIMIT",
        "product_type": "MIS",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 1400.0,
        "instrument_token": 2885,
    },
    {
        "category": "index_option",
        "symbol": "NIFTY-Feb2026-19800-CE",
        "exchange_segment": "NSE_FNO",
        "order_type": "LIMIT",
        "product_type": "MIS",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 120.0,
        "instrument_token": 64666,
    },
    {
        "category": "stock_option",
        "symbol": "RELIANCE-Feb2026-680-CE",
        "exchange_segment": "NSE_FNO",
        "order_type": "LIMIT",
        "product_type": "MIS",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 80.0,
        "instrument_token": 62583,
    },
    {
        "category": "index_futures",
        "symbol": "NIFTY-Feb2026-FUT",
        "exchange_segment": "NSE_FNO",
        "order_type": "LIMIT",
        "product_type": "MIS",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 25000.0,
        "instrument_token": 59182,
    },
    {
        "category": "stock_futures",
        "symbol": "RELIANCE-Feb2026-FUT",
        "exchange_segment": "NSE_FNO",
        "order_type": "LIMIT",
        "product_type": "MIS",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 1500.0,
        "instrument_token": 59460,
    },
    {
        "category": "commodity_futures",
        "symbol": "CRUDEOIL MAR FUT",
        "exchange_segment": "MCX_FO",
        "order_type": "LIMIT",
        "product_type": "NORMAL",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 8000.0,
        "instrument_token": 472789,
    },
    {
        "category": "commodity_option",
        "symbol": "CRUDEOIL 17 MAR 2350 PUT",
        "exchange_segment": "MCX_FO",
        "order_type": "LIMIT",
        "product_type": "NORMAL",
        "quantity": 1,
        "side": "BUY",
        "limit_price": 150.0,
        "instrument_token": 562547,
    },
]


def classify(code: int) -> str:
    if code in (200, 201):
        return "PASS"
    if code in (400, 403, 422, 503):
        return "WARN"
    return "FAIL"


def login(role: str) -> str | None:
    creds = USERS[role]
    r = requests.post(f"{API_BASE_URL}/auth/login", json=creds, timeout=20)
    if r.status_code != 200:
        return None
    return r.json().get("access_token")


def post_order(token: str, inst: dict) -> dict:
    body = {
        "symbol": inst["symbol"],
        "exchange_segment": inst["exchange_segment"],
        "quantity": inst["quantity"],
        "side": inst["side"],
        "order_type": inst["order_type"],
        "product_type": inst["product_type"],
    }
    if inst.get("limit_price") is not None:
        body["limit_price"] = inst["limit_price"]

    r = requests.post(
        f"{API_BASE_URL}/trading/orders",
        json=body,
        headers={"X-AUTH": token, "Content-Type": "application/json"},
        timeout=30,
    )
    text = r.text
    try:
        payload = r.json()
    except Exception:
        payload = {"raw": text[:250]}

    return {
        "category": inst["category"],
        "symbol": inst["symbol"],
        "exchange_segment": inst["exchange_segment"],
        "status_code": r.status_code,
        "status": classify(r.status_code),
        "response": payload,
    }


def fetch_common(role: str, token: str) -> dict:
    headers = {"X-AUTH": token}
    out = {}
    for name, path in [
        ("orders", "/trading/orders"),
        ("positions", "/portfolio/positions"),
        ("margin", "/margin/account"),
    ]:
        r = requests.get(f"{API_BASE_URL}{path}", headers=headers, timeout=20)
        try:
            payload = r.json()
        except Exception:
            payload = {"raw": r.text[:250]}
        out[name] = {
            "status_code": r.status_code,
            "status": classify(r.status_code) if r.status_code != 200 else "PASS",
            "response": payload,
        }

    invalid = {
        "symbol": "",
        "exchange_segment": "NSE_FNO",
        "quantity": 0,
        "side": "BUY",
        "order_type": "LIMIT",
        "product_type": "MIS",
        "limit_price": -1,
    }
    r = requests.post(
        f"{API_BASE_URL}/trading/orders",
        json=invalid,
        headers={"X-AUTH": token, "Content-Type": "application/json"},
        timeout=20,
    )
    out["invalid_order"] = {
        "status_code": r.status_code,
        "status": "PASS" if r.status_code in (400, 422, 403) else "FAIL",
        "response": (r.json() if r.text else {}),
    }
    return out


def verify_mock_quotes() -> dict:
    tokens = [i["instrument_token"] for i in INSTRUMENTS]
    r = requests.post(MOCK_QUOTE_URL, json={"security_ids": tokens}, timeout=20)
    data = r.json() if r.text else {}
    quotes = data.get("data", {}).get("quotes", []) if isinstance(data, dict) else []
    return {
        "status_code": r.status_code,
        "tokens_requested": tokens,
        "quotes_returned": len(quotes),
        "sample_quotes": quotes[:5],
        "status": "PASS" if r.status_code == 200 and len(quotes) >= 5 else "FAIL",
    }


def summarize(role_data: dict) -> dict:
    checks = []
    checks.extend(role_data.get("phase_4_orders_by_category", []))
    for k in ("orders", "positions", "margin", "invalid_order"):
        checks.append(role_data["phase_5_common"][k])

    total = len(checks)
    passed = sum(1 for c in checks if c.get("status") == "PASS")
    warned = sum(1 for c in checks if c.get("status") == "WARN")
    failed = sum(1 for c in checks if c.get("status") == "FAIL")
    return {
        "total": total,
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "pass_rate": f"{(passed / total * 100):.1f}%" if total else "0%",
    }


def main() -> None:
    report = {
        "phase": "4-5-E2E-MULTI-CATEGORY-MULTI-ROLE",
        "timestamp": datetime.now().isoformat(),
        "environment": "LOCAL_DOCKER_MOCK_DHAN_FORCE_OPEN",
        "mock_quote_validation": verify_mock_quotes(),
        "instruments_used": INSTRUMENTS,
        "roles": {},
    }

    for role in ("USER", "SUPER_USER"):
        role_result = {"phase_4_orders_by_category": [], "phase_5_common": {}}
        token = login(role)
        if not token:
            role_result["auth"] = {"status": "FAIL", "message": "login failed"}
            report["roles"][role] = role_result
            continue

        role_result["auth"] = {"status": "PASS"}

        for inst in INSTRUMENTS:
            role_result["phase_4_orders_by_category"].append(post_order(token, inst))

        role_result["phase_5_common"] = fetch_common(role, token)
        role_result["summary"] = summarize(role_result)
        report["roles"][role] = role_result

    with open("audit_phase4_5_E2E_MULTI_CATEGORY_MULTI_ROLE_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report.get("mock_quote_validation", {}), indent=2))
    for role, data in report["roles"].items():
        print(role, data.get("summary", {}))
    print("Saved: audit_phase4_5_E2E_MULTI_CATEGORY_MULTI_ROLE_report.json")


if __name__ == "__main__":
    main()
