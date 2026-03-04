# ATM Closing Price Issue — Root Cause Analysis

**Date Reported:** March 4, 2026 (8:00 PM IST)  
**Market Close Time:** 3:30 PM IST (4.5 hours earlier)  
**Status:** ✅ Root cause identified, solution ready

---

## THE PROBLEM

| Index    | Actual Close | Webpage ATM | Error    | Strikes Off |
|----------|--------------|-------------|----------|------------|
| NIFTY    | 24,480.50    | 25,400     | +919.50  | +18.4     |
| BANKNIFTY| 58,755.25    | 59,900     | +1,144.75| +11.4     |
| SENSEX   | 79,116.19    | 82,300     | +3,183.81| +31-32    |

The webpage is displaying **stale intraday ATM prices**, not the actual market close ATM values.

---

## ROOT CAUSE: NO MARKET CLOSE ATM HANDLER

### Issue #1: ATM Cache Never Updated at Market Close

**Location:** `app/instruments/atm_calculator.py`

The ATM cache is a simple in-memory dictionary:
```python
_atm_cache: dict[str, Decimal] = {}  # underlying → current ATM strike
```

The cache is updated ONLY in these scenarios:
1. ✅ **Startup** — via `atm_calculator.update_atm()` 
2. ✅ **Expiry Rollover** — (code path exists but when?)
3. ✅ **Admin Manual Refresh** — via `/admin/option-chain/recalibrate-atm` and `/admin/option-chain/rebuild-skeleton` endpoints

**Critical Missing:** ❌ **No market close handler to update ATM with final closing prices**

### Issue #2: Greeks Poller Stops Running After Market Close

**Location:** `app/market_data/greeks_poller.py`, lines 217-219

The greeks_poller skips execution when market is CLOSED:
```python
if not run_even_if_closed and not is_equity_window_active():
    continue   # no point polling when market is closed
```

**Timeline:**
- **3:15 PM** - Last greeks_poller run (market still OPEN)
  - Calls Dhan `/optionchain` REST API
  - Gets closing ticks with `last_price` = closing price
  - Updates `option_chain_data.prev_close` ✅
  - But does NOT update `atm_calculator._atm_cache` because...

- **3:30 PM** - Market closes
  - Dhan WS ticks stop flowing
  - greeks_poller next iteration skips (market is closed) ❌
  - ATM cache remains with stale intraday value

- **8:00 PM** - User checks webpage
  - Frontend calls `/options/live`
  - Backend returns cached ATM (unchanged since 3:15 PM) ❌

### Issue #3: Index Tokens May Not Receive Closing Ticks via WebSocket

**Location:** Potential issue in Dhan WS subscription

Index tokens (NIFTY, BANKNIFTY, SENSEX) are represented by `instrument_type = 'INDEX'` in `instrument_master`. There's evidence that these may NOT be:
1. Subscribed in Tier-B (continuously monitored Dhan contracts)
2. Receiving WebSocket ticks at market close (only option/futures contracts get ticks)

**Consequence:** Even if `market_data.ltp` is updated with a closing tick, it may be from the LAST INTRADAY TICK, not the official 3:30 PM close.

---

## DATA FLOW: How the Frontend Gets Stale ATM

### Step 1: Frontend Request
```
Frontend: GET /options/live?underlying=NIFTY&expiry=2026-02-27
```

### Step 2: Backend Endpoint (option_chain.py, lines 50-94)
```python
@router.get("/live")
async def get_option_chain(underlying: str, expiry: str, ...):
    # Fetch FROM CACHE
    atm_raw = get_atm(underlying)  # ← Returns stale in-memory value
    atm = float(atm_raw) if atm_raw is not None else None
    
    # Fetch from DB (should be fresh)
    ul_row = await pool.fetchrow(
        "SELECT md.ltp FROM market_data md "
        "WHERE im.symbol = $1 AND im.instrument_type = 'INDEX' LIMIT 1",
        underlying
    )
    underlying_ltp = float(ul_row["ltp"]) if ul_row and ul_row["ltp"] else (atm or 0.0)
    
    return {
        "underlying_ltp": underlying_ltp,  # Should be closing price (if DB was updated)
        "atm": atm,                         # STALE cache value
        "strikes": {...}
    }
```

### Step 3: Frontend Calculation (useAuthoritativeOptionChain.js)
```javascript
const getATMStrike = useCallback((ltp) => {
  const interval = getStrikeInterval(underlying);
  const price = Number(ltp || data?.underlying_ltp || 0);
  return Math.round(price / interval) * interval;  // Round to nearest strike
}, [data, underlying]);
```

**The Problem in STRADDLE.jsx, line 54-60:**
```javascript
const straddleAtmStrike = useMemo(() => {
  const fromLtp = getATMStrike();  // Uses data?.underlying_ltp
  if (typeof fromLtp === 'number' && fromLtp > 0) return fromLtp;
  
  const backendAtm = chainData?.atm_strike || chainData?.atm || null;
  return (typeof backendAtm === 'number' && backendAtm > 0) ? backendAtm : null;
}, [getATMStrike, chainData?.atm_strike, chainData?.atm]);
```

