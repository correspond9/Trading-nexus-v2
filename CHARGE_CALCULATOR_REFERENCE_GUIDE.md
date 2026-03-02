# CHARGE CALCULATOR - SEGMENT REFERENCE & CALCULATION GUIDE

## Quick Segment Identification

| Segment | Code | Type | Example | Intraday | Delivery |
|---------|------|------|---------|----------|----------|
| **Equity** | NSE_EQ, BSE_EQ | EQUITY | TCS, INFY | MIS | NORMAL |
| **Index Futures** | NSE_FNO | FUTIDX | NIFTY50, BANKNIFTY | MIS | NORMAL* |
| **Stock Futures** | NSE_FNO | FUTSTK | TCS-FUT, INFY-FUT | MIS | NORMAL* |
| **Index Options** | NSE_FNO | OPTIDX | NIFTY50-CALL, PE | MIS | Expiry |
| **Stock Options** | NSE_FNO | OPTSTK | TCS-CALL, PE | MIS | Expiry |
| **Commodity Futures** | MCX_COMM | FUTCOM | CRUDEOIL, TURMERIC | MIS | NORMAL |
| **Commodity Options** | MCX_COMM | OPTCOM | GOLD-CALL, PE | MIS | Expiry |

*Delivery settlement is rare for futures (only for physical delivery commodities)

---

## CHARGE CALCULATION STRUCTURE BY SEGMENT

### 1️⃣ EQUITY - INTRADAY (MIS)

**Example Trade:** Buy 100 TCS @ ₹3,500, Sell @ ₹3,510

```
Turnover = (3500 × 100) + (3510 × 100) = ₹701,000

1. BROKERAGE: ₹20.00 (flat fee)
2. STT: ₹351,000 × 0.025% = ₹87.75 (SELL side only)
3. STAMP DUTY: ₹350,000 × 0.003% = ₹10.50 (BUY side only)
4. EXCHANGE: ₹701,000 × 0.00325% = ₹22.78
5. SEBI: ₹701,000 × 0.0001% = ₹0.70
6. DP: ₹0 (not applicable for intraday)
7. GST (18%): (20 + 22.78 + 0.70) × 18% = ₹7.69

PLATFORM COST (Brokerage): ₹20.00
TRADE EXPENSE (Regulatory): ₹87.75 + 10.50 + 22.78 + 0.70 + 0 + 7.69 = ₹129.42
TOTAL CHARGES: ₹149.42
```

**✓ No DP charges for intraday**  
**✓ STT on SELL side only**  
**✓ Lowest stamp duty rate (0.003%)**

---

### 2️⃣ EQUITY - DELIVERY (NORMAL)

**Example Trade:** Buy 100 TCS @ ₹3,500, Sell (deliver) @ ₹3,510

```
Turnover = ₹701,000 (same quantities)

1. BROKERAGE: ₹20.00
2. STT: (₹350,000 × 0.1%) + (₹351,000 × 0.1%) = ₹701.00 (BOTH SIDES)
3. STAMP DUTY: ₹350,000 × 0.015% = ₹52.50 (BUY side only)
4. EXCHANGE: ₹701,000 × 0.00325% = ₹22.78
5. SEBI: ₹701,000 × 0.0001% = ₹0.70
6. DP: ₹13.50 (flat, per ISIN on SELL side only)
7. GST (18%): (20 + 22.78 + 0.70 + 13.50) × 18% = ₹9.95

PLATFORM COST: ₹20.00
TRADE EXPENSE: ₹701.00 + 52.50 + 22.78 + 0.70 + 13.50 + 9.95 = ₹800.43
TOTAL CHARGES: ₹820.43
```

**⚠️ 5x higher STT (0.1% vs 0.025%)**  
**⚠️ Higher stamp duty (0.015% vs 0.003%)**  
**⚠️ DP charges apply (₹13.50 per ISIN)**  
**⚠️ Much higher total charges**

---

### 3️⃣ INDEX FUTURES (FUTIDX)

**Example Trade:** Buy 50 NIFTY50 @ ₹20,000, Sell @ ₹20,100

```
Turnover = (20000 × 50) + (20100 × 50) = ₹2,005,000

1. BROKERAGE: ₹40.00 (flat fee, higher for futures)
2. STT: ₹1,002,500 × 0.0125% = ₹125.31 (SELL side only)
3. STAMP DUTY: ₹1,000,000 × 0.002% = ₹20.00 (BUY side, lower rate)
4. EXCHANGE: ₹2,005,000 × 0.002% = ₹40.10
5. SEBI: ₹2,005,000 × 0.0001% = ₹2.01
6. DP: ₹0 (not for futures)
7. GST (18%): (40 + 40.10 + 2.01) × 18% = ₹14.78

PLATFORM COST: ₹40.00
TRADE EXPENSE: ₹125.31 + 20 + 40.10 + 2.01 + 14.78 = ₹202.20
TOTAL CHARGES: ₹242.20
```

