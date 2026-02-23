"""
app/routers/theme.py
Theme endpoints for admin-defined neumorphic theme presets and per-user preference.
"""
import json
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.database import get_pool
from app.dependencies import CurrentUser, get_admin_user, get_current_user

router = APIRouter(prefix="/theme", tags=["Theme"])


class ThemeModeUpdate(BaseModel):
    theme_mode: str


class ThemePresetUpdate(BaseModel):
    preset_name: str
    mode: str
    config: Dict[str, Any]
    is_default: bool = False


def _validate_mode(mode: str) -> str:
    norm = (mode or "").strip().lower()
    if norm not in {"light", "dark"}:
        raise HTTPException(status_code=400, detail="theme_mode must be 'light' or 'dark'.")
    return norm


@router.get("/definitions")
async def get_theme_definitions():
    """Get all theme presets"""
    pool = get_pool()
    rows = await pool.fetch(
        "SELECT preset_name, mode, config, is_default FROM ui_theme_definitions ORDER BY preset_name"
    )
    presets = [
        {
            "preset_name": row["preset_name"],
            "mode": row["mode"],
            "config": row["config"],
            "is_default": row["is_default"]
        }
        for row in rows
    ]
    return {"presets": presets}


@router.get("/me")
async def get_my_theme(user: CurrentUser = Depends(get_current_user)):
    pool = get_pool()
    row = await pool.fetchrow("SELECT theme_mode FROM users WHERE id=$1::uuid", user.id)
    return {"theme_mode": row["theme_mode"] if row else "dark"}


@router.put("/me")
async def update_my_theme(
    body: ThemeModeUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    mode = _validate_mode(body.theme_mode)
    pool = get_pool()
    await pool.execute("UPDATE users SET theme_mode=$1 WHERE id=$2::uuid", mode, user.id)
    return {"success": True, "theme_mode": mode}


@router.get("/definitions/admin")
async def get_theme_definitions_admin(
    _: CurrentUser = Depends(get_admin_user),
):
    """Admin endpoint to get all theme presets"""
    return await get_theme_definitions()


@router.put("/definitions")
async def update_theme_definitions(
    body: List[ThemePresetUpdate],
    _: CurrentUser = Depends(get_admin_user),
):
    """Admin endpoint to update multiple theme presets"""
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            for preset in body:
                await conn.execute(
                    """
                    INSERT INTO ui_theme_definitions (preset_name, mode, config, is_default) 
                    VALUES ($1, $2, $3::jsonb, $4)
                    ON CONFLICT (preset_name) DO UPDATE SET 
                        mode = EXCLUDED.mode,
                        config = EXCLUDED.config,
                        is_default = EXCLUDED.is_default
                    """,
                    preset.preset_name,
                    preset.mode,
                    json.dumps(preset.config),
                    preset.is_default,
                )

    return {"success": True}
