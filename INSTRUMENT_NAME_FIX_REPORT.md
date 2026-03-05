# Instrument Name Expiry Date Display Fix

## Issue Summary
When placing orders directly from the **Straddle** or **Options** chain pages, instrument names did NOT include expiry dates in the order modal dialog. For example, it would show just `NIFTY 24600 CE` instead of `NIFTY 24600 CE 10MAR`.

The Watchlist page displayed the full name with expiry in the UI but this was only visual - the actual order data didn't include it.

## Root Cause
1. **STRADDLE.jsx**: Built symbols as `${symbol} ${strike} CE` without expiry information
2. **OPTIONS.jsx**: Same issue - built incomplete symbols  
3. **WATCHLIST.jsx**: Had formatted labels with expiry for display, but passed raw `inst.symbol` when placing orders
4. **OrderModal.jsx**: Displayed whatever symbol was passed without any formatting or fallback

## Solution Implemented

### 1. Created Utility Function
**File**: `frontend/src/utils/formatInstrumentLabel.js`

```javascript
export const formatOptionLabel = (config) => {
  // Formats option instruments as: UNDERLYING STRIKE OPTIONTYPE DD-MON
  // Example: NIFTY 24600 CE 10MAR
}
```

### 2. Updated STRADDLE.jsx
- Added import for `formatOptionLabel`
- Modified BUY button: Now calls `formatOptionLabel()` to create `displaySymbol` before passing to `handleOpenOrderModal`
- Modified SELL button: Same changes as BUY
- Passes both `symbol` (for API) and `displaySymbol` (for UI) in order data

### 3. Updated OPTIONS.jsx  
- Added import for `formatOptionLabel`
- Updated 4 trade buttons (Buy/Sell for both CE and PE):
  - Each button now calculates and passes `displaySymbol`
  - Maintains backward compatibility by including raw `symbol` for API calls

### 4. Updated WATCHLIST.jsx
- Added import for `formatOptionLabel`
- Modified Buy/Sell buttons to pass:
  - `displaySymbol`: The formatted label with expiry (e.g., from `formatOptionLabel`)
  - Additional instrument details: `instrumentType`, `expiryDate`, `strikePrice`, `optionType`, `underlying`
  - Falls back to raw symbol if label is undefined

### 5. Updated OrderModal.jsx
Modified three display locations to use `displaySymbol` when available:

**Header Title** 
- Before: `{orderData?.symbol || 'Order'}`
- After: `{orderData?.displaySymbol || orderData?.symbol || 'Order'}`

**Legs Display** (for multi-leg orders like Straddles)
- Before: `<span>{leg.symbol}</span>`
- After: `<span>{leg.displaySymbol || leg.symbol}</span>`

**Success Message**
- Before: `...× ${orderData?.symbol || ''}`
- After: `...× ${displayName}` (where displayName uses displaySymbol if available)

## Result
Now when placing orders from any page (Straddle, Options, or Watchlist), the order modal displays instrument names with expiry dates:
- **Straddle page**: NIFTY 24600 CE 10MAR, NIFTY 24600 PE 10MAR
- **Options page**: Same format
- **Watchlist page**: Same format (instead of just showing the raw symbol)

## Backward Compatibility
- All changes are backward compatible
- Falls back to raw `symbol` if `displaySymbol` is not provided
- No database schema changes required
- No API contract changes

## Files Modified
1. `frontend/src/utils/formatInstrumentLabel.js` - **NEW FILE**
2. `frontend/src/pages/STRADDLE.jsx`
3. `frontend/src/pages/OPTIONS.jsx`
4. `frontend/src/pages/WATCHLIST.jsx`
5. `frontend/src/components/OrderModal.jsx`
