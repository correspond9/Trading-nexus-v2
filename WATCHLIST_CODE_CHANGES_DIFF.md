# Code Diff Summary - Watchlist Persistence Implementation

## 1. app/routers/watchlist.py

### Added Function: _auto_clean_tier_a()

```python
def _auto_clean_tier_a(pool: Pool, watchlist_id: int):
    """
    Auto-clean old Tier-A items without open positions.
    
    Removes Tier-A (on-demand) items that:
    1. Were added more than 1 hour ago
    2. User has NO open position in them
    
    Never removes:
    - Tier-B items (subscribed)
    - Recently added items (grace period < 1 hour)
    - Items with open positions
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
    
    try:
        with pool.connection() as conn:
            conn.execute("""
                DELETE FROM watchlist_items
                WHERE watchlist_id = %s
                  AND instrument_token IN (
                    SELECT im.instrument_token 
                    FROM watchlist_items wi
                    JOIN instrument_master im 
                      ON im.instrument_token = wi.instrument_token
                    LEFT JOIN paper_positions pp 
                      ON pp.instrument_token = im.instrument_token
                      AND pp.user_id = (
                        SELECT user_id FROM watchlists WHERE id = %s
                      )
                    WHERE wi.watchlist_id = %s
                      AND im.tier = 'A'
                      AND wi.added_at < %s
                      AND pp.id IS NULL
                  )
            """, [watchlist_id, watchlist_id, watchlist_id, cutoff_time])
            conn.commit()
    except Exception as e:
        logger.error(f"Error during watchlist cleanup: {e}")
```

### Modified Endpoint: GET /watchlist/{user_id}

**Before:**
```python
@router.get("/{user_id}")
async def get_watchlist(user_id: int, pool: Depends(get_pool)):
    """Get watchlist items with market data"""
    # ... existing code ...
    return {
        "status": "success",
        "data": items  # items didn't have tier/position info
    }
```

**After:**
```python
@router.get("/{user_id}")
async def get_watchlist(user_id: int, pool: Depends(get_pool)):
    """Get watchlist items with market data and tier/position info"""
    
    # Auto-clean old Tier-A items without positions
    _auto_clean_tier_a(pool, watchlist_id)
    
    # ... get items from database ...
    # Now includes: tier, has_position, added_at
    
    return {
        "status": "success",
        "data": [
            {
                "token": item['token'],
                "symbol": item['symbol'],
                "tier": item['tier'],              # ← NEW
                "has_position": item['has_position'],  # ← NEW
                "added_at": item['added_at'],      # ← NEW
                "ltp": item['ltp'],
                "close": item['close'],
                "volume": item['volume'],
                "oi": item['oi']
            }
            for item in items
        ]
    }
```

### Query Used to Fetch Watchlist

**Modified to include tier and position info:**

```sql
SELECT 
    wi.instrument_token as token,
    im.symbol,
    im.tier,                    -- ← NEW
    CASE 
        WHEN pp.id IS NOT NULL THEN true 
        ELSE false 
    END as has_position,        -- ← NEW
    wi.added_at,                -- ← NEW
    md.ltp,
    md.close,
    md.volume,
    md.oi
FROM watchlist_items wi
JOIN instrument_master im ON im.instrument_token = wi.instrument_token
LEFT JOIN market_data md ON md.instrument_token = im.instrument_token
LEFT JOIN paper_positions pp 
    ON pp.instrument_token = im.instrument_token 
    AND pp.user_id = %s
WHERE wi.watchlist_id = (SELECT id FROM watchlists WHERE user_id = %s)
ORDER BY wi.added_at DESC;
```

---

## 2. frontend/src/pages/WATCHLIST.jsx

### Modified Function: mapServerItems()

**Before:**
```javascript
const mapServerItems = (items) => {
  return (items || []).map((item, idx) => ({
    id: idx,
    token: item.token,
    symbol: item.symbol,
    ltp: item.ltp,
    close: item.close,
    volume: item.volume,
    oi: item.oi,
  }));
};
```

**After:**
```javascript
const mapServerItems = (items) => {
  return (items || []).map((item, idx) => ({
    id: idx,
    token: item.token,
    symbol: item.symbol,
    tier: item.tier || 'B',              // ← NEW: Default to B if not provided
    hasPosition: item.has_position,      // ← NEW: Position status
    addedAt: item.added_at,              // ← NEW: When added to watchlist
    ltp: item.ltp,
    close: item.close,
    volume: item.volume,
    oi: item.oi,
  }));
};
```

### Modified Section: Render Watchlist Item with Badges

**Before:**
```javascript
<div style={{ display: 'flex', justifyContent: 'space-between', ...}}>
  <div>
    <strong>{inst.symbol}</strong>
    <div style={{ fontSize: '12px', color: '#888' }}>
      {exchangeName}
    </div>
  </div>
</div>
```

