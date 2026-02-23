"""
app/routers/margin.py
POST /margin/calculate   {user_id, symbol, security_id, exchange_segment,
                          transaction_type, quantity, order_type, product_type, price}
GET  /margin/account?user_id=X
GET  /margin/span-data?symbol=NIFTY   (admin/debug — returns raw SPAN cache entry)

Margin calculation uses real daily NSE SPAN® + Exposure Limit data downloaded
from nsearchives.nseindia.com every morning at 08:45 IST.

Formula:
    Option buyer  → total = premium           (= ltp × quantity)
    Option seller → total = SPAN + Exposure
    Futures       → total = SPAN + Exposure

Where:
    SPAN margin  = priceScan (from SPAN® file) × quantity
    Exposure     = ref_price × quantity × ELM% / 100  (from AEL file)
"""
import logging
from typing import Optional

from fastapi  import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from app.database           import get_pool
from app.dependencies       import CurrentUser, get_current_user
from app.margin.nse_margin_data import (
    calculate_margin as _nse_calculate_margin,
    get_span_data,
    get_store,
    download_and_refresh,
)

log    = logging.getLogger(__name__)
router = APIRouter(prefix="/margin", tags=["Margin"])


def _uid(request: Request, user_id_param, current_user: Optional[CurrentUser] = None) -> str:
    if user_id_param:
        return str(user_id_param)
    hdr = request.headers.get("X-USER")
    if hdr:
        return hdr
    if current_user:
        return str(current_user.id)
    raise HTTPException(status_code=401, detail="Authentication required")


def _detect_instrument(symbol: str, exchange_segment: str) -> tuple[bool, bool, bool]:
    """Detect (is_option, is_futures, is_commodity) from symbol + segment."""
    sym = (symbol or "").upper()
    seg = (exchange_segment or "").upper()

    is_option  = (
        "OPT" in seg
        or sym.endswith("CE")
        or sym.endswith("PE")
        or "CE " in sym
        or "PE " in sym
    )
    is_futures = (
        not is_option
        and ("FUT" in seg or seg in ("NSE_FNO", "BSE_FNO", "MCX_FO", "NSE_COM"))
    )
    is_commodity = "MCX" in seg or "COM" in seg

    return is_option, is_futures, is_commodity


def _extract_underlying(symbol: str) -> str:
    """
    Extract underlying symbol from a full option/futures symbol.
    E.g.  "NIFTY24FEB25000CE" → "NIFTY"
          "BANKNIFTY"         → "BANKNIFTY"
          "RELIANCE"          → "RELIANCE"
    """
    sym = (symbol or "").upper().strip()
    # Strip trailing CE/PE
    for suffix in ("CE", "PE"):
        if sym.endswith(suffix):
            sym = sym[:-2]
            break
    # Strip trailing digit-only expiry/strike (e.g. 24FEB25000 → just letters)
    import re
    # Try to match known index/stock prefixes
    m = re.match(r"^([A-Z&]+)", sym)
    if m:
        return m.group(1)
    return sym


class MarginCalcRequest(BaseModel):
    user_id:          Optional[str]   = None
    symbol:           Optional[str]   = None
    security_id:      Optional[str]   = None
    exchange_segment: Optional[str]   = "NSE_FNO"
    transaction_type: Optional[str]   = "BUY"
    quantity:         Optional[int]   = 1
    order_type:       Optional[str]   = "MARKET"
    product_type:     Optional[str]   = "INTRADAY"
    price:            Optional[float] = 0.0


@router.post("/calculate")
@router.post("/calculate/")
async def calculate_margin_endpoint(body: MarginCalcRequest, request: Request):
    pool  = get_pool()
    price = body.price or 0.0
    sym   = (body.symbol or "").strip()
    seg   = (body.exchange_segment or "NSE_FNO").strip()

    # ── Resolve LTP if price not supplied ────────────────────────────────────
    if price == 0.0 and (body.security_id or sym):
        # IMPORTANT:
        # - The frontend sends `security_id` but it is actually the instrument_token.
        # - instrument_master does NOT have a `security_id` column.
        instrument_token: Optional[int] = None
        if body.security_id is not None:
            sid = str(body.security_id).strip()
            if sid.isdigit():
                instrument_token = int(sid)

        if instrument_token is None and sym:
            instrument_token = await pool.fetchval(
                "SELECT instrument_token FROM instrument_master WHERE symbol=$1 LIMIT 1",
                sym,
            )

        if instrument_token:
            ltp_row = await pool.fetchrow(
                "SELECT ltp FROM market_data WHERE instrument_token=$1",
                instrument_token,
            )
            if ltp_row and ltp_row["ltp"]:
                price = float(ltp_row["ltp"])

    if price == 0.0:
        price = 0.0   # margin will be 0 — caller should supply price

    qty      = int(body.quantity or 1)
    tx_type  = (body.transaction_type or "BUY").upper()

    is_option, is_futures, is_commodity = _detect_instrument(sym, seg)

    # For SPAN lookup, use the underlying symbol (strip expiry/strike)
    underlying = _extract_underlying(sym)

    # ── NSE SPAN + ELM margin calculation ────────────────────────────────────
    breakdown = _nse_calculate_margin(
        symbol=underlying,
        transaction_type=tx_type,
        quantity=qty,
        ltp=price,
        is_option=is_option,
        is_futures=is_futures,
        is_commodity=is_commodity,
    )

    # calculate_margin() can return an error dict (missing keys like span_source)
    # when SPAN/ELM data is unavailable. Never 500 here — the UI treats failures
    # as 0 and should not break the modal.
    required_margin = breakdown.get("total_margin")
    if required_margin is None:
        required_margin = 0.0

    return {
        "data": {
            "required_margin": required_margin,
            "span_margin":     breakdown.get("span_margin"),
            "exposure_margin": breakdown.get("exposure_margin"),
            "premium":         breakdown.get("premium"),
            "elm_pct":         breakdown.get("elm_pct"),
            "price_used":      round(price, 2),
            "quantity":        qty,
            "underlying":      underlying,
            "span_source":     breakdown.get("span_source"),
            "data_as_of":      breakdown.get("data_as_of"),
            "error":           breakdown.get("error"),
        }
    }


