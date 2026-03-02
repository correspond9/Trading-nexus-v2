#!/usr/bin/env python3
"""
Calculate statutory charges for the three user scenarios
"""

from app.services.charge_calculator import calculate_position_charges

print("\n" + "="*80)
print("STATUTORY CHARGES CALCULATION")
print("="*80)

# Scenario 1: EQUITY Delivery
print("\n" + "-"*80)
print("SCENARIO 1: EQUITY DELIVERY")
print("-"*80)
print("Buy Price:  ₹450")
print("Sell Price: ₹480")
print("Quantity:   400")
print()

charges1 = calculate_position_charges(
    quantity=400,
    buy_price=450.0,
    sell_price=480.0,
    exchange_segment="NSE_EQ",
    product_type="NORMAL",      # DELIVERY
    instrument_type="EQUITY",
    brokerage_flat=0.0,
    brokerage_percent=0.0,
    is_option=False
)

print("Statutory Charges Breakdown:")
print(f"  STT/CTT:            ₹{charges1['stt_ctt_charge']:>10.2f}")
print(f"  Stamp Duty:         ₹{charges1['stamp_duty']:>10.2f}")
print(f"  Exchange Charge:    ₹{charges1['exchange_charge']:>10.2f}")
print(f"  SEBI Charge:        ₹{charges1['sebi_charge']:>10.2f}")
print(f"  DP Charge:          ₹{charges1['dp_charge']:>10.2f}")
print(f"  Clearing Charge:    ₹{charges1['clearing_charge']:>10.2f}")
print(f"  GST (18%):          ₹{charges1['gst_charge']:>10.2f}")
print(f"  " + "-"*40)
print(f"  TOTAL TRADE EXPENSE:₹{charges1['trade_expense']:>10.2f}")
print(f"\nBrokerage Charge:   ₹{charges1['brokerage_charge']:>10.2f}")
print(f"TOTAL CHARGES:      ₹{charges1['total_charges']:>10.2f}")

# Scenario 2: F&O Options
print("\n" + "-"*80)
print("SCENARIO 2: F&O OPTIONS (Equity)")
print("-"*80)
print("Buy Price:  ₹100")
print("Sell Price: ₹110")
print("Quantity:   650")
print()

charges2 = calculate_position_charges(
    quantity=650,
    buy_price=100.0,
    sell_price=110.0,
    exchange_segment="NSE_FNO",
    product_type="MIS",
    instrument_type="OPTIDX",   # OR OPTSTK, rates same
    brokerage_flat=0.0,
    brokerage_percent=0.0,
    is_option=True,
    option_exercised=False
)

print("Statutory Charges Breakdown:")
print(f"  STT/CTT:            ₹{charges2['stt_ctt_charge']:>10.2f}")
print(f"  Stamp Duty:         ₹{charges2['stamp_duty']:>10.2f}")
print(f"  Exchange Charge:    ₹{charges2['exchange_charge']:>10.2f}")
print(f"  SEBI Charge:        ₹{charges2['sebi_charge']:>10.2f}")
print(f"  DP Charge:          ₹{charges2['dp_charge']:>10.2f}")
print(f"  Clearing Charge:    ₹{charges2['clearing_charge']:>10.2f}")
print(f"  GST (18%):          ₹{charges2['gst_charge']:>10.2f}")
print(f"  " + "-"*40)
print(f"  TOTAL TRADE EXPENSE:₹{charges2['trade_expense']:>10.2f}")
print(f"\nBrokerage Charge:   ₹{charges2['brokerage_charge']:>10.2f}")
print(f"TOTAL CHARGES:      ₹{charges2['total_charges']:>10.2f}")

# Scenario 3: Futures (Index or Stock - same rates)
print("\n" + "-"*80)
print("SCENARIO 3: FUTURES (Index/Stock - same rates)")
print("-"*80)
print("Buy Price:  ₹25,100")
print("Sell Price: ₹25,200")
print("Quantity:   650")
print()

charges3 = calculate_position_charges(
    quantity=650,
    buy_price=25100.0,
    sell_price=25200.0,
    exchange_segment="NSE_FNO",
    product_type="MIS",
    instrument_type="FUTIDX",   # OR FUTSTK, rates same
    brokerage_flat=0.0,
    brokerage_percent=0.0,
    is_option=False
)

print("Statutory Charges Breakdown:")
print(f"  STT/CTT:            ₹{charges3['stt_ctt_charge']:>10.2f}")
print(f"  Stamp Duty:         ₹{charges3['stamp_duty']:>10.2f}")
print(f"  Exchange Charge:    ₹{charges3['exchange_charge']:>10.2f}")
print(f"  SEBI Charge:        ₹{charges3['sebi_charge']:>10.2f}")
print(f"  DP Charge:          ₹{charges3['dp_charge']:>10.2f}")
print(f"  Clearing Charge:    ₹{charges3['clearing_charge']:>10.2f}")
print(f"  GST (18%):          ₹{charges3['gst_charge']:>10.2f}")
print(f"  " + "-"*40)
print(f"  TOTAL TRADE EXPENSE:₹{charges3['trade_expense']:>10.2f}")
print(f"\nBrokerage Charge:   ₹{charges3['brokerage_charge']:>10.2f}")
print(f"TOTAL CHARGES:      ₹{charges3['total_charges']:>10.2f}")

# Summary
print("\n" + "="*80)
print("SUMMARY TABLE")
print("="*80)
print(f"\n{'Scenario':<20} {'Turnover':<15} {'Trade Expense':<15} {'% of Turnover':<15}")
print("-"*80)

turnover1 = 400 * (450 + 480)
turnover2 = 650 * (100 + 110)
turnover3 = 650 * (25100 + 25200)

pct1 = (charges1['trade_expense'] / turnover1) * 100
pct2 = (charges2['trade_expense'] / turnover2) * 100
pct3 = (charges3['trade_expense'] / turnover3) * 100

print(f"{'Equity Delivery':<20} ₹{turnover1:>12,.0f}  ₹{charges1['trade_expense']:>12,.2f}  {pct1:>12.3f}%")
print(f"{'F&O Options':<20} ₹{turnover2:>12,.0f}  ₹{charges2['trade_expense']:>12,.2f}  {pct2:>12.3f}%")
print(f"{'Futures':<20} ₹{turnover3:>12,.0f}  ₹{charges3['trade_expense']:>12,.2f}  {pct3:>12.3f}%")

print("\n" + "="*80)