**After:**
```javascript
<div style={{ display: 'flex', justifyContent: 'space-between', ...}}>
  <div style={{ flex: 1 }}>
    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
      <strong>{inst.symbol}</strong>
      
      {/* Tier Badge - Shows for all items */}
      <span style={{
        paddingLeft: '6px',
        paddingRight: '6px',
        paddingTop: '2px',
        paddingBottom: '2px',
        fontSize: '11px',
        fontWeight: '600',
        borderRadius: '4px',
        backgroundColor: inst.tier === 'A'
          ? 'rgba(255,165,0,0.2)'      // Orange for Tier-A
          : 'rgba(76,175,80,0.2)',     // Green for Tier-B
        color: inst.tier === 'A' ? '#FFA500' : '#4CAF50',
      }}>
        Tier-{inst.tier}
      </span>

      {/* Position Badge - Shows only for Tier-A items */}
      {inst.tier === 'A' && (
        <span style={{
          paddingLeft: '6px',
          paddingRight: '6px',
          paddingTop: '2px',
          paddingBottom: '2px',
          fontSize: '11px',
          fontWeight: '600',
          borderRadius: '4px',
          backgroundColor: inst.hasPosition
            ? 'rgba(76,175,80,0.2)'    // Green if position exists
            : 'rgba(244,67,54,0.2)',   // Red if no position
          color: inst.hasPosition ? '#4CAF50' : '#F44336',
        }}>
          {inst.hasPosition ? '✓ Position' : '⊘ No Position'}
        </span>
      )}
    </div>
    
    <div style={{ fontSize: '12px', color: '#888' }}>
      {exchangeName}
    </div>
  </div>
</div>
```

---

## Summary of Changes

### Files Modified: 2
1. `app/routers/watchlist.py` - Backend API
2. `frontend/src/pages/WATCHLIST.jsx` - Frontend UI

### Lines of Code Changed: ~60
- Backend: ~40 lines (new function + response enhancement)
- Frontend: ~20 lines (field mapping + badge rendering)

### New Database Columns Used (Not Added):
- `instrument_master.tier` - Already exists
- `watchlist_items.added_at` - Already exists
- `paper_positions`relationship - Already exists

### No Schema Changes Required ✅

### Backward Compatibility ✅
- If `tier` field missing, defaults to 'B'
- If `has_position` missing, defaults to false
- Existing watchlist items work without modification

---

## How to Verify Changes

### 1. Backend Verification
```bash
# Check watchlist.py has _auto_clean_tier_a function
grep -n "_auto_clean_tier_a" app/routers/watchlist.py

# Should see: Function definition, and call in GET endpoint
```

### 2. Frontend Verification
```bash
# Check WATCHLIST.jsx has tier field
grep -n "tier" frontend/src/pages/WATCHLIST.jsx

# Should see: mapServerItems includes tier
#            Badge rendering with Tier-A/B colors
```

### 3. API Response Verification
```bash
# Call the API and check response includes new fields
curl http://localhost:8000/watchlist/{user_id}

# Should see tier, has_position, added_at in each item
```

### 4. UI Visual Check
```
Launch app → Go to Watchlist tab
Should see colored badges next to each item:
- Green [Tier-B] for subscribed items
- Orange [Tier-A] for on-demand items
- Plus [✓ Position] or [⊘ No Position] for Tier-A items
```

---

## Execution Flow

### When User Opens Watchlist:

```
1. Frontend calls GET /watchlist/{user_id}
   ↓
2. Backend function:
   a. Call _auto_clean_tier_a(pool, watchlist_id)
      - Deletes old Tier-A items without positions
   b. Query watchlist items with tier/position info
   c. Return [items] with new fields
   ↓
3. Frontend receives response:
   a. Map items with tier, hasPosition, addedAt
   b. Store in React state
   c. Render with badges
   ↓
4. User sees:
   - Tier-B items [green badge] (permanent)
   - Tier-A items [orange badge]
     - With [✓ Position] [green] if protected
     - With [⊘ No Position] [red] if will expire
```

### Auto-Cleanup Triggers:

```
1. Every GET /watchlist/{user_id} call
2. Checks for Tier-A items where:
   - added_at < NOW() - 1 hour  (older than grace period)
   - No open position in paper_positions
3. Silently deletes matching items
4. Returns updated watchlist to user
```

---

## Testing Checklist

- [ ] Add Tier-B item → Stays on refresh
- [ ] Add Tier-A item → Shows orange badge
- [ ] Tier-A without position → Shows red "⊘ No Position"
- [ ] Open position → Badge changes to green "✓ Position"
- [ ] Wait 1+ hour without position → Item auto-removed
- [ ] Wait 1+ hour with position → Item stays
- [ ] Manually delete button → Works for all tiers
- [ ] Colors display correctly → Badges visible and readable

---

## Deployment Steps

1. Deploy backend changes first (no downtime)
2. Test API returns new fields
3. Deploy frontend changes
4. Clear browser cache
5. Test in UI

All changes are additive and don't break existing functionality.