**✓ Low stamp duty (0.002%)**  
**✓ Low STT (0.0125%)**  
**✓ No DP charges**  
**✓ Much lower charges than equity**

---

### 4️⃣ INDEX OPTIONS - NORMAL EXPIRY

**Example Trade:** Buy 100 NIFTY50 CALL @ ₹200 premium, Sell @ ₹250

```
Premium Turnover = (200 × 100) + (250 × 100) = ₹45,000

1. BROKERAGE: ₹30.00
2. STT: (₹45,000 / 2) × 0.0625% = ₹14.06 (SELL premium only, NORMAL rate)
3. STAMP DUTY: (₹45,000 / 2) × 0.003% = ₹0.68 (BUY premium only)
4. EXCHANGE: ₹45,000 × 0.035% = ₹15.75 (on premium)
5. SEBI: ₹45,000 × 0.0001% = ₹0.045
6. DP: ₹0 (not for options)
7. GST (18%): (30 + 15.75 + 0.045) × 18% = ₹8.23

PLATFORM COST: ₹30.00
TRADE EXPENSE: ₹14.06 + 0.68 + 15.75 + 0.045 + 8.23 = ₹38.72
TOTAL CHARGES: ₹68.72
```

**✓ STT at NORMAL rate (0.0625%)**  
**✓ Very low charges for options**  
**✓ Premium-based calculation**

---

### 5️⃣ INDEX OPTIONS - EXERCISED

**Same premium values, but STT rate is DOUBLED**

```
Premium Turnover = ₹45,000 (same)

STT: (₹45,000 / 2) × 0.125% = ₹28.13 (EXERCISED rate, 2x normal)

[All other charges remain same]

TOTAL CHARGES: ₹97.35 (vs ₹68.72 for normal expiry)
```

**⚠️ STT doubles if option is exercised (0.125% instead of 0.0625%)**  
**⚠️ Exercise scenario needs flag: `option_exercised=True`**

---

### 6️⃣ COMMODITY FUTURES - NON-AGRICULTURAL

**Example Trade:** Buy 100 Crude Oil @ ₹4,000/barrel, Sell @ ₹4,100

```
Turnover = (4000 × 100) + (4100 × 100) = ₹810,000

1. BROKERAGE: ₹50.00
2. CTT: ₹405,000 × 0.01% = ₹40.50 (SELL side only, NON-AGRI rate)
3. STAMP DUTY: ₹400,000 × 0.002% = ₹8.00 (BUY side)
4. EXCHANGE: ₹810,000 × 0.0002% = ₹1.62
5. SEBI: ₹810,000 × 0.0001% = ₹0.81
6. DP: ₹0 (commodity futures)
7. GST (18%): (50 + 1.62 + 0.81) × 18% = ₹9.29

PLATFORM COST: ₹50.00
TRADE EXPENSE: ₹40.50 + 8.00 + 1.62 + 0.81 + 9.29 = ₹60.22
TOTAL CHARGES: ₹110.22
```

**✓ Use rate: `is_commodity=True, is_agricultural_commodity=False`**  
**✓ CTT 0.01% (non-agricultural)**  
**✓ Higher exchange charges than equity futures**

---

### 7️⃣ COMMODITY FUTURES - AGRICULTURAL

**Same trade parameters, but with AGRICULTURAL commodity (e.g., Turmeric)**

```
CTT: ₹405,000 × 0.05% = ₹202.50 (5x HIGHER than non-agri!)

TOTAL CHARGES: ₹261.00 (vs ₹110.22 for non-agri)
```

**⚠️ Agricultural commodities have 5x higher CTT rate (0.05% vs 0.01%)**  
**⚠️ Use flag: `is_commodity=True, is_agricultural_commodity=True`**  
**⚠️ Massive impact on charge calculation**

---

### 8️⃣ COMMODITY OPTIONS

**Example Trade:** Buy 50 Gold options @ ₹100 premium, Sell @ ₹150

```
Premium Turnover = (100 × 50) + (150 × 50) = ₹12,500

CTT: (₹12,500 / 2) × 0.05% = ₹3.13 (SELL premium only)
STAMP DUTY: (₹12,500 / 2) × 0.003% = ₹0.19 (BUY premium only)

[Rest follow similar pattern as equity options]

TOTAL CHARGES: ~₹35-40 (estimated)
```

**✓ Use flag: `is_commodity=True, is_option=True`**  
**✓ CTT on premium value only**

---

## PARAMETER MAPPING QUICK REFERENCE

