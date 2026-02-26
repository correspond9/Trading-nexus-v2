# Watchlist Persistence Fix - Implementation Complete ✅

**Date:** February 25, 2026  
**Issue:** Instruments get wiped from watchlist on refresh  
**Solution:** Implement tier-based persistence logic  
**Status:** ✅ IMPLEMENTED

---

## 🎯 The Problem

When adding instruments to the watchlist:
- ❌ Items disappear on page refresh
- ❌ No distinction between permanent (Tier-B) and temporary (Tier-A) items
- ❌ User loses track of which items will persist

## ✅ The Solution

Implement **tier-based watchlist persistence**:

### Tier Classifications

| Tier | Type | Origin | Behavior |
|------|------|--------|----------|
| **Tier-B** | Subscribed | Always enabled in feed | ✅ Keep permanently until manually deleted |
| **Tier-A** | On-Demand | Added to watchlist on-demand | ⚡ Keep if in open positions, auto-remove if not |

---

## 📋 Implementation Details

### Backend Changes (app/routers/watchlist.py)

#### 1. Updated GET /watchlist/{user_id} Endpoint
**New Response Includes:**
- `tier` - Classification (A or B)
- `has_position` - Whether instrument has open position
- `added_at` - When added to watchlist

```python
{
  "data": [
    {
      "token": 123456,
      "symbol": "RELIANCE",
      "tier": "B",              # ← NEW
      "has_position": false,    # ← NEW
      "added_at": "2026-02-25T14:30:00",  # ← NEW
      "ltp": 1410.25,
      "close": 1398.50
    }
  ]
}
```

#### 2. Auto-Clean Tier-A Items
**Function:** `_auto_clean_tier_a(pool, watchlist_id)`

**Logic:**
Remove Tier-A items if:
1. NO open position AND
2. Added >1 hour ago (grace period for just-added items)

**Execution:**
- Called automatically on every GET /watchlist request
- Prevents old Tier-A items from accumulating
- Grace period: 1 hour (prevents immediate removal)

**Example:**
```
User adds NIFTY 22000 CE (Tier-A on-demand)
├─ 0-1 hour: Kept in watchlist (grace period)
├─ If position opened: Kept permanently
└─ If no position after 1 hour: Auto-removed
```

### Frontend Changes (frontend/src/pages/WATCHLIST.jsx)

#### 1. Enhanced Data Mapping
**New Fields Tracked:**
```javascript
{
  ...existing fields...
  tier: item.tier || 'B',        // Tier-A or Tier-B
  hasPosition: item.has_position,  // Open position exists
  addedAt: item.added_at,         // Timestamp
}
```

#### 2. Visual Indicators (Badges)
**For Each Watchlist Item, Display:**
- **Tier Badge:** "Tier-A" (orange) or "Tier-B" (green)
- **Position Badge:** Shows only for Tier-A items
  - "✓ Position" (green) = Will be kept
  - "⊘ No Position" (red) = Will be removed if not used

**Display:**
```
RELIANCE [Tier-B]
NIFTY 22000 CE [Tier-A] [✓ Position]     ← Will stay
NIFTY 22100 CE [Tier-A] [⊘ No Position]  ← Will be removed
```

---

## 🔄 Complete Watchlist Lifecycle

### 1. Adding an Instrument

```
User clicks Add → Searches for NIFTY 22000 CE
                ├─ Query instrument_master for tier
                ├─ Determine if Tier-A or Tier-B
                └─ Insert into watchlist_items with timestamp

API Response includes:
  tier: "A"
  has_position: false
  added_at: "2026-02-25T14:30:00"
```

### 2. Display with Indicators

```
Frontend Renders:
- NIFTY 22000 CE [Tier-A] [⊘ No Position]
  
User sees: This is on-demand, currently not in position
```

### 3. Opening a Position

```
User opens a position in NIFTY 22000 CE
  ├─ paper_positions table updated
  └─ Next watchlist refresh shows:
      [Tier-A] [✓ Position]  ← Now protected from removal

User can trade freely without losing watchlist item
```

### 4. Closing Position & Refresh

```
User closes the position
  ├─ Waits 1 hour grace period
  ├─ Refreshes page after 1+ hours
  └─ Auto-cleanup runs:
      └─ "Is Tier-A? YES, Has position? NO, Older than 1h? YES"
         └─ Removes from watchlist

User doesn't see tool clutter
```

### 5. Tier-B Items (Never Removed)

```
User adds RELIANCE (Tier-B subscribed)
  ├─ Stays permanently
  ├─ No expiry
  ├─ Shows [Tier-B] badge
  └─ Only removed by manual delete button
```

---

## 🎨 Visual Example

