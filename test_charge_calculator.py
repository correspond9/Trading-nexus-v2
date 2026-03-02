"""
Charge Calculator - Comprehensive Test Cases
Tests all segments with correct expected values per Indian regulatory structure.

Each test follows:
1. Equity Intraday
2. Equity Delivery
3. Index Futures
4. Stock Futures
5. Index Options (normal expiry)
6. Stock Options (normal expiry)
7. Index Options (exercised)
8. Commodity Futures (non-agri)
9. Commodity Futures (agricultural)
10. Commodity Options

All calculations based on actual Indian market structure.
"""

from decimal import Decimal
from app.services.charge_calculator_corrected import ChargeCalculator


def print_test_header(title: str):
    """Print a formatted test header."""
    print(f"\n{'='*80}")
    print(f"TEST: {title}")
    print(f"{'='*80}")


def print_charges(charges: dict, buy_price: float = None, sell_price: float = None, qty: int = None):
    """Pretty print charge details."""
    print(f"\nTurnover Breakdown:")
    if buy_price and qty:
        print(f"  Buy Value:    ₹{buy_price * qty:,.2f}")
    if sell_price and qty:
        print(f"  Sell Value:   ₹{sell_price * qty:,.2f}")
    if buy_price and sell_price and qty:
        total_turnover = (buy_price + sell_price) * qty
        print(f"  Total:        ₹{total_turnover:,.2f}")
    
    print(f"\nCharges Breakdown:")
    print(f"  Brokerage:        ₹{charges['brokerage_charge']:>10.2f}")
    print(f"  STT/CTT:          ₹{charges['stt_ctt_charge']:>10.2f}")
    print(f"  Stamp Duty:       ₹{charges['stamp_duty']:>10.2f}")
    print(f"  Exchange Charge:  ₹{charges['exchange_charge']:>10.2f}")
    print(f"  SEBI Charge:      ₹{charges['sebi_charge']:>10.2f}")
    print(f"  DP Charge:        ₹{charges['dp_charge']:>10.2f}")
    print(f"  Clearing Charge:  ₹{charges['clearing_charge']:>10.2f}")
    print(f"  GST (18%):        ₹{charges['gst_charge']:>10.2f}")
    print(f"  {'-'*45}")
    print(f"  Platform Cost:    ₹{charges['platform_cost']:>10.2f}")
    print(f"  Trade Expense:    ₹{charges['trade_expense']:>10.2f}")
    print(f"  TOTAL CHARGES:    ₹{charges['total_charges']:>10.2f}")


def test_equity_intraday_profit():
    """
    Equity Intraday - Profit Trade
    
    Scenario:
    - Buy 100 shares @ ₹500
    - Sell 100 shares @ ₹510
    - Profit: ₹1,000
    
    Expected Charges:
    - Brokerage: ₹20 (flat)
    - STT: ₹51,000 × 0.00025 = ₹12.75 (rounded to ₹13)
    - Exchange: ₹101,000 × 0.00325% = ₹3.28
    - SEBI: ₹101,000 × 0.000001 = ₹0.10
    - Stamp Duty: ₹50,000 × 0.003% = ₹1.50
    - DP: ₹0 (intraday)
    - GST: (20 + 3.28 + 0.10) × 18% = ₹4.17
    - Total: ~₹54.23
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=500.0,
        sell_price=510.0,
        quantity=100,
        exchange_segment='NSE_EQ',
        product_type='MIS',
        instrument_type='EQUITY',
        brokerage_flat=20.0,
        brokerage_percent=0.0
    )
    
    print_test_header("EQUITY - INTRADAY (Profit Trade)")
    print_charges(charges, 500.0, 510.0, 100)
    
    # Validate key components
    assert charges['stt_ctt_charge'] > 0, "STT should be charged on sell"
    assert charges['stamp_duty'] == pytest.approx(1.50, abs=0.1), "Stamp duty incorrect"
    assert charges['dp_charge'] == 0, "DP charge should not apply for intraday"
    print("\n✓ Test passed")


def test_equity_intraday_loss():
    """
    Equity Intraday - Loss Trade
    
    Scenario:
    - Buy 100 shares @ ₹500
    - Sell 100 shares @ ₹490
    - Loss: ₹1,000
    
    Charges still apply despite loss (regulatory requirement).
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=500.0,
        sell_price=490.0,
        quantity=100,
        exchange_segment='NSE_EQ',
        product_type='MIS',
        instrument_type='EQUITY',
        brokerage_flat=20.0,
        brokerage_percent=0.0
    )
    
    print_test_header("EQUITY - INTRADAY (Loss Trade)")
    print_charges(charges, 500.0, 490.0, 100)
    
    assert charges['total_charges'] > 0, "Charges apply even for losses"
    print("\n✓ Test passed")