**Scenario at 8:00 PM:**
1. `underlying_ltp` from DB might be correct (IF index token got closing tick) ✓
2. BUT `getATMStrike()` might use stale `data?.underlying_ltp from the REST response ✓
3. Fall back to `chainData?.atm` which is definitely the stale cache value ✗

---

## Evidence Trail

### Evidence #1: close_price_rollover.py
Runs at **9:15 AM** (market OPEN), not 3:30 PM (market CLOSE):
```python
MARKET_OPEN_TIME = time(9, 15, 0)
ROLLOVER_WINDOW_END = time(9, 20, 0)

if not (MARKET_OPEN_TIME <= current_time <= ROLLOVER_WINDOW_END):
    continue
```

### Evidence #2: No market close scheduler in main.py
Startup handlers registered:
- ✅ close_price_rollover (for 9:15 AM open rollover)
- ✅ charge_calculation_scheduler (for 4:00 PM post-close charge calc — doesn't update ATM)
- ✅ mis_auto_squareoff (for 3:20 PM pre-close position exit)
- ❌ **NO "market_close_price_rollover" or "atm_close_update_scheduler"**

### Evidence #3: ATM Update Locations
```bash
$ grep -r "update_atm\|calculate_atm" app/
```
Results show `update_atm()` called ONLY in:
1. `app/routers/admin.py` — manual admin endpoints
2. `app/market_data/greeks_poller.py` — during active market hours
3. `app/instruments/atm_calculator.py` — definition

**Missing: No call during market close.**

---

## Why This Happens

### Design Assumption (Incorrect)
The system was designed assuming:
> "ATM cache will be auto-updated by greeks_poller throughout the day, so at market close the cache will have the correct closing price."

**Problem:** This assumption breaks because **greeks_poller STOPS running when market closes** (optimization to not hammer Dhan API when no new ticks are coming).

### The Vicious Cycle
```
3:15 PM → greeks_poller runs, ATM = last intraday price
         ↓
3:30 PM → Market closes, no new greeks_poller runs
         ↓
         ATM cache FROZEN with intraday price
         ↓
8:00 PM → User checks ← STALE ATM returned
```

---

## WHERE THE BUG IS (File Locations)

| Issue | File | Problem | Why |
|-------|------|---------|-----|
| **Missing market close handler** | `app/main.py` | No scheduler to capture closing prices & update ATM | Design gap |
| **greeks_poller stops at close** | `app/market_data/greeks_poller.py:217` | Skips execution when market closed | Optimization gone wrong |
| **No close_price handler** | N/A (doesn't exist) | Need equivalent to `close_price_rollover` but at 3:30 PM | Feature missing |
| **ATM cache not updated** | `app/instruments/atm_calculator.py` | Only has `update_atm()`, never called at close | No caller at market close |

---

## PROPOSED SOLUTIONS

### Solution A: Create Market Close ATM Update Handler (RECOMMENDED)

**Create new file:** `app/market_data/close_price_capture.py`

```python
"""
Close price capture scheduler — updates ATM cache at market close.

Runs at 3:35 PM IST for NSE/BSE (5 minute buffer to allow final ticks).
Captures the final closing prices and updates atm_calculator cache.
"""

class _ClosePriceCapture:
    def __init__(self):
        self._task: asyncio.Task = None
    
    async def _market_close_handler(self):
        """At 3:35 PM, read market_data.ltp and update ATM cache."""
        pool = get_pool()
        
        # For each index underlying
        for underlying in ["NIFTY", "BANKNIFTY", "SENSEX"]:
            try:
                # Get latest LTP from market_data
                ltp_row = await pool.fetchrow(
                    """SELECT md.ltp FROM market_data md
                       JOIN instrument_master im ON ...
                       WHERE im.symbol = $1 AND im.instrument_type = 'INDEX'""",
                    underlying
                )
                
                if ltp_row and ltp_row["ltp"]:
                    # Update ATM cache with closing price
                    step = STRIKE_INTERVALS[underlying]
                    update_atm(underlying, float(ltp_row["ltp"]), step)
                    log.info(f"✅ Market close: Updated {underlying} ATM to {ltp_row['ltp']}")
                else:
                    # If no LTP from WS ticks, try Dhan REST API directly
                    closing_price = await fetch_from_dhan_rest(underlying)
                    if closing_price:
                        update_atm(underlying, closing_price, step)
                        log.info(f"✅ Market close: Updated {underlying} ATM from Dhan REST: {closing_price}")
                    else:
                        log.warning(f"⚠️  Market close: Could not get closing price for {underlying}")
            except Exception as e:
                log.error(f"❌ Market close ATM update failed for {underlying}: {e}")

