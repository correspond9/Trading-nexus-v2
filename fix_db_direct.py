#!/usr/bin/env python3
"""Direct fix for migration 028 - Function signature mismatch"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

# Connection details
DB_HOST = "72.62.228.112"
DB_NAME = "trading_terminal"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # Check if this matches your setup
DB_PORT = 5432

# SQL to execute
FIX_SQL = """
CREATE OR REPLACE FUNCTION calculate_position_margin(
    p_instrument_token BIGINT,
    p_symbol VARCHAR,
    p_exchange_segment VARCHAR,
    p_quantity INTEGER,
    p_product_type VARCHAR
) RETURNS NUMERIC AS $$
DECLARE
    v_ltp NUMERIC;
    v_span_margin NUMERIC;
    v_exposure_margin NUMERIC;
    v_margin NUMERIC;
BEGIN
    SELECT COALESCE(ltp, 0) INTO v_ltp
    FROM market_data
    WHERE instrument_token = p_instrument_token
    LIMIT 1;
    
    IF v_ltp IS NULL OR v_ltp = 0 THEN
        RETURN 0;
    END IF;
    
    IF (p_exchange_segment ILIKE '%OPT%' 
        OR p_symbol ILIKE '%CE' 
        OR p_symbol ILIKE '%PE') THEN
        
        IF p_quantity > 0 THEN
            RETURN ABS(p_quantity) * v_ltp;
        END IF;
        
        IF p_quantity < 0 THEN
            SELECT COALESCE(price_scan, 0) INTO v_span_margin
            FROM span_margin_cache
            WHERE symbol = p_symbol AND is_latest = true
            LIMIT 1;
            
            IF v_span_margin > 0 THEN
                SELECT COALESCE(exposure_limit_margin, 0) INTO v_exposure_margin
                FROM span_margin_cache
                WHERE symbol = p_symbol AND is_latest = true
                LIMIT 1;
                RETURN (v_span_margin * ABS(p_quantity)) + (v_exposure_margin * ABS(p_quantity));
            ELSE
                RETURN ABS(p_quantity) * v_ltp;
            END IF;
        END IF;
        
        RETURN 0;
    END IF;
    
    IF (p_exchange_segment ILIKE '%FUT%' OR p_symbol ILIKE '%FUT%') THEN
        SELECT COALESCE(price_scan, 0) INTO v_span_margin
        FROM span_margin_cache
        WHERE symbol = p_symbol AND is_latest = true
        LIMIT 1;
        
        IF v_span_margin > 0 THEN
            SELECT COALESCE(exposure_limit_margin, 0) INTO v_exposure_margin
            FROM span_margin_cache
            WHERE symbol = p_symbol AND is_latest = true
            LIMIT 1;
            RETURN (v_span_margin * ABS(p_quantity)) + (v_exposure_margin * ABS(p_quantity));
        ELSE
            RETURN v_ltp * ABS(p_quantity) * 0.15;
        END IF;
    END IF;
    
    IF (p_exchange_segment ILIKE '%COMM%' OR p_exchange_segment ILIKE '%MCX%') THEN
        SELECT COALESCE(price_scan, 0) INTO v_span_margin
        FROM mcx_span_margin_cache
        WHERE symbol = p_symbol AND is_latest = true
        LIMIT 1;
        
        IF v_span_margin > 0 THEN
            SELECT COALESCE(exposure_limit_margin, 0) INTO v_exposure_margin
            FROM mcx_span_margin_cache
            WHERE symbol = p_symbol AND is_latest = true
            LIMIT 1;
            RETURN (v_span_margin * ABS(p_quantity)) + (v_exposure_margin * ABS(p_quantity));
        ELSE
            RETURN v_ltp * ABS(p_quantity) * 0.10;
        END IF;
    END IF;
    
    IF (p_exchange_segment ILIKE '%EQ%' OR p_exchange_segment ILIKE 'NSE' OR p_exchange_segment ILIKE 'BSE') THEN
        RETURN ABS(p_quantity) * v_ltp;
    END IF;
    
    RETURN ABS(p_quantity) * v_ltp;
END;
$$ LANGUAGE plpgsql STABLE;
"""

try:
    print("🔗 Connecting to database...")
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        connect_timeout=10
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("✅ Connected")
    
    # Execute the fix
    print("\n1️⃣ Creating corrected function with BIGINT signature...")
    cursor.execute(FIX_SQL)
    print("   ✅ Function created")
    
    # Create views
    print("\n2️⃣ Creating views...")
    cursor.execute("""
        CREATE OR REPLACE VIEW v_positions_with_margin AS
        SELECT 
            pp.position_id,
            pp.user_id,
            pp.instrument_token,
            pp.symbol,
            pp.exchange_segment,
            pp.quantity,
            pp.avg_price,
            pp.product_type,
            pp.status,
            pp.opened_at,
            pp.closed_at,
            COALESCE(md.ltp, pp.avg_price) as current_ltp,
            COALESCE(md.ltp - pp.avg_price, 0) * pp.quantity as mtm,
            calculate_position_margin(
                pp.instrument_token,
                pp.symbol,
                pp.exchange_segment,
                pp.quantity,
                pp.product_type
            ) as required_margin
        FROM paper_positions pp
        LEFT JOIN market_data md ON md.instrument_token = pp.instrument_token
        WHERE pp.status = 'OPEN' AND pp.quantity != 0;
    """)
    print("   ✅ v_positions_with_margin view created")
    
    cursor.execute("""
        CREATE OR REPLACE VIEW v_user_margin_summary AS
        SELECT
            pa.user_id,
            COALESCE(pa.balance, 0) as wallet_balance,
            COALESCE(pa.margin_allotted, 0) as margin_allotted,
            COALESCE(SUM(pwm.required_margin), 0) as used_margin_real,
            NULL as available_margin
        FROM paper_accounts pa
        LEFT JOIN v_positions_with_margin pwm ON pwm.user_id = pa.user_id
        GROUP BY pa.user_id, pa.balance, pa.margin_allotted;
    """)
    print("   ✅ v_user_margin_summary view created")
    
    # Verify
    print("\n3️⃣ Verifying function creation...")
    cursor.execute("""
        SELECT pg_get_functiondef(oid) 
        FROM pg_proc 
        WHERE proname = 'calculate_position_margin'
        LIMIT 1;
    """)
    result = cursor.fetchone()
    if result and result[0]:
        if "bigint" in result[0].lower():
            print("   ✅ BIGINT signature confirmed!")
        else:
            print("   ⚠️ Function exists but signature unclear")
            print(f"      {result[0][:100]}...")
    else:
        print("   ❌ Function not found!")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Migration 028 fix applied successfully!")
    print("\nNext steps:")
    print("1. Restart the backend container: docker restart <backend-container-id>")
    print("2. Check if the migration now passes")
    
except psycopg2.OperationalError as e:
    print(f"❌ Connection error: {e}")
    print("\nMake sure the database is accessible from this machine.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
