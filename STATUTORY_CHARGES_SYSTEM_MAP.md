# Statutory Charges System Architecture
## Complete Terminology & Database Mapping

---

## 1. TERMINOLOGY MAPPING

### The Core Concept: **One Value, Multiple Names**

The system uses **different terminology** on different pages, but they all refer to the **same calculated value**:

| **Context** | **Column/Header Name** | **Database Column** | **What It Represents** |
|---|---|---|---|
| **P&L Report (UI)** | `TRADE EXPENSE` | `trade_expense` | Sum of all regulatory/statutory charges |
| **Ledger/Statement** | `Trade Expense` | `trade_expense` | Sum of all regulatory/statutory charges |
| **Internal Calc** | `Statutory Charges` | Calculated in calculator | STT + Stamp + Exchange + SEBI + GST + DP charges |
| **Database** | `trade_expense` | `paper_positions.trade_expense` | Final calculated value saved |

---

## 2. STATUTORY CHARGES BREAKDOWN

### What's Included in `trade_expense`?

```
TRADE EXPENSE = STT/CTT + Stamp Duty + Exchange Charge + SEBI Charge + DP Charge + GST
```

**Example (Equity Delivery ₹450 buy → ₹480 sell, qty 400):**
- STT/CTT:       ₹372.00  (0.1% buy + 0.1% sell on ₹186,000 each)
- Stamp Duty:    ₹27.00   (0.015% on buy side ₹180,000)
- Exchange Chg:  ₹12.09   (0.00325% on ₹372k turnover)
- SEBI Charge:   ₹0.37    (₹10 per crore on ₹37.2M)
- DP Charge:     ₹0.00    (Not applicable for intraday)
- GST:           ₹4.67    (18% on taxable charges ₹25.89)
- **TOTAL:       ₹429.64**

---

## 3. DATABASE SCHEMA

### `paper_positions` Table — Charge Columns

All charge columns are `NUMERIC(16,2)` stored with 2 decimal precision:

```sql
-- Individual charge components
brokerage_charge        NUMERIC(16,2)  -- Broker commission only
stt_ctt_charge          NUMERIC(16,2)  -- Securities Transaction Tax (nearest rupee)
stamp_duty              NUMERIC(16,2)  -- Stamp duty (state-specific)
exchange_charge         NUMERIC(16,2)  -- Exchange fees
sebi_charge             NUMERIC(16,2)  -- SEBI regulatory charge
dp_charge               NUMERIC(16,2)  -- Demat Participant charges
ipft_charge             NUMERIC(16,2)  -- Investments and Profits Fund Tax
gst_charge              NUMERIC(16,2)  -- GST on applicable charges
platform_cost           NUMERIC(16,2)  -- Total platform cost (brokerage only)
trade_expense           NUMERIC(16,2)  -- *** STATUTORY CHARGES (regulated by RBI/SEBI) ***
total_charges           NUMERIC(16,2)  -- platform_cost + trade_expense

-- Calculation tracking flag
charges_calculated      BOOLEAN        -- FALSE = needs recalculation, TRUE = fully calculated
charges_calculated_at   TIMESTAMPTZ    -- When charges were last calculated
```

### Key Distinction:
```
Total Charges = Platform Cost + Trade Expense
              =  Brokerage   + (STT + Stamp + Exchange + SEBI + GST...)
```

---

## 4. CALCULATION FLOW

### Step-by-Step: Position Close → Trade Expense Display

```
FLOW:
┌─────────────────────────────────────────────────────────────┐
│ 1. USER CLOSES POSITION → paper_positions row created      │
│    Status: CLOSED                                            │
│    charges_calculated: FALSE  ← PENDING CALCULATION         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CHARGE SCHEDULER RUNS (automatic or manual trigger)      │
│    - Finds all rows where charges_calculated = FALSE        │
│    - For each position: normalize_enums() + calculate       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CALCULATOR.calculate_position_charges()                   │
│    - Input: buy_price, sell_price, quantity, enums          │
│    - Process: Apply regulatory rate tables                  │
│    - Output: Dict with trade_expense, stt_ctt, etc..        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DATABASE UPDATE                                           │
│    UPDATE paper_positions                                    │
│    SET trade_expense = <calculated_value>,                  │
│        charges_calculated = TRUE,                           │
│        ...other charge columns...                           │
│    WHERE position_id = <id>                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. P&L REPORT (User views on UI)                            │
│    SELECT trade_expense FROM paper_positions                │
│    Display as "TRADE EXPENSE" column                        │
│    = ₹429.64 (no longer ₹0.00)                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. THREE AUTOMATIC BACKFILL TRIGGERS

The system attempts to **automatically backfill missing charges** in three ways:

### Trigger 1: P&L Report Request (LIVE)
**When:** User opens P&L report
**Location:** `app/routers/positions.py:346-369`
**Action:** 
```python
# Check if have pending charges
pending_count = "SELECT COUNT(*) WHERE charges_calculated = FALSE"
if pending_count > 0:
    await scheduler.run_once(...)  # Automatic backfill
