# Market Hours Validation - Implementation Summary

## Problem Identified
User was able to close positions outside market hours (after 15:30 IST), which shouldn't be allowed in a real trading system.

## Solution Implemented

### 1. **Market Hours Validation Added to Position Close Endpoint**
   - File: `app/routers/positions.py`
   - Endpoint: `POST /portfolio/positions/{position_id}/close`
   - Added validation to check if market is open before allowing position closure
   - Rejects with HTTP 403 if market is closed

### 2. **Existing Market Hours Infrastructure Used**
   - `app/market_hours.py` already had comprehensive market timing logic:
     - `is_market_open(exchange_segment, symbol)` - Returns True only during trading hours
     - `get_market_state(exchange_segment, symbol)` - Returns current market state (OPEN/CLOSED/PRE_OPEN/POST_CLOSE)
   - Market hours (IST):
     - **NSE/BSE**: 09:15 - 15:30 (Mon-Fri, excluding holidays)
     - **MCX**: 09:00 - 23:30 (Mon-Fri, excluding holidays)
     - **MCX International Commodities**: 09:00 - 23:55

### 3. **Comprehensive Coverage**

| Operation | Endpoint | Market Hours Check | Status |
|-----------|----------|-------------------|--------|
| Place Order | `POST /trading/orders` | ✅ Already enforced | Working |
| Execute Basket | `POST /trading/basket-orders/execute` | ✅ Already enforced | Working |
| Close Position | `POST /portfolio/positions/{id}/close` | ✅ **NOW ENFORCED** | **NEW** |
| Admin Backdate | `POST /admin/backdate-position` | ❌ Not checked | Intentional (admin feature) |

### 4. **Error Response Example**

When user tries to trade outside market hours:

```json
{
  "detail": "Market is CLOSED. Positions can only be closed during market hours."
}
```

HTTP Status: 403 Forbidden

## Additional Fix: F&O Exchange Segment

### Bug Found
- Database has F&O instruments with `exchange_segment = "NSE_FNO"` (F-N-O)
- Backend was mapping to `exchange_segment = "NSE_FO"` (F-O)
- **Result**: F&O positions couldn't be created via admin backdate

### Fix Applied
- File: `app/routers/admin.py` line 1547
- Changed: `NSE_FO` → `NSE_FNO`
- **Result**: Stock Options and Index Options can now be created successfully

## Testing

### To verify market hours validation:
```bash
python test_market_hours_validation.py
```

This test should be run **outside market hours** (before 09:15 or after 15:30 IST).

Expected behavior:
- ✅ Orders rejected with "Market is CLOSED" message
- ✅ Position closes rejected with "Market is CLOSED" message

### To verify F&O support:
```bash
python test_fo_after_fix.py
```

Expected behavior:
- ✅ Stock Options (OPTSTK) positions created successfully
- ✅ Index Options (OPTIDX) positions created successfully

## Impact

### Production Behavior Changes:
1. **Traders cannot exit positions outside market hours**
   - Previously: Could exit anytime
   - Now: Must wait for market to open

2. **Traders cannot place orders outside market hours** (already existed)
   - This was already enforced, no change

3. **Admin backdate still works anytime** (intentionally not restricted)
   - Admins can create historic positions for any date/time
   - This is a legitimate admin feature for position reconciliation

## Files Modified

1. `app/routers/positions.py`
   - Added import: `from app.market_hours import is_market_open, get_market_state`
   - Added market hours validation in `close_position()` function

2. `app/routers/admin.py`
   - Fixed NSE F&O exchange segment mapping (NSE_FO → NSE_FNO)

## Deployment

- **Commit**: `a02f939` - "Enforce market hours validation on position exits"
- **Previous Commit**: `c071a9f` - "Fix NSE F&O exchange segment mapping"
- **Deployment UUID**: Triggered force rebuild on Coolify
- **Status**: Deployed to production

## Next Steps

If you want to test:
1. Wait until after 15:30 IST (market close)
2. Try to close a position via UI
3. You should see: "Market is CLOSED. Positions can only be closed during market hours."

If you need to allow after-hours closures (e.g., for risk management), we can:
- Add a separate admin API endpoint for force-close
- Add a user permission flag for after-hours trading
- Implement extended hours trading sessions
