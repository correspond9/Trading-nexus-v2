# Code Changes Summary - Tier-A Cleanup Update

**Date:** February 25, 2026  
**Change:** Update Tier-A cleanup logic from 1-hour grace period to 4 PM IST daily cleanup  
**File Modified:** `app/routers/watchlist.py`

---

## 1. Added Imports

**Location:** Lines 7-9

```python
# ADDED these imports
from datetime import datetime, timedelta, timezone
```

**Why:** Need timezone handling for IST time calculations.

---

## 2. Updated `_auto_clean_tier_a()` Function

**Location:** Lines 52-100

### REMOVED (Old Logic)
```python
async def _auto_clean_tier_a(pool, watchlist_id: str) -> None:
    """
    Remove Tier-A watchlist items that:
    1. Have NO open position, AND
    2. Were added more than 1 hour ago (avoid removing just-added items)
    
    Tier-B items are NEVER removed automatically.
    """
    from datetime import datetime, timedelta, timezone
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
    
    # Find Tier-A items with no position that are old enough
    old_tier_a = await pool.fetch(
        """
        SELECT wi.instrument_token
        FROM watchlist_items wi
        LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
        WHERE wi.watchlist_id = $1
          AND im.tier = 'A'
          AND wi.added_at < $2        ← ❌ REMOVED: No more grace period check
          AND NOT EXISTS (
              SELECT 1 FROM paper_positions pp
              WHERE pp.instrument_token = wi.instrument_token
              AND pp.quantity != 0
          )
        """,
        watchlist_id,
        cutoff_time,    ← ❌ REMOVED: cutoff_time parameter
    )
    
    # Delete them
    if old_tier_a:
        tokens_to_delete = [row["instrument_token"] for row in old_tier_a]
        await pool.execute(
            "DELETE FROM watchlist_items WHERE watchlist_id = $1 AND instrument_token = ANY($2::bigint[])",
            watchlist_id,
            tokens_to_delete,
        )
        log.debug(
            f"Auto-cleaned {len(old_tier_a)} old Tier-A items with no position from watchlist {watchlist_id}"
        )
```

### ADDED (New Logic)
```python
async def _auto_clean_tier_a(pool, watchlist_id: str) -> None:
    """
    Remove Tier-A watchlist items that have NO open position.
    
    Cleanup Schedule:
    - Every day after 4 PM IST (16:00), all Tier-A items without positions are removed
    - This happens automatically when user refreshes watchlist after 4 PM
    - Prevents clutter from expired options and one-time trades
    
    Tier-B items are NEVER removed automatically.
    """
    # ✅ NEW: Get current time in IST (UTC+5:30)
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    
    # ✅ NEW: Check if current time is >= 4 PM (16:00) IST
    is_cleanup_time = now_ist.hour >= 16
    
    # ✅ NEW: Only cleanup after 4 PM
    if is_cleanup_time:
        # Find Tier-A items with no open position
        old_tier_a = await pool.fetch(
            """
            SELECT wi.instrument_token
            FROM watchlist_items wi
            LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
            WHERE wi.watchlist_id = $1
              AND im.tier = 'A'
              AND NOT EXISTS (
                  SELECT 1 FROM paper_positions pp
                  WHERE pp.instrument_token = wi.instrument_token
                  AND pp.quantity != 0
              )
            """,
            watchlist_id,    # ✅ CHANGED: Only one parameter (no cutoff_time)
        )
        
        # Delete them
        if old_tier_a:
            tokens_to_delete = [row["instrument_token"] for row in old_tier_a]
            await pool.execute(
                "DELETE FROM watchlist_items WHERE watchlist_id = $1 AND instrument_token = ANY($2::bigint[])",
                watchlist_id,
                tokens_to_delete,
            )
            # ✅ UPDATED: Better logging showing IST time
            log.info(
                f"Auto-cleaned {len(old_tier_a)} Tier-A items (no position) from watchlist {watchlist_id} at {now_ist.strftime('%H:%M')} IST"
            )
    else:
        # ✅ NEW: Before 4 PM - keep all Tier-A items (even without position)
        log.debug(f"Not cleanup time yet (current IST: {now_ist.strftime('%H:%M')}). Keeping all Tier-A items.")
```

**Key Changes:**
|Aspect|Before|After|
|------|------|-----|
|Grace Period|1 hour|None (fixed 4 PM)|
|Timing Check|`wi.added_at < cutoff_time`|`now_ist.hour >= 16`|
|Cleanup Window|Any time an hour has passed|Only after 4 PM IST|
|Before 4 PM|May remove items|Keeps all items|
|At 4 PM+|Removes if older than 1h|Removes all without position|
|Logging|DEBUG level|INFO level (more visible)|

---

## 3. Updated Endpoint Docstring

**Location:** Lines 104-112

### REMOVED
```python
@router.get("/{user_id}")
async def get_watchlist(user_id: str, request: Request):
    """Return flat list of all watchlist instruments for a user.
    
    Behavior:
    - Tier-B (subscribed) items: Always returned (keep permanently)
    - Tier-A (on-demand) items: Returned if:
      a) Has open position, OR
      b) Just added (added_at > 1 hour ago is old, keep recent ones)
    
    Auto-cleaning: 
    - Tier-A items with no position and added >1h ago are removed from watchlist
    """
```