```
WATCHLIST

Market Status: OPEN (11:30 AM IST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RELIANCE [Tier-B]
NSE _EQ
₹ 1,410.25   +0.86 %
BUY | SELL | ×

NIFTY 50 [Tier-B]
NSE FNO
₹ 25,482.50 +0.42%
BUY | SELL | ×

NIFTY 22000 CE [Tier-A] [✓ Position]
NSE FNO
₹ 850.25 +5.20%
BUY | SELL | ×

NIFTY 22100 CE [Tier-A] [⊘ No Position]  ← Will auto-remove if >1h old
NSE FNO
₹ 650.75 +3.10%
BUY | SELL | ×

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🧪 Testing

### Test 1: Add Tier-A Item
1. Open Watchlist
2. Add NIFTY 22000 CE (Tier-A, on-demand)
3. Should show `[Tier-A] [⊘ No Position]`
4. Close page, reopen within 1 hour
5. ✅ Item should still be there (grace period)

### Test 2: Open Position Protection
1. Add NIFTY 22000 CE
2. Open a BUY position
3. Badge should change to `[✓ Position]`
4. Wait 1+ hours, refresh
5. ✅ Item stays (protected by position)

### Test 3: Auto-Cleanup
1. Add NIFTY 22000 CE
2. Wait 1 hour without opening position
3. Refresh page
4. ✅ Item auto-removed (old & no position)

### Test 4: Tier-B Persistence
1. Add RELIANCE (Tier-B)
2. Shows `[Tier-B]` badge
3. Wait any amount of time
4. Refresh multiple times
5. ✅ Always stays (manual delete only)

---

##configuration Parameters

### In Backend (app/routers/watchlist.py)

```python
# Grace period for Tier-A items (before auto-cleanup)
cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)

# Adjust this value to change grace period:
# - 30 minutes: timedelta(minutes=30)
# - 2 hours: timedelta(hours=2)
# - 1 day: timedelta(days=1)
```

### In Frontend (frontend/src/pages/WATCHLIST.jsx)

Badge styling can be customized:
```javascript
// Tier-A color
backgroundColor: 'rgba(255,165,0,0.2)',  // Orange
color: '#FFA500'

// Position indicator color
backgroundColor: inst.hasPosition ? 'rgba(76,175,80,0.2)' : 'rgba(244,67,54,0.2)',
color: inst.hasPosition ? '#4CAF50' : '#F44336'
```

---

## 🚀 Deployment Checklist

- [x] Backend endpoint modified to include tier/position info
- [x] Auto-cleanup function implemented
- [x] Frontend mapping updated for new fields
- [x] Visual badges added to UI
- [x] Error handling in place
- [x] No database schema changes needed

**To Deploy:**
1. Deploy backend changes first
2. Deploy frontend changes
3. Monitor audit logs for auto-cleanup activity
4. Users will see tier indicators immediately

---

## 📊 Expected Behavior After Implementation

| Scenario | Before | After |
|----------|--------|-------|
| Add Tier-B item, refresh | ❌ Removed | ✅ Stays forever |
| Add Tier-A, no position, refresh after 1h | ❌ Removed immediately | ✅ Stays 1h, then auto-removes |
| Add Tier-A, open position, refresh | ❌ Removed | ✅ Stays (protected) |
| Close position, refresh after 1h | ❌ Stays (bug) | ✅ Auto-removes (correct) |
| Manually delete item | ✅ Removed | ✅ Removed |

---

## 🔍 Monitoring

### Check Cleanup Activity

```sql
-- See what was cleaned up
SELECT 
  watchlist_id,
  COUNT(*) as removed_count,
  MAX(deleted_at) as last_cleanup
FROM watchlist_cleanup_log
GROUP BY watchlist_id
ORDER BY last_cleanup DESC;
```

### Monitor Tier Distribution

```sql
SELECT 
  im.tier,
  COUNT(*) as count,
  COUNT(DISTINCT wi.watchlist_id) as watchlists
FROM watchlist_items wi
LEFT JOIN instrument_master im ON im.instrument_token = wi.instrument_token
GROUP BY im.tier;
```

---

## 📞 User Documentation

**"Where did my watchlist item go?"**

**Answer:**
- If **[Tier-B]** badge: It won't disappear (manually delete to remove)
- If **[Tier-A] [✓ Position]** badge: It's protected by your open position
- If **[Tier-A] [⊘ No Position]** badge: Will auto-remove after 1 hour of inactivity

**"How do I keep a Tier-A item?"**

**Answer:**
- Open a position in it (it gets protected while you hold it)
- OR use the add button within 1 hour each time
- OR ask admin to reclassify it as Tier-B (if important for you)

**"Can I change an item's Tier?"**

**Answer:**
- Tier is set by instrument classification (instrument_master.tier)
- Most indices and actively traded instruments are Tier-B
- Less common instruments are Tier-A (on-demand)
- Contact admin if you want an item moved between tiers

---

## 🔧 Troubleshooting

### Issue: Items keep disappearing
**Check:**
1. Are they Tier-A? `SELECT tier FROM instrument_master WHERE symbol = ?`
2. Do you have position? Check in Positions tab
3. Is it been >1 hour? Check `added_at` timestamp

### Issue: Badge not showing
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check browser console for errors

### Issue: Auto-cleanup too aggressive
1. Increase grace period in backend
2. Adjust `timedelta(hours=1)` to larger value
3. Redeploy

---

**✅ Watchlist now works as intended!**

Tier-B (subscribed) items will stay forever, while Tier-A (on-demand) items intelligently clean up to prevent clutter.
