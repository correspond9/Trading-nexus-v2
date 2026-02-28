"""app/routers/ledger.py

Ledger endpoints for wallet statement.

- GET /ledger
  - normal user: sees own ledger
  - admin: may pass ?user_id=<uuid> to see any user's ledger
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database import get_pool
from app.dependencies import CurrentUser, get_current_user

log = logging.getLogger(__name__)

router = APIRouter(prefix="/ledger", tags=["Ledger"])


@router.get("")
async def get_ledger(
    current_user: CurrentUser = Depends(get_current_user),
    user_id: Optional[str] = Query(None, description="Admin override: target user UUID"),
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    """
    Returns unified wallet and P&L statement.
    - Wallet entries: deposits, withdrawals, fees
    - P&L entries: realized gains/losses from closed positions (created by charge scheduler)
    """
    pool = get_pool()

    target_user_id = user_id or current_user.id
    if user_id and user_id != current_user.id and current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        raise HTTPException(status_code=403, detail="Admin access required for other users' ledgers.")

    rows = await pool.fetch(
        """
        SELECT created_at, description, debit, credit, balance_after
        FROM ledger_entries
        WHERE user_id = $1::uuid
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
        """,
        target_user_id,
        limit,
        offset,
    )

    data = []
    for r in rows:
        created_at = r["created_at"]
        debit = r["debit"]
        credit = r["credit"]
        bal = r["balance_after"]

        # Determine type based on description containing "Realized P&L"
        entry_type = "trade_pnl" if "Realized P&L" in r["description"] else "wallet"

        data.append({
            "date": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
            "type": entry_type,
            "description": r["description"],
            "debit": float(debit) if debit is not None else None,
            "credit": float(credit) if credit is not None else None,
            "balance": float(bal) if bal is not None else 0.0,
        })

    return {"data": data}
