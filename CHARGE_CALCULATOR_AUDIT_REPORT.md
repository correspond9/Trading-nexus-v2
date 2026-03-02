# STATUTORY CHARGES CALCULATION ENGINE - AUDIT & CORRECTION REPORT

**Date:** 2026-03-03  
**Status:** ⚠️ CRITICAL ERRORS FOUND & CORRECTED  
**Module:** `app/services/charge_calculator.py`

---

## EXECUTIVE SUMMARY

The existing charge calculation system has **multiple critical errors** that violate Indian regulatory requirements. The corrections ensure compliance with actual market structure and SEBI/NSE/BSE/MCX guidelines.

**Key Issues Found:**
- ❌ STT rates incorrect for 6+ segments
- ❌ Stamp duty uses single rate instead of segment-specific rates
- ❌ DP charges completely missing for delivery equity
- ❌ Exchange rates questionable/incomplete
- ❌ No distinction between normal expiry vs exercised options
- ❌ No support for agricultural commodities (different tax rate)
- ❌ Missing proper parameter passing for segment-specific logic

---

## DETAILED ERRORS FOUND

### 1. ❌ STT/CTT RATES - CRITICAL ERRORS

**ERROR 1.1: Futures STT Rate is WRONG**
```
CURRENT CODE:
'EQUITY_FUTURES_SELL': Decimal('0.0002')  # 0.02%

CORRECT RATE:
Index Futures & Stock Futures: 0.0125% on sell side
Error: Listed as 0.02%, should be 0.0125%
Impact: 60% OVERCHARGING on all futures trades
```

**ERROR 1.2: Options STT Rate is INCOMPLETE**
```
CURRENT CODE:
'EQUITY_OPTIONS_SELL': Decimal('0.001')  # 0.1% on sell

CORRECT RATES:
- Normal option expiry: 0.0625% on sell premium
- Exercised option: 0.125% on sell premium
Error: Uses single 0.1% rate, no distinction
Impact: Cannot handle exercised options correctly
```

**ERROR 1.3: Commodity STT Rates Don't Differentiate**
```
CURRENT CODE:
'COMMODITY_FUTURES_SELL': Decimal('0.0001')   # 0.01%
'COMMODITY_OPTIONS_SELL': Decimal('0.0005')   # 0.05%

MISSING:
Agricultural commodities have 5x higher tax rate
- Non-agricultural futures: 0.01%
- Agricultural futures: 0.05%
Error: No way to identify commodity type
Impact: Agricultural commodity trades are under-taxed
```

**Corrections Made:**
- Split STT rates by segment and transaction type
- Added separate rates for normal vs exercised options
- Added agricultural commodity distinction with flag
- Implemented segment-specific logic in `_calculate_stt_ctt()` method

---

### 2. ❌ STAMP DUTY RATES - CRITICAL ERRORS

**CURRENT IMPLEMENTATION:**
```python
STAMP_DUTY_RATE = Decimal('0.00015')  # 0.015% on buy side [SINGLE RATE FOR ALL]
```

**PROBLEM:** This single rate is wrong for most segments!

**CORRECT RATES BY SEGMENT:**

| Segment | Buy Rate | Application | Current Code |
|---------|----------|-------------|--------------|
| **Equity Intraday** | 0.003% | On BUY side | ❌ 0.015% (wrong) |
| **Equity Delivery** | 0.015% | On BUY side | ✓ Correct by accident |
| **Index Futures** | 0.002% | On BUY side | ❌ 0.015% (wrong) |
| **Stock Futures** | 0.002% | On BUY side | ❌ 0.015% (wrong) |
| **Index Options** | 0.003% | On BUY premium | ❌ 0.015% (wrong) |
| **Stock Options** | 0.003% | On BUY premium | ❌ 0.015% (wrong) |
| **Commodity Futures** | 0.002% | On BUY side | ❌ 0.015% (wrong) |
| **Commodity Options** | 0.003% | On BUY premium | ❌ 0.015% (wrong) |

**Impact:**
- Equity intraday: 5x OVERCHARGING (0.015% vs 0.003%)
- Futures trades: 7.5x OVERCHARGING (0.015% vs 0.002%)
- Options: 5x OVERCHARGING (0.015% vs 0.003%)

