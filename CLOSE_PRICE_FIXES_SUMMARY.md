# Close Price Fixes Implementation Summary
**Date:** February 25, 2026  
**Status:** ✅ Completed

---

## 🎯 What Was Fixed

Three immediate fixes implemented to address wrong closing prices:

### 1. **Close Price Validation** ✅
- **Rejects invalid close prices** before storing to database
- **Validation rules:**
  - ❌ Close price ≤ 0
  - ❌ Deviation from previous close > 50%
  - ❌ Deviation from LTP > 20% (during market hours)
- **Applied to:**
  - WebSocket tick processor (all instruments)
  - Greeks poller (option prev_close)

### 2. **Daily Rollover Mechanism** ✅
- **Automatic update** at 9:15 AM IST each trading day
- **Updates:** `market_data.close = yesterday's LTP`
- **Prevents:** Stale close prices from previous sessions
- **Tracking:** Logs each rollover to prevent duplicates

### 3. **Admin Rollover Endpoint** ✅
- **Manual trigger** for testing: `POST /api/v2/admin/close-price/rollover`
- **SUPER_ADMIN only**
- **Returns:** Updated count, skipped count, rollover date

---

## 📁 Files Modified

### New Files Created
1. **app/market_data/close_price_validator.py** - Validation logic
2. **app/market_data/close_price_rollover.py** - Daily rollover scheduler
3. **migrations/029_close_price_rollover_log.sql** - Rollover tracking table
4. **audit_close_prices.py** - Diagnostic tool to audit current close prices

### Modified Files
1. **app/market_data/tick_processor.py**
   - Added validation before storing close prices
   - Fetches existing close for deviation checks
   - Logs rejected close prices to notifications

2. **app/market_data/greeks_poller.py**
   - Added validation for `prev_close` from REST API
   - Validates before storing to `option_chain_data`
   - Validates before seeding `market_data`

3. **app/main.py**
   - Added `close_price_rollover` import
   - Starts rollover scheduler at startup (both Dhan enabled/disabled)
   - Stops rollover scheduler on shutdown

4. **app/routers/admin.py**
   - Added `POST /admin/close-price/rollover` endpoint
   - SUPER_ADMIN only access

---

## 🧪 How to Test

### Step 1: Run the Audit Tool (Before Fix)
```powershell
# Check current state of close prices
python audit_close_prices.py
```

**What to look for:**
- Instruments with close = 0 or negative
- Extreme deviations (>20%) between LTP and close
- Stale close prices (>24 hours old)
- Missing close prices

### Step 2: Start the Application
```powershell
# Normal startup (rollover scheduler starts automatically)
python -m uvicorn app.main:app --reload
```

**Check logs for:**
```
[11] Starting close price rollover scheduler…
Close price rollover scheduler started.
```

### Step 3: Force Manual Rollover (Testing)
```powershell
# Use curl or Postman
curl -X POST http://localhost:8000/api/v2/admin/close-price/rollover \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_TOKEN"
```

**Expected response:**
```json
{
  "status": "completed",
  "rollover_date": "2026-02-25",
  "updated_count": 1234,
  "skipped_count": 56
}
```

### Step 4: Run Audit Again (After Fix)
```powershell
python audit_close_prices.py
```

**Expected improvements:**
- ✅ No close prices <= 0
- ✅ No extreme deviations unless market genuinely moved
- ✅ Fresh close prices (updated today)
- ✅ Fewer missing close prices

### Step 5: Check Validation Logs
Monitor application logs for validation rejections:

```
[CLOSE_VALIDATION] Rejected RELIANCE (123456): Close price <= 0: -10.5
[CLOSE_VALIDATION] Rejected NIFTY 22000CE (789012): Deviation from prev_close too high: 75.2%
```

### Step 6: Check Rollover Log Database
```sql
-- Check rollover history
SELECT * FROM close_price_rollover_log ORDER BY rollover_date DESC;
```

---

## 📊 Validation Rules Details

### Rule 1: Zero/Negative Check
```python
if close_price <= 0:
    REJECT
```
**Why:** Close prices can never be zero or negative in real markets.

### Rule 2: Extreme Deviation from Previous Close
```python
if abs(close - prev_close) / prev_close > 0.50:  # 50%
    REJECT
```
**Why:** Price can't realistically move >50% between sessions without circuit breakers.