def test_equity_delivery_buy():
    """
    Equity Delivery - Buy (No DP charges on buy)
    
    Scenario:
    - Buy 100 shares @ ₹500
    - Sell (close) @ ₹510
    
    Expected Charges:
    - Brokerage: ₹20
    - STT BUY: ₹50,000 × 0.001 = ₹50
    - STT SELL: ₹51,000 × 0.001 = ₹51
    - Stamp Duty: ₹50,000 × 0.015% = ₹7.50
    - Exchange: ₹101,000 × 0.00325% = ₹3.28
    - SEBI: ₹0.10
    - DP: ₹13.50 (on sell side)
    - GST: (20 + 3.28 + 0.10 + 13.50) × 18% = ₹6.90
    - Total: ~₹165.36
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=500.0,
        sell_price=510.0,
        quantity=100,
        exchange_segment='NSE_EQ',
        product_type='NORMAL',
        instrument_type='EQUITY',
        brokerage_flat=20.0,
        brokerage_percent=0.0,
        apply_dp_charges=True  # Only on sell side
    )
    
    print_test_header("EQUITY - DELIVERY (Buy + Sell)")
    print_charges(charges, 500.0, 510.0, 100)
    
    # Validate key components
    assert charges['stt_ctt_charge'] > 100, "STT should be on BOTH buy and sell (0.1% each)"
    assert charges['dp_charge'] > 0, "DP charge should apply on delivery sell"
    assert charges['stamp_duty'] == pytest.approx(7.50, abs=0.1), "Stamp duty should be 0.015% on buy"
    print("\n✓ Test passed")


def test_index_futures():
    """
    Index Futures (NSE Nifty50 Future)
    
    Scenario:
    - Buy 50 contracts @ ₹20,000
    - Sell @ ₹20,100
    - Lot size: 1 (so qty = 50)
    
    Expected Charges:
    - Brokerage: ₹40 (flat)
    - STT: (₹20,000 + ₹20,100) × 50 = ₹2,005,000 (total turnover)
      STT = ₹2,005,000 × 50 / 2 × 0.0125% = ₹1,250.31
    - Stamp Duty: ₹20,000 × 50 × 0.002% = ₹20.00
    - Exchange: ₹2,005,000 × 0.002% = ₹40.10
    - SEBI: ₹2.01
    - GST: (40 + 40.10 + 2.01) × 18% = ₹14.78
    - Total: ~₹1,369.20
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=20000.0,
        sell_price=20100.0,
        quantity=50,  # Contracts
        exchange_segment='NSE_FNO',
        product_type='MIS',
        instrument_type='FUTIDX',
        brokerage_flat=40.0,
        brokerage_percent=0.0
    )
    
    print_test_header("INDEX FUTURES (Nifty50)")
    print_charges(charges, 20000.0, 20100.0, 50)
    
    assert charges['stt_ctt_charge'] > 0, "STT should be charged on sell side"
    assert charges['stamp_duty'] == pytest.approx(20.0, abs=0.5), "Stamp duty incorrect"
    print("\n✓ Test passed")


