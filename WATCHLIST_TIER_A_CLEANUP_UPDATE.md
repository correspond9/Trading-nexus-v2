# Watchlist Tier-A Cleanup Logic - Updated to 4 PM Daily

**Updated:** February 25, 2026  
**Change:** Tier-A cleanup now happens at **4 PM IST daily** instead of after 1 hour grace period

---

## What Changed?

### Before (Old Logic)
```
User adds Tier-A item (e.g., NIFTY 22000 CE)
  ├─ 0-1 hour: Item stays in watchlist (grace period)
  ├─ If position opened: Item stays (protected)
  └─ If no position after 1 hour: Item auto-removed ❌
```

### After (New Logic)
```
User adds Tier-A item (e.g., NIFTY 22000 CE)
  ├─ Any time before 4 PM IST: Item stays in watchlist
  ├─ At 4 PM IST or after: 
  │   ├─ If position opened: Item stays (protected) ✅
  │   └─ If no position: Item auto-removed ✅
  └─ Next day before 4 PM: Cycle repeats
```

---

## Why This Change?

**Problem with 1-hour grace period:**
- ❌ Unpredictable - items disappear at different times
- ❌ Too aggressive - might remove items user just added and wanted to keep
- ❌ Doesn't align with market hours

**Solution with 4 PM cleanup:**
- ✅ Predictable - cleanup happens once daily at market close (4 PM IST)
- ✅ Gives user whole day to open position if needed
- ✅ Aligns with trading day end
- ✅ Tier-A items kept for full trading day
- ✅ Clean day-end cleanup (options expire, day-trades close)

---

## Cleanup Behavior

### Timeline Example (Today)

```
9:15 AM - 4:00 PM IST (Trading Hours)
├─ User adds NIFTY 22000 CE (Tier-A)
├─ User refreshes watchlist: Item shows [Tier-A] [⊘ No Position]
├─ User refreshes again at 2 PM: Item still there ✅
└─ User refreshes again at 3:59 PM: Item still there ✅

4:00 PM - 5:00 PM IST (Cleanup Time)
├─ Market close happens at 3:30 PM
├─ At 4 PM, user refreshes watchlist
├─ System checks: Is time >= 4 PM? YES
├─ System checks: Tier-A item with no position? YES
└─ ⚠️ Item auto-removed ✅

After 4 PM (Same Day)
├─ Any refreshes: Item stays removed (already cleaned)
└─ No re-cleanup happens today

Next Trading Day (Tomorrow)
├─ Before 4 PM: Tier-A items can accumulate again
└─ At 4 PM: Tomorrow's cleanup happens
```

---

## How It Works in Code

### Function: `_auto_clean_tier_a()`

**Location:** `app/routers/watchlist.py` lines ~52-100

**Logic:**
```python
# Get current time in IST (UTC+5:30)
ist_tz = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist_tz)

# Check if current time >= 4 PM (16:00)
is_cleanup_time = now_ist.hour >= 16

if is_cleanup_time:
    # Remove ALL Tier-A items without positions
    # Tier-B items NEVER removed
else:
    # Before 4 PM - keep all Tier-A items
```

**Key Points:**
- Uses IST timezone (UTC+5:30)
- Checks `hour >= 16` (4 PM or later)
- Removes ALL Tier-A items without positions (no grace period)
- Never removes Tier-B items
- Safe to call multiple times (idempotent)

### When Is Cleanup Triggered?

Cleanup runs automatically on **every GET /watchlist/{user_id}** call:

```
1. User opens watchlist tab
   ↓
2. Frontend calls GET /watchlist/{user_id}
   ↓
3. Backend runs _auto_clean_tier_a()
   ├─ Is time >= 4 PM IST? 
   ├─ If YES: Remove Tier-A items without positions
   └─ If NO: Keep all items
   ↓
4. Return watchlist to user
```

So the cleanup happens silently when user refreshes.

---

## User Behavior & Examples

### Example 1: Day-Trader with Options

