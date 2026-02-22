"""
app/main.py
============
FastAPI application entry point.
Lifespan: ordered startup sequence → graceful shutdown.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config                               import get_settings
from app.database                             import init_db, close_db, get_pool
from app.credentials.credential_store         import load_credentials
from app.credentials.credential_store         import get_client_id, get_access_token
from app.credentials.credential_store         import is_static_configured, set_auth_mode
from app.credentials.token_refresher          import token_refresher
from app.instruments.scrip_master             import (
    seed_subscription_lists_if_empty,
    refresh_instruments,
    scrip_scheduler,
)
import app.instruments.subscription_manager     as subscription_manager
from app.market_data.tick_processor           import tick_processor
from app.market_data.websocket_manager        import ws_manager
from app.market_data.depth_ws_manager         import depth_ws_manager
from app.market_data.greeks_poller            import greeks_poller
from app.market_data.rate_limiter             import dhan_client
from app.routers                              import admin, market_data, option_chain, watchlist, orders, positions, ws_feed
from app.routers                              import ledger
from app.routers                              import payouts
from app.routers                              import auth, baskets, margin, search
from app.routers                              import theme
from app.margin.nse_margin_data               import (
    download_and_refresh   as refresh_margin_data,
    nse_margin_scheduler,
    _load_latest_from_db   as load_margin_from_db,
)
from app.margin.exchange_holidays             import (
    sync_exchange_holidays,
    load_holidays_into_memory,
)
from app.margin import mcx_margin_data
from app.margin import bse_margin_data
from app.market_hours                         import load_exchange_holidays_from_db
from app.execution_simulator.super_order_monitor import (
    start_monitor   as start_super_order_monitor,
    stop_monitor    as stop_super_order_monitor,
)
from app.market_data.static_auth_monitor import static_auth_monitor
from app.positions.eod_archiver               import eod_closed_position_archiver
from app.runtime.market_timing                import market_timing_controller
from app.schedulers.charge_calculation_scheduler import charge_calculation_scheduler

log = logging.getLogger(__name__)
cfg = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup sequence (order matters):
      1.  DB pool + migrations
      1b. Download and cache trading holidays for NSE, BSE, MCX
      2.  Credential load from DB
      3.  Seed subscription lists from local CSV files (disk only, no network)
      4.  Instrument master seed/refresh
            → DHAN DISABLED: reads local CSV only
            → DHAN ENABLED:  downloads fresh CSV from DhanHQ CDN
      5.  [DHAN ONLY] TOTP token refresher
      6.  [DHAN ONLY] Tier-B subscription initialisation
      7.  [DHAN ONLY] Tick processor
      8.  [DHAN ONLY] Live Feed WebSocket manager (5 slots)
      9.  [DHAN ONLY] Full Depth WebSocket manager
     10.  [DHAN ONLY] Option chain skeleton + Greeks poller
     11.  [DHAN ONLY] Daily scrip master scheduler (06:00 IST)
     12.  NSE margin data initial load (SPAN + ELM) — always enabled
     12b. MCX and BSE margin data initial load
     13.  NSE margin daily scheduler (08:45 IST) — always enabled
     14.  Market hours updated with cached holidays
     15.  Super Order monitor (Target + SL + Trailing)
    """
    try:
        log.info("─── Startup ────────────────────────────────────────────────")

        log.info("[1] Initialising database pool + running migrations…")
        await init_db()

        log.info("[1b] Syncing trading holidays from exchange websites…")
        try:
            holidays_synced = await sync_exchange_holidays()
            if holidays_synced:
                log.info("[1b] ✓ Trading holidays synced from NSE, MCX, BSE")
            else:
                log.warning("[1b] Could not sync all holidays; using fallback list")
        except Exception as exc:
            log.warning(f"[1b] Holiday sync failed ({exc}); using fallback")

        log.info("[2] Loading DhanHQ credentials from DB…")
        await load_credentials()

        if is_static_configured():
            log.info("[2a] Static IP credentials detected — setting auth_mode=static_ip")
            await set_auth_mode("static_ip")
            try:
                resp = await dhan_client.verify_static_auth()
                if resp.status_code == 200:
                    log.info("[2a] Static IP auth verified successfully.")
                else:
                    log.warning(
                        "[2a] Static IP auth verification failed (HTTP %s) — "
                        "falling back to auto_totp.",
                        resp.status_code,
                    )
                    await set_auth_mode("auto_totp")
            except Exception as exc:
                log.warning(
                    "[2a] Static IP auth verification error (%s) — falling back to auto_totp.",
                    exc,
                )
                await set_auth_mode("auto_totp")
        else:
            log.info("[2a] Static IP credentials not present — setting auth_mode=auto_totp")
            await set_auth_mode("auto_totp")

        log.info("[2b] Starting static IP auth monitor…")
        await static_auth_monitor.start()

        log.info("[3] Seeding subscription lists from local CSV files…")
        await seed_subscription_lists_if_empty()

        if cfg.dhan_disabled:
            log.info("[4] Loading instrument master from local CSV (Dhan disabled)…")
            await refresh_instruments(download=False)

            log.info("[10] Building option chain skeleton (Dhan disabled)…")
            await greeks_poller.build_skeleton()

            log.warning(
                "[⚠] DHAN CONNECTIONS DISABLED — token refresher, WebSocket managers, "
                "Greeks poller, and daily CDN refresh are all off. "
                "Set DISABLE_DHAN_WS=false + STARTUP_START_STREAMS=true to enable."
            )
        else:
            log.info("[4] Downloading fresh instrument master from DhanHQ CDN…")
            await refresh_instruments(download=True)

            # If startup streams are disabled, leave everything off and rely on
            # explicit SuperAdmin action: POST /admin/dhan/connect.
            if not cfg.startup_start_streams:
                log.warning(
                    "[⚠] STARTUP_START_STREAMS=false — skipping Dhan stream startup. "
                    "Use SuperAdmin → Connect to Dhan to start streams at runtime."
                )
            elif not (get_client_id() and get_access_token()):
                log.warning(
                    "[⚠] No Dhan credentials in DB — skipping Dhan stream startup. "
                    "Save Client ID + Access Token in SuperAdmin, then Connect to Dhan."
                )
            else:
                log.info("[5] Starting TOTP token refresher…")
                await token_refresher.start()

                if cfg.startup_load_tier_b:
                    log.info("[6] Initialising Tier-B subscriptions…")
                    await subscription_manager.initialise_tier_b()
                else:
                    log.warning(
                        "[6] STARTUP_LOAD_TIER_B=false — skipping Tier-B init at startup. "
                        "(Connect to Dhan will initialise on demand.)"
                    )

                log.info("[7] Starting tick processor…")
                await tick_processor.start()

                log.info("[8] Starting Live Feed WebSocket manager (5 slots)…")
                await ws_manager.start_all()

                log.info("[9] Starting Full Depth WebSocket manager…")
                pool = get_pool()
                depth_rows = await pool.fetch(
                    """
                    SELECT instrument_token FROM instrument_master
                    WHERE underlying = ANY($1::text[])
                      AND instrument_type IN ('FUTIDX','OPTIDX')
                    LIMIT 10
                    """,
                    cfg.depth_20_underlying,
                )
                depth_tokens = [r["instrument_token"] for r in depth_rows]
                await depth_ws_manager.start(depth_tokens)

                log.info("[10] Building option chain skeleton + starting Greeks poller…")
                await greeks_poller.build_skeleton()
                await greeks_poller.start()

                log.info("[11] Starting daily scrip master scheduler (06:00 IST)…")
                await scrip_scheduler.start()

        log.info("[12] Loading NSE margin data (SPAN® + Exposure Limit) …")
        try:
            # First try loading from database cache
            db_loaded = await load_margin_from_db()
            if db_loaded:
                log.info("[12] ✓ Loaded NSE SPAN margin data from database cache")
            
            # Then attempt fresh download (will save to DB if successful)
            await refresh_margin_data()
        except Exception as exc:
            log.warning(f"[12] NSE margin initial load failed ({exc}); will retry at 08:45 IST.")

        log.info("[12b] Loading MCX and BSE margin data …")
        try:
            # Load MCX margins from database cache
            await mcx_margin_data._load_latest_from_db()
            log.info("[12b] ✓ Loaded MCX margin data from database cache")
        except Exception as exc:
            log.warning(f"[12b] MCX margin load failed ({exc})")
        
        try:
            # Load BSE margins from database cache
            await bse_margin_data._load_latest_from_db()
            log.info("[12b] ✓ Loaded BSE margin data from database cache")
        except Exception as exc:
            log.warning(f"[12b] BSE margin load failed ({exc})")

        log.info("[13] Starting NSE margin daily scheduler (08:45 IST) …")
        await nse_margin_scheduler.start()

        log.info("[14] Loading exchange holidays into market_hours…")
        try:
            holidays_loaded = await load_exchange_holidays_from_db()
            if holidays_loaded:
                log.info("[14] ✓ Exchange holidays loaded for market state checks")
            else:
                log.warning("[14] Could not load holidays from database; using empty set")
        except Exception as exc:
            log.warning(f"[14] Holiday loading failed ({exc})")

        log.info("[15] Starting Super Order monitor (Target + SL + Trailing) …")
        await start_super_order_monitor()

        log.info("[16] Starting EOD closed-position archiver (16:00 IST) …")
        await eod_closed_position_archiver.start()

        log.info("[17] Starting charge calculation scheduler (16:00 IST NSE/BSE, 00:00 IST MCX) …")
        await charge_calculation_scheduler.start()

        log.info("[18] Starting market timing controller (auto START/STOP) …")
        await market_timing_controller.start()

        log.info("─── Application ready ─────────────────────────────────────")

    except Exception as exc:
        log.exception(f"Startup failed: {exc}")
        raise

    yield  # ── Application runs here ──────────────────────────────────────

    log.info("─── Shutdown ───────────────────────────────────────────────")
    await market_timing_controller.stop()
    await charge_calculation_scheduler.stop()
    await eod_closed_position_archiver.stop()
    await static_auth_monitor.stop()
    await stop_super_order_monitor()
    await nse_margin_scheduler.stop()
    if not cfg.dhan_disabled:
        await scrip_scheduler.stop()
        await greeks_poller.stop()
        await token_refresher.stop()
        await depth_ws_manager.stop()
        await ws_manager.stop_all()
        await tick_processor.stop()
        await dhan_client.close()
    await close_db()
    log.info("─── Shutdown complete ─────────────────────────────────────────")


