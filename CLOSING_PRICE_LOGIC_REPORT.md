# Closing Price Logic Report

## Executive Summary
The system displays closing prices from multiple sources with fallback logic. When markets are closed and live ticks (LTP) are unavailable, the system falls back to **previous session close prices** stored in the database.

---

## Database Schema

### 1. `market_data` Table
**Location**: `migrations/001_initial_schema.sql` (line 64-82)

```sql
CREATE UNLOGGED TABLE market_data (
    instrument_token  BIGINT        PRIMARY KEY,
    exchange_segment  VARCHAR(20)   NOT NULL,
    symbol            VARCHAR(100),
    ltp               NUMERIC(12,2),
    open              NUMERIC(12,2),
    high              NUMERIC(12,2),
    low               NUMERIC(12,2),
    close             NUMERIC(12,2),   -- ⚠️ previous session close
    bid_depth         JSONB,
    ask_depth         JSONB,
    ltt               TIMESTAMPTZ,
    updated_at        TIMESTAMPTZ
);
```

### 2. `option_chain_data` Table
**Location**: `migrations/001_initial_schema.sql` (line 87-105)

```sql
CREATE UNLOGGED TABLE option_chain_data (
    instrument_token    BIGINT         PRIMARY KEY,
    underlying          VARCHAR(20)    NOT NULL,
    expiry_date         DATE           NOT NULL,
    strike_price        NUMERIC(12,2)  NOT NULL,
    option_type         CHAR(2)        NOT NULL,
    iv                  NUMERIC(12,6),
    delta               NUMERIC(12,6),
    theta               NUMERIC(12,6),
    gamma               NUMERIC(12,6),
    vega                NUMERIC(12,6),
    prev_close          NUMERIC(12,2),  -- ⚠️ previous close from REST API
    prev_oi             BIGINT,
    greeks_updated_at   TIMESTAMPTZ
);
```

---

## Data Sources for Closing Prices

### 1. **Live WebSocket Ticks** (Primary Source)
**File**: `app/market_data/tick_processor.py` (lines 133-169)

- Receives `close` field from Dhan WebSocket packets
- Stores in `market_data.close` column
- Updated continuously during market hours

```python
async def _upsert(self, batch: list[dict]) -> None:
    # ...
    rows.append((
        instrument_token,
        segment,
        symbol,
        tick.get("ltp"),
        tick.get("open"),
        tick.get("high"),
        tick.get("low"),
        tick.get("close"),  # ⚠️ From WebSocket
        bid_depth,
        ask_depth,
        tick.get("ltt"),
    ))
```

**Update Strategy**:
```sql
ON CONFLICT (instrument_token) DO UPDATE SET
    close = COALESCE(EXCLUDED.close, market_data.close)
```
- Preserves existing close price if new tick doesn't have one

---

### 2. **Greeks Poller REST API** (Options Only)
**File**: `app/market_data/greeks_poller.py` (lines 320-367)

- Fetches `previous_close_price` from Dhan REST API
- Stores in `option_chain_data.prev_close`
- Runs every 15 seconds (configurable)

```python
rows.append((
    int(sec_id),
    underlying,
    exp_date,
    strike,
    opt_type.upper(),
    opt_data.get("implied_volatility"),
    greeks.get("delta"),
    # ... other greeks
    opt_data.get("previous_close_price"),  # ⚠️ From REST API
    opt_data.get("previous_oi"),
))
```

**Also seeds market_data**:
```python
await pool.execute(
    """
    INSERT INTO market_data (instrument_token, exchange_segment,
        ltp, close, updated_at)
    VALUES ($1, $2, $3, $4, now())
    ON CONFLICT (instrument_token) DO NOTHING
    """,
    int(sec_id),
    seg,
    opt_data["last_price"],
    opt_data.get("previous_close_price"),  # ⚠️ Seeds close price
)
```

---

## Display Logic Throughout System

### 1. **WebSocket Broadcast** (`/ws/prices`)
**File**: `app/routers/ws_feed.py` (lines 75-95)

**Logic**: LTP first, fallback to close
```python
for r in core_rows:
    val = r["ltp"] if r["ltp"] is not None else r["close"]  # ⚠️ Fallback
    if val is not None:
        prices[r["underlying"]] = float(val)

# For global snapshot
for r in rows:
    val = r["ltp"] if r["ltp"] is not None else r["close"]  # ⚠️ Fallback
    if val is None:
        continue
    prices.setdefault(str(r["instrument_token"]), float(val))
```

