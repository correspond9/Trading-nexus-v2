"""
app/config.py
=============
All environment-driven settings loaded once at startup.
Use python-dotenv for local dev; real deployments inject env vars directly.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ΓöÇΓöÇ PostgreSQL ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    database_url: str = "postgresql://postgres:postgres@localhost:5432/trading_nexus"

    # ΓöÇΓöÇ DhanHQ (initial values ΓÇö can be overridden at runtime via Admin API) ΓöÇ
    dhan_client_id:    str = ""
    dhan_access_token: str = ""  # optional when TOTP auto-refresh is configured
    dhan_base_url:     str = "https://api.dhan.co/v2"
    dhan_feed_url:     str = "wss://api-feed.dhan.co"
    dhan_depth_20_url: str = "wss://depth-api-feed.dhan.co/twentydepth"

    # ΓöÇΓöÇ DhanHQ TOTP auto-refresh (permanent token ΓÇö no manual rotation) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    # Set both to enable headless 24-hour token renewal.
    dhan_pin:          str = ""   # 6-digit Dhan login PIN
    dhan_totp_secret:  str = ""   # TOTP shared secret shown on Dhan TOTP setup page

    # ΓöÇΓöÇ App ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    debug:             bool = False
    log_level:         str  = "INFO"
    cors_origins_raw:  str  = "http://localhost:3000,http://localhost:5173"  # comma-separated

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    # ΓöÇΓöÇ Market data ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    tick_batch_ms:         int   = 100     # flush tick buffer every N ms
    greeks_poll_seconds:   int   = 15      # REST /optionchain poll interval
    max_ws_connections:    int   = 5
    max_tokens_per_ws:     int   = 5000
    max_msg_instruments:   int   = 100     # DhanHQ limit per JSON message

    # ΓöÇΓöÇ 20-Level Depth instruments (get top-20 bid/ask) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    # Index spot tokens ΓÇö fetched from instrument_master at startup
    depth_20_underlying: list[str] = ["NIFTY", "BANKNIFTY", "SENSEX"]

    # ΓöÇΓöÇ Startup safety flags ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    # Set DISABLE_DHAN_WS=true or STARTUP_START_STREAMS=false in .env to
    # prevent any outbound connections to DhanHQ servers on startup.
    # Use this for local dev / testing to avoid conflicting with production.
    disable_dhan_ws:        bool = False  # DISABLE_DHAN_WS
    disable_market_streams: bool = False  # DISABLE_MARKET_STREAMS
    startup_start_streams:  bool = True   # STARTUP_START_STREAMS
    startup_load_master:    bool = True   # STARTUP_LOAD_MASTER
    startup_load_tier_b:    bool = True   # STARTUP_LOAD_TIER_B

    @property
    def dhan_disabled(self) -> bool:
        """True if ALL DhanHQ outbound connections should be skipped."""
        return (
            self.disable_dhan_ws
            or self.disable_market_streams
            or not self.startup_start_streams
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
