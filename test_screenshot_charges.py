#!/usr/bin/env python3
"""
Test: Replicate the EXACT calculation for screenshot positions
"""
from decimal import Decimal
from app.services.charge_calculator import calculate_position_charges

# From Nikhil Maiji screenshot
# Trade 1: NIFTY 24650 PE - Buy ₹69.10, qty 130, Sell ₹46.20
print("\n" + "="*100)
print("NIKHIL MAIJI - NIFTY 24650 PE")
print("="*100)
print("Buy: qty 130 @ ₹69.10    | Sell: qty 130 @ ₹46.20")
print("Screenshot Trade Expense: ₹3.60")
print()

try:
    charges_pe1 = calculate_position_charges(
        quantity=130,
        buy_price=69.10,
        sell_price=46.20,
        exchange_segment="NSE_FNO",
        product_type="MIS",
        instrument_type="OPTIDX",  # Assuming NIFTY is index options
        brokerage_flat=20.0,  # Default flat fee
        brokerage_percent=0.0,
        is_option=True
    )
    
    print("Calculated Charges:")
    for key, val in sorted(charges_pe1.items()):
        print(f"  {key:20} = ₹{val:10.2f}")
    
    print(f"\nMATCH? Trade Expense {charges_pe1['trade_expense']:.2f} == Screenshot ₹3.60? {charges_pe1['trade_expense'] == 3.60}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()


#From screenshot - Super Admin equity
print("\n" + "="*100)
print("SUPER ADMIN - LENSKART (EQUITY)")
print("="*100)
print("Buy: qty 380 @ ₹524.60  | Sell: qty 380 @ (calc from value)")
print("Screenshot Trade Expense: ₹0.00")
print()

try:
    charges_eq = calculate_position_charges(
        quantity=380,
        buy_price=524.60,
        sell_price=524.60,  # Assuming breakeven for nil brokerage user
        exchange_segment="NSE_EQ",
        product_type="NORMAL",
        instrument_type="EQUITY",
        brokerage_flat=0.0,  # NIL BROKERAGE
        brokerage_percent=0.0,
        is_option=False
    )
    
    print("Calculated Charges:")
    for key, val in sorted(charges_eq.items()):
        print(f"  {key:20} = ₹{val:10.2f}")
    
    print(f"\nMATCH? Trade Expense {charges_eq['trade_expense']:.2f} == Screenshot ₹0.00? {charges_eq['trade_expense'] == 0.0}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()


# Test with higher price equity to see STT calculation
print("\n" + "="*100)
print("TEST - EQUITY DELIVERY (with brokerage)")
print("="*100)
print("Buy: qty 400 @ ₹450  | Sell: qty 400 @ ₹480")
print()

try:
    charges_test = calculate_position_charges(
        quantity=400,
        buy_price=450.0,
        sell_price=480.0,
        exchange_segment="NSE_EQ",
        product_type="NORMAL",
        instrument_type="EQUITY",
        brokerage_flat=20.0,
        brokerage_percent=0.0,
        is_option=False
    )
    
    print("Calculated Charges:")
    for key, val in sorted(charges_test.items()):
        print(f"  {key:20} = ₹{val:10.2f}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