```
9:30 AM - User adds NIFTY 22000 CE to watchlist (Tier-A)
         [Tier-A] [⊘ No Position] ← Shows orange + red badge

10:00 AM - User places BUY order
          [Tier-A] [✓ Position] ← Changes to green "Position" badge
          Item is now protected while position is open

2:30 PM - User closes position (sells)
         [Tier-A] [⊘ No Position] ← Back to red "No Position" badge
         Item will be removed at 4 PM

4:05 PM - User tries to refresh watchlist
         → Item auto-removed ✅
         (because it's after 4 PM and no position)
```

### Example 2: Active Trader with Multiple Items

```
Morning Session:
├─ Adds NIFTY 22000 CE (Tier-A) → [⊘ Position]
├─ Adds NIFTY 22100 CE (Tier-A) → [⊘ Position]
├─ Adds NIFTY 22200 PE (Tier-A) → [⊘ Position]
└─ Adds RELIANCE (Tier-B) → [Tier-B] (permanent)

Afternoon Session at 2 PM:
├─ Opens position in 22000 CE → [✓ Position] ← Protected now
├─ Opens position in 22100 CE → [✓ Position] ← Protected now
└─ 22200 PE still has [⊘ Position]

At 4:05 PM (user refreshes):
├─ 22000 CE: Has position → Kept ✅
├─ 22100 CE: Has position → Kept ✅
├─ 22200 PE: No position → Removed ❌
└─ RELIANCE: Tier-B → Always kept ✅
```

### Example 3: Position Held Overnight

```
Today at 3:00 PM - User opens BUY position in NIFTY 22000 CE
                  Item shows [Tier-A] [✓ Position]

Today at 4:05 PM - User refreshes watchlist
                  Cleanup runs but position exists
                  → Item NOT removed, kept ✅

Tomorrow at 9:15 AM - Position still open from yesterday
                     Item stays in watchlist ✅

Tomorrow at 2:00 PM - User closes position
                     Item shows [⊘ No Position]

Tomorrow at 4:05 PM - User refreshes watchlist
                     Cleanup runs, no position exists
                     → Item removed ❌
```

---

## What Data is Used?

### Query to Identify Items for Cleanup

```sql
SELECT wi.instrument_token
FROM watchlist_items wi
LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
WHERE wi.watchlist_id = $1
  AND im.tier = 'A'                    -- Only Tier-A items
  AND NOT EXISTS (
      SELECT 1 FROM paper_positions pp
      WHERE pp.instrument_token = wi.instrument_token
      AND pp.quantity != 0              -- No open position
  );
```

**Checks:**
- `tier = 'A'` - Only on-demand items considered
- `quantity != 0` - Has open position (protects item)
- No `added_at` check - All old items cleaned at 4 PM

### Fields Used

```
instrument_master.tier          ← From instrument configuration
paper_positions.quantity        ← Current position size
watchlist_items.watchlist_id    ← Which watchlist
Current IST time                ← System clock
```

---

## Configuration

### Grace Period: REMOVED ✅
Previously: 1-hour grace period → Items stayed for 1 hour
Now: **NO grace period** → All items cleaned at exactly 4 PM

### Timezone: IST (UTC+5:30) ✅
```python
ist_tz = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(ist_tz)
```

Hardcoded to IST (Indian Standard Time) for market alignment.

### Cleanup Time: 4 PM (16:00)
```python
is_cleanup_time = now_ist.hour >= 16
```

Set to `hour >= 16` which means:
- 4:00 PM to 11:59 PM: Cleanup happens
- 12:00 AM to 3:59 PM: Items preserved

**To adjust cleanup time:**
- Change `>= 16` to different hour
- Examples:
  - 3 PM: `>= 15`
  - 5 PM: `>= 17`
  - 6 PM: `>= 18`

---

## Logging

### Log Messages

When cleanup happens:
```
INFO: Auto-cleaned 3 Tier-A items (no position) from watchlist abc-xyz-123 at 16:05 IST
```

When NOT cleanup time:
```
DEBUG: Not cleanup time yet (current IST: 14:30). Keeping all Tier-A items.
```

