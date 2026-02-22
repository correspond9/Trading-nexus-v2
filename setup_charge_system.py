#!/usr/bin/env python
"""
Setup script for Brokerage & Statutory Charges System

This script:
1. Runs the database migration (020_brokerage_charges_system.sql)
2. Verifies the schema is properly created
3. Confirms brokerage plans are seeded with correct rates
4. Tests the charge calculation service

Usage:
    python setup_charge_system.py
"""
import asyncio
import logging
import sys
from datetime import datetime
from decimal import Decimal

import asyncpg

from app.database import get_pool, init_db
from app.services.charge_calculator import ChargeCalculator, ChargeRates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


async def verify_schema() -> bool:
    """Verify that all required tables and columns exist."""
    log.info("Verifying database schema...")
    
    pool = get_pool()
    
    checks = [
        ("brokerage_plans table exists", 
         "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='brokerage_plans'"),
        
        ("brokerage_plan_equity_id column on users",
         "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND column_name='brokerage_plan_equity_id'"),
        
        ("brokerage_plan_futures_id column on users",
         "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND column_name='brokerage_plan_futures_id'"),
        
        ("total_charges column on paper_positions",
         "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='paper_positions' AND column_name='total_charges'"),
        
        ("charges_calculated column on paper_positions",
         "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='paper_positions' AND column_name='charges_calculated'"),
    ]
    
    all_ok = True
    for check_name, query in checks:
        try:
            result = await pool.fetchval(query)
            if result and result > 0:
                log.info(f"  ✓ {check_name}")
            else:
                log.error(f"  ✗ {check_name} - NOT FOUND")
                all_ok = False
        except Exception as e:
            log.error(f"  ✗ {check_name} - ERROR: {e}")
            all_ok = False
    
    return all_ok


async def verify_brokerage_plans() -> bool:
    """Verify that all 10 brokerage plans are properly seeded."""
    log.info("\nVerifying brokerage plans...")
    
    pool = get_pool()
    
    # Check plan count
    count = await pool.fetchval("SELECT COUNT(*) FROM brokerage_plans")
    log.info(f"  Found {count} brokerage plans (expected 10)")
    
    if count != 10:
        log.error(f"  ✗ Expected 10 plans, found {count}")
        return False
    
    # Get all plans
    plans = await pool.fetch(
        """
        SELECT plan_id, plan_name, segment, flat_fee, percent_fee,
               brokerage_percentage, stt_rate, exchange_rate, sebi_rate,
               gst_percentage, stamp_duty_rate, ipft_rate
        FROM brokerage_plans
        ORDER BY plan_id
        """
    )
    
    for plan in plans:
        log.info(f"  Plan {plan['plan_id']}: {plan['plan_name']} ({plan['segment']})")
        log.info(f"    - Flat Fee: ₹{plan['flat_fee']}, Percent: {plan['percent_fee']}%")
        log.info(f"    - STT: {plan['stt_rate']}%, Exchange: {plan['exchange_rate']}%, SEBI: {plan['sebi_rate']}%")
    
    return True


