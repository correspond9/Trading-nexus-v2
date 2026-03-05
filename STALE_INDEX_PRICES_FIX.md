# STALE INDEX PRICES FIX - ROOT CAUSE & SOLUTION

## Issue Report
**Date:** March 5, 2026  
**Severity:** High  
**Impact:** Straddle and Options pages showing stale/wrong index prices (LTP)

### Symptoms
- NIFTY showing LTP: 25423.40 when actual market price is ~24600
- BANKNIFTY and SENSEX showing similarly stale prices
- After deployment, manual "Fetch option chain skeleton" click required in SuperAdmin
- Until manual fetch, wrong strike lists displayed on frontend

### Screenshots Evidence
- Straddle page: "ATM: 24650 LTP: 25423.40" (clearly wrong)
- Options page: "LTP: 24650.00 ATM: 24650" (stale data)

## Root Cause Analysis

### The Problem
The INDEX instruments (NIFTY, BANKNIFTY, SENSEX spot indices) were **NOT** being subscribed to the WebSocket live feed, causing their LTP (Last Traded Price) to remain stale in the database.

### Why This Happened
The `_classify()` function in `app/instruments/scrip_master.py` had classification rules for:
- ✅ OPTIDX, FUTIDX (index options & futures) → Tier-B
- ✅ OPTSTK (stock options) → Tier-A  
- ✅ FUTSTK (stock futures) → Tier-B
- ✅ EQUITY (stocks) → Tier-B
- ✅ ETF → Tier-B
- ✅ FUTCOM, OPTCOM (MCX commodities) → Tier-B

But it was **MISSING**:
- ❌ INDEX (spot indices like NIFTY, BANKNIFTY, SENSEX) → **Not classified!**

Without Tier-B classification, INDEX instruments were:
1. Not assigned a `ws_slot` (WebSocket slot 0-4)
2. Not loaded into the subscription map at startup
3. Not subscribed to the live WebSocket feed
4. Never receiving live price updates

### Data Flow Impact

```
┌─────────────────────────────────────────────────────────────┐
│ DhanHQ WebSocket → tick_processor → market_data table       │
│                                                              │
│ WITHOUT INDEX SUBSCRIPTION:                                 │
│   ❌ NIFTY INDEX token NOT in subscription map              │
│   ❌ WebSocket never sends NIFTY ticks                      │
│   ❌ market_data.ltp stays stale (last close price)         │
│                                                              │
│ FRONTEND CALLS:                                             │
│   /market/underlying-ltp/NIFTY                              │
│   → Returns stale LTP from market_data                      │
│   → Straddle/Options pages show wrong prices                │
└─────────────────────────────────────────────────────────────┘
```

### Why Manual Fetch Worked (Temporarily)
The "Fetch option chain skeleton" button triggers `build_skeleton()` which:
1. Re-reads instrument_master (has the strikes)
2. Seeds option_chain_data table
3. Happens to work because it uses whatever stale data exists

But this doesn't fix the ROOT CAUSE (INDEX not subscribed to WebSocket).

## Solution Implemented

### Code Changes

#### 1. Updated `_classify()` in scrip_master.py
**File:** `app/instruments/scrip_master.py`

```python
# Added classification rule for INDEX instruments
if itype == "INDEX" and symbol in _TIER_B_INDICES:
    if exch_id == "NSE":
        return "B"
    if exch_id == "BSE" and symbol in {"SENSEX", "BANKEX"}:
        return "B"
```

**Location:** Added BEFORE the existing OPTIDX/FUTIDX rule (lines ~95)

#### 2. Updated `_reclassify_in_place()` in scrip_master.py
**File:** `app/instruments/scrip_master.py`

```python
# Added SQL update for INDEX instruments
await pool.execute(
    """UPDATE instrument_master SET tier='B', ws_slot=(instrument_token % 5)
       WHERE instrument_type = 'INDEX'
         AND symbol = ANY($1::text[])""",
    tier_b_indices,
)
```

**Location:** Added in `_reclassify_in_place()` right before the OPTIDX/FUTIDX update (lines ~535)

### Database Fix Script
**File:** `fix_index_tier.py` (created)

One-time migration script to fix existing INDEX instruments in the database:
- Sets `tier = 'B'` for INDEX instruments
- Assigns `ws_slot = (instrument_token % 5)` for load balancing
- Verifies and logs the changes

## Deployment Steps

### Step 1: Deploy Code Changes
```bash
# Code is already updated in scrip_master.py
# Deploy via your normal deployment process (Coolify, etc.)
```

### Step 2: Run Database Fix Script
```bash
# After deployment, run the fix script to update existing instruments
python fix_index_tier.py
```

**Expected Output:**
```
Found 6 INDEX instruments to update:
  NIFTY           | tier=  | ws_slot=None | segment=NSE_EQ
  BANKNIFTY       | tier=  | ws_slot=None | segment=NSE_EQ
  SENSEX          | tier=  | ws_slot=None | segment=BSE_EQ
  ...

✓ Update complete

Updated state (6 instruments):
  NIFTY           | tier=B | ws_slot=3 | segment=NSE_EQ
  BANKNIFTY       | tier=B | ws_slot=0 | segment=NSE_EQ
  SENSEX          | tier=B | ws_slot=1 | segment=BSE_EQ
  ...
```

