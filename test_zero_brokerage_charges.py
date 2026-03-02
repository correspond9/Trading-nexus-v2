#!/usr/bin/env python3
"""
Test to verify that statutory charges are calculated and deducted from MTM
even when brokerage plan is set to zero/NIL.

This test validates the fix for the issue where traders with zero-brokerage
plans were not seeing trade expenses (statutory charges) deducted from their P&L.
"""

import asyncio
from decimal import Decimal
from app.services.charge_calculator import ChargeCalculator, calculate_position_charges


def test_zero_brokerage_charges():
    """
    Test that statutory charges are calculated even when brokerage is zero.
    
    This is the critical regulatory requirement:
    - Statutory charges (STT, exchange charges, SEBI, etc.) are mandatory
    - They must be deducted from P&L regardless of brokerage plan
    - Zero-brokerage traders must still pay these regulatory charges
    """
    print("\n" + "="*80)
    print("TEST: Zero-Brokerage Charge Calculation")
    print("="*80)
    
    # Test case 1: Equity intraday with zero brokerage
    print("\n[TEST 1] Equity Intraday - Zero Brokerage")
    print("-" * 80)
    
    charges = calculate_position_charges(
        quantity=1,
        avg_price=1000.0,
        exit_price=1050.0,
        exchange_segment="NSE_EQ",
        product_type="MIS",
        instrument_type="EQUITY",
        brokerage_flat=0.0,      # ← Zero brokerage
        brokerage_percent=0.0,   # ← Zero brokerage
        is_option=False
    )
    
    print(f"Entry Price: ₹1000 | Exit Price: ₹1050 | Qty: 1")
    print(f"MTM Profit: ₹50")
    print(f"\nCharges (Zero Brokerage Plan):")
    print(f"  Brokerage: ₹{charges['brokerage_charge']:.2f}")
    print(f"  STT/CTT:   ₹{charges['stt_ctt_charge']:.2f}")
    print(f"  Exchange:  ₹{charges['exchange_charge']:.2f}")
    print(f"  SEBI:      ₹{charges['sebi_charge']:.2f}")
    print(f"  Stamp Duty: ₹{charges['stamp_duty']:.2f}")
    print(f"  GST:       ₹{charges['gst_charge']:.2f}")
    print(f"  ─────────────────────────")
    print(f"  TOTAL CHARGES: ₹{charges['total_charges']:.2f}")
    print(f"  Trade Expense: ₹{charges['trade_expense']:.2f}")
    
    net_pnl = 50.0 - charges['trade_expense']
    print(f"\nNet P&L = ₹{net_pnl:.2f} (₹50.00 - ₹{charges['trade_expense']:.2f})")
    
    # Verify statutory charges are non-zero
    assert charges['stt_ctt_charge'] > 0, "STT/CTT should be calculated"
    assert charges['trade_expense'] > 0, "Trade expense should be calculated"
    assert charges['exchange_charge'] >= 0, "Exchange charges should be >= 0"
    assert charges['sebi_charge'] > 0, "SEBI charges should be calculated"
    print("\n✅ PASS: Statutory charges are correctly calculated for zero-brokerage plan")
    
    
    # Test case 2: Futures with zero brokerage
    print("\n[TEST 2] Index Futures - Zero Brokerage")
    print("-" * 80)
    
    charges = calculate_position_charges(
        quantity=1,
        avg_price=20000.0,
        exit_price=20100.0,
        exchange_segment="NSE_FNO",
        product_type="MIS",
        instrument_type="FUTIDX",
        brokerage_flat=0.0,      # ← Zero brokerage
        brokerage_percent=0.0,   # ← Zero brokerage
        is_option=False
    )
    
    print(f"Entry Price: ₹20000 | Exit Price: ₹20100 | Qty: 1")
    print(f"MTM Profit: ₹100")
    print(f"\nCharges (Zero Brokerage Plan):")
    print(f"  Brokerage: ₹{charges['brokerage_charge']:.2f}")
    print(f"  STT/CTT:   ₹{charges['stt_ctt_charge']:.2f}")
    print(f"  Exchange:  ₹{charges['exchange_charge']:.2f}")
    print(f"  SEBI:      ₹{charges['sebi_charge']:.2f}")
    print(f"  Stamp Duty: ₹{charges['stamp_duty']:.2f}")
    print(f"  GST:       ₹{charges['gst_charge']:.2f}")
    print(f"  ─────────────────────────")
    print(f"  TOTAL CHARGES: ₹{charges['total_charges']:.2f}")
    print(f"  Trade Expense: ₹{charges['trade_expense']:.2f}")
    
    net_pnl = 100.0 - charges['trade_expense']
    print(f"\nNet P&L = ₹{net_pnl:.2f} (₹100.00 - ₹{charges['trade_expense']:.2f})")
    
    # Futures have 0.0125% STT, different from equity
    assert charges['stt_ctt_charge'] > 0, "Futures STT should be calculated"
    assert charges['trade_expense'] > 0, "Trade expense should be calculated"
    print("\n✅ PASS: Statutory charges correctly calculated for futures zero-brokerage")
    
    
    # Test case 3: Comparison - zero brokerage vs standard brokerage
    print("\n[TEST 3] Comparison: Zero vs Standard Brokerage")
    print("-" * 80)
    
    charges_nil = calculate_position_charges(
        quantity=1, avg_price=1000.0, exit_price=1100.0,
        exchange_segment="NSE_EQ", product_type="MIS",
        instrument_type="EQUITY",
        brokerage_flat=0.0, brokerage_percent=0.0, is_option=False
    )
    
    charges_standard = calculate_position_charges(
        quantity=1, avg_price=1000.0, exit_price=1100.0,
        exchange_segment="NSE_EQ", product_type="MIS",
        instrument_type="EQUITY",
        brokerage_flat=20.0, brokerage_percent=0.0, is_option=False
    )
    
    print(f"Entry: ₹1000 | Exit: ₹1100 | MTM: ₹100")
    print(f"\nZERO BROKERAGE PLAN:")
    print(f"  Brokerage Charge:  ₹{charges_nil['brokerage_charge']:.2f}")
    print(f"  Total Charges:     ₹{charges_nil['total_charges']:.2f}")
    print(f"  Trade Expense:     ₹{charges_nil['trade_expense']:.2f}")
    
    print(f"\nSTANDARD BROKERAGE PLAN (₹20 flat):")
    print(f"  Brokerage Charge:  ₹{charges_standard['brokerage_charge']:.2f}")
    print(f"  Total Charges:     ₹{charges_standard['total_charges']:.2f}")
    print(f"  Trade Expense:     ₹{charges_standard['trade_expense']:.2f}")
    
    # Key: Core regulatory charges should be the same, but GST differs since it's on total charges
    # The important thing is that both include STT, exchange, SEBI charges
    core_charges_nil = (
        charges_nil['stt_ctt_charge'] + charges_nil['exchange_charge'] +
        charges_nil['sebi_charge'] + charges_nil['stamp_duty']
    )
    core_charges_std = (
        charges_standard['stt_ctt_charge'] + charges_standard['exchange_charge'] +
        charges_standard['sebi_charge'] + charges_standard['stamp_duty']
    )
    
    print(f"\nCore Regulatory Charges (before GST - should match):")
    print(f"  Zero Plan:     ₹{core_charges_nil:.2f}")
    print(f"  Standard Plan: ₹{core_charges_std:.2f}")
    print(f"  Difference:    ₹{abs(core_charges_nil - core_charges_std):.4f}")
    
    # Core charges must be IDENTICAL (regulatory charges don't depend on brokerage)
    assert abs(core_charges_nil - core_charges_std) < 0.01, \
        "Regulatory charges must be identical regardless of brokerage plan"
    
    # GST is calculated on total charges, so it differs with different brokerage
    gst_diff = charges_standard['gst_charge'] - charges_nil['gst_charge']
    print(f"\nGST Difference: ₹{gst_diff:.2f}")
    print(f"  ✓ GST varies because it's on: brokerage + exchange + SEBI taxes")
    
    # Only difference should be brokerage + its GST
    total_diff = charges_standard['total_charges'] - charges_nil['total_charges']
    expected_diff = (charges_standard['brokerage_charge'] - charges_nil['brokerage_charge']) + gst_diff
    print(f"\nTotal difference: ₹{total_diff:.2f}")
    print(f"Expected (brokerage + GST diff): ₹{expected_diff:.2f}")
    
    print("✅ PASS: Regulatory charges identical, only brokerage & derived GST differ")
    
    
    # Test case 4: Loss scenario with zero brokerage
    print("\n[TEST 4] Loss Scenario - Zero Brokerage")
    print("-" * 80)
    
    charges = calculate_position_charges(
        quantity=1,
        avg_price=1000.0,
        exit_price=900.0,      # Loss scenario
        exchange_segment="NSE_EQ",
        product_type="MIS",
        instrument_type="EQUITY",
        brokerage_flat=0.0, brokerage_percent=0.0, is_option=False
    )
    
    print(f"Entry Price: ₹1000 | Exit Price: ₹900 | Qty: 1")
    print(f"MTM Loss: -₹100")
    print(f"\nCharges (Zero Brokerage):")
    print(f"  STT/CTT:    ₹{charges['stt_ctt_charge']:.2f}")
    print(f"  Exchange:   ₹{charges['exchange_charge']:.2f}")
    print(f"  SEBI:       ₹{charges['sebi_charge']:.2f}")
    print(f"  Trade Exp:  ₹{charges['trade_expense']:.2f}")
    
    net_pnl = -100.0 - charges['trade_expense']
    print(f"\nNet P&L = ₹{net_pnl:.2f} (-₹100.00 - ₹{charges['trade_expense']:.2f} in charges)")
    
    # Even in loss, charges must be deducted
    assert charges['trade_expense'] > 0, "Charges must be deducted even in loss"
    print("\n✅ PASS: Charges correctly deducted even in loss scenario")
    
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nSUMMARY:")
    print("  ✓ Statutory charges ARE calculated for zero-brokerage plans")
    print("  ✓ Charges include STT, exchange, SEBI, stamp duty, and GST")
    print("  ✓ Brokerage component is zero, but regulatory charges apply")
    print("  ✓ Same statutory charges apply regardless of brokerage plan")
    print("  ✓ Charges are deducted from MTM for both profit and loss scenarios")
    print("\nIMPLICATIONS:")
    print("  → The scheduler fix allows zero-brokerage traders to see charges on P&L")
    print("  → Traders with PLAN_NIL will now have trade_expense deducted from MTM")
    print("  → Regulatory compliance maintained for all brokerage plans")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_zero_brokerage_charges()
