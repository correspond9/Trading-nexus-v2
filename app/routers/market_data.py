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

    # Primary: index token (instrument_type='INDEX' with symbol exactly matching underlying)
    row = await pool.fetchrow(
        """
        SELECT md.ltp, md.close, md.updated_at
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE im.symbol = $1 AND im.instrument_type = 'INDEX'
        LIMIT 1
        """,
        u,
    )
    if row and row["ltp"] is not None:
        return {
            "symbol": u,
            "ltp": float(row["ltp"]),
            "close": float(row["close"]) if row.get("close") is not None else None,
            "updated_at": row.get("updated_at"),
            "source": "INDEX",
        }

    # Fallback: nearest futures for this underlying
    fut = await pool.fetchrow(
        """
        SELECT md.ltp, md.close, md.updated_at, im.symbol AS fut_symbol
        FROM instrument_master im
        LEFT JOIN market_data md ON md.instrument_token = im.instrument_token
        WHERE im.underlying = $1
          AND im.instrument_type IN ('FUTIDX','FUTSTK','FUTCOM')
        ORDER BY im.expiry_date ASC NULLS LAST
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

    slots = ws_manager.get_status()
    equity_connected = any(s.get("connected") for s in slots)
    return {
        "equity": {
            "status":        "connected" if equity_connected else "disconnected",
            "subscriptions": sum(int(s.get("tokens") or 0) for s in slots),
        },
        "mcx": {
            "status": "connected" if equity_connected else "disconnected",
        },
        "market_session": "unknown",
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