@router.get("/account")
@router.get("/account/")
async def margin_account(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    user_id: Optional[str] = Query(None),
):
    uid  = _uid(request, user_id, current_user)
    pool = get_pool()

    row = await pool.fetchrow(
        """
        SELECT
            COALESCE(pa.balance, 0)         AS wallet_balance,
            COALESCE(pa.margin_allotted, 0) AS margin_allotted,
            COALESCE(SUM(
                CASE
                    WHEN (pp.exchange_segment ILIKE '%OPT%' OR pp.symbol ILIKE '%CE' OR pp.symbol ILIKE '%PE')
                        THEN COALESCE(md.ltp, pp.avg_price) * ABS(pp.quantity)
                    WHEN (pp.exchange_segment ILIKE '%FUT%' OR pp.symbol ILIKE '%FUT%')
                        THEN COALESCE(md.ltp, pp.avg_price) * ABS(pp.quantity) * 0.15
                    WHEN UPPER(COALESCE(pp.product_type,'MIS')) IN ('MIS','INTRADAY')
                        THEN COALESCE(md.ltp, pp.avg_price) * ABS(pp.quantity) * 0.20
                    ELSE COALESCE(md.ltp, pp.avg_price) * ABS(pp.quantity) * 1.0
                END
            ) FILTER (WHERE pp.status='OPEN' AND pp.quantity != 0), 0) AS used_margin
        FROM paper_accounts pa
        LEFT JOIN paper_positions pp ON pp.user_id = pa.user_id
        LEFT JOIN market_data md ON md.instrument_token = pp.instrument_token
        WHERE pa.user_id = $1::uuid
        GROUP BY pa.balance, pa.margin_allotted
        """,
        uid,
    )
    if not row:
        # Unknown users: margin is explicitly not allotted
        return {
            "data": {
                "available_margin": 0.0,
                "used_margin": 0.0,
                "total_balance": 0.0,
                "allotted_margin": 0.0,
                "wallet_balance": 0.0,
            }
        }

    wallet_balance  = float(row["wallet_balance"]  or 0)
    margin_allotted = float(row["margin_allotted"] or 0)
    used_margin     = float(row["used_margin"]     or 0)

    # If no explicit margin is allotted, default margin to wallet balance.
    # This matches how most users expect to trade in paper mode.
    effective_allotted = margin_allotted if margin_allotted > 0 else wallet_balance
    available = effective_allotted - used_margin

    return {
        "data": {
            "available_margin": round(available, 2),
            "used_margin":      round(used_margin, 2),
            # Backward compatibility: older UI called this total_balance
            "total_balance":    round(effective_allotted, 2),
            "allotted_margin":  round(effective_allotted, 2),
            "wallet_balance":   round(wallet_balance, 2),
        }
    }


# ── Admin / Debug endpoints ───────────────────────────────────────────────────

@router.get("/span-data")
@router.get("/span-data/")
async def get_span_data_endpoint(symbol: Optional[str] = Query(None)):
    """
    Return the cached SPAN® data for one or all symbols.
    Useful for debugging and verifying the daily download.

    GET /margin/span-data/?symbol=NIFTY   → single symbol
    GET /margin/span-data/                → all symbols (may be large)
    """
    store = get_store()
    if not store.ready:
        return {
            "ready": False,
            "message": "NSE margin data not yet loaded. "
                       "It loads at 08:45 IST and on startup.",
            "as_of": None,
        }

    if symbol:
        sym   = symbol.upper()
        entry = get_span_data(sym)
        if not entry:
            return {
                "ready":   True,
                "symbol":  sym,
                "found":   False,
                "as_of":   store.as_of.isoformat() if store.as_of else None,
            }
        return {
            "ready":      True,
            "symbol":     entry.symbol,
            "found":      True,
            "ref_price":  entry.ref_price,
            "price_scan": entry.price_scan,
            "cvf":        entry.cvf,
            "source":     entry.source,
            "as_of":      store.as_of.isoformat() if store.as_of else None,
        }

    # Return all (summary)
    all_entries = [
        {
            "symbol":     e.symbol,
            "ref_price":  e.ref_price,
            "price_scan": e.price_scan,
            "cvf":        e.cvf,
            "source":     e.source,
        }
        for e in store.span.values()
    ]
    return {
        "ready":        True,
        "count":        len(all_entries),
        "as_of":        store.as_of.isoformat() if store.as_of else None,
        "elm_oth_count": len(store.elm_oth),
        "elm_otm_count": len(store.elm_otm),
        "span":         all_entries,
    }


@router.post("/nse-refresh")
async def trigger_nse_refresh():
    """
    Manually trigger an immediate NSE margin data refresh.
    Normally this runs automatically at 08:45 IST.
    Requires admin privileges (enforced by the caller's auth middleware).
    """
    log.info("Manual NSE margin refresh triggered via API …")
    ok = await download_and_refresh()
    store = get_store()
    return {
        "success":       ok,
        "span_symbols":  len(store.span),
        "elm_oth_syms":  len(store.elm_oth),
        "elm_otm_syms":  len(store.elm_otm),
        "as_of":         store.as_of.isoformat() if store.as_of else None,
    }