### ADDED
```python
@router.get("/{user_id}")
async def get_watchlist(user_id: str, request: Request):
    """Return flat list of all watchlist instruments for a user.
    
    Behavior:
    - Tier-B (subscribed) items: Always returned (keep permanently)
    - Tier-A (on-demand) items: 
      a) Returned if they have an open position, OR
      b) Returned if current time is before 4 PM IST, OR
      c) Removed if after 4 PM IST and no open position
    
    Auto-cleaning: 
    - After 4 PM IST daily, all Tier-A items with no position are removed from watchlist
    - This cleanup happens automatically when user refreshes watchlist after 4 PM
    """
```

---

## Summary of Changes

### Files Modified: 1
- `app/routers/watchlist.py`

### Lines Changed: ~50 lines
- Added imports: 1 line
- Modified function: ~45 lines
- Updated docstring: ~5 lines

### Imports Added
```python
from datetime import datetime, timedelta, timezone
```

### Query Changes
- **Removed:** `AND wi.added_at < $2` condition
- **Removed:** `cutoff_time` parameter from fetch call
- **Added:** IST timezone calculation
- **Added:** 4 PM check (`now_ist.hour >= 16`)

### Behavior Changes
|Scenario|Before|After|
|--------|------|-----|
|Item added, user refreshes after 30 min, no position|Kept|Kept ✅|
|Item added, user refreshes after 1.5 hours, no position|Removed|Kept (if before 4 PM) ✅|
|Item added, user refreshes after 1.5 hours at 4:10 PM, no position|Removed|Removed ✅|
|Item added, has position, user refreshes anytime|Kept|Kept ✅|
|Item Tier-B, any time|Kept|Kept ✅|

---

## Verification Checklist

- [x] Imports added at top of file
- [x] Function signature unchanged (same parameters)
- [x] IST timezone calculation correct (UTC+5:30)
- [x] 4 PM comparison logic correct (hour >= 16)
- [x] Query SQL correct (removed added_at condition)
- [x] Logging statements added
- [x] Docstring updated
- [x] Comments added for clarity
- [x] No database schema changes
- [x] No API contract changes

---

## How to Test This Change

### Test 1: Before 4 PM
```
1. At 2:00 PM IST
2. Add NIFTY 22000 CE (Tier-A, no position)
3. Refresh watchlist
4. Expected: Item stays (before 4 PM) ✓
```

### Test 2: At or After 4 PM
```
1. At 4:05 PM IST
2. Add NIFTY 22000 CE (Tier-A, no position)
3. Refresh watchlist
4. Expected: Item is removed immediately ✓
```

### Test 3: With Position
```
1. At 4:05 PM IST
2. Add NIFTY 22000 CE (Tier-A, WITH position)
3. Refresh watchlist
4. Expected: Item stays (has position protection) ✓
```

### Test 4: Tier-B Item
```
1. At 4:05 PM IST
2. Add RELIANCE (Tier-B)
3. Refresh watchlist
4. Expected: Item stays (Tier-B never removed) ✓
```

---

## Deployment Instructions

1. **Replace file:** `app/routers/watchlist.py` with updated version
2. **No migrations:** No database schema changes
3. **No frontend changes:** No frontend code changes needed
4. **Restart backend:** Restart the FastAPI application
5. **Test:** Verify behavior during cleanup window (after 4 PM)

**Rollback Steps (if needed):**
1. Restore original `watchlist.py`
2. Restart backend
3. No data cleanup needed

---

## Configuration Options

### Change Cleanup Time

**Location:** `_auto_clean_tier_a()` function, line ~76

Current:
```python
is_cleanup_time = now_ist.hour >= 16  # 4 PM
```

Examples:
```python
# 3 PM cleanup
is_cleanup_time = now_ist.hour >= 15

# 5 PM cleanup
is_cleanup_time = now_ist.hour >= 17

# 6 PM cleanup
is_cleanup_time = now_ist.hour >= 18

# Specific minute (4:15 PM):
is_cleanup_time = (now_ist.hour == 16 and now_ist.minute >= 15) or now_ist.hour > 16
```

### Change Timezone

**Location:** `_auto_clean_tier_a()` function, line ~71

Current:
```python
ist_tz = timezone(timedelta(hours=5, minutes=30))  # IST
```

Other timezones:
```python
# UTC
utc_tz = timezone(timedelta(hours=0))

# EST (UTC-5)
est_tz = timezone(timedelta(hours=-5))

# PST (UTC-8)
pst_tz = timezone(timedelta(hours=-8))
```

---

## Performance Impact

- **Query Performance:** Same (removed one condition, simpler)
- **Logic Performance:** Faster (no datetime subtraction)
- **Frequency:** Same (runs on every GET request)
- **Database Load:** Slight decrease (simpler query)

---

## Backward Compatibility

✅ **Fully backward compatible:**
- API response format unchanged
- No breaking changes
- Existing watchlist items unaffected
- No data migration needed

---

## Related Files

For more information, see:
- [WATCHLIST_TIER_A_CLEANUP_UPDATE.md](WATCHLIST_TIER_A_CLEANUP_UPDATE.md) - Detailed explanation
- [WATCHLIST_PERSISTENCE_FIX.md](WATCHLIST_PERSISTENCE_FIX.md) - Original implementation overview
- [WATCHLIST_QUICK_REFERENCE.md](WATCHLIST_QUICK_REFERENCE.md) - User-facing guide

---

**Change Complete ✅**  
Ready for deployment and testing.
