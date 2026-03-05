"""
fix_index_tier.py
==================
One-time fix to mark INDEX instruments (NIFTY, BANKNIFTY, SENSEX, etc.) as Tier-B
so they are subscribed to the WebSocket for live LTP updates.

This fixes the stale price issue on Straddle and Options pages.

Run this after deploying the scrip_master.py code fix.
"""
import asyncio
import logging

from app.database import init_db, get_pool, close_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Index symbols that should always be Tier-B (must match scrip_master.py)
_TIER_B_INDICES = ["NIFTY", "BANKNIFTY", "SENSEX", "MIDCPNIFTY", "FINNIFTY", "BANKEX", "NIFTYNXT50"]


async def fix_index_tier():
    """Update INDEX instruments to Tier-B with proper ws_slot assignment."""
    await init_db()
    pool = get_pool()
    
    log.info("─── Starting INDEX tier fix ─────────────────────────────")
    
    # Check current state
    before = await pool.fetch(
        """SELECT instrument_token, symbol, tier, ws_slot, exchange_segment
           FROM instrument_master
           WHERE instrument_type = 'INDEX'
             AND symbol = ANY($1::text[])
           ORDER BY symbol""",
        _TIER_B_INDICES,
    )
    
    if not before:
        log.warning("No INDEX instruments found in database for configured indices.")
        log.info("Available INDEX instruments:")
        all_indices = await pool.fetch(
            "SELECT DISTINCT symbol FROM instrument_master WHERE instrument_type = 'INDEX' ORDER BY symbol"
        )
        for row in all_indices:
            log.info(f"  - {row['symbol']}")
        await close_db()
        return
    
    log.info(f"Found {len(before)} INDEX instruments to update:")
    for row in before:
        log.info(
            f"  {row['symbol']:15s} | tier={row['tier']:1s} | ws_slot={row['ws_slot']} | "
            f"segment={row['exchange_segment']}"
        )
    
    # Apply fix
    log.info("\nUpdating INDEX instruments to tier='B' with ws_slot...")
    result = await pool.execute(
        """UPDATE instrument_master 
           SET tier = 'B', ws_slot = (instrument_token % 5)
           WHERE instrument_type = 'INDEX'
             AND symbol = ANY($1::text[])""",
        _TIER_B_INDICES,
    )
    
    # Verify fix
    after = await pool.fetch(
        """SELECT instrument_token, symbol, tier, ws_slot, exchange_segment
           FROM instrument_master
           WHERE instrument_type = 'INDEX'
             AND symbol = ANY($1::text[])
           ORDER BY symbol""",
        _TIER_B_INDICES,
    )
    
    log.info(f"\n✓ Update complete: {result}")
    log.info(f"\nUpdated state ({len(after)} instruments):")
    for row in after:
        log.info(
            f"  {row['symbol']:15s} | tier={row['tier']:1s} | ws_slot={row['ws_slot']} | "
            f"segment={row['exchange_segment']}"
        )
    
    # Verify Tier-B count
    tier_b_count = await pool.fetchval(
        "SELECT COUNT(*) FROM instrument_master WHERE tier = 'B'"
    )
    log.info(f"\nTotal Tier-B instruments in database: {tier_b_count}")
    
    log.info("\n─── Fix complete ────────────────────────────────────────")
    log.info("Next steps:")
    log.info("  1. Restart the backend to reload Tier-B subscriptions")
    log.info("  2. Verify WebSocket connections are active")
    log.info("  3. Check Straddle/Options pages show live prices")
    
    await close_db()


if __name__ == "__main__":
    asyncio.run(fix_index_tier())