**Broadcast Frequency**: Every 0.5 seconds
**Recipients**: All connected frontend clients

---

### 2. **Watchlist Component**
**File**: `frontend/src/pages/WATCHLIST.jsx`

#### Price Display Logic (lines 380-388)
```javascript
const getDisplayedPrice = (instrument) => {
  const ex = String(instrument?.exchange || '').toUpperCase();
  const isCommodity = ex.includes('MCX') || ex.includes('COM');
  const marketActive = isCommodity
    ? (pulse?.marketActiveCommodity ?? pulse?.marketActive)
    : (pulse?.marketActiveEquity ?? pulse?.marketActive);

  // ⚠️ When market is closed, show close price
  if (marketActive === false) return instrument.close ?? instrument.ltp ?? null;
  return instrument.ltp ?? null;
};
```

**Fallback Chain (Market Closed)**:
1. `instrument.close` (previous session close)
2. `instrument.ltp` (last known LTP)
3. `null` (no data)

#### Change % Calculation (lines 409-413)
```javascript
const getChangePct = (instrument, ltpOverride = null) => {
  const ltp = ltpOverride !== null ? ltpOverride : instrument?.ltp;
  const close = instrument?.close;
  if (ltp == null || close == null || Number(close) === 0) return null;
  const pct = ((Number(ltp) - Number(close)) / Number(close)) * 100;  // ⚠️
  return Number.isFinite(pct) ? pct : null;
};
```

**Depends on**: Accurate `close` value for % calculation

---

### 3. **Option Chain API**
**File**: `app/routers/option_chain.py` (lines 141-145)

**Market Closed Fallback**:
```python
# Closed-market fallback: use prev_close when ltp/close are missing.
if row.get("ltp") is None and row.get("ocd_prev_close") is not None:
    row["ltp"] = row.get("ocd_prev_close")      # ⚠️ Use prev_close as LTP
if row.get("close") is None and row.get("ocd_prev_close") is not None:
    row["close"] = row.get("ocd_prev_close")    # ⚠️ Use prev_close as close
```

**Purpose**: Ensures option chain displays prices even when market is closed

---

### 4. **Market Data Serializer**
**File**: `app/serializers/market_data.py` (lines 33-34)

**Change % Calculation**:
```python
change_pct = None
if ltp is not None and close and close != 0:
    change_pct = round((float(ltp) - float(close)) / float(close) * 100, 2)
```

**Depends on**: Valid `close` value

---

### 5. **Underlying LTP Endpoint**
**File**: `app/routers/market_data.py` (lines 26-79)

**Returns Both LTP and Close**:
```python
@router.get("/underlying-ltp/{symbol}")
async def get_underlying_ltp(symbol: str):
    # Primary: INDEX token
    row = await pool.fetchrow("""
        SELECT md.ltp, md.close, md.updated_at
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE im.symbol = $1 AND im.instrument_type = 'INDEX'
        LIMIT 1
    """, u)
    
    if row and row["ltp"] is not None:
        return {
            "symbol": u,
            "ltp": float(row["ltp"]),
            "close": float(row["close"]) if row.get("close") else None,  # ⚠️
            "updated_at": row.get("updated_at"),
            "source": "INDEX",
        }
    
    # Fallback: FUTURES
    fut = await pool.fetchrow("""
        SELECT md.ltp, md.close, md.updated_at, im.symbol AS fut_symbol
        FROM instrument_master im
        LEFT JOIN market_data md ON md.instrument_token = im.instrument_token
        WHERE im.underlying = $1
          AND im.instrument_type IN ('FUTIDX','FUTSTK','FUTCOM')
        ORDER BY im.expiry_date ASC NULLS LAST
        LIMIT 1
    """, u)
    
    if fut and fut["ltp"] is not None:
        return {
            "symbol": u,
            "ltp": float(fut["ltp"]),
            "close": float(fut["close"]) if fut.get("close") else None,  # ⚠️
            "updated_at": fut.get("updated_at"),
            "source": "FUTURES",
        }
```

---

## Potential Issues & Root Causes

### ⚠️ Issue 1: Wrong Close Price from Data Provider
**Root Cause**: Dhan WebSocket or REST API provides incorrect `close`/`previous_close_price`

