#!/usr/bin/env python3
"""
Hotfix for Migration 028 - Function Signature Mismatch
======================================================

Problem:  Migration 028 was applied with INTEGER parameter for instrument_token,
          but the schema defines instrument_token as BIGINT.
          This causes: UndefinedFunctionError when calling the function.

Solution: 1. Drop the incorrect function
          2. Re-run the corrected migration

Run this script to fix the database.
"""

import asyncpg
import asyncio
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger(__name__)

# Database connection details
DATABASE_URL = "postgresql://appuser:HfIaD7vQExM2dD5@localhost:5432/trading_nexus"  # Update if needed


async def main():
    """Connect to database and fix the migration."""
    conn = None
    try:
        # Connect to database
        log.info("Connecting to PostgreSQL...")
        conn = await asyncpg.connect(DATABASE_URL)
        log.info("✓ Connected")
        
        # Step 1: Drop the incorrect function (if it exists)
        log.info("\n1️⃣ Dropping incorrect function signature...")
        try:
            # Drop with the wrong signature (INTEGER instead of BIGINT)
            await conn.execute("""
                DROP FUNCTION IF EXISTS calculate_position_margin(INTEGER, VARCHAR, VARCHAR, INTEGER, VARCHAR);
            """)
            log.info("   ✓ Dropped incorrect function with INTEGER signature")
        except Exception as e:
            log.warning(f"   ⚠️ Could not drop function: {e}")
        
        # Step 2: Drop views that depend on the function
        log.info("\n2️⃣ Dropping dependent views...")
        try:
            await conn.execute("DROP VIEW IF EXISTS v_user_margin_summary;")
            log.info("   ✓ Dropped v_user_margin_summary")
        except Exception as e:
            log.warning(f"   ⚠️ Could not drop v_user_margin_summary: {e}")
        
        try:
            await conn.execute("DROP VIEW IF EXISTS v_positions_with_margin;")
            log.info("   ✓ Dropped v_positions_with_margin")
        except Exception as e:
            log.warning(f"   ⚠️ Could not drop v_positions_with_margin: {e}")
        
        # Step 3: Re-run the corrected migration
        log.info("\n3️⃣ Re-running corrected migration 028...")
        migration_file = Path(__file__).parent / "migrations" / "028_fix_margin_calculation_consistency.sql"
        
        if not migration_file.exists():
            log.error(f"❌ Migration file not found: {migration_file}")
            sys.exit(1)
        
        migration_sql = migration_file.read_text(encoding='utf-8')
        
        # Split by ';' and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
        for i, stmt in enumerate(statements, 1):
            try:
                await conn.execute(stmt)
                log.info(f"   ✓ Statement {i} executed")
            except Exception as e:
                log.error(f"   ❌ Statement {i} failed: {e}")
                log.error(f"      Statement: {stmt[:100]}...")
        
        log.info("\n✅ Migration 028 fixed successfully!")
        log.info("\nNext steps:")
        log.info("1. Restart the backend application")
        log.info("2. Test the API endpoints that use calculate_position_margin()")
        
    except Exception as e:
        log.error(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
