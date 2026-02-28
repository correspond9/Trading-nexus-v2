"""
app/routers/watchlist.py  (v2 — simplified flat API matching frontend)
GET  /watchlist/{user_id}          → [{symbol, token, exchange, ...}]
POST /watchlist/add                → {user_id, token, symbol, exchange}
POST /watchlist/remove             → {user_id, token}
"""
import logging
import uuid
from typing import Optional
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.database import get_pool
from app.dependencies import CurrentUser
import app.instruments.subscription_manager as subscription_manager


log = logging.getLogger(__name__)

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


def _uid(request: Request, user_id_param, current_user: Optional[CurrentUser] = None) -> str:
    if user_id_param:
        return str(user_id_param)
    hdr = request.headers.get("X-USER")
    if hdr:
        return hdr
    if current_user:
        return str(current_user.id)
    raise HTTPException(status_code=401, detail="Authentication required")


def _require_uuid(uid: str) -> str:
    try:
        return str(uuid.UUID(str(uid)))
    except Exception:
        raise HTTPException(status_code=422, detail="user_id must be a UUID")


class AddItemRequest(BaseModel):
    user_id:  Optional[str] = None
    token:    Optional[str] = None       # instrument token (string or int)
    symbol:   Optional[str] = None
    exchange: Optional[str] = None


class RemoveItemRequest(BaseModel):
    user_id: Optional[str] = None
    token:   Optional[str] = None


async def _resolve_token_from_db(pool, token_val: Optional[int], symbol: str) -> Optional[int]:
    if token_val:
        row = await pool.fetchrow(
            """
            SELECT instrument_token
            FROM instrument_master
            WHERE instrument_token = $1
               OR security_id = $1
            LIMIT 1
            """,
            int(token_val),
        )
        if row:
            return int(row["instrument_token"])

    if symbol:
        try:
            row = await pool.fetchrow(
                """
                SELECT instrument_token
                FROM instrument_master
                WHERE upper(symbol) = upper($1)
                   OR upper(COALESCE(trading_symbol, '')) = upper($1)
                   OR upper(COALESCE(display_name, '')) = upper($1)
                   OR upper(COALESCE(underlying, '')) = upper($1)
                   OR symbol ILIKE $2
                   OR COALESCE(trading_symbol, '') ILIKE $2
                   OR COALESCE(display_name, '') ILIKE $2
                   OR COALESCE(underlying, '') ILIKE $2
                ORDER BY
                    CASE
                        WHEN upper(symbol) = upper($1) THEN 0
                        WHEN upper(COALESCE(trading_symbol, '')) = upper($1) THEN 0
                        WHEN upper(COALESCE(display_name, '')) = upper($1) THEN 1
                        WHEN upper(COALESCE(underlying, '')) = upper($1) THEN 1
                        ELSE 2
                    END,
                    instrument_token
                LIMIT 1
                """,
                symbol,
                f"%{symbol}%",
            )
        except Exception:
            # Backward-compatible fallback for schemas without trading_symbol column.
            row = await pool.fetchrow(
                """
                SELECT instrument_token
                FROM instrument_master
                WHERE upper(symbol) = upper($1)
                   OR upper(COALESCE(display_name, '')) = upper($1)
                   OR upper(COALESCE(underlying, '')) = upper($1)
                   OR symbol ILIKE $2
                   OR COALESCE(display_name, '') ILIKE $2
                   OR COALESCE(underlying, '') ILIKE $2
                ORDER BY
                    CASE
                        WHEN upper(symbol) = upper($1) THEN 0
                        WHEN upper(COALESCE(display_name, '')) = upper($1) THEN 1
                        WHEN upper(COALESCE(underlying, '')) = upper($1) THEN 1
                        ELSE 2
                    END,
                    instrument_token
                LIMIT 1
                """,
                symbol,
                f"%{symbol}%",
            )
        if row:
            return int(row["instrument_token"])

    return None


async def _resolve_token_with_csv_fallback(pool, token_val: Optional[int], symbol: str) -> Optional[int]:
    resolved = await _resolve_token_from_db(pool, token_val, symbol)
    if resolved:
        return resolved

    # If not found in DB, refresh instrument_master from local CSV and retry once.
    try:
        from app.instruments.scrip_master import refresh_instruments
        await refresh_instruments(download=False)
    except Exception as exc:
        log.warning("CSV fallback refresh failed while resolving watchlist token: %s", exc)

    return await _resolve_token_from_db(pool, token_val, symbol)


