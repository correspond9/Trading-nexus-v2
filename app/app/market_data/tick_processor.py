"""
app/market_data/tick_processor.py
===================================
Receives raw tick dicts from WebSocket handlers, batches them,
and flushes to PostgreSQL every 100ms via a single UPSERT.

Also notifies:
  - ExecutionEngine.on_tick() for pending limit order checks
  - WebSocket push to subscribed frontend clients
"""
import asyncio
import json
import logging
from collections import defaultdict

from app.database import get_pool
from app.config   import get_settings

log = logging.getLogger(__name__)
cfg = get_settings()


class _TickProcessor:
    """
    Buffer: instrument_token ΓåÆ latest tick dict.
    Latest tick wins within the batch window (no stale overwrites).
    """

    def __init__(self):
        # token ΓåÆ dict with latest fields
        self._buffer: dict[int, dict] = {}
        self._lock   = asyncio.Lock()
        self._task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def start(self) -> None:
        if self.is_running:
            return
        self._task = asyncio.create_task(self._flush_loop(), name="tick-processor")
        log.info(f"Tick processor started (batch interval {cfg.tick_batch_ms}ms).")

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
            async with self._lock:
                self._buffer.clear()

    async def flush_now(self) -> None:
        """Force an immediate flush (admin diagnostics)."""
        if not self.is_running:
            return
        await self._flush()

    async def push(self, tick: dict) -> None:
        """
        Called by WS handlers on every incoming tick.
        Merges into the buffer (latest values win).
        """
        if not self.is_running:
            return
        token = tick.get("instrument_token")
        if not token:
            return
        async with self._lock:
            if token in self._buffer:
                self._buffer[token].update({k: v for k, v in tick.items() if v is not None})
            else:
                self._buffer[token] = dict(tick)

    async def _flush_loop(self) -> None:
        interval = cfg.tick_batch_ms / 1000.0
        while True:
            await asyncio.sleep(interval)
            await self._flush()

    async def _flush(self) -> None:
        async with self._lock:
            if not self._buffer:
                return
            batch = list(self._buffer.values())
            self._buffer.clear()

        try:
            await self._upsert(batch)
            await self._notify_execution_engine(batch)
            await self._push_to_frontend(batch)
        except Exception as exc:
            log.error(f"Tick processor flush error: {exc}")

    async def _upsert(self, batch: list[dict]) -> None:
        pool = get_pool()

        # Fetch symbol + segment for tokens not yet in market_data
        # (instrument_master is source of truth)
        tokens = [t["instrument_token"] for t in batch]
        meta_rows = await pool.fetch(
            "SELECT instrument_token, symbol, exchange_segment "
            "FROM instrument_master WHERE instrument_token = ANY($1::bigint[])",
            tokens,
        )
        meta = {r["instrument_token"]: r for r in meta_rows}

        rows = []
        for tick in batch:
            t   = tick["instrument_token"]
            m   = meta.get(t, {})
            sym = m.get("symbol") or tick.get("symbol")
            seg = m.get("exchange_segment") or tick.get("exchange_segment", "NSE_FNO")

            bid = json.dumps(tick.get("bid_depth")) if tick.get("bid_depth") else None
            ask = json.dumps(tick.get("ask_depth")) if tick.get("ask_depth") else None

            rows.append((
                t,
                seg,
                sym,
                tick.get("ltp"),
                tick.get("open"),
                tick.get("high"),
                tick.get("low"),
                tick.get("close"),
                bid,
                ask,
                tick.get("ltt"),
            ))

        async with pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO market_data
                    (instrument_token, exchange_segment, symbol,
                     ltp, open, high, low, close,
                     bid_depth, ask_depth, ltt, updated_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,
                        $9::jsonb, $10::jsonb, $11, now())
                ON CONFLICT (instrument_token) DO UPDATE SET
                    exchange_segment = COALESCE(EXCLUDED.exchange_segment, market_data.exchange_segment),
                    symbol       = COALESCE(NULLIF(market_data.symbol, ''), EXCLUDED.symbol),
                    ltp          = COALESCE(EXCLUDED.ltp,          market_data.ltp),
                    open         = COALESCE(EXCLUDED.open,         market_data.open),
                    high         = COALESCE(EXCLUDED.high,         market_data.high),
                    low          = COALESCE(EXCLUDED.low,          market_data.low),
                    close        = COALESCE(EXCLUDED.close,        market_data.close),
                    bid_depth    = COALESCE(EXCLUDED.bid_depth,    market_data.bid_depth),
                    ask_depth    = COALESCE(EXCLUDED.ask_depth,    market_data.ask_depth),
                    ltt          = COALESCE(EXCLUDED.ltt,          market_data.ltt),
                    updated_at   = now()
                WHERE EXCLUDED.ltp          IS DISTINCT FROM market_data.ltp
                   OR EXCLUDED.bid_depth    IS DISTINCT FROM market_data.bid_depth
                   OR EXCLUDED.ask_depth    IS DISTINCT FROM market_data.ask_depth
                """,
                rows,
            )

    async def _notify_execution_engine(self, batch: list[dict]) -> None:
        """Notify execution engine on_tick for pending limit order checks."""
        # Execution engine exposes module-level functions (not a singleton object).
        from app.execution_simulator import execution_engine
        from app.execution_simulator.execution_config import get_tick_size

        for tick in batch:
            if tick.get("ltp") is None:
                continue
            seg = tick.get("exchange_segment") or "NSE_FNO"
            market_snap = {
                "ltp": tick.get("ltp"),
                "bid_depth": tick.get("bid_depth"),
                "ask_depth": tick.get("ask_depth"),
                "ltt": tick.get("ltt"),
                "tick_size": float(get_tick_size(seg)),
            }
            await execution_engine.on_tick(tick["instrument_token"], market_snap)

    async def _push_to_frontend(self, batch: list[dict]) -> None:
        """Push serialized ticks to subscribed frontend WebSocket clients."""
        from app.websocket_push import push_ticks
        await push_ticks(batch)


# Singleton
tick_processor = _TickProcessor()
