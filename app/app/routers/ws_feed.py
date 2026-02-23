"""
app/routers/ws_feed.py
========================
WebSocket endpoint for real-time tick streaming to the frontend.
Clients subscribe / unsubscribe by sending JSON messages.

Connection flow:
  1. GET /ws/feed  ΓåÆ upgrade to WS
  2. Client sends: {"action": "subscribe",   "tokens": [123, 456]}
  3. Client sends: {"action": "unsubscribe", "tokens": [123]}
  4. Server pushes: {"type": "tick", "data": <serialize_tick output>}
  5. Server pushes: {"type": "pong"} in response to {"action": "ping"}
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.websocket_push import ws_push
import app.instruments.subscription_manager as subscription_manager
from app.database           import get_pool
from app.serializers.market_data import serialize_tick
from app.market_hours import is_market_open

router = APIRouter(prefix="/ws", tags=["WebSocket Feed"])
log    = logging.getLogger(__name__)

DEFAULT_USER_ID = "default"   # TODO: replace with auth guard


@router.websocket("/prices")
async def websocket_prices(ws: WebSocket):
    """Broadcast all market prices ΓÇö used by useMarketPulse hook."""
    await ws_push.connect(ws, DEFAULT_USER_ID)
    try:
        while True:
            # Periodically push all cached prices
            await asyncio.sleep(0.5)
            pool = get_pool()

            # Global market_active: treat NSE derivatives session as the primary clock.
            market_active = is_market_open("NSE_FNO")

            # 1) Core keys required by Admin Dashboard cards.
            # Map underlying -> LTP using nearest futures where available.
            core_underlyings = ["NIFTY", "BANKNIFTY", "CRUDEOIL", "RELIANCE"]
            core_rows = await pool.fetch(
                """
                SELECT DISTINCT ON (im.underlying)
                    im.underlying,
                    md.ltp,
                    md.close
                FROM instrument_master im
                JOIN market_data md ON md.instrument_token = im.instrument_token
                WHERE im.underlying = ANY($1::text[])
                  AND im.instrument_type = ANY($2::text[])
                  AND (md.ltp IS NOT NULL OR md.close IS NOT NULL)
                ORDER BY
                    im.underlying,
                    (im.expiry_date >= CURRENT_DATE) DESC,
                    im.expiry_date NULLS LAST,
                    md.updated_at DESC
                """,
                core_underlyings,
                ["FUTIDX", "FUTSTK", "FUTCOM"],
            )
            prices: dict[str, float] = {}
            for r in core_rows:
                val = r["ltp"] if r["ltp"] is not None else r["close"]
                if val is not None:
                    prices[r["underlying"]] = float(val)

            # 2) Also publish tokenΓåÆltp and symbolΓåÆltp for Watchlist/other pages.
            # Always include watchlist tokens first so the Watchlist UI can
            # reliably show prices (even if market_data is huge).
            wl_tokens = await pool.fetch(
                "SELECT DISTINCT instrument_token FROM watchlist_items WHERE instrument_token IS NOT NULL"
            )
            wl_ids = [int(r["instrument_token"]) for r in wl_tokens if r.get("instrument_token")]
            if wl_ids:
                wl_rows = await pool.fetch(
                    """
                    SELECT md.instrument_token, md.ltp, md.close, im.symbol
                    FROM market_data md
                    LEFT JOIN instrument_master im ON im.instrument_token = md.instrument_token
                    WHERE md.instrument_token = ANY($1::bigint[])
                    """,
                    wl_ids,
                )
                for r in wl_rows:
                    val = r["ltp"] if r["ltp"] is not None else r["close"]
                    if val is None:
                        continue
                    prices[str(r["instrument_token"])] = float(val)
                    if r["symbol"]:
                        prices[r["symbol"]] = float(val)

            # Then add a capped global snapshot for other pages.
            rows = await pool.fetch(
                """
                SELECT instrument_token, ltp, close, symbol
                FROM market_data
                WHERE ltp IS NOT NULL OR close IS NOT NULL
                ORDER BY updated_at DESC
                LIMIT 2000
                """
            )
            for r in rows:
                val = r["ltp"] if r["ltp"] is not None else r["close"]
                if val is None:
                    continue
                prices.setdefault(str(r["instrument_token"]), float(val))
                if r["symbol"]:
                    prices.setdefault(r["symbol"], float(val))

            payload = {
                "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                "status": "active",
                "market_active": market_active,
                "prices": prices,
            }
            await ws.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        await ws_push.disconnect(ws, DEFAULT_USER_ID)
    except Exception:
        await ws_push.disconnect(ws, DEFAULT_USER_ID)


@router.websocket("/feed")
async def websocket_feed(ws: WebSocket):
    await ws_push.connect(ws, DEFAULT_USER_ID)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
                continue

            action = msg.get("action")

            if action == "subscribe":
                tokens = [int(t) for t in msg.get("tokens", [])]
                if not tokens:
                    continue
                # Request Tier-A subscriptions for any that aren't already live
                for token in tokens:
                    await subscription_manager.subscribe_tier_a(token)
                await ws_push.subscribe(ws, tokens)
                # Send immediate snapshot for all requested tokens
                pool     = get_pool()
                rows     = await pool.fetch(
                    """
                    SELECT md.*, im.exchange_segment, im.trading_symbol
                    FROM market_data md
                    JOIN instrument_master im ON im.instrument_token = md.instrument_token
                    WHERE md.instrument_token = ANY($1::bigint[])
                    """,
                    tokens,
                )
                snapshots = [
                    serialize_tick(dict(r), r["exchange_segment"], r["symbol"])
                    for r in rows
                ]
                await ws.send_text(json.dumps({"type": "snapshot", "data": snapshots}))

            elif action == "unsubscribe":
                tokens = [int(t) for t in msg.get("tokens", [])]
                await ws_push.unsubscribe(ws, tokens)

            elif action == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))

            else:
                await ws.send_text(json.dumps({"type": "error", "message": f"Unknown action: {action}"}))

    except WebSocketDisconnect:
        pass
    finally:
        await ws_push.disconnect(ws, DEFAULT_USER_ID)