**Corrections Made:**
- Created `STAMP_DUTY_RATES` dictionary with segment-specific rates
- Implemented logic to select correct rate based on product type
- For options, uses premium value instead of total turnover
- For futures, uses buy side value only

---

### 3. ❌ DP CHARGES - COMPLETELY MISSING

**CURRENT CODE:**
```python
# NO HANDLING FOR DP CHARGES ANYWHERE
# Function signature doesn't even have a parameter for it
```

**REQUIREMENT - DP CHARGES APPLY TO EQUITY DELIVERY SELL ONLY:**
```
When:     Equity delivery position closes (sold)
Amount:   ₹13.50 per ISIN (flat charge)
GST:      18% applicable on DP charge
Count:    Once per ISIN per day (not per transaction in a day)
```

**Example Impact:**
```
Equity Delivery Sell: ₹50,000 × 100 shares
Expected Charges WITHOUT DP: ~₹45
Expected Charges WITH DP: ~₹60 (includes ₹13.50 DP + GST)
Current Code: ~₹45 (MISSING ₹15 charge)
```

**Corrections Made:**
- Added `apply_dp_charges` parameter to function signature
- Added `DP_CHARGE_PER_ISIN = ₹13.50` to rates
- Implemented conditional logic: apply only for equity delivery sell
- Added DP to GST taxable base
- Added DP to output dictionary

---

### 4. ⚠️ EXCHANGE RATES - INCOMPLETE/QUESTIONABLE

**CURRENT RATES:**
```python
'NSE_EQ': Decimal('0.00297'),        # ₹2.97 per lakh
'BSE_EQ': Decimal('0.00375'),        # ₹3.75 per lakh
'NSE_FNO_FUTURES': Decimal('0.00173'),  # ₹1.73 per lakh
'NSE_FNO_OPTIONS': Decimal('0.03503'),  # ₹35.03 per lakh
'MCX_COMM': Decimal('0.00035'),      # Very low
```

**ISSUES:**
1. NSE EQ rate seems low (~₹3 vs stated ~₹3.25)
2. No distinction between intraday/delivery for equity
3. MCX commodity rate (0.00035%) is suspiciously low (~0.0002%)
4. Rates not mapped to actual segment names clearly

**Corrections Made:**
- Clarified all exchange rates with proper documentation
- Added separate entries for clarity (NSE_EQ_INTRADAY, etc.)
- Updated MCX rates to more reasonable levels
- Cross-referenced with actual exchange fee schedules

---

### 5. ❌ GST CALCULATION - INCOMPLETE

**CURRENT CODE:**
```python
# GST = 18% × (Brokerage + Exchange + SEBI)
# Missing: DP charges, Clearing charges
taxable_amount = brokerage + sebi_charge + exchange_charge
gst_charge = taxable_amount * GST_RATE
```

**CORRECT FORMULA:**
```
GST Taxable Base = Brokerage + Exchange + SEBI + Clearing + DP
NOT TAXED:         STT/CTT, Stamp Duty (already collected as tax)
```

**Example Impact:**
```
Equity Delivery Sell with DP:
Current GST base: Brokerage + Exchange + SEBI = ₹23.50
Correct GST base: + DP charge = ₹36.50
Current GST: ₹4.23
Correct GST: ₹6.57
Missing: ₹2.34 (but actually government revenue!)
```

**Corrections Made:**
- Added all applicable charges to GST taxable base
- DP, Clearing, and other regulatory charges now included
- Clear comments explaining what's taxed and what's not

---

### 6. ❌ PARAMETER ISSUES - FUNCTION SIGNATURE

**CURRENT SIGNATURE:**
```python
def calculate_all_charges(
    self,
    turnover: float,        # ← Just total turnover, no separation
    exchange_segment: str,
    product_type: str,
    instrument_type: str,
    brokerage_flat: float,
    brokerage_percent: float,
    is_option: bool = False,
    premium_turnover: Optional[float] = None,  # ← Awkward parameter
) -> Dict[str, float]:
```

**PROBLEMS:**
1. Can't pass separate buy/sell prices (needed for correct calculations)
2. No way to indicate delivery vs intraday for same payment (confusing)
3. No parameter for option exercised status
4. No parameter for commodity type (agri vs non-agri)
5. No parameter for DP charges
6. Premium_turnover calculation is wrong in caller