**Impact**:
- Incorrect % change calculations
- Wrong baseline for P&L calculations
- Misleading market data display

**Evidence**:
- All closing prices originate from Dhan
- No validation or sanitization of close prices
- System blindly trusts provider data

---

### ⚠️ Issue 2: Stale Close Prices
**Root Cause**: Close prices not updated daily

**Current Behavior**:
```python
ON CONFLICT (instrument_token) DO UPDATE SET
    close = COALESCE(EXCLUDED.close, market_data.close)
```
- **Keeps old close** if new tick doesn't have one
- No daily rollover mechanism visible

**Risk**: 
- Multi-day old close prices
- Incorrect % change after settlement

---

### ⚠️ Issue 3: Missing Close Prices (New Instruments)
**Root Cause**: Instruments added mid-session have no close price

**Fallback Chain**:
1. WebSocket tick `close` field (may be null for new instruments)
2. Greeks poller `previous_close_price` (options only)
3. Database existing value (may not exist)

**Result**: `null` or `0` close prices → Division by zero in % calculations

---

### ⚠️ Issue 4: No Close Price Validation
**Current Logic**:
```python
# No validation!
tick.get("close")  # Could be 0, negative, or nonsensical
```

**Missing**:
- Range checks (close should be within reasonable % of LTP)
- Zero/null validation before storage
- Historical comparison

---

## Recommendations

### 1. **Add Close Price Validation**
```python
def validate_close_price(close: float, ltp: float) -> bool:
    if close is None or close <= 0:
        return False
    if ltp and abs((ltp - close) / close) > 0.20:  # 20% threshold
        log.warning(f"Close price {close} far from LTP {ltp}")
        return False
    return True
```

### 2. **Daily Close Price Reset**
Create migration for daily settlement:
```sql
-- Run at market open (09:00 IST)
UPDATE market_data
SET 
    close = ltp,  -- Yesterday's last price becomes today's close
    open = NULL,  -- Reset OHLC
    high = NULL,
    low = NULL
WHERE updated_at < CURRENT_DATE;
```

### 3. **Close Price Audit Endpoint**
```python
@router.get("/admin/audit/close-prices")
async def audit_close_prices():
    """Find instruments with suspicious close prices"""
    rows = await pool.fetch("""
        SELECT 
            im.symbol,
            md.ltp,
            md.close,
            md.updated_at,
            ABS((md.ltp - md.close) / NULLIF(md.close, 0)) AS deviation_pct
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.close IS NOT NULL 
          AND md.ltp IS NOT NULL
          AND md.close > 0
          AND ABS((md.ltp - md.close) / md.close) > 0.10  -- 10% threshold
        ORDER BY deviation_pct DESC
        LIMIT 100
    """)
    return {"suspicious_close_prices": rows}
```

### 4. **Frontend Warning for Stale Data**
Display visual indicator when:
- Close price is >24 hours old
- Close price deviates >20% from LTP
- No close price available

### 5. **Manual Override UI**
Admin panel option to:
- View current close prices
- Manually correct wrong close prices
- Bulk update from CSV

---

## Action Items

1. ✅ **Immediate**: Run audit query to find current wrong close prices
2. ⚠️ **High Priority**: Add close price validation in tick processor
3. ⚠️ **High Priority**: Implement daily close price rollover
4. 📊 **Medium Priority**: Add admin audit endpoint
5. 🎨 **Medium Priority**: Add frontend staleness indicators
6. 🔧 **Low Priority**: Manual override UI

---

## Files Involved

### Backend
- `app/market_data/tick_processor.py` - Stores close from ticks
- `app/market_data/greeks_poller.py` - Stores prev_close from REST
- `app/routers/ws_feed.py` - Broadcasts LTP/close fallback
- `app/routers/market_data.py` - Returns LTP and close
- `app/routers/option_chain.py` - Uses prev_close fallback
- `app/serializers/market_data.py` - Calculates change %

### Frontend
- `frontend/src/pages/WATCHLIST.jsx` - Displays close when market closed
- `frontend/src/pages/STRADDLE.jsx` - Uses close as fallback
- `frontend/src/hooks/useMarketPulse.js` - Receives price broadcasts

### Database
- `migrations/001_initial_schema.sql` - market_data and option_chain_data tables

---

**Report Generated**: February 25, 2026
**Status**: Current closing price logic documented. Issues identified. Recommendations provided.