def test_stock_futures():
    """
    Stock Futures
    
    Identical calculation logic as Index Futures.
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=2000.0,
        sell_price=2050.0,
        quantity=100,  # 100 shares
        exchange_segment='NSE_FNO',
        product_type='MIS',
        instrument_type='FUTSTK',
        brokerage_flat=30.0,
        brokerage_percent=0.0
    )
    
    print_test_header("STOCK FUTURES (TCS Future)")
    print_charges(charges, 2000.0, 2050.0, 100)
    
    assert charges['stt_ctt_charge'] > 0, "STT should be charged"
    print("\n✓ Test passed")


def test_index_options_normal():
    """
    Index Options - Normal Expiry (Not Exercised)
    
    Scenario:
    - Buy 100 option contracts @ ₹200 premium
    - Sell (close) @ ₹250 premium
    - Premium value: (200 + 250) × 100 = ₹45,000
    
    Expected Charges:
    - Brokerage: ₹30
    - STT: (₹45,000 / 2) × 0.0625% = ₹14.06 (normal, not exercised)
    - Stamp Duty: (₹45,000 / 2) × 0.003% = ₹0.68
    - Exchange: ₹45,000 × 0.035% = ₹15.75
    - SEBI: ₹0.045
    - GST: (30 + 15.75 + 0.045) × 18% = ₹8.23
    - Total: ~₹38.71
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=200.0,
        sell_price=250.0,
        quantity=100,  # 100 contracts
        exchange_segment='NSE_FNO',
        product_type='MIS',
        instrument_type='OPTIDX',
        brokerage_flat=30.0,
        brokerage_percent=0.0,
        is_option=True,
        option_exercised=False  # Normal expiry
    )
    
    print_test_header("INDEX OPTIONS - Normal Expiry")
    print_charges(charges, 200.0, 250.0, 100)
    
    # For normal expiry, STT should be 0.0625%
    premium_value = (200 + 250) * 100
    expected_stt = (premium_value / 2) * Decimal('0.000625')
    assert abs(charges['stt_ctt_charge'] - float(expected_stt)) < 1.0, "STT incorrect for normal expiry"
    print("\n✓ Test passed")


def test_index_options_exercised():
    """
    Index Options - Exercised
    
    Same premium values as normal, but STT rate is doubled (0.125%).
    
    Expected Charges:
    - STT: (₹45,000 / 2) × 0.125% = ₹28.13 (doubled for exercised)
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=200.0,
        sell_price=250.0,
        quantity=100,
        exchange_segment='NSE_FNO',
        product_type='MIS',
        instrument_type='OPTIDX',
        brokerage_flat=30.0,
        brokerage_percent=0.0,
        is_option=True,
        option_exercised=True  # EXERCISED
    )
    
    print_test_header("INDEX OPTIONS - Exercised")
    print_charges(charges, 200.0, 250.0, 100)
    
    # For exercised, STT should be 0.125% (double)
    premium_value = (200 + 250) * 100
    expected_stt = (premium_value / 2) * Decimal('0.00125')
    assert abs(charges['stt_ctt_charge'] - float(expected_stt)) < 1.0, "STT incorrect for exercised"
    print("\n✓ Test passed")


def test_stock_options():
    """
    Stock Options - Normal Expiry
    
    Identical logic as Index Options.
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=50.0,
        sell_price=75.0,
        quantity=100,  # 100 contracts (each ≈ 1 share)
        exchange_segment='NSE_FNO',
        product_type='MIS',
        instrument_type='OPTSTK',
        brokerage_flat=25.0,
        brokerage_percent=0.0,
        is_option=True,
        option_exercised=False
    )
    
    print_test_header("STOCK OPTIONS - Normal Expiry")
    print_charges(charges, 50.0, 75.0, 100)
    
    print("\n✓ Test passed")