def create_app() -> FastAPI:
    app = FastAPI(
        title       = "Trading Nexus",
        description = "Paper trading system backed by DhanHQ v2 DATA APIs.",
        version     = "1.0.0",
        lifespan    = lifespan,
        docs_url    = "/api/v2/docs",
        redoc_url   = "/api/v2/redoc",
        openapi_url = "/api/v2/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins     = cfg.cors_origins,
        allow_credentials = True,
        allow_methods     = ["*"],
        allow_headers     = ["*"],
    )

    V2 = "/api/v2"
    app.include_router(admin.router,        prefix=V2)
    app.include_router(market_data.router,  prefix=V2)
    app.include_router(option_chain.router, prefix=V2)
    app.include_router(watchlist.router,    prefix=V2)
    app.include_router(orders.router,       prefix=V2)
    app.include_router(positions.router,    prefix=V2)
    app.include_router(ledger.router,       prefix=V2)
    app.include_router(payouts.router,      prefix=V2)
    app.include_router(ws_feed.router,      prefix=V2)
    app.include_router(auth.router,         prefix=V2)
    app.include_router(baskets.router,      prefix=V2)
    app.include_router(margin.router,       prefix=V2)
    app.include_router(search.router,       prefix=V2)
    app.include_router(theme.router,        prefix=V2)

    @app.get("/health", tags=["Health"])
    async def health_root():
        return {"status": "ok", "version": "1.0.0"}

    @app.get("/api/v2/health", tags=["Health"])
    async def health_v2():
        """Health check with database and Dhan API status."""
        db_ok = "ok"
        try:
            pool = get_pool()
            await pool.fetchval("SELECT 1")
        except Exception:
            db_ok = "error"
        return {
            "status":   "ok",
            "version":  "1.0.0",
            "database": db_ok,
            "dhan_api": "connected" if not cfg.dhan_disabled else "disabled",
        }

    return app


app = create_app()