```
**Result:** Charges are calculated BEFORE report displays

---

### Trigger 2: Scheduled (Background)
**When:** Market close times (4:00 PM IST for NSE/BSE, 12:00 AM IST for MCX)
**Location:** `app/schedulers/charge_calculation_scheduler.py:_run_loop()`
**Action:** Checks every 5 minutes if market closed, runs scheduler
**Result:** Auto-processes all pending closed positions

---

### Trigger 3: Manual (Admin/Debugging)
**When:** `python recalculate_all_charges.py` executed on server
**Location:** `recalculate_all_charges.py`
**Action:** Resets + recalculates ALL positions regardless of flag
**Result:** Full historical recomputation

---

## 6. TERMINOLOGY CONSISTENCY

### Where Each Term Is Used:

| **Term** | **Where Used** | **Database Reference** |
|---|---|---|
| **TRADE EXPENSE** | P&L Report table (user-facing) | `trade_expense` column |
| **Statutory Charges** | Documentation, code comments | Sum of all regulatory charges |
| **Platform Cost** | P&L report, ledger (when broken down) | `platform_cost` column |
| **Charges** | General term (ambiguous) | Could mean `total_charges` or `trade_expense` |
| **Total Charges** | Ledger entry, detailed view | `total_charges` = `platform_cost` + `trade_expense` |

---

## 7. VERIFICATION CHECKLIST

### To Verify System Is Working:

**✓ Step 1: Check Recent Closed Positions**
```sql
SELECT position_id, symbol, realized_pnl, trade_expense, charges_calculated
FROM paper_positions
WHERE status = 'CLOSED'
AND closed_at > NOW() - INTERVAL '7 days'
LIMIT 10;
```
Expected: `trade_expense > 0` and `charges_calculated = TRUE`

**✓ Step 2: Check P&L Report Frontend**
- Navigate to: **P&L Report** page
- Set date range to include recent closed trades
- Column **"TRADE EXPENSE"** should show values like ₹429.64, not ₹0.00

**✓ Step 3: Check Individual Trade Details**
- Click on any closed position
- Expand "Charges" or "Fee Breakdown"
- Should show itemized: STT ₹XXX, Stamp ₹XX, Exchange ₹X.XX, etc.

**✓ Step 4: Check Ledger (if implemented)**
- Navigate to **Ledger**
- Realized P&L entries should show net_pnl - trade_expense = actual credit/debit

---

## 8. TROUBLESHOOTING

### Problem: TRADE EXPENSE Still Shows ₹0.00

**Cause 1: Charges Not Yet Calculated**
```sql
SELECT COUNT(*) FROM paper_positions 
WHERE status = 'CLOSED' AND charges_calculated = FALSE;
-- If COUNT > 0, charges still pending
```
**Fix:** Wait 5 minutes (scheduler runs every 300 sec) OR refresh P&L report (triggers backfill)

---

**Cause 2: Scheduler Failed Silently**
**Check:** Application logs for error messages like:
```
⚠️ Charge backfill FAILED for user XXX: <error message>
```
**Fix:** 
- If import error: Ensure `from app.database import init_db` works
- If DB error: Verify database connectivity
- Run manual recalculation: `python recalculate_all_charges.py`

---

**Cause 3: Enum Mismatch (Old Database Values)**
**Check:** Database contains old enum values like 'DELIVERY' instead of 'NORMAL'
```sql
SELECT DISTINCT product_type FROM paper_positions;
-- If shows: DELIVERY, INTRADAY (old), need normalization
```
**Fix:** Scheduler's `normalize_enums()` should convert automatically, but logs may show:
```
Enum normalization: DELIVERY/STOCK/NIFTY → NORMAL/EQUITY/FUTIDX
```

---

## 9. CODE References

### Key Files:

| **File** | **Purpose** | **Key Function** |
|---|---|---|
| `app/services/charge_calculator.py` | Statutory charge calculation | `calculate_all_charges()` returns dict with `trade_expense` |
| `app/schedulers/charge_calculation_scheduler.py` | Auto-processor for pending charges | `run_once()` triggers calculation, `normalize_enums()` maps old values |
| `app/routers/positions.py` | P&L report endpoint | Lines 346-369 trigger backfill before response |
| `migrations/020_brokerage_charges_system.sql` | Database schema | Adds `trade_expense` and all charge columns |
| `frontend/src/pages/PandL.jsx` | UI rendering | Line 220-225 displays `p.trade_expense` as TRADE EXPENSE |

---

## 10. SUMMARY

**The system knows that STATUTORY CHARGES = TRADE EXPENSE:**
- ✅ Calculator computes and returns `trade_expense` value
- ✅ Scheduler saves it to database column `trade_expense`
- ✅ P&L report queries and displays `trade_expense` as "TRADE EXPENSE" header
- ✅ Frontend receives and shows the value
- ✅ Automatic backfill triggers when P&L report is requested

**If you still see ₹0.00:**
1. Check application logs for backfill errors (newly added logging)
2. Run `python recalculate_all_charges.py` on production server
3. Verify `charges_calculated = TRUE` for affected positions
4. Refresh P&L report to confirm

---

**Last Updated:** 2026-03-03
**Status:** System fully wired for automatic charge population