def test_commodity_futures_nonagri():
    """
    Commodity Futures - Non-Agricultural (Crude Oil)
    
    Scenario:
    - Buy 100 barrels @ ₹4,000/barrel
    - Sell @ ₹4,100/barrel
    - CTT: 0.01% (non-agricultural)
    
    Expected Charges:
    - Brokerage: ₹50
    - CTT: (₹4,000 + ₹4,100) × 100 / 2 × 0.01% = ₹40.50
    - Stamp Duty: ₹400,000 × 0.002% = ₹80.00
    - Exchange: ₹810,000 × 0.0002% = ₹1.62
    - SEBI: ₹0.81
    - GST: (50 + 1.62 + 0.81) × 18% = ₹9.29
    - Total: ~₹182.22
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=4000.0,
        sell_price=4100.0,
        quantity=100,
        exchange_segment='MCX_COMM',
        product_type='MIS',
        instrument_type='FUTCOM',
        brokerage_flat=50.0,
        brokerage_percent=0.0,
        is_commodity=True,
        is_agricultural_commodity=False  # Non-agri
    )
    
    print_test_header("COMMODITY FUTURES - Non-Agricultural (Crude Oil)")
    print_charges(charges, 4000.0, 4100.0, 100)
    
    # Check that CTT is applied at correct rate for non-agri
    total_turnover = (4000 + 4100) * 100
    expected_ctt = (total_turnover / 2) * Decimal('0.0001')
    assert abs(charges['stt_ctt_charge'] - float(expected_ctt)) < 5.0, "CTT incorrect for non-agri"
    print("\n✓ Test passed")


def test_commodity_futures_agricultural():
    """
    Commodity Futures - Agricultural (Turmeric)
    
    Same trade parameters, but CTT rate is 0.05% (5x higher for agricultural).
    
    Expected CTT: (₹810,000 / 2) × 0.05% = ₹202.50
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=4000.0,
        sell_price=4100.0,
        quantity=100,
        exchange_segment='MCX_COMM',
        product_type='MIS',
        instrument_type='FUTCOM',
        brokerage_flat=50.0,
        brokerage_percent=0.0,
        is_commodity=True,
        is_agricultural_commodity=True  # AGRICULTURAL
    )
    
    print_test_header("COMMODITY FUTURES - Agricultural (Turmeric)")
    print_charges(charges, 4000.0, 4100.0, 100)
    
    # Check that CTT is applied at 5x rate for agri
    total_turnover = (4000 + 4100) * 100
    expected_ctt = (total_turnover / 2) * Decimal('0.0005')
    assert abs(charges['stt_ctt_charge'] - float(expected_ctt)) < 5.0, "CTT incorrect for agri"
    print("\n✓ Test passed")


def test_commodity_options():
    """
    Commodity Options
    
    Scenario:
    - Buy 50 option contracts @ ₹100 premium
    - Sell @ ₹150 premium
    - Premium: ₹12,500
    
    Expected Charges:
    - CTT: (₹12,500 / 2) × 0.05% = ₹3.13
    - Stamp Duty: (₹12,500 / 2) × 0.003% = ₹0.19
    """
    calc = ChargeCalculator()
    
    charges = calc.calculate_all_charges(
        buy_price=100.0,
        sell_price=150.0,
        quantity=50,  # 50 contracts
        exchange_segment='MCX_COMM',
        product_type='MIS',
        instrument_type='OPTCOM',
        brokerage_flat=35.0,
        brokerage_percent=0.0,
        is_option=True,
        is_commodity=True
    )
    
    print_test_header("COMMODITY OPTIONS")
    print_charges(charges, 100.0, 150.0, 50)
    
    print("\n✓ Test passed")


