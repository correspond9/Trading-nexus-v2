"""
End-of-Day Charge Calculation Scheduler

Automatically calculates brokerage and statutory charges for closed positions
at market close times:
- NSE/BSE: 4:00 PM IST (after 3:30 PM market close)
- MCX: 12:00 AM IST (after 11:30 PM-11:55 PM market close)

Only processes positions that:
1. Status = 'CLOSED'
2. charges_calculated = FALSE
3. closed_at is within the current trading day
"""
import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import List, Optional
import pytz

from app.database import get_pool
from app.services.charge_calculator import calculate_position_charges

logger = logging.getLogger(__name__)

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

# Market close times (IST)
NSE_BSE_CHARGE_TIME = time(hour=16, minute=0)  # 4:00 PM
MCX_CHARGE_TIME = time(hour=0, minute=0)       # 12:00 AM (midnight)


class ChargeCalculationScheduler:
    """
    Scheduler for end-of-day charge calculation.
    """
    
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_run_nse = None
        self._last_run_mcx = None
        self._stats = {
            'total_processed': 0,
            'total_errors': 0,
            'last_run_at': None,
            'last_run_duration': None,
        }
    
    async def start(self):
        """Start the scheduler."""
        if self._running:
            logger.warning("Charge calculation scheduler already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("🔄 Charge calculation scheduler started")
    
    async def stop(self):
        """Stop the scheduler."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️ Charge calculation scheduler stopped")
    
    async def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            try:
                await self._check_and_run()
                # Check every 5 minutes
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in charge calculation scheduler loop: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_run(self):
        """Check if it's time to run charge calculation."""
        now_ist = datetime.now(IST)
        today_date = now_ist.date()
        current_time = now_ist.time()
        
        # Check NSE/BSE (4:00 PM IST)
        if (current_time >= NSE_BSE_CHARGE_TIME and 
            (self._last_run_nse is None or self._last_run_nse.date() < today_date)):
            logger.info("⏰ Running NSE/BSE charge calculation (4:00 PM IST)")
            await self.run_once(exchanges=['NSE', 'BSE'])
            self._last_run_nse = now_ist
        
        # Check MCX (12:00 AM IST - midnight)
        if (current_time >= MCX_CHARGE_TIME and 
            current_time < time(hour=1, minute=0) and
            (self._last_run_mcx is None or self._last_run_mcx.date() < today_date)):
            logger.info("⏰ Running MCX charge calculation (12:00 AM IST)")
            await self.run_once(exchanges=['MCX'])
            self._last_run_mcx = now_ist
    
    async def run_once(self, exchanges: Optional[List[str]] = None) -> dict:
        """
        Manually trigger charge calculation.
        
        Args:
            exchanges: List of exchanges to process ['NSE', 'BSE', 'MCX']
                      If None, processes all exchanges
        
        Returns:
            Statistics dictionary
        """
        start_time = datetime.now()
        logger.info(f"🧮 Starting charge calculation for exchanges: {exchanges or 'ALL'}")
        
        try:
            pool = get_pool()
            
            # Build exchange filter
            exchange_filter = ""
            if exchanges:
                exchange_list = "', '".join(f"{ex}" for ex in exchanges)
                exchange_filter = f"AND (exchange_segment LIKE '{exchange_list}%' OR " + \
                                " OR ".join(f"exchange_segment LIKE '%{ex}%'" for ex in exchanges) + ")"
            
            # Get uncalculated closed positions
            query = f"""
                SELECT 
                    pp.position_id,
                    pp.user_id,
                    pp.quantity,
                    pp.avg_price,
                    pp.realized_pnl,
                    pp.symbol,
                    pp.exchange_segment,
                    pp.product_type,
                    pp.instrument_token,
                    pp.closed_at,
                    u.brokerage_plan_equity_id,
                    u.brokerage_plan_futures_id,
                    im.instrument_type,
                    im.option_type
                FROM paper_positions pp
                JOIN users u ON u.id = pp.user_id
                LEFT JOIN instrument_master im ON im.instrument_token = pp.instrument_token
                WHERE pp.status = 'CLOSED'
                  AND pp.charges_calculated = FALSE
                  AND pp.closed_at IS NOT NULL
                  {exchange_filter}
                ORDER BY pp.closed_at ASC
            """
            
            rows = await pool.fetch(query)
            total = len(rows)
            
            if total == 0:
                logger.info("✅ No positions to process")
                return {'processed': 0, 'errors': 0, 'skipped': 0}
            
            logger.info(f"📊 Found {total} positions to process")
            
            processed = 0
            errors = 0
            skipped = 0
            
            for row in rows:
                try:
                    await self._calculate_and_update_charges(dict(row), pool)
                    processed += 1
                    
                    if processed % 10 == 0:
                        logger.info(f"Progress: {processed}/{total}")
                        
                except Exception as e:
                    logger.error(f"Error processing position {row['position_id']}: {e}")
                    errors += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Update stats
            self._stats['total_processed'] += processed
            self._stats['total_errors'] += errors
            self._stats['last_run_at'] = start_time.isoformat()
            self._stats['last_run_duration'] = duration
            
            logger.info(f"✅ Charge calculation complete: {processed} processed, {errors} errors, {duration:.2f}s")
            
            return {
                'processed': processed,
                'errors': errors,
                'skipped': skipped,
                'duration_seconds': duration
            }
            
        except Exception as e:
            logger.error(f"Fatal error in charge calculation: {e}")
            raise
    
    async def _calculate_and_update_charges(self, position: dict, pool):
        """
        Calculate charges for a position and update database.
        """
        try:
            # Get brokerage plan
            is_futures = 'FUT' in (position.get('instrument_type') or '')
            plan_id = position.get('brokerage_plan_futures_id') if is_futures else position.get('brokerage_plan_equity_id')
            
            if not plan_id:
                logger.warning(f"No brokerage plan for user {position['user_id']}, skipping position {position['position_id']}")
                return
            
            # Fetch brokerage plan details
            plan = await pool.fetchrow(
                "SELECT flat_fee, percent_fee FROM brokerage_plans WHERE plan_id = $1",
                plan_id
            )
            
            if not plan:
                logger.warning(f"Brokerage plan {plan_id} not found")
                return
            
            # Determine exit price (use LTP or avg_price as last resort)
            ltp_row = await pool.fetchrow(
                "SELECT ltp FROM market_data WHERE instrument_token = $1",
                position['instrument_token']
            )
            exit_price = float(ltp_row['ltp']) if ltp_row and ltp_row['ltp'] else float(position['avg_price'])
            
            # Calculate charges
            is_option = position.get('option_type') in ('CE', 'PE')
            charges = calculate_position_charges(
                quantity=position['quantity'],
                avg_price=float(position['avg_price']),
                exit_price=exit_price,
                exchange_segment=position['exchange_segment'] or 'NSE_FNO',
                product_type=position['product_type'] or 'MIS',
                instrument_type=position.get('instrument_type') or 'EQUITY',
                brokerage_flat=float(plan['flat_fee'] or 0),
                brokerage_percent=float(plan['percent_fee'] or 0),
                is_option=is_option
            )
            
            # Update position with calculated charges
            await pool.execute(
                """
                UPDATE paper_positions
                SET
                    brokerage_charge = $1,
                    stt_ctt_charge = $2,
                    exchange_charge = $3,
                    sebi_charge = $4,
                    stamp_duty = $5,
                    ipft_charge = $6,
                    gst_charge = $7,
                    platform_cost = $8,
                    trade_expense = $9,
                    total_charges = $10,
                    charges_calculated = TRUE,
                    charges_calculated_at = NOW()
                WHERE position_id = $11
                """,
                charges['brokerage_charge'],
                charges['stt_ctt_charge'],
                charges['exchange_charge'],
                charges['sebi_charge'],
                charges['stamp_duty'],
                charges['ipft_charge'],
                charges['gst_charge'],
                charges['platform_cost'],
                charges['trade_expense'],
                charges['total_charges'],
                position['position_id']
            )
            
            logger.debug(f"✓ Calculated charges for position {position['position_id']}: ₹{charges['total_charges']:.2f}")
            
        except Exception as e:
            logger.error(f"Error calculating charges for position {position.get('position_id')}: {e}")
            raise
    
    def get_stats(self) -> dict:
        """Get scheduler statistics."""
        return {
            **self._stats,
            'running': self._running,
            'last_run_nse': self._last_run_nse.isoformat() if self._last_run_nse else None,
            'last_run_mcx': self._last_run_mcx.isoformat() if self._last_run_mcx else None,
        }


# Global singleton instance
charge_calculation_scheduler = ChargeCalculationScheduler()
