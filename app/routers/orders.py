"""
app/routers/orders.py  (v2 — frontend-compatible prefix + API shape)
"""
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from pydantic import BaseModel, validator

from app.database                              import get_pool
from app.dependencies                          import CurrentUser, get_current_user
from app.execution_simulator.execution_engine import is_mock_mode
from app.margin.nse_margin_data               import calculate_margin as _nse_calculate_margin
from app.market_hours                          import is_market_open, get_market_state

log = logging.getLogger(__name__)

router = APIRouter(prefix="/trading/orders", tags=["Orders"])


def _detect_instrument(
    symbol: str,
    exchange_segment: str,
    instrument_type: Optional[str] = None,
    option_type: Optional[str] = None,
) -> tuple[bool, bool, bool]:
    """Detect (is_option, is_futures, is_commodity) from symbol + segment + metadata."""
    sym = (symbol or "").upper()
    seg = (exchange_segment or "").upper()
    inst = (instrument_type or "").upper()
    opt = (option_type or "").upper()

    is_option = False
    if opt in {"CE", "PE"}:
        is_option = True
    elif inst.startswith("OPT"):
        is_option = True
    elif "OPT" in seg:
        is_option = True
    else:
        if sym.endswith(("CE", "PE", "CALL", "PUT")):
            is_option = True
        elif " CE " in sym or " PE " in sym or " CALL " in sym or " PUT " in sym:
            is_option = True
        else:
            parts = sym.replace("-", " ").replace("/", " ").split()
            if parts and parts[-1] in {"CE", "PE", "CALL", "PUT"}:
                is_option = True

    is_commodity = (
        "MCX" in seg
        or "COM" in seg
        or inst.endswith("COM")
        or inst.startswith("FUTCOM")
        or inst.startswith("OPTFUT")
    )
    is_futures = (
        not is_option
        and (
            inst.startswith("FUT")
            or "FUT" in seg
            or seg in ("NSE_FNO", "BSE_FNO", "MCX_FO", "NSE_COM")
        )
    )

    return is_option, is_futures, is_commodity


def _extract_underlying(symbol: str) -> str:
    """
    Extract underlying symbol from a full option/futures symbol.
    E.g.  "NIFTY24FEB25000CE" → "NIFTY"
          "BANKNIFTY"         → "BANKNIFTY"
          "RELIANCE"          → "RELIANCE"
    """
    import re
    sym = (symbol or "").upper().strip()
    # Strip trailing CE/PE
    for suffix in ("CE", "PE"):
        if sym.endswith(suffix):
            sym = sym[:-2]
            break
    # Try to match known index/stock prefixes
    m = re.match(r"^([A-Z&]+)", sym)
    if m:
        return m.group(1)
    return sym


def _calculate_required_margin(
    price: float, 
    qty: int, 
    exchange_segment: str, 
    product_type: str, 
    symbol: str,
    transaction_type: str = "BUY",
    instrument_type: Optional[str] = None,
    option_type: Optional[str] = None,
) -> dict:
    """
    Calculate required margin using NSE SPAN + ELM data.
    Returns dict with total_margin and breakdown.
    """
    if qty <= 0:
        return {"total_margin": 0.0, "span_margin": 0.0, "exposure_margin": 0.0, "premium": 0.0}
    
    is_option, is_futures, is_commodity = _detect_instrument(
        symbol,
        exchange_segment,
        instrument_type=instrument_type,
        option_type=option_type,
    )
    is_equity = not is_option and not is_futures and not is_commodity
    underlying = _extract_underlying(symbol)

    # Cash equity margin: qty × price
    if is_equity:
        cash = round(float(price or 0) * int(qty), 2)
        return {
            "total_margin": cash,
            "span_margin": 0.0,
            "exposure_margin": 0.0,
            "premium": cash,
        }

    # Option BUY margin: premium only
    if is_option and transaction_type.upper() == "BUY":
        premium = round(float(price or 0) * int(qty), 2)
        return {
            "total_margin": premium,
            "span_margin": 0.0,
            "exposure_margin": 0.0,
            "premium": premium,
        }

    breakdown = _nse_calculate_margin(
        symbol=underlying,
        transaction_type=transaction_type,
        quantity=int(qty),
        ltp=float(price or 0),
        is_option=is_option,
        is_futures=is_futures,
        is_commodity=is_commodity,
    )

    return breakdown


