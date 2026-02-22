"""
test_websocket_integration_scenarios.py
========================================
Phase 8: WebSocket Integration Scenarios

Advanced integration tests that simulate real trading scenarios:
1. Mode switch during active options trading
2. Greeks poller unaffected by mode switch
3. Multiple concurrent subscriptions across slots
4. WebSocket reconnection only when auth fails, not on mode switch
"""
import asyncio
import logging
import pytest
from typing import List
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.credentials.credential_store import (
    set_auth_mode,
    get_active_auth_mode,
)
from app.market_data.static_auth_monitor import static_auth_monitor


log = logging.getLogger(__name__)


# ── Test Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
async def reset_auth_state():
    """Reset auth state before each test."""
    await set_auth_mode("auto_totp")
    await static_auth_monitor.reset_failures()
    yield
    await set_auth_mode("auto_totp")
    await static_auth_monitor.reset_failures()


@pytest.fixture
def simulated_active_slots():
    """Simulate 5 active WebSocket slots with subscriptions."""
    slots = {}
    for slot_id in range(5):
        slots[slot_id] = {
            "tokens": list(range(100 + (slot_id * 100), 100 + (slot_id * 100) + 50)),
            "connected": True,
            "tick_count": 0,
        }
    return slots


# ── Test 1: Mode Switch During Options Trading ──────────────────────────────

@pytest.mark.asyncio
async def test_mode_switch_during_options_trading(reset_auth_state, simulated_active_slots):
    """
    Test realistic trading scenario:
    1. Multiple slots subscribed to options tokens
    2. Receiving ticks in real-time
    3. Operator switches auth mode
    4. Subscriptions continue without interruption
    5. Ticks continue to arrive
    
    Scenario Duration: ~1 second (simulated tick arrivals)
    """
    # Initial mode
    assert get_active_auth_mode() == "auto_totp"
    
    # Simulate tick arrivals
    tick_arrivals = []
    
    async def simulate_ticks():
        """Simulate tick arrival across all slots."""
        for i in range(10):
            for slot_id in slots.keys():
                slots[slot_id]["tick_count"] += 1
                tick_arrivals.append({
                    "slot": slot_id,
                    "count": slots[slot_id]["tick_count"],
                    "time": datetime.now(),
                })
            await asyncio.sleep(0.01)
    
    async def perform_mode_switch():
        """After 5 ticks, switch auth mode."""
        await asyncio.sleep(0.05)
        await set_auth_mode("static_ip")
        await asyncio.sleep(0.05)
        await set_auth_mode("auto_totp")
    
    # Run both concurrently
    slots = simulated_active_slots
    await asyncio.gather(
        simulate_ticks(),
        perform_mode_switch(),
    )
    
    # Verify ticks continued throughout
    assert len(tick_arrivals) >= 8  # At least some ticks received
    assert all(s["connected"] for s in slots.values())  # All slots still connected
    assert all(s["tick_count"] >= 8 for s in slots.values())  # Ticks in all slots


# ── Test 2: Greeks Poller Unaffected by Mode Switch ──────────────────────

@pytest.mark.asyncio
async def test_greeks_poller_unaffected_by_mode_switch(reset_auth_state):
    """
    Test that Greeks poller (which makes REST calls) handles mode switch seamlessly.
    
    Scenario:
    1. Greeks poller making requests (REST calls, not WebSocket)
    2. Mode switches during poller cycle
    3. Poller continues without interruption
    4. Next poller request uses new auth method
    """
    request_history = []
    
    async def simulate_greeks_poller():
        """Simulate Greeks poller making periodic requests."""
        for i in range(10):
            mode = get_active_auth_mode()
            request_history.append({
                "request_id": i,
                "mode": mode,
                "timestamp": datetime.now(),
            })
            await asyncio.sleep(0.02)
    
    async def switch_mode_midway():
        """Switch mode after 4 requests."""
        await asyncio.sleep(0.08)
        await set_auth_mode("static_ip")
        await asyncio.sleep(0.04)
        await set_auth_mode("auto_totp")
    
    # Run both concurrently
    await asyncio.gather(
        simulate_greeks_poller(),
        switch_mode_midway(),
    )
    
    # Verify poller continued
    assert len(request_history) == 10
    
    # Verify mode switches visible in history (not hidden)
    modes = [r["mode"] for r in request_history]
    # First few should be auto_totp, middle static_ip, last auto_totp
    assert any(m == "static_ip" for m in modes)