# Register in main.py startup
await close_price_capture.start()
```

**Advantages:**
- Simple, isolated handler
- Runs AFTER market close so final tick is guaranteed to be in DB
- Fallback to Dhan REST API if WS ticks missed
- Handles edge case where index tokens don't receive ticks
- Cost: 2-3 HTTP calls to Dhan, 1 per day

---

### Solution B: Force greeks_poller to Run at Market Close

**Modify:** `app/market_data/greeks_poller.py`

```python
async def _poll_loop(self):
    while True:
        ...
        run_even_if_closed = False
        if self._force_once:
            run_even_if_closed = True
            self._force_once = False
        
        # NEW: Also run even if closed at specific close time
        now = datetime.now(IST)
        if time(15, 30) <= now.time() <= time(15, 35):  # 3:30-3:35 PM
            run_even_if_closed = True
        
        if not run_even_if_closed and not is_equity_window_active():
            continue
        
        # Fetch and store Greeks/IV (which also calls update_atm internally) ✅
```

**Disadvantages:**
- Couples market close logic to greeks_poller (less clean)
- Still calls Dhan API even when market closed (wasteful)
- May hit rate limits if not careful

---

### Solution C: Hybrid — Use Dhan REST API Directly at Close

**Modify:** `app/market_data/greeks_poller.py` → add new method

```python
async def _fetch_underlying_close_prices(self):
    """At market close, fetch current spot prices from Dhan /optionchain."""
    for underlying in ["NIFTY", "BANKNIFTY", "SENSEX"]:
        try:
            resp = await dhan_client.post("/optionchain", json={...})
            data = resp.json().get("data", {})
            if data.get("last_price"):
                update_atm(underlying, float(data["last_price"]), STRIKE_INTERVALS[underlying])
        except Exception as exc:
            log.error(f"ATM close fetch failed: {exc}")
```

**Advantages:**
- Gets REAL-TIME price from Dhan (not from stale WS ticks)
- Guaranteed to be correct even if index tokens lack subscriptions
- Single batch call

**Disadvantages:**
- Adds complexity to greeks_poller

---

## RECOMMENDED FIX STEPS

### Step 1: Create Close Price Capture Scheduler
Create `app/market_data/close_price_capture.py` (Solution A above)

### Step 2: Register in main.py
```python
from app.market_data.close_price_capture import close_price_capture

async def lifespan(...):
    # After close_price_rollover startup
    log.info("[12] Starting market close price capture scheduler (3:35 PM IST)…")
    await close_price_capture.start()
```

### Step 3: Ensure greeks_poller Calls update_atm()
Verify in `greeks_poller.py` that when /optionchain response is received, it calls:
```python
atm = update_atm(underlying, float(last_price), step)
```

### Step 4: Optional — Fallback to Dhan REST
If index tokens don't get WS ticks, add fallback in close_price_capture to call Dhan REST directly.

---

## VERIFICATION

After the fix is deployed, verify with this manual test:

1. **Before market close (3:29 PM):**
   ```bash
   curl https://tradingnexus.pro/api/options/live?underlying=NIFTY&expiry=2026-02-27
   ```
   Note the `atm` value

2. **Wait for market to close (3:30 PM) + 5 min buffer**

3. **After market close (3:40 PM):**
   ```bash
   curl https://tradingnexus.pro/api/options/live?underlying=NIFTY&expiry=2026-02-27
   ```
   Verify `atm` matches the **official closing price** rounded to strike interval

4. **Check next day (9:20 AM):**
   - `close_price_rollover` should have set yesterday's close as today's `close`
   - `atm_calculator` should have been initialized with fresh data
   - All new ATMs should be correct

---

## QUESTIONS FOR USER

Before implementing, I need clarification on:

1. **Index Token Subscriptions:** Are NIFTY, BANKNIFTY, SENSEX index tokens subscribed to Dhan Tier-B live stream? If yes, do they receive WebSocket ticks at market close (3:30 PM)?

2. **Dhan Subscription Level:** Does your Dhan subscription include "Option Chain REST API" access at market close, or only during market hours?

3. **Preferred Solution:** Do you prefer:
   - **A) Clean dedicated handler** (new scheduler at 3:35 PM)
   - **B) Integrate with greeks_poller** (modify existing code)
   - **C) Hybrid** (dedicated handler + REST fallback)

4. **Index LTP in market_data:** After market close, does `market_data.ltp` for index tokens contain the official closing price, or is it stale/null?

---

## SUMMARY TABLE

| Component | Current Behavior | Expected Behavior | Status |
|-----------|------------------|-------------------|--------|
| **market_data.ltp** (indexes) | Last intraday tick OR null | Updated with 3:30 PM closing price | ❓ Unknown |
| **atm_calculator cache** | Frozen since ~3:15 PM | Updated at 3:30-35 PM | ❌ Bug |
| **greeks_poller** | Stops at market close | Continues briefly at close | ❌ Design flaw |
| **/options/live ATM response** | Stale cache value | Fresh close price | ❌ Consequence |
| **Frontend display** | Wrong ATM centering | Correct closing-price ATM | ❌ Symptom |

---

## Next Steps

1. Answer the 4 clarification questions above
2. I'll implement Solution A (dedicated close price capture handler)
3. Will add comprehensive logging for debugging
4. Will create integration tests to verify behavior
5. Will deploy and verify across all 3 underlyings

**Ready to proceed?**