def _uid(request: Request, user_id_param) -> str:
    if user_id_param:
        return str(user_id_param)
    hdr = request.headers.get("X-USER")
    return hdr if hdr else "default"


class PlaceOrderRequest(BaseModel):
    user_id:          Optional[str]   = None
    symbol:           Optional[str]   = None
    security_id:      Optional[int]   = None
    instrument_token: Optional[int]   = None
    exchange_segment: Optional[str]   = None
    transaction_type: Optional[str]   = None
    side:             Optional[str]   = None
    quantity:         int             = 1
    order_type:       str             = "MARKET"
    product_type:     str             = "MIS"
    price:            Optional[float] = None
    limit_price:      Optional[float] = None
    trigger_price:    Optional[float] = None
    is_super:         bool            = False
    target_price:     Optional[float] = None
    stop_loss_price:  Optional[float] = None
    trailing_jump:    Optional[float] = None

    @validator('symbol', 'exchange_segment', pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return ""
        return str(v).strip()

    @validator('security_id', 'instrument_token', pre=True)
    def empty_int_to_none(cls, v):
        if v == "" or v is None:
            return None
        return int(v)

    @validator('quantity', pre=True)
    def coerce_quantity(cls, v):
        if v is None or v == "":
            return 1
        return int(v)

    @validator('is_super', pre=True)
    def coerce_bool(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return bool(v)


@router.post("", status_code=status.HTTP_201_CREATED)
async def place_paper_order(
    body: PlaceOrderRequest,
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
):
    # Authorization: Only ADMIN/SUPER_ADMIN can place orders for other users
    if body.user_id and str(body.user_id) != str(current_user.id):
        if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
            raise HTTPException(
                status_code=403,
                detail="You can only place orders for yourself. Admin access required to place orders for other users."
            )
    
    user_id   = body.user_id or current_user.id
    pool      = get_pool()
    
    log.info(f"Order placement attempt - User: {current_user.id} (role: {current_user.role}), Target: {user_id}, Symbol: {body.symbol}, Side: {body.side or body.transaction_type}")

    # ── User status enforcement ────────────────────────────────────────────
    try:
        uuid.UUID(str(user_id))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    try:
        _status_row = await pool.fetchrow(
            "SELECT status FROM users WHERE id=$1::uuid", user_id
        )
    except Exception as exc:
        log.warning("User status check skipped: %s", exc)
        _status_row = None

    if _status_row:
        _us = _status_row["status"]
        if _us == "BLOCKED":
            raise HTTPException(
                status_code=403,
                detail="Your account is blocked. You can only submit payout requests.",
            )
        if _us == "SUSPENDED":
            raise HTTPException(
                status_code=403,
                detail="Your account is suspended. You can only exit existing positions.",
            )
        if _us == "PENDING":
            raise HTTPException(
                status_code=403,
                detail="Your account is pending activation. Please contact your admin.",
            )
    token     = body.security_id or body.instrument_token

    if not token:
        if body.symbol and body.symbol.strip():
            row = await pool.fetchrow(
                "SELECT instrument_token FROM instrument_master WHERE symbol ILIKE $1 OR underlying ILIKE $1 LIMIT 1",
                body.symbol.strip(),
            )
            token = row["instrument_token"] if row else 0
        else:
            log.error(f"Order placement failed: No instrument identifier provided (no token and no symbol)")
            raise HTTPException(
                status_code=400,
                detail="Either security_id/instrument_token or symbol must be provided"
            )

    # ── Normalize/repair exchange_segment from instrument_master (robustness) ──
    # Look up exchange_segment from instrument_master if not provided
    seg_in = (body.exchange_segment or "").strip().upper()
    inst_type = None
    opt_type = None
    if token:
        im_seg_row = await pool.fetchrow(
            """
            SELECT exchange_segment, instrument_type, option_type
            FROM instrument_master
            WHERE instrument_token=$1
            """,
            int(token),
        )
        im_seg = (im_seg_row["exchange_segment"] if im_seg_row else None) or None
        im_seg_u = str(im_seg).strip().upper() if im_seg else ""
        if im_seg_row:
            inst_type = im_seg_row.get("instrument_type")
            opt_type = im_seg_row.get("option_type")

        # Use database value if not provided or generic exchange name given
        if (not seg_in) or seg_in in {"NSE", "BSE", "MCX"}:
            if im_seg_u:
                body.exchange_segment = im_seg_u

    # Get LTP for fill simulation
    ltp_row = await pool.fetchrow(
        "SELECT ltp FROM market_data WHERE instrument_token=$1", token
    ) if token else None
    fill_price = float(ltp_row["ltp"]) if (ltp_row and ltp_row["ltp"]) \
                 else (body.price or body.limit_price or 100.0)

    side     = (body.transaction_type or body.side or "BUY").upper()
    qty      = body.quantity
    ord_type = body.order_type.upper()
    prod     = body.product_type.upper()
    lp       = body.limit_price or body.price

    order_id = str(uuid.uuid4())

    # ── Market hours validation ────────────────────────────────────────────
    if not is_market_open(body.exchange_segment, body.symbol):
        market_state = get_market_state(body.exchange_segment, body.symbol)
        
        # Log REJECTED order for audit trail
        await pool.execute(
            """
            INSERT INTO paper_orders
                (order_id, user_id, instrument_token, symbol, exchange_segment,
                 side, order_type, quantity, limit_price, fill_price, filled_qty,
                 status, product_type, security_id, placed_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 0, 'REJECTED', $11, $12, NOW())
            """,
            order_id, user_id, token or 0, body.symbol, body.exchange_segment,
            side, ord_type, qty, lp, fill_price, prod, token or 0
        )
        
        raise HTTPException(
            status_code=403,
            detail=f"Market is {market_state.value}. Orders can only be placed during market hours."
        )

    # ── Margin enforcement & Order placement in transaction (prevents race condition) ──
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Lock paper_accounts row to prevent concurrent order race condition
            if side == "BUY":
                margin_breakdown = _calculate_required_margin(
                    fill_price,
                    qty,
                    body.exchange_segment,
                    prod,
                    body.symbol,
                    side,
                    instrument_type=inst_type,
                    option_type=opt_type,
                )
                required = margin_breakdown.get("total_margin")
                if required is None:
                    raise HTTPException(
                        status_code=503,
                        detail=margin_breakdown.get("error")
                        or "Margin data not available for this symbol right now.",
                    )

                # SELECT FOR UPDATE locks the row until transaction commits
                margin_row = await conn.fetchrow(
                    """
                    SELECT
                        COALESCE(pa.margin_allotted, 0) AS margin_allotted,
                        COALESCE(SUM(
                            calculate_position_margin(
                                pp.instrument_token,
                                pp.symbol,
                                pp.exchange_segment,
                                pp.quantity,
                                pp.product_type
                            )
                        ) FILTER (WHERE pp.status='OPEN' AND pp.quantity != 0), 0) AS used_margin
                    FROM paper_accounts pa
                    LEFT JOIN paper_positions pp ON pp.user_id = pa.user_id
                    WHERE pa.user_id = $1::uuid
                    GROUP BY pa.margin_allotted
                    FOR UPDATE OF pa
                    """,
                    user_id,
                )
                if not margin_row:
                    raise HTTPException(status_code=403, detail="No margin account found for this user.")

                allotted = float(margin_row["margin_allotted"] or 0)
                used = float(margin_row["used_margin"] or 0)
                available = allotted - used

                if allotted <= 0:
                    raise HTTPException(status_code=403, detail="No margin allotted. Please contact your admin.")
                if required > available + 1e-6:
                    raise HTTPException(
                        status_code=403,
                        detail=(
                            f"Insufficient margin. Required {required:.2f}, available {available:.2f}."
                        ),
                    )

            # Insert order record
            await conn.execute(
                """
                INSERT INTO paper_orders
                    (order_id, user_id, instrument_token, symbol, exchange_segment,
                     side, order_type, quantity, limit_price, fill_price, filled_qty,
                     status, product_type, security_id,
                     is_super, target_price, stop_loss_price, trailing_jump)
                VALUES
                    ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,'FILLED',$12,$13,$14,$15,$16,$17)
                """,
                order_id, user_id, token or 0, body.symbol, body.exchange_segment,
                side, ord_type, qty, lp, fill_price, qty,
                prod, token or 0,
                body.is_super, body.target_price, body.stop_loss_price, body.trailing_jump,
            )

            # Update or create position (fixed for same-day re-entry)
            if side == "BUY":
                # Check if an OPEN position exists
                open_pos = await conn.fetchrow(
                    """
                    SELECT position_id, quantity, avg_price
                    FROM paper_positions
                    WHERE user_id = $1 AND instrument_token = $2 AND status = 'OPEN'
                    """,
                    user_id, token or 0
                )

                if open_pos:
                    # Update existing OPEN position
                    new_qty = open_pos["quantity"] + qty
                    new_avg = (
                        (open_pos["avg_price"] * open_pos["quantity"] + fill_price * qty) / new_qty
                    )
                    await conn.execute(
                        """
                        UPDATE paper_positions
                        SET quantity = $1, avg_price = $2
                        WHERE position_id = $3
                        """,
                        new_qty, new_avg, open_pos["position_id"]
                    )
                else:
                    # Insert new position (allows multiple CLOSED positions for same instrument)
                    await conn.execute(
                        """
                        INSERT INTO paper_positions
                            (user_id, instrument_token, symbol, exchange_segment,
                             quantity, avg_price, product_type, status)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,'OPEN')
                        """,
                        user_id, token or 0, body.symbol, body.exchange_segment,
                        qty, fill_price, prod,
                    )
            else:
                # SELL: reduce or close existing OPEN position
                open_pos = await conn.fetchrow(
                    """
                    SELECT position_id, quantity, avg_price
                    FROM paper_positions
                    WHERE user_id = $1 AND instrument_token = $2 AND status = 'OPEN'
                    """,
                    user_id, token or 0
                )

                if open_pos:
                    new_qty = max(0, open_pos["quantity"] - qty)
                    if new_qty == 0:
                        # Position fully closed
                        realized_pnl = (fill_price - open_pos["avg_price"]) * open_pos["quantity"]
                        await conn.execute(
                            """
                            UPDATE paper_positions
                            SET quantity = 0, status = 'CLOSED', 
                                realized_pnl = $1, closed_at = NOW()
                            WHERE position_id = $2
                            """,
                            realized_pnl, open_pos["position_id"]
                        )
                    else:
                        # Partial close
                        realized_pnl = (fill_price - open_pos["avg_price"]) * qty
                        await conn.execute(
                            """
                            UPDATE paper_positions
                            SET quantity = $1,
                                realized_pnl = COALESCE(realized_pnl, 0) + $2
                            WHERE position_id = $3
                            """,
                            new_qty, realized_pnl, open_pos["position_id"]
                        )
                else:
                    # No open position to close (short selling or error)
                    # Create short position
                    await conn.execute(
                        """
                        INSERT INTO paper_positions
                            (user_id, instrument_token, symbol, exchange_segment,
                             quantity, avg_price, product_type, status)
                        VALUES ($1,$2,$3,$4,$5,$6,$7,'OPEN')
                        """,
                        user_id, token or 0, body.symbol, body.exchange_segment,
                        -qty, fill_price, prod,
                    )

    return {"order_id": order_id, "status": "FILLED",
            "fill_price": fill_price, "filled_qty": qty}


@router.get("")
async def list_orders(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    user_id:              Optional[str]  = Query(None),
    current_session_only: bool           = Query(False),
    status_filter:        Optional[str]  = Query(None),
    from_date:            Optional[str]  = Query(None),
    to_date:              Optional[str]  = Query(None),
):
    """
    List all orders placed during the day.
    Shows pending, executed, rejected, and cancelled orders.
    Admin/Super Admin can see all users' orders; regular users see their own.
    """
    from datetime import datetime
    
    uid   = user_id or current_user.id
    pool  = get_pool()
    
    # Non-admin users can only see their own orders
    if current_user.role not in ("ADMIN", "SUPER_ADMIN") and user_id and str(user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only view your own orders")
    
    q     = "SELECT * FROM paper_orders WHERE user_id=$1 AND archived_at IS NULL"
    args  = [uid]
    
    # Filter by status if provided
    if status_filter:
        q += f" AND status=${len(args)+1}"
        args.append(status_filter.upper())
    
    # Filter by date range if provided
    if from_date:
        q += f" AND DATE(placed_at AT TIME ZONE 'Asia/Kolkata') >= ${len(args)+1}"
        args.append(datetime.strptime(from_date, '%Y-%m-%d').date())
    
    if to_date:
        q += f" AND DATE(placed_at AT TIME ZONE 'Asia/Kolkata') <= ${len(args)+1}"
        args.append(datetime.strptime(to_date, '%Y-%m-%d').date())
    
    # Filter to only current session if requested
    if current_session_only:
        q += " AND placed_at >= CURRENT_DATE"
    
    q += " ORDER BY placed_at DESC LIMIT 500"
    rows = await pool.fetch(q, *args)
    return {"data": [_fmt(r) for r in rows]}


@router.get("/historic/orders")
async def get_historic_orders(
    current_user: CurrentUser = Depends(get_current_user),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    mobile: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
):
    """
    Get historic orders (archived) for admin/super admin.
    Allows filtering by date range and user ID or mobile number.
    
    Only ADMIN and SUPER_ADMIN roles can access this.
    """
    from datetime import datetime
    
    pool = get_pool()
    
    # Check if user is admin
    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=403,
            detail="Only admins can access historic orders."
        )
    
    # Build query
    q = "SELECT o.* FROM paper_orders o LEFT JOIN paper_accounts pa ON o.user_id = pa.user_id WHERE archived_at IS NOT NULL"
    args = []
    
    # Date range filtering (convert strings to date objects)
    if from_date:
        q += f" AND DATE(o.placed_at AT TIME ZONE 'Asia/Kolkata') >= ${len(args)+1}"
        args.append(datetime.strptime(from_date, '%Y-%m-%d').date())
    if to_date:
        q += f" AND DATE(o.placed_at AT TIME ZONE 'Asia/Kolkata') <= ${len(args)+1}"
        args.append(datetime.strptime(to_date, '%Y-%m-%d').date())
    
    # User filtering
    if user_id:
        q += f" AND o.user_id = ${len(args)+1}::uuid"
        args.append(user_id)
    elif mobile:
        q += f" AND pa.mobile = ${len(args)+1}"
        args.append(mobile)
    
    # Status filtering
    if status_filter:
        q += f" AND o.status = ${len(args)+1}"
        args.append(status_filter.upper())
    
    q += " ORDER BY o.placed_at DESC LIMIT 1000"
    
    rows = await pool.fetch(q, *args)
    return {"data": [_fmt(r) for r in rows]}


@router.get("/{order_id}")
async def get_order(
    order_id: str = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    pool = get_pool()
    row  = await pool.fetchrow("SELECT * FROM paper_orders WHERE order_id=$1", order_id)
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Authorization: Users can only view their own orders (except admins)
    if current_user.role not in ("ADMIN", "SUPER_ADMIN") and str(row["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only view your own orders")
    
    return _fmt(row)


@router.delete("/{order_id}")
async def cancel_order(
    order_id: str = Path(...),
    current_user: CurrentUser = Depends(get_current_user),
):
    pool = get_pool()
    
    # First check if order exists and belongs to the user
    row = await pool.fetchrow(
        "SELECT user_id, status FROM paper_orders WHERE order_id=$1",
        order_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Authorization: Users can only cancel their own orders (except admins)
    if current_user.role not in ("ADMIN", "SUPER_ADMIN") and str(row["user_id"]) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only cancel your own orders")
    
    # Check if order can be cancelled
    if row["status"] != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status {row['status']}. Only PENDING orders can be cancelled."
        )
    
    n = await pool.execute(
        "UPDATE paper_orders SET status='CANCELLED' WHERE order_id=$1",
        order_id,
    )
    return {"success": True, "order_id": order_id}


def _fmt(r) -> dict:
    d = dict(r)
    d["id"]               = str(d.get("order_id", ""))
    d["transaction_type"] = d.get("transaction_type") or d.get("side", "")
    d["product_type"]     = d.get("product_type") or "MIS"
    d["security_id"]      = d.get("security_id") or d.get("instrument_token")
    d["price"]            = float(d.get("fill_price") or d.get("limit_price") or 0)
    d["status"]           = d.get("status", "PENDING")
    for k, v in list(d.items()):
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
        elif hasattr(v, "__class__") and v.__class__.__name__ == "Decimal":
            d[k] = float(v)
    return d