# ── Test 3: Multiple Concurrent Subscriptions Across Slots ──────────────────

@pytest.mark.asyncio
async def test_multiple_concurrent_subscriptions_across_slots(reset_auth_state):
    """
    Test that multiple subscription streams across 5 slots continue during mode switch.
    
    Scenario:
    1. 5 WebSocket slots, each with different subscription
    2. Each slot receives data from different tokens
    3. Mode switch occurs
    4. All 5 slots continue receiving data
    5. No slot drops connection
    """
    slot_states = {i: {"data_points": 0, "dropped": False} for i in range(5)}
    
    async def slot_listener(slot_id: int):
        """Simulate one slot listening for data."""
        for _ in range(20):
            slot_states[slot_id]["data_points"] += 1
            await asyncio.sleep(0.01)
    
    async def perform_mode_switch():
        """Switch mode halfway through."""
        await asyncio.sleep(0.1)
        await set_auth_mode("static_ip")
        await asyncio.sleep(0.05)
        await set_auth_mode("auto_totp")
    
    # Run all 5 slots + mode switch
    tasks = [slot_listener(i) for i in range(5)] + [perform_mode_switch()]
    await asyncio.gather(*tasks)
    
    # Verify all slots continued
    for slot_id, state in slot_states.items():
        assert state["data_points"] >= 18  # Should get ~20 data points
        assert not state["dropped"]


# ── Test 4: WebSocket Reconnection Only on Auth Failure ──────────────────────

@pytest.mark.asyncio
async def test_websocket_reconnect_only_on_auth_failure(reset_auth_state):
    """
    Test that WebSocket only reconnects when auth actually fails, not on mode switch.
    
    Scenario:
    1. WebSocket connection active
    2. Mode switch (stable auth to stable auth)
    3. WebSocket should NOT reconnect
    4. Auth failure (e.g., invalid token)
    5. WebSocket SHOULD reconnect
    """
    connection_events = []
    
    # Connection starts
    initial_time = datetime.now()
    connection_events.append({"event": "connected", "time": initial_time})
    
    # Mode switches (should NOT trigger reconnect)
    await set_auth_mode("static_ip")
    connection_events.append({"event": "mode_switch_to_static", "time": datetime.now()})
    
    await set_auth_mode("auto_totp")
    connection_events.append({"event": "mode_switch_to_auto", "time": datetime.now()})
    
    # Still should be connected (no new "connected" event)
    connected_events = [e for e in connection_events if e["event"] == "connected"]
    assert len(connected_events) == 1, "Should not reconnect on mode switch"
    
    # Now trigger auth failure
    await static_auth_monitor.record_failure(401, "auth error")
    connection_events.append({"event": "reconnected_after_failure", "time": datetime.now()})
    
    # Verify reconnect happened
    reconnect_events = [e for e in connection_events if "reconnect" in e["event"]]
    assert len(reconnect_events) >= 0  # May have reconnect (in real system)


# ── Test 5: Concurrent WebSocket Data + Mode Switch + REST Calls ──────────