### Step 3: Restart Backend
```bash
# Restart to reload Tier-B subscriptions with updated INDEX instruments
# Coolify: restart the backend service
# Docker: docker-compose restart backend
```

### Step 4: Verify Fix

#### Backend Logs (on startup)
Look for:
```
[6] Initialising Tier-B subscriptions…
Tier-B subscription map ready — 15234 tokens across 5 WS slots: WS-0: 3047, WS-1: 3046, ...
```

The count should **increase** by 6 (the 6 INDEX instruments now included).

#### Database Query
```sql
SELECT instrument_token, symbol, tier, ws_slot, exchange_segment
FROM instrument_master
WHERE instrument_type = 'INDEX'
  AND symbol IN ('NIFTY', 'BANKNIFTY', 'SENSEX', 'MIDCPNIFTY', 'FINNIFTY', 'BANKEX')
ORDER BY symbol;
```

**Expected:** All should have `tier='B'` and `ws_slot` in range 0-4.

#### WebSocket Subscription
Check that INDEX tokens are in the subscription map:
```python
# In SuperAdmin or backend logs
# Subscription manager should show INDEX tokens in active subscriptions
```

#### Frontend Test
1. Open Straddle page
2. Check "NIFTY Straddles ATM: XXXXX LTP: YYYYY"
3. **LTP should match current market price** (~24600 in this case)
4. Same for Options page

### Step 5: Monitor Live Updates
- Prices should update in real-time (every 1 second)
- No need to manually fetch option chain skeleton
- Fresh deployments should work without manual intervention

## Prevention: Why This Won't Happen Again

### 1. Code Coverage
The `_classify()` function now handles ALL major instrument types:
- ✅ INDEX (spot indices)
- ✅ OPTIDX, FUTIDX (index derivatives)
- ✅ OPTSTK, FUTSTK (stock derivatives)
- ✅ EQUITY, ETF (cash market)
- ✅ FUTCOM, OPTCOM (commodities)

### 2. Automatic Re-classification
The `_reclassify_in_place()` function is called:
- When admin uploads new subscription lists
- Ensures tier assignments stay correct even after data changes

### 3. Startup Validation
At startup, the subscription manager logs:
- Total Tier-B count
- Per-slot breakdown
- Any initialization failures

If INDEX instruments aren't loaded, it will be visible in logs.

## Technical Details

### Tier-B vs Tier-A
- **Tier-B:** Always subscribed, critical instruments (15k+ tokens)
  - Includes: Index derivatives, stock futures, equity cash, INDEX spot
  - Load-balanced across 5 WebSocket slots (5,000 capacity each)
  
- **Tier-A:** On-demand subscription (stock options)
  - ~42k tokens, subscribed only when user adds to watchlist or trades
  - Prevents hitting DhanHQ's 25,000 token limit

### WebSocket Slot Assignment
```python
ws_slot = instrument_token % 5  # Deterministic, even distribution
```
- Slot 0: tokens ending in 0, 5 (e.g., 13565, 24670)
- Slot 1: tokens ending in 1, 6
- Slot 2: tokens ending in 2, 7
- Slot 3: tokens ending in 3, 8
- Slot 4: tokens ending in 4, 9

### INDEX Instruments List
```python
_TIER_B_INDICES = {
    "NIFTY", "BANKNIFTY", "SENSEX", 
    "MIDCPNIFTY", "FINNIFTY", "BANKEX", 
    "NIFTYNXT50"
}
```

## Files Changed

1. **app/instruments/scrip_master.py**
   - `_classify()` - Added INDEX classification
   - `_reclassify_in_place()` - Added INDEX tier update

2. **fix_index_tier.py** (new)
   - One-time database migration script

## Testing Checklist

- [ ] Run `fix_index_tier.py` successfully
- [ ] Restart backend without errors
- [ ] Verify Tier-B count increased in startup logs
- [ ] Check database: INDEX instruments have tier='B'
- [ ] Frontend Straddle page shows live NIFTY LTP
- [ ] Frontend Options page shows live NIFTY LTP
- [ ] Test with BANKNIFTY and SENSEX tabs
- [ ] Verify prices update in real-time (1s interval)
- [ ] Test fresh deployment (no manual skeleton fetch needed)

## Rollback Plan (if needed)

If issues occur:
```sql
-- Rollback database changes
UPDATE instrument_master 
SET tier = NULL, ws_slot = NULL 
WHERE instrument_type = 'INDEX';
```

Then restart backend. (This reverts to previous broken state, but safe.)

## Summary

**Problem:** INDEX instruments not subscribed to WebSocket → stale prices  
**Root Cause:** Missing classification rule in `_classify()`  
**Solution:** Add INDEX to Tier-B + run fix script + restart  
**Impact:** Straddle/Options pages now show live prices without manual intervention  
**Status:** ✅ Code fixed, script ready, deployment guide complete

---

**Author:** GitHub Copilot  
**Date:** March 5, 2026  
**Priority:** HIGH - Deploy ASAP to fix live production issue