```python
# ===== EQUITY INTRADAY =====
calculate_position_charges(
    quantity=100,
    buy_price=500.0,
    sell_price=510.0,
    exchange_segment='NSE_EQ',      # or 'BSE_EQ'
    product_type='MIS',              # Key: 'MIS' for intraday
    instrument_type='EQUITY',
    apply_dp_charges=False            # No DP for intraday
)

# ===== EQUITY DELIVERY =====
calculate_position_charges(
    quantity=100,
    buy_price=500.0,
    sell_price=510.0,
    exchange_segment='NSE_EQ',
    product_type='NORMAL',            # Key: 'NORMAL' for delivery
    instrument_type='EQUITY',
    apply_dp_charges=True             # Apply DP charges
)

# ===== INDEX FUTURES =====
calculate_position_charges(
    quantity=50,                      # Contracts
    buy_price=20000.0,
    sell_price=20100.0,
    exchange_segment='NSE_FNO',
    product_type='MIS',
    instrument_type='FUTIDX',         # Key identifier
)

# ===== STOCK FUTURES =====
calculate_position_charges(
    quantity=100,
    buy_price=2000.0,
    sell_price=2050.0,
    exchange_segment='NSE_FNO',
    product_type='MIS',
    instrument_type='FUTSTK',         # Key identifier
)

# ===== INDEX OPTIONS - NORMAL =====
calculate_position_charges(
    quantity=100,
    buy_price=200.0,
    sell_price=250.0,
    exchange_segment='NSE_FNO',
    product_type='MIS',
    instrument_type='OPTIDX',
    is_option=True,                   # Critical flag
    option_exercised=False            # Normal expiry
)

# ===== INDEX OPTIONS - EXERCISED =====
calculate_position_charges(
    quantity=100,
    buy_price=200.0,
    sell_price=250.0,
    exchange_segment='NSE_FNO',
    product_type='MIS',
    instrument_type='OPTIDX',
    is_option=True,
    option_exercised=True             # EXERCISED (double STT)
)

# ===== COMMODITY FUTURES - NON-AGRICULTURAL =====
calculate_position_charges(
    quantity=100,
    buy_price=4000.0,
    sell_price=4100.0,
    exchange_segment='MCX_COMM',
    product_type='MIS',
    instrument_type='FUTCOM',         # Commodity futures
    is_commodity=True,
    is_agricultural_commodity=False   # Non-agri rate
)

# ===== COMMODITY FUTURES - AGRICULTURAL =====
calculate_position_charges(
    quantity=100,
    buy_price=4000.0,
    sell_price=4100.0,
    exchange_segment='MCX_COMM',
    product_type='MIS',
    instrument_type='FUTCOM',
    is_commodity=True,
    is_agricultural_commodity=True    # Agri rate (5x higher)
)

# ===== COMMODITY OPTIONS =====
calculate_position_charges(
    quantity=50,
    buy_price=100.0,
    sell_price=150.0,
    exchange_segment='MCX_COMM',
    product_type='MIS',
    instrument_type='OPTCOM',         # Commodity option
    is_option=True,
    is_commodity=True
)
```

---

## CHARGE COMPARISON MATRIX

| Metric | Equity Intraday | Equity Delivery | Futures | Options |
|--------|-----------------|-----------------|---------|---------|
| **STT Rate** | 0.025% (sell) | 0.1% (both) | 0.0125% (sell) | 0.0625%/0.125% |
| **Stamp Duty** | 0.003% | 0.015% | 0.002% | 0.003% |
| **DP Charges** | No | Yes (₹13.50) | No | No |
| **Exchange Fee** | 0.00325% | 0.00325% | 0.002% | 0.035% |
| **Relative Cost** | BASE | 5-6x | 0.3-0.4x | 0.2-0.3x |

---

## COMMON MISTAKES TO AVOID

❌ **Mistake 1:** Using 'MIS' for delivery trades  
✓ **Correct:** Use 'NORMAL' for delivery

❌ **Mistake 2:** Forgetting `apply_dp_charges=True` for equity delivery  
✓ **Correct:** Always set to True for NORMAL equity trades

❌ **Mistake 3:** Not setting `option_exercised=True` when option is exercised  
✓ **Correct:** Set based on actual settlement type

❌ **Mistake 4:** Forgetting `is_agricultural_commodity=True` for agri commodities  
✓ **Correct:** Always check commodity type for MCX trades

❌ **Mistake 5:** Using wrong segment codes  
✓ **Correct:** NSE_EQ (equity), NSE_FNO (futures/options), MCX_COMM (commodities)

---

## EXAMPLE OUTPUT STRUCTURE

```json
{
  "brokerage_charge": 20.00,
  "stt_ctt_charge": 87.75,
  "stamp_duty": 10.50,
  "exchange_charge": 22.78,
  "sebi_charge": 0.70,
  "dp_charge": 0.00,
  "clearing_charge": 0.00,
  "gst_charge": 7.69,
  
  "platform_cost": 20.00,           // What broker keeps
  "trade_expense": 129.42,          // Regulatory charges
  "total_charges": 149.42           // Total cost to trader
}
```

---

**Created:** 2026-03-03  
**Version:** 2.0 (Corrected)  
**For Use With:** charge_calculator_corrected.py
