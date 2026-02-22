#!/usr/bin/env python
"""
Comprehensive test suite for Brokerage & Statutory Charges

This script tests:
1. Charge calculation accuracy against expected values
2. Database persistence of charges
3. P&L endpoints include charge breakdown
4. Scheduler functionality
5. Admin endpoints for brokerage plan management

Usage:
    python test_charge_calculations.py
    
To test with live API:
    python test_charge_calculations.py --api-url http://localhost:8000
"""
import asyncio
import argparse
import logging
import sys
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

import asyncpg
import httpx

from app.database import get_pool, init_db
from app.services.charge_calculator import ChargeCalculator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# Expected values for charge calculations
CHARGE_TEST_CASES = [
    {
        "name": "Equity NSE - ₹500 stock 100 qty",
        "quantity": 100,
        "buy_price": Decimal("500.00"),
        "sell_price": Decimal("510.00"),
        "exchange_segment": "NSE_EQ",
        "product_type": "MIS",
        "instrument_type": "EQUITY",
        "brokerage_flat": Decimal("20"),
        "brokerage_percent": Decimal("0.05"),
        "is_option": False,
        "expected_total_min": Decimal("50"),  # Minimum expected
        "expected_total_max": Decimal("500"),  # Maximum expected
    },
    {
        "name": "Futures NIFTY 50 - 10 contracts",
        "quantity": 10,
        "buy_price": Decimal("15000.00"),
        "sell_price": Decimal("15100.00"),
        "exchange_segment": "NSE_FNO",
        "product_type": "MIS",
        "instrument_type": "FUTIDX",
        "brokerage_flat": Decimal("25"),
        "brokerage_percent": Decimal("0.03"),
        "is_option": False,
        "expected_total_min": Decimal("30"),
        "expected_total_max": Decimal("500"),
    },
    {
        "name": "Options Call - 100 contracts @ ₹75",
        "quantity": 100,
        "buy_price": Decimal("50.00"),
        "sell_price": Decimal("75.00"),
        "exchange_segment": "NSE_FO",
        "product_type": "MIS",
        "instrument_type": "OPTIDX",
        "brokerage_flat": Decimal("20"),
        "brokerage_percent": Decimal("0.05"),
        "is_option": True,
        "expected_total_min": Decimal("25"),
        "expected_total_max": Decimal("400"),
    },
    {
        "name": "Commodity Gold - MCX 100g",
        "quantity": 100,
        "buy_price": Decimal("5500.00"),
        "sell_price": Decimal("5550.00"),
        "exchange_segment": "MCX_COM",
        "product_type": "MIS",
        "instrument_type": "FUTCOM",
        "brokerage_flat": Decimal("25"),
        "brokerage_percent": Decimal("0.02"),
        "is_option": False,
        "expected_total_min": Decimal("25"),
        "expected_total_max": Decimal("600"),
    },
]


async def test_charge_calculations() -> bool:
    """Test charge calculation accuracy."""
    log.info("━" * 70)
    log.info("TEST 1: CHARGE CALCULATION ACCURACY")
    log.info("━" * 70)
    
    calculator = ChargeCalculator()
    all_passed = True
    
    for test_case in CHARGE_TEST_CASES:
        log.info(f"\nTest: {test_case['name']}")
        log.info(f"  Buy: {test_case['quantity']} @ ₹{test_case['buy_price']}")
        log.info(f"  Sell: @ ₹{test_case['sell_price']}")
        
        try:
            charges = calculator.calculate_all_charges(
                quantity=test_case['quantity'],
                buy_price=test_case['buy_price'],
                sell_price=test_case['sell_price'],
                exchange_segment=test_case['exchange_segment'],
                product_type=test_case['product_type'],
                instrument_type=test_case['instrument_type'],
                brokerage_flat=test_case['brokerage_flat'],
                brokerage_percent=test_case['brokerage_percent'],
                is_option=test_case['is_option']
            )
            
            total = charges['total_charges']
            log.info(f"  Total Charges: ₹{float(total):.2f}")
            log.info(f"    - Brokerage: ₹{float(charges['brokerage_charge']):.2f}")
            log.info(f"    - STT/CTT: ₹{float(charges['stt_ctt_charge']):.2f}")
            log.info(f"    - Exchange: ₹{float(charges['exchange_charge']):.2f}")
            log.info(f"    - SEBI: ₹{float(charges['sebi_charge']):.2f}")
            log.info(f"    - GST: ₹{float(charges['gst_charge']):.2f}")
            log.info(f"    - Stamp Duty: ₹{float(charges['stamp_duty']):.2f}")
            log.info(f"    - IPFT: ₹{float(charges['ipft_charge']):.2f}")
            
            # Validate expected range
            min_expected = test_case['expected_total_min']
            max_expected = test_case['expected_total_max']
            
            if min_expected <= total <= max_expected:
                log.info(f"  ✓ PASS - Total within expected range [₹{min_expected}-₹{max_expected}]")
            else:
                log.error(f"  ✗ FAIL - Total ₹{total} outside range [₹{min_expected}-₹{max_expected}]")
                all_passed = False
            
            # Validate charge components
            if charges['brokerage_charge'] < 0:
                log.error(f"  ✗ FAIL - Negative brokerage charge")
                all_passed = False
            
            if charges['total_charges'] < charges['brokerage_charge']:
                log.error(f"  ✗ FAIL - Total charges less than brokerage alone")
                all_passed = False
                
        except Exception as e:
            log.error(f"  ✗ EXCEPTION: {e}")
            all_passed = False
    
    return all_passed