async def _repair_zero_token_rows(pool, watchlist_id: str) -> None:
    rows = await pool.fetch(
        """
        SELECT instrument_token, symbol
        FROM watchlist_items
        WHERE watchlist_id = $1 AND instrument_token = 0
        """,
        watchlist_id,
    )
    if not rows:
        return

    repaired = 0
    for row in rows:
        symbol = (row.get("symbol") or "").strip()
        if not symbol:
            continue
        resolved = await _resolve_token_with_csv_fallback(pool, None, symbol)
        if not resolved:
            continue
        try:
            await pool.execute(
                "DELETE FROM watchlist_items WHERE watchlist_id=$1 AND instrument_token=$2",
                watchlist_id,
                resolved,
            )
            await pool.execute(
                """
                UPDATE watchlist_items
                SET instrument_token = $3
                WHERE watchlist_id = $1 AND instrument_token = 0 AND symbol = $2
                """,
                watchlist_id,
                symbol,
                resolved,
            )
            repaired += 1
        except Exception:
            continue

    if repaired:
        log.info("Repaired %s legacy watchlist rows with token=0 for watchlist %s", repaired, watchlist_id)


# ── Helper functions ──────────────────────────────────────────────────────────

async def _auto_clean_tier_a(pool, watchlist_id: str) -> None:
    """
    Remove Tier-A watchlist items that have NO open position.
    
    Cleanup Schedule:
    - Every day after 4 PM IST (16:00), all Tier-A items without positions are removed
    - This happens automatically when user refreshes watchlist after 4 PM
    - Prevents clutter from expired options and one-time trades
    
    Tier-B items are NEVER removed automatically.
    """
    # Get current time in IST (UTC+5:30)
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    
    # Check if current time is >= 4 PM (16:00) IST
    is_cleanup_time = now_ist.hour >= 16
    
    if is_cleanup_time:
        # Find Tier-A items with no open position
        old_tier_a = await pool.fetch(
            """
            SELECT wi.instrument_token
            FROM watchlist_items wi
            LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
            WHERE wi.watchlist_id = $1
              AND im.tier = 'A'
              AND NOT EXISTS (
                  SELECT 1 FROM paper_positions pp
                  WHERE pp.instrument_token = wi.instrument_token
                  AND pp.quantity != 0
              )
            """,
            watchlist_id,
        )
        
        # Delete them
        if old_tier_a:
            tokens_to_delete = [row["instrument_token"] for row in old_tier_a]
            await pool.execute(
                "DELETE FROM watchlist_items WHERE watchlist_id = $1 AND instrument_token = ANY($2::bigint[])",
                watchlist_id,
                tokens_to_delete,
            )
            log.info(
                f"Auto-cleaned {len(old_tier_a)} Tier-A items (no position) from watchlist {watchlist_id} at {now_ist.strftime('%H:%M')} IST"
            )
    else:
        # Before 4 PM - keep all Tier-A items (even without position)
        log.debug(f"Not cleanup time yet (current IST: {now_ist.strftime('%H:%M')}). Keeping all Tier-A items.")


