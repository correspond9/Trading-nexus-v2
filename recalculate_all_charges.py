#!/usr/bin/env python3
"""
Manually trigger charge recalculation for all past closed positions.

This script:
1. Finds all closed positions (both calculated and uncalculated)
2. Recalculates charges using the corrected calculator
3. Updates the database with new charge values
4. Logs progress and results
"""

import asyncio
import logging
import sys
from datetime import datetime

from app.database import get_pool, init_db
from app.schedulers.charge_calculation_scheduler import charge_calculation_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def recalculate_all_charges():
    """
    Recalculate charges for ALL closed positions.
    """
    logger.info("=" * 80)
    logger.info("CHARGE RECALCULATION - ALL CLOSED POSITIONS")
    logger.info("=" * 80)
    
    try:
        # Initialize database pool
        await init_db()
        pool = get_pool()
        
        # Get total count of closed positions
        total_count = await pool.fetchval(
            "SELECT COUNT(*) FROM paper_positions WHERE status = 'CLOSED' AND closed_at IS NOT NULL"
        )
        
        logger.info(f"📊 Total closed positions: {total_count}")
        
        if total_count == 0:
            logger.info("✅ No closed positions to process")
            return
        
        # Reset all charge_calculated flags to FALSE so scheduler will reprocess them
        logger.info("🔄 Resetting charge_calculated flags...")
        reset_count = await pool.execute(
            "UPDATE paper_positions SET charges_calculated = FALSE WHERE status = 'CLOSED' AND closed_at IS NOT NULL"
        )
        logger.info(f"✅ Reset {total_count} positions for recalculation")
        
        # Run the scheduler to calculate charges
        logger.info("\n🧮 Starting charge calculation...")
        result = await charge_calculation_scheduler.run_once(
            exchanges=None,  # All exchanges
            user_id=None,    # All users
        )
        
        # Report results
        logger.info("\n" + "=" * 80)
        logger.info("RECALCULATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"✅ Processed:  {result['processed']} positions")
        logger.info(f"❌ Errors:     {result['errors']} positions")
        logger.info(f"⏱️  Duration:   {result['duration_seconds']:.2f} seconds")
        
        # Verify results
        calculated_count = await pool.fetchval(
            "SELECT COUNT(*) FROM paper_positions WHERE charges_calculated = TRUE AND status = 'CLOSED'"
        )
        logger.info(f"📊 Total with charges calculated: {calculated_count}/{total_count}")
        
        # Sample some results
        logger.info("\n📋 Sample Trade Expenses (first 5 closed positions):")
        samples = await pool.fetch(
            """
            SELECT 
                position_id,
                symbol,
                realized_pnl,
                trade_expense,
                total_charges
            FROM paper_positions
            WHERE status = 'CLOSED'
            ORDER BY closed_at DESC
            LIMIT 5
            """
        )
        
        for row in samples:
            logger.info(f"  {row['symbol']:20} | Realized P&L: ₹{row['realized_pnl']:>10.2f} | Trade Expense: ₹{row['trade_expense']:>8.2f} | Total: ₹{row['total_charges']:>8.2f}")
        
        logger.info("\n✅ Recalculation complete! Refresh your P&L report to see updated charges.")
        
    except Exception as e:
        logger.error(f"❌ Error during recalculation: {e}", exc_info=True)
        raise
    finally:
        logger.info("=" * 80)


async def main():
    """Main entry point."""
    try:
        await recalculate_all_charges()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Recalculation interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