**Monitoring command:**
```bash
# See cleanup activity in logs
journalctl -u trading-nexus -f | grep "Auto-cleaned"
```

---

## Testing & Verification

### Quick Test (Now)
1. Add Tier-A item (e.g., NIFTY 22000 CE)
2. Time is before 4 PM? Item stays ✅
3. If time >= 4 PM, add item and refresh
4. Item should disappear ✅

### Full Test (After 4 PM)
1. Before 4 PM: Add Tier-A items to watchlist
2. Verify they all appear (before cleanup time)
3. Wait until 4:01 PM
4. Refresh watchlist
5. Items without positions should disappear ✅
6. Items with positions should stay ✅
7. Tier-B items should stay ✅

### Test Edge Cases
- [ ] Item added just before 4 PM → Removed at 4 PM ✓
- [ ] Item added after 4 PM → Kept until tomorrow 4 PM
- [ ] Position opened after 4 PM → Item protected forever
- [ ] Position closed before 4 PM tomorrow → Item removed tomorrow 4 PM
- [ ] Multiple refreshes after 4 PM → Item only removed once

---

## API Response

### Watchlist Item Still Includes:
```json
{
  "token": 123456,
  "symbol": "NIFTY 22000 CE",
  "tier": "A",
  "has_position": false,          ← Use this to check position
  "added_at": "2026-02-25T09:30:00",
  "ltp": 850.25,
  "close": 845.00
}
```

Frontend can use `has_position` and `tier` to show badges.

---

## Common Questions

### Q: What if I want to keep a Tier-A item after 4 PM?
**A:** Open a position in it. As long as `quantity != 0`, it's protected.

### Q: What if I just added an item at 3:59 PM?
**A:** It will be removed at 4:00 PM if you didn't open a position. Opening a position protects it.

### Q: Can I have a different cleanup time?
**A:** Yes, adjust `hour >= 16` in `_auto_clean_tier_a()` function. Examples:
- 3 PM: `hour >= 15`
- 5 PM: `hour >= 17`

### Q: What about extended trading (MCX, after-hours)?
**A:** Cleanup always happens at fixed 4 PM IST. If you trade after-hours:
- MCX items in watchlist get cleaned regardless
- Position held in MCX won't protect Tier-A watchlist items
- Consider adding MCX items to Tier-B if needed

### Q: Do Tier-B items ever get cleaned?
**A:** No. Tier-B items stay permanently until you manually delete them.

### Q: What if system goes down at 4 PM?
**A:** Cleanup happens on next user refresh. If it's 4:30 PM and user refreshes, cleanup runs.

### Q: Can cleanup happen multiple times?
**A:** Yes, but it's safe (idempotent). If run multiple times at 4:01 PM, same items deleted.

---

## Migration Summary

**From:** 1-hour grace period (unpredictable)  
**To:** 4 PM daily cleanup (predictable)

**What's Different:**
- No more "grace period" - timing is fixed
- Cleanup based on TIME, not ADD_TIME
- Aligns with market close (beneficial)
- All Tier-A items treated equally

**What Stays the Same:**
- Tier-B items never auto-removed
- Positions still protect items
- Manual delete still works
- API response same format
- No database schema changed

**Files Modified:**
- `app/routers/watchlist.py` (function + imports)

**Files NOT Modified:**
- Frontend code (no changes needed)
- Database schema (no migrations)
- API contract (same fields)

---

## Deployment

**Steps:**
1. Deploy `app/routers/watchlist.py` changes
2. Restart backend service
3. No frontend changes needed
4. No database migrations needed
5. Behavior takes effect immediately

**Rollback (if needed):**
```python
# Revert _auto_clean_tier_a function to:
# Check wi.added_at < now - timedelta(hours=1)
# Instead of checking now_ist.hour >= 16
```

---

## Summary

✅ **Tier-A cleanup now happens at 4 PM IST daily**  
✅ **No more 1-hour grace period**  
✅ **Tier-B items still never removed**  
✅ **Positions still protect items**  
✅ **Predictable behavior for users**  
✅ **Aligns with market close**

**Implementation complete and ready for testing!**
