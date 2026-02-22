"""
app/market_data/greeks_poller.py
==================================
Polling loop — calls POST /optionchain every 15 seconds per active expiry.
Writes Greeks + IV into option_chain_data table (REST skeleton + live hydration).

At startup, also builds the option chain skeleton (all strikes + metadata)
so the frontend always has a complete row structure to query, even before
WebSocket ticks arrive for each token.

Rate: 1 unique call per 3s (DhanHQ limit). Application polls every 15s.
With 12 active expiry slots → 12 calls per 15s cycle = 0.8 req/s — well within limit.
"""
import asyncio
import logging
from datetime import datetime, date
from decimal import Decimal

from app.config                   import get_settings
from app.database                 import get_pool
from app.market_data.rate_limiter import dhan_client
from app.market_hours             import is_market_open, is_equity_window_active
from app.instruments.atm_calculator import update_atm, get_atm

log = logging.getLogger(__name__)
cfg = get_settings()

# DhanHQ segment code for index underlyings
_IDX_SEG = "IDX_I"
_IDX_SECURITY_IDS = {
    "NIFTY":     13,
    "BANKNIFTY": 25,
    "SENSEX":    51,
}

# Strike interval mapping (kept in-sync with /options endpoints)
_STRIKE_INTERVALS = {
    "NIFTY": 50,
    "BANKNIFTY": 100,
    "SENSEX": 100,
    "MIDCPNIFTY": 25,
    "FINNIFTY": 50,
    "BANKEX": 100,
}

_STRIKES_EACH_SIDE = 15  # ATM ± 15 = 31 strikes