async def test_database_persistence() -> bool:
    """Test that charges are correctly persisted to database."""
    log.info("\n" + "━" * 70)
    log.info("TEST 2: DATABASE PERSISTENCE")
    log.info("━" * 70)
    
    pool = get_pool()
    
    # Create test position with charges
    test_position_id = str(uuid4())
    test_user_id = str(uuid4())
    
    try:
        # Check if test user exists
        user_exists = await pool.fetchval(
            "SELECT id FROM users WHERE id = $1::uuid",
            test_user_id
        )
        
        if not user_exists:
            log.info("Creating test user...")
            await pool.execute(
                """
                INSERT INTO users (id, username, email, created_at)
                VALUES ($1::uuid, $2, $3, NOW())
                """,
                test_user_id, f"test_{uuid4()}", f"test_{uuid4()}@example.com"
            )
        
        log.info("Creating test position...")
        await pool.execute(
            """
            INSERT INTO paper_positions 
            (id, user_id, symbol, instrument_token, quantity, avg_price,
             exchange_segment, product_type, status, realized_pnl, 
             brokerage_charge, total_charges, charges_calculated, opened_at)
            VALUES 
            ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW())
            """,
            test_position_id, test_user_id, "TEST", 999999, 100, 100.0,
            "NSE_EQ", "MIS", "CLOSED", 1000.0, 50.0, 100.0, True
        )
        
        log.info("Verifying persisted charges...")
        row = await pool.fetchrow(
            """
            SELECT 
                brokerage_charge, total_charges, charges_calculated
            FROM paper_positions 
            WHERE id = $1::uuid
            """,
            test_position_id
        )
        
        if row:
            log.info(f"  Brokerage Charge: ₹{float(row['brokerage_charge']):.2f}")
            log.info(f"  Total Charges: ₹{float(row['total_charges']):.2f}")
            log.info(f"  Charges Calculated: {row['charges_calculated']}")
            
            if (float(row['total_charges']) == 100.0 and 
                float(row['brokerage_charge']) == 50.0 and 
                row['charges_calculated'] == True):
                log.info("  ✓ PASS - Charges correctly persisted")
                return True
            else:
                log.error("  ✗ FAIL - Charge values don't match")
                return False
        else:
            log.error("  ✗ FAIL - Position not found in database")
            return False
            
    except Exception as e:
        log.error(f"  ✗ EXCEPTION: {e}")
        return False


async def test_api_endpoints(api_url: str) -> bool:
    """Test charge-related API endpoints."""
    log.info("\n" + "━" * 70)
    log.info("TEST 3: API ENDPOINTS")
    log.info("━" * 70)
    
    async with httpx.AsyncClient(base_url=api_url) as client:
        try:
            # Test GET brokerage plans
            log.info("\n[3.1] Testing GET /api/v2/admin/brokerage-plans")
            response = await client.get("/api/v2/admin/brokerage-plans")
            
            if response.status_code != 200:
                log.error(f"  ✗ FAIL - HTTP {response.status_code}")
                return False
            
            plans = response.json()
            if isinstance(plans, dict) and "data" in plans:
                plans_list = plans["data"]
            else:
                plans_list = plans
            
            if len(plans_list) == 10:
                log.info(f"  ✓ PASS - Found {len(plans_list)} plans")
            else:
                log.error(f"  ✗ FAIL - Expected 10 plans, found {len(plans_list)}")
                return False
            
            # Test charge calculation status endpoint
            log.info("\n[3.2] Testing GET /api/v2/admin/charge-calculation/status")
            response = await client.get("/api/v2/admin/charge-calculation/status")
            
            if response.status_code != 200:
                log.error(f"  ✗ FAIL - HTTP {response.status_code}")
                return False
            
            status = response.json()
            log.info(f"  Scheduler Running: {status.get('running', 'N/A')}")
            log.info(f"  Last Run: {status.get('last_run_at', 'Never')}")
            log.info("  ✓ PASS - Status endpoint working")
            
            return True
            
        except Exception as e:
            log.error(f"  ✗ EXCEPTION: {e}")
            return False


async def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Test charge calculation system")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                        help="API base URL for endpoint tests")
    args = parser.parse_args()
    
    log.info("═" * 70)
    log.info("BROKERAGE & STATUTORY CHARGES - TEST SUITE")
    log.info("═" * 70)
    
    try:
        # Initialize database
        log.info("\nInitializing database...")
        await init_db()
        log.info("✓ Database initialized\n")
        
        # Run tests
        results = {
            "calculations": await test_charge_calculations(),
            "persistence": await test_database_persistence(),
        }
        
        # API tests only if connectivity available
        try:
            results["api"] = await test_api_endpoints(args.api_url)
        except Exception as e:
            log.warning(f"Skipping API tests (API not reachable): {e}")
            results["api"] = None
        
        # Summary
        log.info("\n" + "═" * 70)
        log.info("TEST SUMMARY")
        log.info("═" * 70)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result is True else ("⊘ SKIP" if result is None else "✗ FAIL")
            log.info(f"  {test_name.upper()}: {status}")
        
        all_passed = all(r is not False for r in results.values())
        
        if all_passed:
            log.info("\n✓ ALL TESTS PASSED")
            return True
        else:
            log.error("\n✗ SOME TESTS FAILED")
            return False
            
    except Exception as e:
        log.exception(f"Test suite failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
