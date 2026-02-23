"""
app/execution_simulator/fill_engine.py
========================================
Walks the bid/ask ladder consuming available liquidity level by level.
Produces one FillEvent per price level hit ΓÇö natural partial fills.
BUY  ΓåÆ consumes ask ladder from best ask upward
SELL ΓåÆ consumes bid ladder from best bid downward
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from .slippage_model import calculate_slippage


@dataclass
class FillEvent:
    fill_price:    Decimal
    fill_qty:      int
    remaining_qty: int
    slippage:      Decimal
    timestamp:     Optional[object]   # datetime from exchange ltt


def execute_market_fill(
    order,                  # duck typing: .side, .quantity, .exchange_segment
    market_snap: dict,
    tick_size: Decimal,
    lot_size: int = 1,
) -> list[FillEvent]:
    """
    Walk the order book ladder. Returns a list of FillEvents.
    The list may contain one event (full fill) or many (partial fills).
    Every fill quantity is a whole-lot multiple ΓÇö any leftover below one lot
    at a given depth level is deferred to the next level.
    If fills[-1].remaining_qty > 0, the order was not fully satisfied
    by the available depth.
    """
    depth_key = "ask_depth" if order.side == "BUY" else "bid_depth"
    depth     = market_snap.get(depth_key) or []
    remaining = getattr(order, "remaining_qty", order.quantity)
    fills: list[FillEvent] = []
    _lot = max(lot_size, 1)   # guard against 0

    for level in depth:
        if remaining <= 0:
            break
        available   = level.get("qty", 0)
        if available <= 0:
            continue
        # Raw fill capped by both remaining and available depth
        raw_fill    = min(remaining, available)
        # Floor to the nearest whole-lot boundary
        filled_here = (raw_fill // _lot) * _lot
        if filled_here <= 0:
            # Can't fill even one lot at this level ΓÇö skip
            continue

        slippage = calculate_slippage(
            order.exchange_segment, filled_here, available, tick_size
        )
        fill_px = Decimal(str(level["price"]))
        # BUY: higher price (adverse), SELL: lower price (adverse)
        fill_px = fill_px + slippage if order.side == "BUY" else fill_px - slippage

        fills.append(FillEvent(
            fill_price    = fill_px.quantize(tick_size),
            fill_qty      = filled_here,
            remaining_qty = remaining - filled_here,
            slippage      = slippage,
            timestamp     = market_snap.get("ltt"),
        ))
        remaining -= filled_here

    if not fills:
        # No depth at all ΓÇö return a zero-qty event so caller knows
        fills.append(FillEvent(
            fill_price=Decimal("0"),
            fill_qty=0,
            remaining_qty=remaining,
            slippage=Decimal("0"),
            timestamp=market_snap.get("ltt"),
        ))

    return fills
