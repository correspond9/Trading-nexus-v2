#!/usr/bin/env python3
"""
Diagnostic: Audit Current Close Prices
Check for wrong/stale/missing close prices in market_data
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'trading_nexus'),
}

async def audit_close_prices():
    """Comprehensive close price audit"""
    pool = await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=5)
    
    print("="*80)
    print("CLOSE PRICE AUDIT REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Overall stats
    print("1. OVERALL STATISTICS")
    print("-" * 80)
    stats = await pool.fetchrow("""
        SELECT 
            COUNT(*) as total_instruments,
            COUNT(md.ltp) as has_ltp,
            COUNT(md.close) as has_close,
            COUNT(CASE WHEN md.close = 0 THEN 1 END) as close_is_zero,
            COUNT(CASE WHEN md.close < 0 THEN 1 END) as close_is_negative,
            COUNT(CASE WHEN md.close IS NOT NULL AND md.ltp IS NOT NULL THEN 1 END) as has_both
        FROM market_data md
    """)
    
    print(f"Total Instruments:         {stats['total_instruments']:>10}")
    print(f"Has LTP:                   {stats['has_ltp']:>10} ({stats['has_ltp']/stats['total_instruments']*100:.1f}%)")
    print(f"Has Close Price:           {stats['has_close']:>10} ({stats['has_close']/stats['total_instruments']*100:.1f}%)")
    print(f"Close = 0:                 {stats['close_is_zero']:>10} ⚠️")
    print(f"Close < 0:                 {stats['close_is_negative']:>10} ⚠️")
    print(f"Has Both LTP & Close:      {stats['has_both']:>10}")
    print()
    
    # 2. Extreme deviations (LTP vs Close)
    print("2. EXTREME LTP vs CLOSE DEVIATIONS (>20%)")
    print("-" * 80)
    extreme = await pool.fetch("""
        SELECT 
            im.symbol,
            im.exchange_segment,
            md.ltp,
            md.close,
            md.updated_at,
            ROUND(ABS((md.ltp - md.close) / NULLIF(md.close, 0)) * 100, 2) AS deviation_pct
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.close IS NOT NULL 
          AND md.ltp IS NOT NULL
          AND md.close > 0
          AND ABS((md.ltp - md.close) / md.close) > 0.20
        ORDER BY deviation_pct DESC
        LIMIT 20
    """)
    
    if extreme:
        print(f"{'Symbol':<25} {'Exchange':<10} {'LTP':>10} {'Close':>10} {'Dev %':>10} {'Updated':<20}")
        print("-" * 100)
        for row in extreme:
            print(f"{row['symbol']:<25} {row['exchange_segment']:<10} "
                  f"{row['ltp']:>10.2f} {row['close']:>10.2f} "
                  f"{row['deviation_pct']:>9.1f}% "
                  f"{row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else 'N/A':<20}")
    else:
        print("✅ No extreme deviations found")
    print()
    
    # 3. Stale close prices (>24 hours old)
    print("3. STALE CLOSE PRICES (>24 hours old)")
    print("-" * 80)
    cutoff = datetime.now() - timedelta(hours=24)
    stale = await pool.fetch("""
        SELECT 
            im.symbol,
            im.exchange_segment,
            md.ltp,
            md.close,
            md.updated_at,
            EXTRACT(EPOCH FROM (NOW() - md.updated_at))/3600 AS hours_old
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.close IS NOT NULL
          AND md.updated_at < $1
        ORDER BY md.updated_at ASC
        LIMIT 20
    """, cutoff)
    
    if stale:
        print(f"{'Symbol':<25} {'Exchange':<10} {'LTP':>10} {'Close':>10} {'Hours Old':>10} {'Updated':<20}")
        print("-" * 100)
        for row in stale:
            print(f"{row['symbol']:<25} {row['exchange_segment']:<10} "
                  f"{row['ltp'] if row['ltp'] else 'N/A':>10} {row['close']:>10.2f} "
                  f"{row['hours_old']:>9.1f}h "
                  f"{row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else 'N/A':<20}")
    else:
        print("✅ No stale close prices found")
    print()
    
    # 4. Missing close prices (has LTP but no close)
    print("4. MISSING CLOSE PRICES (Has LTP but no Close)")
    print("-" * 80)
    missing = await pool.fetch("""
        SELECT 
            im.symbol,
            im.exchange_segment,
            im.instrument_type,
            md.ltp,
            md.updated_at
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.ltp IS NOT NULL
          AND md.close IS NULL
        ORDER BY md.updated_at DESC
        LIMIT 20
    """)
    
    if missing:
        print(f"{'Symbol':<30} {'Exchange':<10} {'Type':<10} {'LTP':>10} {'Updated':<20}")
        print("-" * 100)
        for row in missing:
            print(f"{row['symbol']:<30} {row['exchange_segment']:<10} {row['instrument_type']:<10} "
                  f"{row['ltp']:>10.2f} "
                  f"{row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else 'N/A':<20}")
    else:
        print("✅ All instruments with LTP have close prices")
    print()
    
    # 5. Zero/Negative close prices
    print("5. ZERO OR NEGATIVE CLOSE PRICES")
    print("-" * 80)
    invalid = await pool.fetch("""
        SELECT 
            im.symbol,
            im.exchange_segment,
            md.ltp,
            md.close,
            md.updated_at
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.close IS NOT NULL
          AND md.close <= 0
        LIMIT 50
    """)
    
    if invalid:
        print(f"{'Symbol':<30} {'Exchange':<10} {'LTP':>10} {'Close':>10} {'Updated':<20}")
        print("-" * 100)
        for row in invalid:
            print(f"{row['symbol']:<30} {row['exchange_segment']:<10} "
                  f"{row['ltp'] if row['ltp'] else 'N/A':>10} {row['close']:>10.2f} "
                  f"{row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else 'N/A':<20}")
    else:
        print("✅ No zero or negative close prices found")
    print()
    
    # 6. Sample of normal close prices (for comparison)
    print("6. SAMPLE OF NORMAL CLOSE PRICES (for reference)")
    print("-" * 80)
    normal = await pool.fetch("""
        SELECT 
            im.symbol,
            im.exchange_segment,
            md.ltp,
            md.close,
            md.updated_at,
            ROUND(ABS((md.ltp - md.close) / NULLIF(md.close, 0)) * 100, 2) AS deviation_pct
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE md.close IS NOT NULL 
          AND md.ltp IS NOT NULL
          AND md.close > 0
          AND ABS((md.ltp - md.close) / md.close) <= 0.10
        ORDER BY md.updated_at DESC
        LIMIT 10
    """)
    
    if normal:
        print(f"{'Symbol':<30} {'Exchange':<10} {'LTP':>10} {'Close':>10} {'Dev %':>8}")
        print("-" * 80)
        for row in normal:
            print(f"{row['symbol']:<30} {row['exchange_segment']:<10} "
                  f"{row['ltp']:>10.2f} {row['close']:>10.2f} {row['deviation_pct']:>7.2f}%")
    print()
    
    # 7. Options prev_close check
    print("7. OPTION CHAIN PREV_CLOSE CHECK")
    print("-" * 80)
    opt_stats = await pool.fetchrow("""
        SELECT 
            COUNT(*) as total_options,
            COUNT(prev_close) as has_prev_close,
            COUNT(CASE WHEN prev_close = 0 THEN 1 END) as prev_close_zero,
            COUNT(CASE WHEN prev_close < 0 THEN 1 END) as prev_close_negative
        FROM option_chain_data
    """)
    
    print(f"Total Options:             {opt_stats['total_options']:>10}")
    print(f"Has prev_close:            {opt_stats['has_prev_close']:>10} ({opt_stats['has_prev_close']/opt_stats['total_options']*100:.1f}%)")
    print(f"prev_close = 0:            {opt_stats['prev_close_zero']:>10}")
    print(f"prev_close < 0:            {opt_stats['prev_close_negative']:>10}")
    print()
    
    # Summary
    print("="*80)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*80)
    
    issues_found = []
    if stats['close_is_zero'] > 0:
        issues_found.append(f"⚠️  {stats['close_is_zero']} instruments have close = 0")
    if stats['close_is_negative'] > 0:
        issues_found.append(f"⚠️  {stats['close_is_negative']} instruments have close < 0")
    if len(extreme) > 0:
        issues_found.append(f"⚠️  {len(extreme)} instruments have >20% LTP vs close deviation")
    if len(stale) > 0:
        issues_found.append(f"⚠️  {len(stale)} instruments have close prices >24h old")
    if len(missing) > 0:
        issues_found.append(f"⚠️  {len(missing)} instruments have LTP but no close price")
    
    if issues_found:
        print("ISSUES FOUND:")
        for issue in issues_found:
            print(f"  {issue}")
        print("\nRECOMMENDED ACTIONS:")
        print("  1. Investigate data source (Dhan WebSocket/REST API)")
        print("  2. Implement close price validation before storage")
        print("  3. Add daily close price rollover mechanism")
        print("  4. Set up alerts for extreme deviations")
        print("  5. Manual correction UI for admin")
    else:
        print("✅ No major issues found with close prices")
        print("   All close prices appear reasonable and up-to-date")
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(audit_close_prices())
