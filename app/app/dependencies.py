"""
app/dependencies.py
====================
Shared FastAPI dependencies for authentication and authorization.

Usage:
    from app.dependencies import get_current_user, get_admin_user, CurrentUser

    @router.get("/something")
    async def endpoint(user: CurrentUser = Depends(get_current_user)):
        ...
"""
import logging
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.database import get_pool

log = logging.getLogger(__name__)


# ── Shared user model returned by all auth dependencies ──────────────────────

class CurrentUser(BaseModel):
    id:     str
    name:   str
    mobile: str
    role:   str
    theme_mode: Optional[str] = None


# ── Internal: extract raw token string from request headers ──────────────────

async def _resolve_token(
    x_auth:        Optional[str] = Header(None, alias="X-AUTH"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[str]:
    if x_auth:
        return x_auth.strip()
    if authorization:
        return authorization.replace("Bearer ", "").strip()
    return None


# ── Public dependencies ───────────────────────────────────────────────────────

async def get_current_user(
    token: Optional[str] = Depends(_resolve_token),
) -> CurrentUser:
    """
    Validate the session token (X-AUTH or Bearer) and return the logged-in user.
    Raises HTTP 401 if the token is missing, expired, or invalid.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required — provide X-AUTH or Authorization header.",
        )
    pool = get_pool()
    row = await pool.fetchrow(
        """
        SELECT u.id, u.name, u.mobile, u.role, u.theme_mode
        FROM user_sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = $1::uuid
          AND s.expires_at > NOW()
          AND u.is_active = TRUE
        """,
        token,
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid.",
        )
    return CurrentUser(
        id=str(row["id"]),
        name=row["name"],
        mobile=row["mobile"],
        role=row["role"],
        theme_mode=row.get("theme_mode"),
    )


async def get_admin_user(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Require ADMIN or SUPER_ADMIN role. Raises HTTP 403 otherwise."""
    if user.role not in ("ADMIN", "SUPER_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return user


async def get_super_admin_user(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Require SUPER_ADMIN role. Raises HTTP 403 otherwise."""
    if user.role != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super-admin access required.",
        )
    return user
