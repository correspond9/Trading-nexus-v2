"""
app/routers/auth.py
POST /auth/login                    {mobile, password}                    → {access_token, token_type, user}
POST /auth/logout                   {token}                              → {success}
GET  /auth/me                                                            → user from X-AUTH header
POST /auth/portal/signup            {name, email, experience_level}      → {success, message, user_id}
"""
import logging
from typing import Optional
import re

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


class PortalSignupRequest(BaseModel):
    name: str
    email: str
    experience_level: str


@router.post("/login")
@router.post("/login/")
async def login(body: LoginRequest):
    pool = get_pool()

    user = await pool.fetchrow(
        "SELECT * FROM users WHERE mobile=$1 AND is_active=true", body.mobile
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if user is archived (soft deleted)
    if user.get("is_archived"):
        raise HTTPException(status_code=403, detail="Account has been archived and is unavailable")

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
    }


@router.post("/portal/signup")
@router.post("/portal/signup/")
async def portal_signup(body: PortalSignupRequest):
    """
    Register a new user for the educational portal.
    
    Validates:
    - Email format
    - Required fields (name, email, experience_level)
    - Email uniqueness
    
    Returns:
    - user_id: UUID of the created portal user
    - message: Confirmation message
    """
    pool = get_pool()
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, body.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate required fields
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")
    
    if not body.experience_level or not body.experience_level.strip():
        raise HTTPException(status_code=400, detail="Experience level is required")
    
    # Normalize inputs
    email = body.email.strip().lower()
    name = body.name.strip()
    experience_level = body.experience_level.strip()
    
    try:
        # Check if email already exists
        existing = await pool.fetchrow(
            "SELECT id FROM portal_users WHERE email=$1",
            email
        )
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Email already registered for the educational portal"
            )
        
        # Insert new portal user
        user = await pool.fetchrow(
            """
            INSERT INTO portal_users (name, email, experience_level)
            VALUES ($1, $2, $3)
            RETURNING id, name, email, created_at
            """,
            name, email, experience_level
        )
        
        log.info(f"New portal signup: {email}")
        
        return {
            "success": True,
            "message": f"Welcome {name}! You've been registered for the Trading Nexus educational portal.",
            "user_id": str(user["id"]),
            "email": user["email"],
        }
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Portal signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again later.")