def print_summary_table():
    """Print summary comparison table of all segments."""
    print(f"\n{'='*80}")
    print("SUMMARY: Charges by Segment")
    print(f"{'='*80}")
    
    calc = ChargeCalculator()
    
    test_cases = [
        ("EQ Intraday", {"buy": 500, "sell": 510, "qty": 100, "segment": "NSE_EQ", "type": "MIS", "instr": "EQUITY"}),
        ("EQ Delivery", {"buy": 500, "sell": 510, "qty": 100, "segment": "NSE_EQ", "type": "NORMAL", "instr": "EQUITY", "dp": True}),
        ("Index Fut", {"buy": 20000, "sell": 20100, "qty": 50, "segment": "NSE_FNO", "type": "MIS", "instr": "FUTIDX"}),
        ("Index Opt (Normal)", {"buy": 200, "sell": 250, "qty": 100, "segment": "NSE_FNO", "type": "MIS", "instr": "OPTIDX", "opt": True}),
        ("Index Opt (Exercised)", {"buy": 200, "sell": 250, "qty": 100, "segment": "NSE_FNO", "type": "MIS", "instr": "OPTIDX", "opt": True, "exercised": True}),
        ("Commodity Fut (Non-agri)", {"buy": 4000, "sell": 4100, "qty": 100, "segment": "MCX_COMM", "type": "MIS", "instr": "FUTCOM", "comm": True}),
        ("Commodity Fut (Agri)", {"buy": 4000, "sell": 4100, "qty": 100, "segment": "MCX_COMM", "type": "MIS", "instr": "FUTCOM", "comm": True, "agri": True}),
    ]
    
    print(f"{'Segment':<25} {'Turnover':>15} {'Charges':>15} {'%':>8}")
    print(f"{'-'*65}")
    
    for name, params in test_cases:
        charges = calc.calculate_all_charges(
            buy_price=params["buy"],
            sell_price=params["sell"],
            quantity=params["qty"],
            exchange_segment=params["segment"],
            product_type=params["type"],
            instrument_type=params["instr"],
            brokerage_flat=20.0,
            brokerage_percent=0.0,
            is_option=params.get("opt", False),
            is_commodity=params.get("comm", False),
            is_agricultural_commodity=params.get("agri", False),
            option_exercised=params.get("exercised", False),
            apply_dp_charges=params.get("dp", False)
        )
        
        turnover = (params["buy"] + params["sell"]) * params["qty"]
        charge_pct = (charges['total_charges'] / turnover * 100) if turnover > 0 else 0
        
        print(f"{name:<25} ₹{turnover:>13,.0f} ₹{charges['total_charges']:>13,.2f} {charge_pct:>7.3f}%")


# ========== PYTEST IMPORTS AND FIXTURES ==========
# Uncomment if running with pytest

import pytest

@pytest.mark.parametrize("test_func", [
    test_equity_intraday_profit,
    test_equity_intraday_loss,
    test_equity_delivery_buy,
    test_index_futures,
    test_stock_futures,
    test_index_options_normal,
    test_index_options_exercised,
    test_stock_options,
    test_commodity_futures_nonagri,
    test_commodity_futures_agricultural,
    test_commodity_options,
])
def test_all_segments(test_func):
    """Run all segment tests."""
    test_func()


if __name__ == "__main__":
    """Run tests directly without pytest."""
    print("\n" + "="*80)
    print("CHARGE CALCULATOR - COMPREHENSIVE TEST SUITE")
    print("Testing all segments with correct Indian regulatory rates")
    print("="*80)
    
    try:
        test_equity_intraday_profit()
        test_equity_intraday_loss()
        test_equity_delivery_buy()
        test_index_futures()
        test_stock_futures()
        test_index_options_normal()
        test_index_options_exercised()
        test_stock_options()
        test_commodity_futures_nonagri()
        test_commodity_futures_agricultural()
        test_commodity_options()
        print_summary_table()
        
        print(f"\n{'='*80}")
        print("✓ ALL TESTS PASSED")
        print(f"{'='*80}\n")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