@router.get("/{user_id}")
async def get_watchlist(user_id: str, request: Request):
    """Return flat list of all watchlist instruments for a user.
    
    Behavior:
    - Tier-B (subscribed) items: Always returned (keep permanently)
    - Tier-A (on-demand) items: 
      a) Returned if they have an open position, OR
      b) Returned if current time is before 4 PM IST, OR
      c) Removed if after 4 PM IST and no open position
    
    Auto-cleaning: 
    - After 4 PM IST daily, all Tier-A items with no position are removed from watchlist
    - This cleanup happens automatically when user refreshes watchlist after 4 PM
    """
    user_id = _require_uuid(user_id)
    pool = get_pool()

    # Find or create a default watchlist for the user
    wl = await pool.fetchrow(
        "SELECT watchlist_id FROM watchlists WHERE user_id=$1 LIMIT 1", user_id
    )

    if not wl:
        # No watchlist yet — return empty list
        return {"data": []}

    await _repair_zero_token_rows(pool, wl["watchlist_id"])

    # IMPORTANT: do not mutate/watchlist-delete on read.
    # Auto-clean should be handled by an explicit scheduler/admin flow, not on page refresh.

    # Fetch watchlist items with tier and position info
    rows = await pool.fetch(
        """
        SELECT wi.instrument_token AS token,
               CASE
                   WHEN im.instrument_type = 'EQUITY'
                        AND im.underlying IS NOT NULL
                        AND im.underlying <> '' THEN im.underlying
                   ELSE COALESCE(wi.symbol, im.symbol)
               END AS symbol,
               COALESCE(im.exchange_segment, 'NSE') AS exchange,
               COALESCE(im.instrument_type, 'EQ') AS instrument_type,
               im.underlying,
               im.expiry_date,
               im.strike_price,
               im.option_type,
               im.tier,
               md.ltp,
               md.close,
               wi.added_at,
               CASE WHEN EXISTS(
                   SELECT 1 FROM paper_positions pp 
                   WHERE pp.instrument_token = wi.instrument_token 
                   AND pp.quantity != 0
               ) THEN true ELSE false END as has_position
        FROM watchlist_items wi
        LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
        LEFT JOIN market_data md ON md.instrument_token = wi.instrument_token
        WHERE wi.watchlist_id = $1
        ORDER BY wi.added_at DESC
        """,
        wl["watchlist_id"],
    )

    result = []
    for r in rows:
        item = dict(r)
        item["id"]    = str(item["token"])
        item["ltp"]   = float(item["ltp"]) if item.get("ltp") else None
        item["close"] = float(item["close"]) if item.get("close") else None
        if item.get("expiry_date"):
            item["expiry_date"] = str(item["expiry_date"])
        item["strike_price"] = float(item["strike_price"]) if item.get("strike_price") is not None else None
        item["tier"] = item.get("tier") or "B"
        item["added_at"] = item["added_at"].isoformat() if item.get("added_at") else None
        item["has_position"] = bool(item.get("has_position"))
        result.append(item)

    return {"data": result}


@router.post("/add")
async def add_to_watchlist(
    body: AddItemRequest,
    request: Request,
):
    uid  = _require_uuid(_uid(request, body.user_id))
    pool = get_pool()

    token_val = int(body.token) if body.token and str(body.token).isdigit() else None
    symbol    = (body.symbol or "").strip()
    exchange  = (body.exchange or "NSE").strip().upper()

    token_val = await _resolve_token_with_csv_fallback(pool, token_val, symbol)
    if not token_val:
        # Keep API non-breaking; report unresolved but avoid inserting token=0.
        return {"success": False, "token": None, "symbol": symbol, "detail": "Instrument not found in instrument_master/CSV"}

    # Ensure user has a watchlist
    wl = await pool.fetchrow(
        "SELECT watchlist_id FROM watchlists WHERE user_id=$1 LIMIT 1", uid
    )
    if not wl:
        wl = await pool.fetchrow(
            "INSERT INTO watchlists (user_id, name) VALUES ($1, 'Watchlist 1') RETURNING watchlist_id",
            uid,
        )

    wl_id = wl["watchlist_id"]

    await pool.execute(
        """
        INSERT INTO watchlist_items (watchlist_id, instrument_token, symbol)
        VALUES ($1, $2, $3)
        ON CONFLICT (watchlist_id, instrument_token) DO NOTHING
        """,
        wl_id, token_val, symbol,
    )

    # Subscribe Tier-A if applicable
    if token_val:
        try:
            await subscription_manager.subscribe_tier_a(token_val)
        except Exception:
            pass

    return {"success": True, "token": token_val, "symbol": symbol}


@router.post("/remove")
async def remove_from_watchlist(
    body: RemoveItemRequest,
    request: Request,
):
    uid  = _require_uuid(_uid(request, body.user_id))
    pool = get_pool()

    token_val = int(body.token) if body.token and str(body.token).isdigit() else None

    wl = await pool.fetchrow(
        "SELECT watchlist_id FROM watchlists WHERE user_id=$1 LIMIT 1", uid
    )
    if not wl:
        return {"success": True}

    await pool.execute(
        "DELETE FROM watchlist_items WHERE watchlist_id=$1 AND instrument_token=$2",
        wl["watchlist_id"], token_val or 0,
    )

    if token_val:
        try:
            await subscription_manager.unsubscribe_tier_a(token_val)
        except Exception:
            pass

    return {"success": True}