### Rule 3: Market Hours Deviation Check
```python
if is_market_open and abs(close - ltp) / ltp > 0.20:  # 20%
    REJECT
```
**Why:** During market hours, close (yesterday) shouldn't deviate drastically from current LTP unless genuine gap up/down.

---

## 🔄 Daily Rollover Schedule

**Time:** 9:15 AM - 9:20 AM IST (5-minute window)  
**Frequency:** Once per trading day  
**Action:** `UPDATE market_data SET close = ltp WHERE ltp > 0`

### Rollover Logic Flow
1. Check current time (IST)
2. If 9:15 - 9:20 AM AND not done today:
   - Update all `market_data.close` to current `ltp`
   - Log to `close_price_rollover_log`
   - Skip instruments with no LTP
3. Sleep 60 seconds, repeat

### Manual Trigger
```bash
# Force rollover now (regardless of time)
POST /api/v2/admin/close-price/rollover
```

---

## 🚨 Monitoring & Alerts

### Automatic Notifications
Invalid close prices automatically create notifications:

**Category:** `close_price_validation`  
**Severity:** `warning`  
**Dedupe:** 1 hour per instrument  

**Check notifications:**
```sql
SELECT * FROM notifications 
WHERE category = 'close_price_validation' 
ORDER BY created_at DESC;
```

### Log Monitoring
Search logs for validation events:
```bash
# Windows PowerShell
Get-Content app.log | Select-String "CLOSE_VALIDATION"

# Linux/Mac
grep "CLOSE_VALIDATION" app.log
```

---

## 📈 Expected Improvements

### Before Implementation
- ❌ Close prices = 0 for many instruments
- ❌ Stale prices from days/weeks ago
- ❌ Extreme deviations (100%+) not caught
- ❌ Wrong change% calculations

### After Implementation
- ✅ All close prices > 0
- ✅ Fresh close prices (rollover at market open)
- ✅ Rejected close prices logged
- ✅ Accurate change% calculations
- ✅ Audit trail for troubleshooting

---

## 🔍 Troubleshooting

### Issue: Rollover Not Running
**Check:**
1. Is the application running?
2. Is it between 9:15-9:20 AM IST?
3. Check logs for "Close price rollover scheduler started"

**Solution:**
```python
# Force manual rollover
POST /api/v2/admin/close-price/rollover
```

### Issue: Close Prices Still Wrong
**Check:**
1. Run audit tool: `python audit_close_prices.py`
2. Check validation logs for rejections
3. Verify Dhan WebSocket is sending close prices

**Solution:**
```sql
-- Check what Dhan is actually sending
SELECT instrument_token, symbol, ltp, close, updated_at 
FROM market_data 
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC 
LIMIT 20;
```

### Issue: Too Many Rejections
**Symptom:** Logs flooded with `[CLOSE_VALIDATION] Rejected`

**Check:**
1. Is Dhan data provider sending bad data?
2. Are thresholds too strict?

**Solution:**
```python
# Adjust thresholds in close_price_validator.py
MAX_DEVIATION_FROM_PREV_CLOSE = 0.50  # Increase if needed
MAX_DEVIATION_FROM_LTP = 0.20         # Increase if needed
```

---

## 🎯 Next Steps (Optional Enhancements)

### Priority 2 Recommendations
1. **Add Audit Dashboard Endpoint** - `GET /admin/close-price/audit`
2. **Email Alerts** - Notify admin when >10 rejections in 1 hour
3. **Manual Correction UI** - Frontend interface to override close prices
4. **History Tracking** - Store close price change history

### Future Improvements
- Compare Dhan close prices with NSE website for validation
- Add circuit breaker detection (use different thresholds)
- Implement close price forecasting based on historical patterns
- Add WebSocket reconnection handling for missed close prices

---

## ✅ Checklist

- [x] Close price validation implemented
- [x] Daily rollover mechanism created
- [x] Database migration added
- [x] Admin endpoint for manual trigger
- [x] Audit tool created
- [x] Documentation completed
- [x] No compilation errors
- [x] All files committed

---

## 📞 Support

If close prices are still incorrect after implementing these fixes:

1. **Run the audit tool** to identify specific issues
2. **Check validation logs** for rejection patterns
3. **Verify Dhan data source** is sending correct closes
4. **Contact Dhan support** if data provider is sending bad data

---

**Implementation Complete! 🎉**

The system now has robust close price validation and automatic daily rollover to prevent stale prices.