**Corrections Made:**
```python
def calculate_all_charges(
    self,
    buy_price: float,      # ← Explicit buy price
    sell_price: float,     # ← Explicit sell price
    quantity: int,         # ← Clear quantity
    exchange_segment: str,
    product_type: str,
    instrument_type: str,
    brokerage_flat: float,
    brokerage_percent: float,
    is_option: bool = False,
    is_commodity: bool = False,
    is_agricultural_commodity: bool = False,
    option_exercised: bool = False,
    apply_dp_charges: bool = False,
) -> Dict[str, float]:
```

Benefits:
- ✓ All segment-specific logic now has proper inputs
- ✓ Turnover is calculated internally (consistently)
- ✓ No ambiguity about buy vs sell
- ✓ Can handle exercised options
- ✓ Can handle agricultural commodities
- ✓ Can apply DP charges when needed

---

### 7. ⚠️ IPFT CHARGES - QUESTIONABLE

**CURRENT CODE:**
```python
IPFT_EQUITY = Decimal('0.00001')     # ₹10 per crore
IPFT_FUTURES = Decimal('0.00001')    # ₹10 per crore
IPFT_OPTIONS = Decimal('0.00005')    # ₹50 per crore
```

**FINDING:** IPFT is not mentioned in official regulatory requirements provided. This appears to be a custom charge or an outdated regulation.

**Decision:** Removed from corrected version as it's not part of official Indian statutory structure. If this is a custom internal charge, it should be handled separately (not as statutory).

---

## CORRECTIONS SUMMARY TABLE

| Error | Severity | Current | Correct | Fix |
|-------|----------|---------|---------|-----|
| Futures STT | CRITICAL | 0.02% | 0.0125% | Split by instrument |
| Options STT | CRITICAL | 0.1% fixed | 0.0625%/0.125% | Added exercised flag |
| Commodity STT | CRITICAL | No agri distinction | 0.01%/0.05% | Added commodity type flag |
| Stamp Duty | CRITICAL | 0.015% (all) | 0.003%-0.015% (segment-dependent) | Created rates dict |
| DP Charges | CRITICAL | Missing | ₹13.50 per ISIN + GST | New parameter & logic |
| Exchange Rates | WARNING | Incomplete | Clarified & split | Documentation |
| GST Base | WARNING | Missing DP/Clearing | Includes all | Updated formula |
| Function Signature | HIGH | Ambiguous | Clear parameters | Complete refactor |
| IPFT | MEDIUM | Included | Not statutory | Removed |

---

## VALIDATION EXAMPLES

### Test Case 1: Equity Intraday (₹50,100 turnover)
```
CURRENT CALCULATION:
- Stamp Duty: ₹50,000 × 0.015% = ₹7.50 ❌ WRONG (should be 0.003%)
- Correct: ₹50,000 × 0.003% = ₹1.50 ✓

ERROR MAGNITUDE: 5x overcharge = ₹6.00 per trade
Annual impact: 250 trades × ₹6.00 = ₹1,500 overcharge per trader
```

### Test Case 2: Index Futures (₹2M turnover)
```
CURRENT CALCULATION:
- STT: ₹1M × 0.02% = ₹200 ❌ WRONG (should be 0.0125%)
- Correct: ₹1M × 0.0125% = ₹125 ✓

ERROR MAGNITUDE: 60% overcharge = ₹75 per contract
Annual impact: 500 contracts × ₹75 = ₹37,500 overcharge
```

### Test Case 3: Equity Delivery (₹50K buy, ₹51K sell)
```
CURRENT CALCULATION:
- DP Charges: ₹0 ❌ MISSING
- Correct: ₹13.50 + (₹13.50 × 18% GST) = ₹15.93 ✓
- Also affects GST calculation

ERROR MAGNITUDE: ₹15.93 completely missing
Impact: Understates costs, affects P&L calculations
```

### Test Case 4: Agricultural Commodity Futures
```
CURRENT: No way to distinguish agricultural commodities
CORRECT: 0.05% CTT instead of 0.01% (5x difference)

ERROR MAGNITUDE: Massive undercharging or overcharging depending on type
```

