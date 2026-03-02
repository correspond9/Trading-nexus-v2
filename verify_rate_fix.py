#!/usr/bin/env python3
"""
Verify the exchange rate scaling fix is properly deployed.
Tests that 100x inflation is resolved.
"""

import sys
from decimal import Decimal
from app.services.charge_calculator import ChargeCalculator


def verify_exchange_rates() -> bool:
    """Verify all exchange rates have correct decimal representation."""
    calc = ChargeCalculator()
    
    print("=" * 70)
    print("EXCHANGE RATE VERIFICATION")
    print("=" * 70)
    
    expected_rates = {
        'NSE_EQ_INTRADAY': Decimal('0.0000325'),
        'NSE_EQ_DELIVERY': Decimal('0.0000325'),
        'NSE_FNO_FUTURES': Decimal('0.00002'),
        'NSE_FNO_OPTIONS': Decimal('0.00035'),
        'BSE_EQ': Decimal('0.000375'),
        'BSE_FNO_OPTIONS': Decimal('0.0003'),
        'MCX_COMMODITY_FUTURES': Decimal('0.000002'),
        'MCX_COMMODITY_OPTIONS': Decimal('0.00001'),
    }
    
    all_correct = True
    for rate_key, expected_value in expected_rates.items():
        actual_value = calc.rates.EXCHANGE_RATES.get(rate_key)
        status = "✓" if actual_value == expected_value else "✗"
        
        if actual_value != expected_value:
            all_correct = False
            print(f"{status} {rate_key}")
            print(f"  Expected: {expected_value}")
            print(f"  Got:      {actual_value}")
        else:
            print(f"{status} {rate_key:25} = {actual_value}")
    
    print("\n" + "=" * 70)
    return all_correct


def verify_clearing_charges() -> bool:
    """Verify clearing charges are not double-counted."""
    calc = ChargeCalculator()
    
    print("CLEARING CHARGE VERIFICATION")
    print("=" * 70)
    
    clearing_eq = calc.rates.CLEARING_CHARGE_EQ
    expected = Decimal('0')
    
    if clearing_eq == expected:
        print(f"✓ CLEARING_CHARGE_EQ = {clearing_eq} (correctly removed)")
        return True
    else:
        print(f"✗ CLEARING_CHARGE_EQ = {clearing_eq}")
        print(f"  Expected: {expected}")
        return False


def test_calculation_scenarios() -> bool:
    """Test the three critical scenarios to verify 100x fix."""
    calc = ChargeCalculator()
    
    print("\n" + "=" * 70)
    print("CALCULATION SCENARIO VERIFICATION")
    print("=" * 70)
    
    scenarios = [
        {
            'name': 'Equity Delivery',
            'buy_price': 450,
            'sell_price': 480,
            'quantity': 400,
            'exchange_segment': 'NSE_EQ_DELIVERY',
            'product': 'DELIVERY',
            'instrument_type': 'STOCK',
            'expected_exchange_min': 10,
            'expected_exchange_max': 15,
            'expected_total_min': 10,
            'expected_total_max': 30,
        },
        {
            'name': 'F&O Options',
            'buy_price': 100,
            'sell_price': 110,
            'quantity': 650,
            'exchange_segment': 'NSE_FNO_OPTIONS',
            'product': 'OPTIONS',
            'instrument_type': 'INDEX',
            'expected_exchange_min': 45,
            'expected_exchange_max': 50,
            'expected_total_min': 90,
            'expected_total_max': 110,
        },
        {
            'name': 'Futures Contract',
            'buy_price': 25100,
            'sell_price': 25200,
            'quantity': 650,
            'exchange_segment': 'NSE_FNO_FUTURES',
            'product': 'FUTURES',
            'instrument_type': 'INDEX',
            'expected_exchange_min': 600,
            'expected_exchange_max': 1100,
            'expected_total_min': 1000,
            'expected_total_max': 1500,
        },
    ]
    
    all_passed = True
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        
        try:
            charges = calc.calculate_all_charges(
                buy_price=scenario['buy_price'],
                sell_price=scenario['sell_price'],
                quantity=scenario['quantity'],
                exchange_segment=scenario['exchange_segment'],
                product_type=scenario['product'],
                instrument_type=scenario['instrument_type'],
                brokerage_flat=0,
                brokerage_percent=0,
                is_option=scenario['product'] == 'OPTIONS',
                is_commodity=False,
            )
            
            exchange_charge = charges.get('exchange_charge', 0)
            total_charges = charges.get('total_charges', 0)
            turnover = abs(scenario['sell_price'] - scenario['buy_price']) * scenario['quantity']
            
            # Verify exchange charge
            ex_ok = scenario['expected_exchange_min'] <= exchange_charge <= scenario['expected_exchange_max']
            ex_status = "✓" if ex_ok else "✗"
            print(f"  {ex_status} Exchange:  ₹{exchange_charge:.2f} (expected {scenario['expected_exchange_min']}-{scenario['expected_exchange_max']})")
            
            # Verify total charges
            tot_ok = scenario['expected_total_min'] <= total_charges <= scenario['expected_total_max']
            tot_status = "✓" if tot_ok else "✗"
            print(f"  {tot_status} Total:     ₹{total_charges:.2f} (expected {scenario['expected_total_min']}-{scenario['expected_total_max']})")
            
            # Show percentage of turnover
            pct = (total_charges / turnover * 100) if turnover > 0 else 0
            print(f"  Turnover:  ₹{turnover:,.0f}")
            print(f"  % Cost:    {pct:.3f}% (should be < 1%)")
            
            if not (ex_ok and tot_ok):
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error calculating charges: {e}")
            all_passed = False
    
    return all_passed


def main() -> int:
    """Run all verification tests."""
    print("\n")
    print("#" * 70)
    print("# TRADING NEXUS - EXCHANGE RATE FIX VERIFICATION")
    print("# Confirming 100x Inflation is Resolved")
    print("#" * 70)
    print()
    
    test_results = []
    
    # Run all tests
    print("1. Verifying Exchange Rates...")
    rates_ok = verify_exchange_rates()
    test_results.append(("Exchange Rates", rates_ok))
    
    clearing_ok = verify_clearing_charges()
    test_results.append(("Clearing Charges", clearing_ok))
    
    print("\n2. Verifying Calculation Scenarios...")
    scenarios_ok = test_calculation_scenarios()
    test_results.append(("Scenarios", scenarios_ok))
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = all(result[1] for result in test_results)
    
    for test_name, passed in test_results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    print("=" * 70)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - 100x INFLATION FIX VERIFIED!")
        print("   Exchange rates are correctly scaled (divided by 100)")
        print("   All charges now realistic")
        return 0
    else:
        print("\n❌ VERIFICATION FAILED - ISSUES FOUND")
        return 1


if __name__ == '__main__':
    sys.exit(main())
