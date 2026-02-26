# ✅ Watchlist Persistence Fix - Quick Start Guide

## What Was Changed?

Your watchlist now has **intelligent persistence**:

| Item Type | Behavior | Badge |
|-----------|----------|-------|
| **Tier-B** (Subscribed) | Stays forever | 🟢 Tier-B |
| **Tier-A** (On-demand) with position | Stays while you hold it | 🟠 Tier-A 🟢 Position |
| **Tier-A** (On-demand) no position | Auto-removed after 1 hour | 🟠 Tier-A 🔴 No Position |

---

## Where to Look for the Changes

### 1. Backend Changes
**File:** `app/routers/watchlist.py`

**What Changed:**
- GET `/watchlist/{user_id}` now returns:
  - `tier`: A or B
  - `has_position`: true/false
  - `added_at`: timestamp

- New function `_auto_clean_tier_a()`:
  - Removes old Tier-A items without positions
  - Runs automatically on each GET request
  - Grace period: 1 hour (items added recently are kept)

### 2. Frontend Changes
**File:** `frontend/src/pages/WATCHLIST.jsx`

**What Changed:**
- Badges show Tier classification:
  - Orange "Tier-A" for on-demand items
  - Green "Tier-B" for subscribed items

- Position indicator for Tier-A only:
  - "✓ Position" (green) = Will be kept
  - "⊘ No Position" (red) = Will be removed if old

---

## How It Works

### Step-by-Step Example

**Scenario 1: Add a Tier-B Item (RELIANCE)**
```
1. Click: Search → RELIANCE → Add to Watchlist
2. View: [RELIANCE] [Tier-B]
3. Result: ✅ Stays forever (even after refresh/logout)
```

**Scenario 2: Add a Tier-A Item (NIFTY Option)**
```
1. Click: Search → NIFTY 22000 CE → Add to Watchlist
2. View: [NIFTY 22000 CE] [Tier-A] [⊘ No Position]
3. Time 0-1 hour: ✅ Item stays (grace period)
4. Time 1+ hours: ❌ Item auto-removed (old & no position)
```

**Scenario 3: Add Tier-A Item & Open Position**
```
1. Click: Search → NIFTY 22000 CE → Add to Watchlist
2. View: [NIFTY 22000 CE] [Tier-A] [⊘ No Position]
3. Click: Place BUY order
4. View (refreshed): [NIFTY 22000 CE] [Tier-A] [✓ Position]
5. Result: ✅ Item now protected (stays indefinitely while position open)
```

---

## How to Test

### Test 1: Create a Watchlist with Both Tiers
1. Add **RELIANCE** (Tier-B) → Should show green badge
2. Add **NIFTY 22000 CE** (Tier-A) → Should show orange badge
3. Refresh page → Both should be there

### Test 2: Verify Grace Period
1. Add a new Tier-A item (NIFTY 22100 PE)
2. Badge shows "⊘ No Position"
3. Refresh immediately → Should still be there ✓
4. Refresh after 30 minutes → Should still be there ✓
5. Refresh after 2 hours → Should be gone ✓

### Test 3: Position Protection
1. Add Tier-A item: NIFTY 22000 CE
2. Creates with "⊘ No Position" badge
3. Place a BUY order in that option
4. Refresh page → Badge changes to "✓ Position"
5. Wait any amount of time
6. Keep refreshing → Item never disappears ✓

### Test 4: Manual Deletion Still Works
1. Add any item
2. Click the "×" delete button
3. Item should disappear immediately ✓

---

## What You'll See

### Visual Changes in UI

**Before:**
```
WATCHLIST
├─ RELIANCE
├─ NIFTY 50
└─ (items keep disappearing)
```

**After:**
```
WATCHLIST
├─ RELIANCE                    [Tier-B]
├─ NIFTY 50                    [Tier-B]
├─ NIFTY 22000 CE             [Tier-A] [✓ Position]
└─ NIFTY 22100 PE             [Tier-A] [⊘ No Position]
                               (will disappear in 1h)
```

---

## Common Questions

### Q: Why did my item disappear?
**A:** Check the badge:
- [Tier-A] [⊘ No Position] + older than 1 hour = auto-removed ✓
- [Tier-B] = won't disappear (it's subscribed)
- [Tier-A] [✓ Position] = won't disappear while you hold it

### Q: Can I keep a Tier-A item longer?
**A:** Yes! Open a position in it → badge changes to [✓ Position] → stays indefinitely

### Q: How do I know if item is Tier-A or B?
**A:** Look at the colored badge:
- 🟢 Green = Tier-B (subscribed, permanent)
- 🟠 Orange = Tier-A (on-demand, temporary)

### Q: Can I change an item's tier?
**A:** Contact admin. Tier is set by the instrument configuration.

### Q: Is the 1-hour grace period fixed?
**A:** It can be adjusted. Current setting: 1 hour. If too short/long, ask admin.

---

## Technical Details (If You're Curious)

### Query That Removes Items
```sql
DELETE FROM watchlist_items
WHERE:
  - Item is Tier-A (not subscribed)
  - AND added more than 1 hour ago
  - AND user has NO open position in this instrument
```

### API Response Now Includes
```json
{
  "tier": "A",              // or "B"
  "has_position": false,    // or true
  "added_at": "2026-02-25"  // timestamp
}
```

### Grace Period Setting
```python
# In app/routers/watchlist.py
cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
# Change 'hours=1' to different value to adjust grace period
```

---

## Timeline

**February 25, 2026:**
- ✅ Implemented Tier-A auto-cleanup logic
- ✅ Updated API to include tier/position info
- ✅ Added visual badges to UI
- ✅ Created documentation
- 🔄 Awaiting user testing and feedback

**Next Steps:**
1. Test the implementation
2. Verify behavior matches expectations
3. Report any issues
4. Adjust grace period if needed

---

## Support

**If Something Doesn't Work:**
1. Check the badges (what tier is the item?)
2. Check if you have a position open
3. Check how long the item has been in watchlist
4. Report the exact behavior you're seeing

**Expected Behavior Checklist:**
- [ ] Tier-B items never disappear on refresh
- [ ] Tier-A items with position never disappear
- [ ] Tier-A items without position disappear after 1 hour
- [ ] Manual delete button always works
- [ ] Badges display correctly (colors/text)

---

**🎉 Your watchlist is now smarter and won't clutter with old on-demand items!**

Questions? Check [WATCHLIST_PERSISTENCE_FIX.md](WATCHLIST_PERSISTENCE_FIX.md) for detailed explanation.
