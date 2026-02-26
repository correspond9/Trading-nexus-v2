#!/usr/bin/env python3
"""
Diagnostic: Compare Database Close Prices vs Expected Values
Check why system is not displaying correct closing prices
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

# Correct closing prices from user's screenshot (2026-02-25)
EXPECTED_CLOSES = {
    'RELIANCE': 1398.50,
    'NIFTYBANK': 61043.35,
    'NIFTY': 25482.50,
    'SENSEX': 82276.07,
}

async def compare_prices():
    """Compare database close prices with expected values."""
    pool = await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=5)
    
    print("="*100)
    print("CLOSING PRICE COMPARISON: Database vs Expected")
    print("="*100)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Fetch current data for key instruments
    symbols = list(EXPECTED_CLOSES.keys())
    
    results = await pool.fetch("""
        SELECT 
            im.symbol,
            im.instrument_type,
            im.exchange_segment,
            md.ltp,
            md.close,
            md.open,
            md.high,
            md.low,
            md.updated_at
        FROM market_data md
        JOIN instrument_master im ON im.instrument_token = md.instrument_token
        WHERE im.symbol = ANY($1::text[])
        ORDER BY im.symbol
    """, symbols)
    
    print(f"{'Symbol':<15} {'Type':<10} {'Exchange':<12} {'DB Close':>12} {'Expected':>12} {'Match':>8} {'DB LTP':>12} {'Updated':<20}")
    print("="*100)
    
    mismatch_count = 0
    for row in results:
        symbol = row['symbol']
        db_close = float(row['close']) if row['close'] else None
        expected = EXPECTED_CLOSES.get(symbol)
        match = "✅ YES" if (db_close and abs(db_close - expected) < 0.01) else "❌ NO"
        
        if not (db_close and abs(db_close - expected) < 0.01):
            mismatch_count += 1
        
        ltp = f"{float(row['ltp']):.2f}" if row['ltp'] else "N/A"
        db_close_str = f"{db_close:.2f}" if db_close else "NULL"
        expected_str = f"{expected:.2f}" if expected else "?"
        updated = row['updated_at'].strftime('%Y-%m-%d %H:%M:%S') if row['updated_at'] else "N/A"
        
        print(f"{symbol:<15} {row['instrument_type']:<10} {row['exchange_segment']:<12} "
              f"{db_close_str:>12} {expected_str:>12} {match:>8} {ltp:>12} {updated:<20}")
    
    print()
    print("="*100)
    print("ANALYSIS & ROOT CAUSE")
    print("="*100)
    
    if mismatch_count == 0:
        print("✅ All closing prices in database match expected values!")
        print("\nPossible issue: Frontend is not fetching/displaying them correctly.")
        print("Check:")
        print("  1. Frontend API endpoint call → is it getting fresh data?")
        print("  2. Frontend cache → is old data cached?")
        print("  3. Market state detection → is frontend thinking market is closed?")
    else:
        print(f"❌ Found {mismatch_count} mismatched closing prices!")
        print("\nPossible causes:")
        print("  1. Dhan WebSocket not sending correct close prices")
        print("  2. Validation is rejecting correct prices")
        print("  3. Close prices from yesterday still in database")
        print("  4. Greeks poller not seeding correct prev_close")
    
    print()
    print("="*100)
    print("DETAILED INVESTIGATION: WHERE IS CLOSE PRICE SET?")
    print("="*100)
    
    # Check where close prices are coming from
    for symbol in ['RELIANCE']:
        row = await pool.fetchrow("""
            SELECT 
                md.close,
                md.ltp,
                md.updated_at,
                md.open,
                md.high,
                md.low
            FROM market_data md
            JOIN instrument_master im ON im.instrument_token = md.instrument_token
            WHERE im.symbol = $1
        """, symbol)
        
        if row:
            print(f"\n{symbol}:")
            print(f"  Database Close: {float(row['close']) if row['close'] else 'NULL'}")
            print(f"  Database LTP:   {float(row['ltp']) if row['ltp'] else 'NULL'}")
            print(f"  Expected Close: {EXPECTED_CLOSES.get(symbol)}")
            print(f"  Updated At:     {row['updated_at']}")
            print(f"  Open:           {float(row['open']) if row['open'] else 'NULL'}")
            print(f"  High:           {float(row['high']) if row['high'] else 'NULL'}")
            print(f"  Low:            {float(row['low']) if row['low'] else 'NULL'}")
            
            diff = None
            if row['close']:
                diff = (float(row['close']) - EXPECTED_CLOSES.get(symbol, 0)) / EXPECTED_CLOSES.get(symbol, 1) * 100
                print(f"  Difference:     {diff:.2f}%")
    
    print()
    print("="*100)
    print("FRONTEND DISPLAY LOGIC CHECK")
    print("="*100)
    
    print("""
Frontend components that display close prices:
1. Watchlist (frontend/src/pages/WATCHLIST.jsx)
   - getDisplayedPrice() function
   - Logic: if market closed → show 'close', else → show 'ltp'

2. Trade page (frontend/src/pages/Trade.jsx)
   - Uses price from watchlist/market data
   
3. Market data API endpoint
   - GET /api/v2/market-data/{token}
   - Returns: { ltp, close, ... }

Debugging steps:
1. Check browser network tab
   - What does API return for 'close' field?
   - Is it the correct value?
   
2. Check browser console
   - console.log(marketData) in WATCHLIST.jsx
   - What's the actual 'close' value?

3. Check if market state is detected correctly
   - Is frontend detecting market as OPEN or CLOSED?
   - If OPEN, it shows LTP instead of close
   """)
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(compare_prices())
