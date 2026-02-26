"""
app/serializers/market_data.py
================================
Transforms raw DB/cache rows into frontend-safe dicts.
Key rules:
  - Strip bid_qty / ask_qty from depth levels (only price pairs to frontend)
  - Add market_state + is_stale fields
  - Add change_pct (vs prev close)
  - Conditionally include OHLC and depth per market state
"""
from decimal import Decimal
from datetime import datetime
from typing import Any
import math
import json

from app.market_hours import get_market_state, is_stale, MarketState


def serialize_tick(row: dict[str, Any], segment: str = "NSE_EQ", symbol: str = "") -> dict:
    """
    Serialize a market_data row (from DB or live tick dict) to a safe dict
    suitable for WebSocket push or REST API response.

    Strips qty from bid/ask depth — only prices are sent to frontend.
    """
    state    = get_market_state(segment, symbol)
    ltp      = row.get("ltp")
    close    = row.get("close")
    updated  = row.get("updated_at")

    change_pct = None
    if ltp is not None and close and close != 0:
        change_pct = round((float(ltp) - float(close)) / float(close) * 100, 2)

    out: dict[str, Any] = {
        "instrument_token": row.get("instrument_token"),
        "ltp":              _f(ltp),
        "close":            _f(close),  # ✅ ALWAYS include close price
        "change_pct":       change_pct,
        "ltt":              _dt(row.get("ltt")),
        "updated_at":       _dt(updated),
        "market_state":     state.value,
        "is_stale":         is_stale(updated, segment),
    }

    # OHLC — only open/high/low during OPEN and POST_CLOSE
    if state in (MarketState.OPEN, MarketState.POST_CLOSE):
        out["open"]  = _f(row.get("open"))
        out["high"]  = _f(row.get("high"))
        out["low"]   = _f(row.get("low"))

    # Depth — only during OPEN
    if state == MarketState.OPEN:
        out["bid_depth"] = _serialise_depth(row.get("bid_depth") or [])
        out["ask_depth"] = _serialise_depth(row.get("ask_depth") or [])

    return out


def serialize_option_row(tick: dict, ocd: dict, segment: str = "NSE_FNO") -> dict:
    """
    Merges market_data tick with option_chain_data Greeks row.
    Frontend option chain table format.
    """
    base = serialize_tick(tick, segment=segment, symbol=tick.get("symbol", ""))
    base.update({
        "strike_price": _f(ocd.get("strike_price")),
        "option_type":  ocd.get("option_type"),
        "iv":           _f(ocd.get("iv")),
        "delta":        _f(ocd.get("delta")),
        "theta":        _f(ocd.get("theta")),
        "gamma":        _f(ocd.get("gamma")),
        "vega":         _f(ocd.get("vega")),
        "greeks_updated_at": _dt(ocd.get("greeks_updated_at")),
    })
    return base


# ── Depth serialiser (strips qty) ─────────────────────────────────────────

def _serialise_depth(depth: list[dict]) -> list[dict]:
    """Drop qty from each level — send price-only pairs to frontend."""
    if depth is None:
        return []

    # asyncpg may return jsonb as a Python object or as a JSON string,
    # depending on codec configuration.
    if isinstance(depth, str):
        try:
            depth = json.loads(depth)
        except Exception:
            return []

    if not isinstance(depth, list):
        return []

    out: list[dict] = []
    for level in depth:
        if not isinstance(level, dict):
            continue
        price = _f(level.get("price"))
        if price is None:
            continue
        out.append({"price": price})
    return out


# ── Formatting helpers ────────────────────────────────────────────────────

def _f(v) -> float | None:
    if v is None:
        return None
    try:
        out = float(v)
        if not math.isfinite(out):
            return None
        return out
    except (TypeError, ValueError):
        return None


def _dt(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)