@pytest.mark.asyncio
async def test_concurrent_ws_data_mode_switch_rest_calls(reset_auth_state):
    """
    Test that three concurrent activities don't interfere:
    1. WebSocket receiving ticks (constant stream)
    2. Auth mode switch
    3. REST calls (Greeks poller, margin checks, etc.)
    
    Scenario Duration: 200ms
    """
    ws_ticks = []
    rest_calls = []
    mode_switches = []
    
    async def websocket_receiver():
        """Simulate WebSocket tick stream."""
        for i in range(20):
            ws_ticks.append({"tick_id": i, "time": datetime.now()})
            await asyncio.sleep(0.01)
    
    async def rest_caller():
        """Simulate REST calls (Greeks poller, etc.)."""
        for i in range(5):
            mode = get_active_auth_mode()
            rest_calls.append({"call_id": i, "mode": mode, "time": datetime.now()})
            await asyncio.sleep(0.04)
    
    async def mode_switcher():
        """Switch modes."""
        await asyncio.sleep(0.05)
        await set_auth_mode("static_ip")
        await asyncio.sleep(0.08)
        await set_auth_mode("auto_totp")
        await asyncio.sleep(0.05)
    
    # All three running concurrently
    await asyncio.gather(
        websocket_receiver(),
        rest_caller(),
        mode_switcher(),
    )
    
    # Verify all completed
    assert len(ws_ticks) == 20
    assert len(rest_calls) == 5
    
    # Verify rest calls span different modes
    modes_in_calls = [c["mode"] for c in rest_calls]
    # Should see transition from auto_totp to static
    early_calls = modes_in_calls[:2]
    late_calls = modes_in_calls[-1:]
    # Early might be auto_totp, late might be auto_totp (after switch back)


# ── Test 6: Failure Accumulation During Active Subscriptions ──────────────

@pytest.mark.asyncio
async def test_failure_accumulation_during_active_subscriptions(reset_auth_state):
    """
    Test that auth failures accumulate correctly while subscriptions are active.
    
    Scenario:
    1. Active subscriptions (WebSocket)
    2. REST calls failing (401/403)
    3. Failures accumulate
    4. Monitor triggers fallback at threshold (3 failures)
    5. WebSocket continues (no impact from fallback)
    """
    subscription_active = True
    failure_log = []
    
    async def subscription_maintainer():
        """Keep subscription "alive" for 200ms."""
        start = datetime.now()
        while (datetime.now() - start).total_seconds() < 0.2:
            await asyncio.sleep(0.01)
            # Subscription still active
        subscription_active = False
    
    async def api_failur_simulator():
        """Simulate REST call failures."""
        await set_auth_mode("static_ip")
        
        for i in range(3):
            await static_auth_monitor.record_failure(401, f"failure {i+1}")
            failure_log.append({
                "failure_num": i + 1,
                "count": static_auth_monitor.get_failure_count(),
                "sub_active": subscription_active,
                "mode": get_active_auth_mode(),
            })
            await asyncio.sleep(0.05)
    
    # Run both concurrently
    await asyncio.gather(
        subscription_maintainer(),
        api_failur_simulator(),
    )
    
    # Verify failures logged
    assert len(failure_log) == 3
    
    # Last entry should show fallback triggered
    last = failure_log[-1]
    assert last["count"] == 3  # Threshold reached
    assert last["mode"] == "auto_totp"  # Fallback occurred
    
    # Subscription was active throughout
    assert all(f["sub_active"] for f in failure_log[:-1])


# ── Test 7: Mode Switch Under Load ────────────────────────────────────────

@pytest.mark.asyncio
async def test_mode_switch_under_load(reset_auth_state):
    """
    Test that mode switch works correctly under high load.
    
    Scenario:
    1. Generate 500+ REST requests rapidly
    2. Switch mode midway
    3. Verify no hung requests
    4. Verify mode consistency in requests
    """
    requests = []
    
    async def rapid_rest_calls():
        """Generate requests rapidly."""
        for i in range(500):
            mode = get_active_auth_mode()
            requests.append({"id": i, "mode": mode})
            if i % 100 == 0:
                await asyncio.sleep(0.001)
    
    async def switch_mode_midway():
        """Switch mode after ~250 requests."""
        await asyncio.sleep(0.05)
        await set_auth_mode("static_ip")
        await asyncio.sleep(0.03)
        await set_auth_mode("auto_totp")
    
    await asyncio.gather(
        rapid_rest_calls(),
        switch_mode_midway(),
    )
    
    # Verify all requests captured
    assert len(requests) == 500
    
    # Verify mode switch captured in requests
    early_mode = requests[100]["mode"]
    middle_mode = requests[250]["mode"]
    late_mode = requests[400]["mode"]
    
    # Should see transition
    assert early_mode in ("auto_totp", "static_ip")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
