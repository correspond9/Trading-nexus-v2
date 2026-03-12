"""
app/routers/auth.py
POST /auth/login                    {mobile, password}                    → {access_token, token_type, user}
POST /auth/logout                   {token}                              → {success}
GET  /auth/me                                                            → user from X-AUTH header
POST /auth/portal/signup            {name, email, experience_level}      → {success, message, user_id}
GET  /auth/portal/users             (admin only)                         → {users: [...], total: int}
POST /auth/portal/users/delete      (admin only)                         → bulk delete by user_ids
"""
import logging
from typing import Optional, List
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
    mobile: str
    city: str
    experience_level: str
    interest: str
    learning_goal: str


class PortalUsersBulkDeleteRequest(BaseModel):
    user_ids: List[str]


@router.post("/login")
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
async def logout(body: LogoutRequest, request: Request):
    token = body.token or request.headers.get("X-AUTH")
    if not token:
        return {"success": True}
    pool = get_pool()
    await pool.execute("DELETE FROM user_sessions WHERE token=$1::uuid", token)
    return {"success": True}


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)):
    return {
        "id":     user.id,
        "name":   user.name,
        "mobile": user.mobile,
        "role":   user.role,
    }


@router.post("/portal/signup")
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
            INSERT INTO portal_users (name, email, mobile, city, experience_level, interest, learning_goal)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, name, email, mobile, city, experience_level, interest, learning_goal, created_at
            """,
            name, email, body.mobile, body.city, experience_level, body.interest, body.learning_goal
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


@router.get("/portal/users")
async def get_portal_users(user: CurrentUser = Depends(get_current_user)):
    """
    Retrieve all portal signup registrations.
    
    Admin only - requires SUPER_ADMIN role.
    
    Returns:
    - users: List of portal users with id, name, email, experience_level, created_at
    - total: Total count of registrations
    """
    # Verify super admin role
    if user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only super admins can view portal users")
    
    pool = get_pool()
    
    try:
        # Fetch all portal users ordered by creation date (newest first)
        users = await pool.fetch(
            """
            SELECT 
                id, 
                name, 
                email,
                mobile,
                city, 
                experience_level,
                interest,
                learning_goal, 
                created_at,
                updated_at
            FROM portal_users
            ORDER BY created_at DESC
            """
        )
        
        # Get total count
        count_result = await pool.fetchval(
            "SELECT COUNT(*) FROM portal_users"
        )
        
        # Convert to dict format for JSON response
        users_list = [
            {
                "id": str(u["id"]),
                "name": u["name"],
                "email": u["email"],
                "mobile": u["mobile"],
                "city": u["city"],
                "experience_level": u["experience_level"],
                "interest": u["interest"],
                "learning_goal": u["learning_goal"],
                "created_at": u["created_at"].isoformat() if u["created_at"] else None,
                "updated_at": u["updated_at"].isoformat() if u["updated_at"] else None,
            }
            for u in users
        ]
        
        log.info(f"Portal users retrieved by {user.mobile}: {count_result} total")
        
        return {
            "users": users_list,
            "total": count_result,
        }
    
    except Exception as e:
        log.error(f"Error fetching portal users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portal users")


@router.post("/portal/users/delete")
async def delete_portal_users(
    body: PortalUsersBulkDeleteRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Bulk delete portal signup registrations.

    Super admin only.
    """
    if user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only super admins can delete portal users")

    user_ids = [str(uid).strip() for uid in (body.user_ids or []) if str(uid).strip()]
    if not user_ids:
        raise HTTPException(status_code=400, detail="No portal user IDs provided")

    pool = get_pool()

    try:
        deleted_count = await pool.fetchval(
            """
            WITH deleted AS (
                DELETE FROM portal_users
                WHERE id = ANY($1::uuid[])
                RETURNING id
            )
            SELECT COUNT(*)::int FROM deleted
            """,
            user_ids,
        )

        return {
            "success": True,
            "deleted": int(deleted_count or 0),
            "requested": len(user_ids),
            "message": f"Deleted {int(deleted_count or 0)} portal signup(s)",
        }

    except HTTPException:
        raise
    except Exception as e:
        # Most common error case here is invalid UUID in user_ids.
        msg = str(e).lower()
        if "uuid" in msg or "invalid input syntax" in msg:
            raise HTTPException(status_code=400, detail="One or more portal user IDs are invalid")

        log.error(f"Error deleting portal users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete portal users")
