"""
app/routers/market_data.py
============================
REST endpoints for live/cached market data.
GET /market-data/quote?tokens=1234,5678
GET /market-data/snapshot/{token}
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.database                  import get_pool
from app.serializers.market_data   import serialize_tick
from app.market_data.rate_limiter  import market_quote_limiter
from app.market_hours              import (
    get_market_state,
    MarketState,
    is_equity_window_active,
    is_commodity_window_active,
)

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/underlying-ltp/{symbol}")
async def get_underlying_ltp(symbol: str):
    """Return cached underlying LTP for an index/underlying symbol.

    Frontend uses this for centre-strike selection (STRADDLE tab).
    This endpoint is a pure DB read (no Dhan REST call).
    """
    u = (symbol or "").upper().strip()
    if not u:
        raise HTTPException(status_code=400, detail="symbol is required")

    pool = get_pool()

    # Use nearest futures as source for index LTP (INDEX instruments don't exist in Dhan data)
    # Futures track spot indices very closely and are subscribed via Tier-B WebSocket
    fut = await pool.fetchrow(
        """
        SELECT md.ltp, md.close, md.updated_at, im.symbol AS fut_symbol, im.expiry_date
        FROM instrument_master im
        LEFT JOIN market_data md ON md.instrument_token = md.instrument_token
        WHERE im.underlying = $1
          AND im.instrument_type IN ('FUTIDX','FUTSTK','FUTCOM')
          AND im.expiry_date >= CURRENT_DATE
        ORDER BY im.expiry_date ASC
        LIMIT 1
        """,
        u,
    )
    if fut and fut["ltp"] is not None:
        return {
            "symbol": u,
            "ltp": float(fut["ltp"]),
            "close": float(fut["close"]) if fut.get("close") is not None else None,
            "updated_at": fut.get("updated_at"),
            "source": "FUTURES",
            "ref": fut.get("fut_symbol"),
        }

    raise HTTPException(status_code=404, detail=f"No cached LTP found for {u}")


@router.get("/quote")
async def get_quotes(tokens: str = Query(..., description="Comma-separated instrument tokens")):
    """
    Return latest cached tick for requested instrument tokens.
    Data is served from market_data table (written by tick_processor).
    No DhanHQ REST call — pure DB read.
    """
    try:
        token_list = [int(t.strip()) for t in tokens.split(",") if t.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token list")

    if not token_list:
        raise HTTPException(status_code=400, detail="At least one token required")

    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT md.*, im.exchange_segment, im.symbol
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.instrument_token = ANY($1::bigint[])
        """,
        token_list,
    )
    return [
        serialize_tick(
            dict(r),
            segment=r["exchange_segment"],
            symbol=r["symbol"],
        )
        for r in rows
    ]


@router.get("/snapshot/{token}")
async def get_snapshot(token: int):
    """Full snapshot for a single instrument token."""
    pool = get_pool()
    row = await pool.fetchrow(
        """
        SELECT md.*, im.exchange_segment, im.symbol, im.lot_size, im.tick_size
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.instrument_token = $1
        """,
        token,
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Token {token} not found")

    return serialize_tick(
        dict(row),
        segment=row["exchange_segment"],
        symbol=row["symbol"],
    )


@router.get("/stream-status")
async def stream_status():
    """Return WebSocket stream health — used by SystemMonitoring dashboard."""
    from app.market_data.websocket_manager import ws_manager
    pool = get_pool()

    slots = ws_manager.get_status()
    equity_connected = any(s.get("connected") for s in slots)
    equity_state = get_market_state("NSE_FNO").value
    commodity_state = get_market_state("MCX_FO").value
    equity_window_active = is_equity_window_active()
    commodity_window_active = is_commodity_window_active()

    equity_recent_ticks = await pool.fetchval(
        """
        SELECT COUNT(*)
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE im.exchange_segment IN ('NSE_EQ', 'NSE_FNO', 'BSE_EQ', 'BSE_FNO', 'IDX_I')
          AND md.updated_at >= now() - interval '120 seconds'
        """
    )

    mcx_recent_ticks = await pool.fetchval(
        """
        SELECT COUNT(*)
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE im.exchange_segment IN ('MCX_COMM', 'MCX_FO', 'MCX_EQ')
          AND md.updated_at >= now() - interval '180 seconds'
        """
    )

    if not equity_window_active:
        equity_status = "closed"
    elif (equity_recent_ticks or 0) > 0:
        equity_status = "connected"
    elif equity_connected:
        equity_status = "degraded"
    else:
        equity_status = "disconnected"

    if not commodity_window_active:
        mcx_status = "closed"
    elif (mcx_recent_ticks or 0) > 0:
        mcx_status = "connected"
    else:
        mcx_status = "disconnected"

    session_label = "closed"
    if equity_state == MarketState.OPEN.value and commodity_state == MarketState.OPEN.value:
        session_label = "both_open"
    elif equity_state == MarketState.OPEN.value:
        session_label = "equity_open"
    elif commodity_state == MarketState.OPEN.value:
        session_label = "commodity_open"
    elif equity_state == MarketState.PRE_OPEN.value:
        session_label = "equity_pre_open"
    elif commodity_state == MarketState.PRE_OPEN.value:
        session_label = "commodity_pre_open"
    elif equity_state == MarketState.POST_CLOSE.value:
        session_label = "equity_post_close"
    return {
        "equity": {
            "status":        equity_status,
            "subscriptions": sum(int(s.get("tokens") or 0) for s in slots),
            "recent_ticks":  int(equity_recent_ticks or 0),
        },
        "mcx": {
            "status": mcx_status,
            "recent_ticks": int(mcx_recent_ticks or 0),
        },
        "market_session": session_label,
        "exchange_sessions": {
            "equity": equity_state,
            "commodity": commodity_state,
        },
        "windows": {
            "equity_active": equity_window_active,
            "commodity_active": commodity_window_active,
        },
        "slots": slots,
    }


@router.get("/etf-tierb-status")
async def etf_tierb_status():
    """Return ETF Tier-B subscription status."""
    from app.instruments import subscription_manager as sm
    stats = sm.get_stats()
    total = stats.get("total_tokens", 0)
    return {
        "status": "active" if total > 0 else "inactive",
        "subscribed": total,
    }


@router.post("/stream-reconnect")
async def stream_reconnect():
    """Trigger a graceful reconnect of all WebSocket connections."""
    from app.market_data.websocket_manager import ws_manager
    from app.market_data.depth_ws_manager  import depth_ws_manager
    await ws_manager.reconnect_all()
    await depth_ws_manager.reconnect()
    return {"success": True, "message": "WebSocket reconnect triggered."}
