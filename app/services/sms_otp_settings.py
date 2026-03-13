"""DB-backed SMS OTP settings with env fallbacks."""

from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.database import get_pool

_SMS_OTP_KEY_MAP = {
    "message_central_customer_id": "sms_otp_message_central_customer_id",
    "message_central_password": "sms_otp_message_central_password",
    "otp_expiry_seconds": "sms_otp_expiry_seconds",
    "otp_resend_cooldown_seconds": "sms_otp_resend_cooldown_seconds",
    "otp_max_attempts": "sms_otp_max_attempts",
    "sms_test_live_enabled": "sms_otp_test_live_enabled",
    "email_otp_enabled": "email_otp_enabled",
    "email_otp_service_base_url": "email_otp_service_base_url",
    "email_otp_type": "email_otp_type",
    "email_otp_organization": "email_otp_organization",
    "email_otp_subject": "email_otp_subject",
}


def _to_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _to_int(value: Any, default: int, min_value: int, max_value: int) -> int:
    try:
        parsed = int(str(value).strip())
    except Exception:
        return default
    return max(min_value, min(max_value, parsed))


async def _ensure_system_config_table() -> None:
    pool = get_pool()
    await pool.execute(
        """
        CREATE TABLE IF NOT EXISTS system_config (
            key         VARCHAR(100) PRIMARY KEY,
            value       TEXT,
            updated_at  TIMESTAMPTZ DEFAULT now()
        )
        """
    )


def get_default_sms_otp_settings() -> dict[str, Any]:
    cfg = get_settings()
    return {
        "message_central_customer_id": (cfg.message_central_customer_id or "").strip(),
        "message_central_password": (cfg.message_central_password or "").strip(),
        "otp_expiry_seconds": int(cfg.otp_expiry_seconds),
        "otp_resend_cooldown_seconds": int(cfg.otp_resend_cooldown_seconds),
        "otp_max_attempts": int(cfg.otp_max_attempts),
        "sms_test_live_enabled": bool(cfg.sms_test_live_enabled),
        "email_otp_enabled": bool(getattr(cfg, "email_otp_enabled", False)),
        "email_otp_service_base_url": (getattr(cfg, "email_otp_service_base_url", "") or "").strip(),
        "email_otp_type": (getattr(cfg, "email_otp_type", "numeric") or "numeric").strip().lower(),
        "email_otp_organization": (getattr(cfg, "email_otp_organization", "Trading Nexus") or "Trading Nexus").strip(),
        "email_otp_subject": (getattr(cfg, "email_otp_subject", "Email OTP Verification") or "Email OTP Verification").strip(),
    }


async def get_sms_otp_settings() -> dict[str, Any]:
    defaults = get_default_sms_otp_settings()
    await _ensure_system_config_table()
    pool = get_pool()

    db_keys = list(_SMS_OTP_KEY_MAP.values())
    rows = await pool.fetch(
        "SELECT key, value FROM system_config WHERE key = ANY($1::text[])",
        db_keys,
    )
    db_values = {row["key"]: row["value"] for row in rows}

    settings = dict(defaults)
    customer_id = db_values.get(_SMS_OTP_KEY_MAP["message_central_customer_id"])
    password = db_values.get(_SMS_OTP_KEY_MAP["message_central_password"])

    if customer_id is not None:
        settings["message_central_customer_id"] = str(customer_id).strip()
    if password is not None:
        settings["message_central_password"] = str(password).strip()

    settings["otp_expiry_seconds"] = _to_int(
        db_values.get(_SMS_OTP_KEY_MAP["otp_expiry_seconds"]),
        defaults["otp_expiry_seconds"],
        30,
        600,
    )
    settings["otp_resend_cooldown_seconds"] = _to_int(
        db_values.get(_SMS_OTP_KEY_MAP["otp_resend_cooldown_seconds"]),
        defaults["otp_resend_cooldown_seconds"],
        0,
        600,
    )
    settings["otp_max_attempts"] = _to_int(
        db_values.get(_SMS_OTP_KEY_MAP["otp_max_attempts"]),
        defaults["otp_max_attempts"],
        1,
        20,
    )
    settings["sms_test_live_enabled"] = _to_bool(
        db_values.get(_SMS_OTP_KEY_MAP["sms_test_live_enabled"]),
        defaults["sms_test_live_enabled"],
    )
    settings["email_otp_enabled"] = _to_bool(
        db_values.get(_SMS_OTP_KEY_MAP["email_otp_enabled"]),
        defaults["email_otp_enabled"],
    )
    settings["email_otp_service_base_url"] = str(
        db_values.get(_SMS_OTP_KEY_MAP["email_otp_service_base_url"], defaults["email_otp_service_base_url"])
    ).strip()
    settings["email_otp_type"] = str(
        db_values.get(_SMS_OTP_KEY_MAP["email_otp_type"], defaults["email_otp_type"])
    ).strip().lower() or "numeric"
    settings["email_otp_organization"] = str(
        db_values.get(_SMS_OTP_KEY_MAP["email_otp_organization"], defaults["email_otp_organization"])
    ).strip() or "Trading Nexus"
    settings["email_otp_subject"] = str(
        db_values.get(_SMS_OTP_KEY_MAP["email_otp_subject"], defaults["email_otp_subject"])
    ).strip() or "Email OTP Verification"
    return settings


async def save_sms_otp_settings(payload: dict[str, Any]) -> dict[str, Any]:
    await _ensure_system_config_table()
    current = await get_sms_otp_settings()

    normalized = {
        "message_central_customer_id": str(payload.get("message_central_customer_id", current["message_central_customer_id"])).strip(),
        "message_central_password": str(payload.get("message_central_password", current["message_central_password"])).strip(),
        "otp_expiry_seconds": _to_int(payload.get("otp_expiry_seconds"), current["otp_expiry_seconds"], 30, 600),
        "otp_resend_cooldown_seconds": _to_int(payload.get("otp_resend_cooldown_seconds"), current["otp_resend_cooldown_seconds"], 0, 600),
        "otp_max_attempts": _to_int(payload.get("otp_max_attempts"), current["otp_max_attempts"], 1, 20),
        "sms_test_live_enabled": _to_bool(payload.get("sms_test_live_enabled"), current["sms_test_live_enabled"]),
        "email_otp_enabled": _to_bool(payload.get("email_otp_enabled"), current["email_otp_enabled"]),
        "email_otp_service_base_url": str(
            payload.get("email_otp_service_base_url", current["email_otp_service_base_url"])
        ).strip(),
        "email_otp_type": str(payload.get("email_otp_type", current["email_otp_type"]) or "numeric").strip().lower(),
        "email_otp_organization": str(
            payload.get("email_otp_organization", current["email_otp_organization"]) or "Trading Nexus"
        ).strip(),
        "email_otp_subject": str(
            payload.get("email_otp_subject", current["email_otp_subject"]) or "Email OTP Verification"
        ).strip(),
    }

    pool = get_pool()
    for logical_key, db_key in _SMS_OTP_KEY_MAP.items():
        value = normalized[logical_key]
        await pool.execute(
            """
            INSERT INTO system_config (key, value)
            VALUES ($1, $2)
            ON CONFLICT (key) DO UPDATE
              SET value = EXCLUDED.value, updated_at = now()
            """,
            db_key,
            str(value),
        )

    return await get_sms_otp_settings()
