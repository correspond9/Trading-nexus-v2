"""
app/routers/auth.py
POST /auth/login  {mobile, password} ΓåÆ {access_token, token_type, user}
POST /auth/logout {token}            ΓåÆ {success}
GET  /auth/me                        ΓåÆ user from X-AUTH header
"""
import logging
from typing import Optional

import bcrypt
from fastapi  import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.database      import get_pool
from app.dependencies  import CurrentUser, get_current_user

log    = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])


def _hash(pw: str) -> str:
    """Hash a plain-text password with bcrypt. Returns a UTF-8 string."""
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def _check(pw: str, stored_hash: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(pw.encode(), stored_hash.encode())
    except Exception:
        return False


class LoginRequest(BaseModel):
    mobile:   str
    password: str


class LogoutRequest(BaseModel):
    token: Optional[str] = None


@router.post("/login")
@router.post("/login/")
async def login(body: LoginRequest):
    pool = get_pool()

    user = await pool.fetchrow(
        "SELECT * FROM users WHERE mobile=$1 AND is_active=true", body.mobile
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not _check(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session = await pool.fetchrow(
        """
        INSERT INTO user_sessions (user_id, expires_at)
        VALUES ($1, NOW() + INTERVAL '30 days')
        RETURNING token
        """,
        user["id"],
    )
    access_token = str(session["token"])

    return {
        "access_token": access_token,
        "token_type":   "bearer",
        "user": {
            "id":     str(user["id"]),
            "name":   user["name"],
            "mobile": user["mobile"],
            "role":   user["role"],
            "theme_mode": user.get("theme_mode"),
        },
    }


@router.post("/logout")
@router.post("/logout/")
async def logout(body: LogoutRequest, request: Request):
    token = body.token or request.headers.get("X-AUTH")
    if not token:
        return {"success": True}
    pool = get_pool()
    await pool.execute("DELETE FROM user_sessions WHERE token=$1::uuid", token)
    return {"success": True}


@router.get("/me")
@router.get("/me/")
async def me(user: CurrentUser = Depends(get_current_user)):
    return {
        "id":     user.id,
        "name":   user.name,
        "mobile": user.mobile,
        "role":   user.role,
        "theme_mode": user.theme_mode,
    }