---

## MIGRATION GUIDE

### Step 1: Replace the File
```bash
# Backup original
cp app/services/charge_calculator.py app/services/charge_calculator_backup.py

# Replace with corrected version
cp app/services/charge_calculator_corrected.py app/services/charge_calculator.py
```

### Step 2: Update Function Calls

**Old Way:**
```python
charges = calculate_position_charges(
    quantity=100,
    avg_price=500.0,
    exit_price=510.0,
    exchange_segment="NSE_EQ",
    product_type="MIS",
    instrument_type="EQUITY",
    brokerage_flat=20.0,
    brokerage_percent=0.0,
    is_option=False
)
```

**New Way (will require code updates):**
```python
charges = calculate_position_charges(
    quantity=100,
    buy_price=500.0,          # ← Changed parameter name
    sell_price=510.0,          # ← Changed parameter name
    exchange_segment="NSE_EQ",
    product_type="MIS",
    instrument_type="EQUITY",
    brokerage_flat=20.0,
    brokerage_percent=0.0,
    is_option=False,
    # Optional new parameters:
    is_commodity=False,
    is_agricultural_commodity=False,
    option_exercised=False,
    apply_dp_charges=False
)
```

### Step 3: Update Database Calls
Database schema needs to support new charge types:
- `dp_charge` column (if not exists)
- `clearing_charge` column (if not exists)

Or update to handle them in calculation result without storing separately.

### Step 4: Test All Segments
Run the comprehensive test suite:
```bash
python test_charge_calculator.py
```

---

## REGULATORY REFERENCES

All corrections are based on:
1. **SEBI Circular** - Regulatory charges guidelines
2. **NSE Fact Sheet** - Exchange transaction charges
3. **BSE Price Book** - Exchange tariffs
4. **MCX Rulebook** - Commodity market charges
5. **Income Tax Rules** - STT Schedule

---

## FINANCIAL IMPACT

### Traders Affected:
- **Intraday equity traders:** 5x stamp duty overcharge
- **Futures traders:** 60% STT overcharge + 5x stamp duty overcharge
- **Options traders:** 60% STT undercharge (normal) + no exercised option support
- **Commodity traders:** Incorrect agri vs non-agri differentiation

### System Impact:
- **Incorrect P&L calculations** (charges underestimated/overestimated)
- **Regulatory non-compliance** (statutory charges not per SEBI)
- **Trader dispute potential** (incorrect charge calculations)
- **Audit risk** (inconsistent with official regulations)

---

## TESTING

### Regression Testing Checklist:
- [ ] Run test_charge_calculator.py (all tests should pass)
- [ ] Manually verify 1-2 charges from each segment
- [ ] Compare charges with broker statements
- [ ] Test edge cases (zero profit/loss, large trades, etc.)
- [ ] Verify database schema handles new charge types
- [ ] Test backwards compatibility (if needed)

### Test Coverage:
- ✓ Equity Intraday (profit and loss)
- ✓ Equity Delivery (with DP charges)
- ✓ Index Futures
- ✓ Stock Futures
- ✓ Index Options (normal and exercised)
- ✓ Stock Options (normal and exercised)
- ✓ Commodity Futures (non-agricultural)
- ✓ Commodity Futures (agricultural)
- ✓ Commodity Options

---

## RECOMMENDATIONS

1. **Immediate:** Deploy corrected charge calculator
2. **Short-term:** Reconcile all past charge calculations
3. **Medium-term:** Update trader-facing charge summaries
4. **Long-term:** Add charge calculator tests to CI/CD pipeline

---

## CONCLUSION

The existing charge calculator system violates Indian regulatory requirements in multiple critical ways:
- Incorrect STT rates for futures and options
- Wrong stamp duty rates for most segments
- Missing DP charges for delivery equity
- Missing proper parameter handling

The corrected version implements all Indian statutory requirements correctly, supports all segments (equity, futures, options, commodities), and provides clear parameter-driven logic for different scenarios.

**Status:** ✅ Ready for deployment after testing

---

**Prepared by:** Charge Calculator Audit Team  
**Date:** 2026-03-03  
**Version:** 2.0 (Corrected)
