"""app/runtime/market_timing.py

Market-hours-aware START/STOP controller for interval-based background tasks.

Requirements:
- Equity window: 09:00ΓÇô15:30 IST
- Commodity window: 09:00ΓÇô23:30 IST

The controller supports per-scheduler override modes:
- auto (default)
- forced_running
- forced_stopped

"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.market_hours import (
    IST,
    is_equity_window_active,
    is_commodity_window_active,
)

log = logging.getLogger(__name__)


@dataclass
class SchedulerOverride:
    mode: str = "auto"  # auto | forced_running | forced_stopped


class MarketTimingController:
    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._overrides: dict[str, SchedulerOverride] = {}

    def set_override(self, name: str, mode: str) -> None:
        if mode not in ("auto", "forced_running", "forced_stopped"):
            raise ValueError("Invalid override mode")
        self._overrides[name] = SchedulerOverride(mode=mode)

    def get_override(self, name: str) -> str:
        return (self._overrides.get(name) or SchedulerOverride()).mode

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop = asyncio.Event()
        self._task = asyncio.create_task(self._loop(), name="market-timing-controller")
        log.info("MarketTimingController started.")

    async def stop(self) -> None:
        if not self._task:
            return
        self._stop.set()
        try:
            await asyncio.wait_for(self._task, timeout=5)
        except asyncio.TimeoutError:
            self._task.cancel()
        except Exception:
            pass
        finally:
            self._task = None
        log.info("MarketTimingController stopped.")

    async def enforce_now(self) -> None:
        """Apply the start/stop decisions immediately."""
        from app.market_data.tick_processor import tick_processor
        from app.market_data.greeks_poller import greeks_poller
        from app.credentials.token_refresher import token_refresher
        from app.execution_simulator import super_order_monitor

        now = datetime.now(tz=IST)
        equity_on = is_equity_window_active(now)
        comm_on = is_commodity_window_active(now)
        any_on = equity_on or comm_on

        async def _apply(name: str, should_run: bool, start_fn, stop_fn, is_running: bool):
            ov = self.get_override(name)
            if ov == "forced_running":
                should_run = True
            elif ov == "forced_stopped":
                should_run = False

            if should_run and not is_running:
                await start_fn()
            elif (not should_run) and is_running:
                await stop_fn()

        await _apply(
            "tick_processor",
            any_on,
            tick_processor.start,
            tick_processor.stop,
            tick_processor.is_running,
        )

        await _apply(
            "greeks_poller",
            equity_on,
            greeks_poller.start,
            greeks_poller.stop,
            greeks_poller.is_running,
        )

        await _apply(
            "super_order_monitor",
            any_on,
            super_order_monitor.start_monitor,
            super_order_monitor.stop_monitor,
            super_order_monitor.is_running(),
        )

        # Token refresher is only meaningful when enabled and in auto_totp.
        await _apply(
            "token_refresher",
            any_on,
            token_refresher.start,
            token_refresher.stop,
            token_refresher.is_running,
        )

    async def _loop(self) -> None:
        # Periodic enforcement (kept simple and robust)
        while not self._stop.is_set():
            try:
                await self.enforce_now()
            except Exception as exc:
                log.exception("MarketTimingController enforce error: %s", exc)

            # Sleep until next coarse boundary (30s), but allow fast stop.
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=30.0)
                break
            except asyncio.TimeoutError:
                pass


market_timing_controller = MarketTimingController()