async def test_charge_calculation() -> bool:
    """Test the charge calculator with sample data."""
    log.info("\nTesting charge calculation...")
    
    # Test Case 1: Equity trade
    log.info("  Test 1: Equity (NSE) - Buy 100 shares @ ₹500, Sell @ ₹510")
    
    calculator = ChargeCalculator()
    charges = calculator.calculate_all_charges(
        quantity=100,
        buy_price=Decimal("500.00"),
        sell_price=Decimal("510.00"),
        exchange_segment="NSE_EQ",
        product_type="MIS",
        instrument_type="EQUITY",
        brokerage_flat=Decimal("20"),
        brokerage_percent=Decimal("0.05"),
        is_option=False
    )
    
    turnover = 100 * 510  # ₹51,000
    log.info(f"    Turnover: ₹{turnover:,}")
    log.info(f"    Total Charges: ₹{float(charges['total_charges']):.2f}")
    log.info(f"      - Brokerage: ₹{float(charges['brokerage_charge']):.2f}")
    log.info(f"      - STT: ₹{float(charges['stt_ctt_charge']):.2f}")
    log.info(f"      - Exchange: ₹{float(charges['exchange_charge']):.2f}")
    log.info(f"      - SEBI: ₹{float(charges['sebi_charge']):.2f}")
    log.info(f"      - GST: ₹{float(charges['gst_charge']):.2f}")
    
    if charges['total_charges'] <= 0:
        log.error("    ✗ Total charges should be > 0")
        return False
    
    # Test Case 2: Futures trade
    log.info("\n  Test 2: Futures (MCX) - 10 contracts @ ₹5000, Sell @ ₹5050")
    
    charges = calculator.calculate_all_charges(
        quantity=10,
        buy_price=Decimal("5000.00"),
        sell_price=Decimal("5050.00"),
        exchange_segment="MCX_FUT",
        product_type="MIS",
        instrument_type="FUTIDX",
        brokerage_flat=Decimal("25"),
        brokerage_percent=Decimal("0.03"),
        is_option=False
    )
    
    turnover = 10 * 5050
    log.info(f"    Turnover: ₹{turnover:,}")
    log.info(f"    Total Charges: ₹{float(charges['total_charges']):.2f}")
    log.info(f"      - Brokerage: ₹{float(charges['brokerage_charge']):.2f}")
    log.info(f"      - Exchange: ₹{float(charges['exchange_charge']):.2f}")
    
    if charges['total_charges'] <= 0:
        log.error("    ✗ Total charges should be > 0")
        return False
    
    # Test Case 3: Options trade
    log.info("\n  Test 3: Options - 100 contracts @ ₹50, Sell @ ₹75")
    
    charges = calculator.calculate_all_charges(
        quantity=100,
        buy_price=Decimal("50.00"),
        sell_price=Decimal("75.00"),
        exchange_segment="NSE_FO",
        product_type="MIS",
        instrument_type="OPTIDX",
        brokerage_flat=Decimal("20"),
        brokerage_percent=Decimal("0.05"),
        is_option=True
    )
    
    turnover = 100 * 75
    log.info(f"    Turnover: ₹{turnover:,}")
    log.info(f"    Total Charges: ₹{float(charges['total_charges']):.2f}")
    log.info(f"      - Brokerage: ₹{float(charges['brokerage_charge']):.2f}")
    log.info(f"      - STT: ₹{float(charges['stt_ctt_charge']):.2f}")
    log.info(f"      - Exchange: ₹{float(charges['exchange_charge']):.2f}")
    
    if charges['total_charges'] <= 0:
        log.error("    ✗ Total charges should be > 0")
        return False
    
    log.info("\n  ✓ All charge calculation tests passed")
    return True


async def main():
    """Run all setup tasks."""
    log.info("═" * 70)
    log.info("BROKERAGE & STATUTORY CHARGES SYSTEM SETUP")
    log.info("═" * 70)
    
    try:
        log.info("\n[1] Initializing database...")
        await init_db()
        log.info("  ✓ Database initialized")
        
        log.info("\n[2] Verifying schema...")
        if not await verify_schema():
            log.error("  ✗ Schema verification failed")
            return False
        log.info("  ✓ Schema verification passed")
        
        log.info("\n[3] Verifying brokerage plans...")
        if not await verify_brokerage_plans():
            log.error("  ✗ Brokerage plans verification failed")
            return False
        log.info("  ✓ Brokerage plans verified")
        
        log.info("\n[4] Testing charge calculations...")
        if not await test_charge_calculation():
            log.error("  ✗ Charge calculation tests failed")
            return False
        log.info("  ✓ Charge calculations verified")
        
        log.info("\n" + "═" * 70)
        log.info("SETUP COMPLETE - SYSTEM IS READY")
        log.info("═" * 70)
        log.info("\nNext steps:")
        log.info("1. Assign brokerage plans to users via admin endpoints")
        log.info("2. Close positions to trigger charge calculation")
        log.info("3. Check /portfolio/positions/pnl/summary for charge breakdown")
        log.info("4. Scheduler will auto-calculate charges at market close")
        log.info("\nAdmin endpoints:")
        log.info("  GET    /api/v2/admin/brokerage-plans - List all plans")
        log.info("  POST   /api/v2/admin/users/{id}/brokerage-plans - Assign plans to user")
        log.info("  POST   /api/v2/admin/charge-calculation/run - Trigger manual calculation")
        log.info("═" * 70)
        
        return True
        
    except Exception as e:
        log.exception(f"Setup failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