class _GreeksPoller:

    def __init__(self):
        self._task: asyncio.Task | None = None
        self._interval: int = cfg.greeks_poll_seconds
        self._pause_until: float = 0.0  # monotonic timestamp
        # One-time forced poll (even if market is closed) to seed prices/prev_close.
        # Resets to False after the first loop iteration.
        self._force_once: bool = True

    async def start(self) -> None:
        if self.is_running:
            return
        self._task = asyncio.create_task(self._poll_loop(), name="greeks-poller")
        log.info(f"Greeks poller started (interval={self._interval}s).")

    async def stop(self) -> None:
        if not self._task:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def refresh_now(self) -> None:
        """Force the next loop iteration to run even if market is closed."""
        self._force_once = True

    async def set_interval(self, seconds: int) -> None:
        self._interval = seconds

    # ── Skeleton build at startup ───────────────────────────────────────────

    async def build_skeleton(self) -> None:
        """
        Build option_chain_data skeleton from instrument_master (CSV-derived):
          - expiries from instrument_master
          - strikes from instrument_master (ATM-window only)
          - lot size from instrument_master

        Greeks/IV are populated later by the 15s REST poller.
        """
        log.info("Building option chain skeleton from instrument_master…")
        expiry_pairs = await self._get_active_expiry_pairs()
        for underlying, expiry in expiry_pairs:
            try:
                await self._seed_skeleton_from_master(underlying, expiry)
            except Exception as exc:
                log.warning(f"Skeleton seed failed [{underlying} {expiry}]: {exc}")
        log.info("Option chain skeleton seeded.")

    async def _seed_skeleton_from_master(self, underlying: str, expiry: date) -> None:
        """Insert option_chain_data rows (no greeks) for ATM-window strikes."""
        pool = get_pool()
        allowed = await self._allowed_strikes_from_master(underlying, expiry)
        if not allowed:
            return

        rows = await pool.fetch(
            """
            SELECT instrument_token, strike_price, option_type
            FROM instrument_master
            WHERE underlying = $1
              AND instrument_type IN ('OPTIDX','OPTSTK','OPTFUT')
              AND expiry_date = $2::date
              AND strike_price IS NOT NULL
              AND option_type IN ('CE','PE')
            """,
            underlying,
            expiry,
        )

        to_insert = []
        for r in rows:
            sp = float(r["strike_price"])
            if round(sp, 2) not in allowed:
                continue
            to_insert.append((
                int(r["instrument_token"]),
                underlying,
                expiry,
                round(sp, 2),
                r["option_type"],
            ))

        if not to_insert:
            return

        async with pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO option_chain_data
                    (instrument_token, underlying, expiry_date, strike_price, option_type)
                VALUES ($1,$2,$3::date,$4,$5)
                ON CONFLICT (instrument_token) DO NOTHING
                """,
                to_insert,
            )

    async def _allowed_strikes_from_master(self, underlying: str, expiry: date) -> set[float]:
        """Compute allowed strikes = ATM ± N strikes, using market_data LTP + CSV strikes."""
        pool = get_pool()
        underlying = underlying.upper()

        strike_rows = await pool.fetch(
            """
            SELECT DISTINCT strike_price
            FROM instrument_master
            WHERE underlying = $1
              AND instrument_type IN ('OPTIDX','OPTSTK','OPTFUT')
              AND expiry_date = $2::date
              AND strike_price IS NOT NULL
            ORDER BY strike_price
            """,
            underlying,
            expiry,
        )
        strikes = [float(r["strike_price"]) for r in strike_rows]
        if not strikes:
            return set()

        step = float(_STRIKE_INTERVALS.get(underlying) or 0)
        if step <= 0 and len(strikes) >= 2:
            diffs = sorted({round(strikes[i+1] - strikes[i], 2) for i in range(len(strikes) - 1) if strikes[i+1] > strikes[i]})
            step = diffs[0] if diffs else 100.0
        if step <= 0:
            step = 100.0

        # Prefer cached ATM; otherwise derive from live underlying LTP
        atm = get_atm(underlying)
        if atm is None:
            ltp_row = await pool.fetchrow(
                """
                SELECT md.ltp
                FROM market_data md
                JOIN instrument_master im ON im.instrument_token = md.instrument_token
                WHERE im.symbol = $1 AND im.instrument_type = 'INDEX'
                LIMIT 1
                """,
                underlying,
            )
            ltp = float(ltp_row["ltp"]) if (ltp_row and ltp_row["ltp"]) else None
            if ltp is None:
                # Fallback: pick the middle strike as a stable deterministic centre
                center = strikes[len(strikes) // 2]
                atm = update_atm(underlying, float(center), step)
            else:
                atm = update_atm(underlying, float(ltp), step)

        atm_f = float(atm)
        # Find closest available strike to ATM
        closest = min(strikes, key=lambda s: abs(s - atm_f))
        idx = strikes.index(closest)
        lo = max(0, idx - _STRIKES_EACH_SIDE)
        hi = min(len(strikes) - 1, idx + _STRIKES_EACH_SIDE)
        return {round(s, 2) for s in strikes[lo:hi+1]}

    # ── Main poll loop ──────────────────────────────────────────────────────

    async def _poll_loop(self) -> None:
        while True:
            await asyncio.sleep(self._interval)

            # Temporary pause (e.g., Dhan 401/429). Avoid hammering.
            now_m = asyncio.get_running_loop().time()
            if now_m < self._pause_until:
                continue

            run_even_if_closed = False
            if self._force_once:
                run_even_if_closed = True
                self._force_once = False

            if not run_even_if_closed and not is_equity_window_active():
                continue   # no point polling when market is closed

            expiry_pairs = await self._get_active_expiry_pairs()
            for underlying, expiry in expiry_pairs:
                # Pause can be set mid-cycle (e.g., first expiry returns 401/429).
                if asyncio.get_running_loop().time() < self._pause_until:
                    break
                try:
                    await self._fetch_and_store(underlying, str(expiry))
                except Exception as exc:
                    log.error(
                        f"Greeks poll error [{underlying} {expiry}]: {exc}"
                    )

    # ── Fetch & store ───────────────────────────────────────────────────────

    async def _fetch_and_store(self, underlying: str, expiry: str) -> None:
        """
        Post to /optionchain via dhan_client — rate limiting is automatic.
        """
        security_id = _IDX_SECURITY_IDS.get(underlying)
        if not security_id:
            return

        expiry_date = date.fromisoformat(expiry)

        resp = await dhan_client.post(
            "/optionchain",
            json={
                "UnderlyingScrip": security_id,
                "UnderlyingSeg":   _IDX_SEG,
                "Expiry":          expiry,
            },
        )
        # If auth/entitlement is invalid (or we're temporarily blocked), pause polling.
        if resp.status_code in (401, 403):
            body = (resp.text or "").lower()
            # 808: bad token/client id pair. Avoid hammering and getting blocked.
            if "808" in body or "authentication failed" in body or "token invalid" in body:
                self._pause_until = asyncio.get_running_loop().time() + 900.0
                log.error(
                    "Greeks poller paused (15m) — Dhan authentication failed (808). "
                    "Fix client_id/access_token in Admin and reconnect."
                )
                return
            # 806: Data APIs not subscribed.
            if "806" in body or "data apis not subscribed" in body:
                self._pause_until = asyncio.get_running_loop().time() + 600.0
                return
            return
        if resp.status_code == 429:
            self._pause_until = asyncio.get_running_loop().time() + 300.0
            return
        if resp.status_code != 200:
            log.warning(
                f"Option chain API returned {resp.status_code} for "
                f"{underlying} {expiry}"
            )
            return

        data = resp.json().get("data", {})
        if not data:
            return

        last_price = data.get("last_price")
        oc         = data.get("oc", {})

        pool = get_pool()
        allowed = await self._allowed_strikes_from_master(underlying, expiry_date)
        rows = []
        for strike_str, strikes_data in oc.items():
            try:
                strike = round(float(strike_str), 2)
            except ValueError:
                continue
            if allowed and strike not in allowed:
                continue
            for opt_type, opt_data in strikes_data.items():
                if opt_type not in ("ce", "pe"):
                    continue
                greeks    = opt_data.get("greeks", {})
                sec_id    = opt_data.get("security_id")
                if not sec_id:
                    continue

                rows.append((
                    int(sec_id),
                    underlying,
                    expiry_date,
                    strike,
                    opt_type.upper(),
                    opt_data.get("implied_volatility"),
                    greeks.get("delta"),
                    greeks.get("theta"),
                    greeks.get("gamma"),
                    greeks.get("vega"),
                    opt_data.get("previous_close_price"),
                    opt_data.get("previous_oi"),
                ))

                # Also seed market_data with last_price if not yet present
                if opt_data.get("last_price") is not None:
                    seg = "NSE_FNO"
                    if underlying in ("SENSEX", "BANKEX"):
                        seg = "BSE_FNO"
                    await pool.execute(
                        """
                        INSERT INTO market_data (instrument_token, exchange_segment,
                            ltp, close, updated_at)
                        VALUES ($1, $2, $3, $4, now())
                        ON CONFLICT (instrument_token) DO NOTHING
                        """,
                        int(sec_id),
                        seg,
                        opt_data["last_price"],
                        opt_data.get("previous_close_price"),
                    )

        if not rows:
            return

        async with pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO option_chain_data
                    (instrument_token, underlying, expiry_date, strike_price,
                     option_type, iv, delta, theta, gamma, vega,
                     prev_close, prev_oi, greeks_updated_at)
                VALUES ($1,$2,$3::date,$4,$5,$6,$7,$8,$9,$10,$11,$12, now())
                ON CONFLICT (instrument_token) DO UPDATE SET
                    iv                = EXCLUDED.iv,
                    delta             = EXCLUDED.delta,
                    theta             = EXCLUDED.theta,
                    gamma             = EXCLUDED.gamma,
                    vega              = EXCLUDED.vega,
                    prev_close        = EXCLUDED.prev_close,
                    prev_oi           = EXCLUDED.prev_oi,
                    greeks_updated_at = now()
                """,
                rows,
            )
        log.debug(
            f"Greeks updated — {underlying} {expiry}: {len(rows)} strikes."
        )

    # ── Active expiry helper ────────────────────────────────────────────────

    async def _get_active_expiry_pairs(self) -> list[tuple[str, date]]:
        """
        Returns list of (underlying, expiry_date) for all active index option expiries.
        """
        pool = get_pool()
        # Polling every expiry for every underlying can easily exceed Dhan limits.
        # We only poll the nearest N expiries per underlying; the skeleton still
        # exists for all strikes/expiries.
        rows = await pool.fetch(
            """
            WITH ranked AS (
                SELECT
                    underlying,
                    expiry_date,
                    ROW_NUMBER() OVER (PARTITION BY underlying ORDER BY expiry_date) AS rn
                FROM instrument_master
                WHERE instrument_type = 'OPTIDX'
                  AND underlying = ANY($1::text[])
                  AND expiry_date >= CURRENT_DATE
                GROUP BY underlying, expiry_date
            )
            SELECT underlying, expiry_date
            FROM ranked
            WHERE rn <= 2
            ORDER BY underlying, expiry_date
            """,
            list(_IDX_SECURITY_IDS.keys()),
        )
        return [(r["underlying"], r["expiry_date"]) for r in rows]


# Singleton
greeks_poller = _GreeksPoller()
