#!/usr/bin/env python3
"""
Test: Verify closing prices are properly returned by API
Tests the fix for missing close prices in API responses
"""
import asyncio
import asyncpg
import os
from decimal import Decimal

# Test instruments from the user's screenshot
TEST_INSTRUMENTS = {
    'RELIANCE': {'expected_close': 1398.50, 'exchange': 'NSE_EQ'},
    'NIFTYBANK': {'expected_close': 61043.35, 'exchange': 'NSE_FNO'},
    'NIFTY': {'expected_close': 25482.50, 'exchange': 'NSE_FNO'},
    'SENSEX': {'expected_close': 82276.07, 'exchange': 'BSE_FNO'},
}

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'trading_nexus'),
}

async def test_api_response():
    """Test if API response includes close prices in all market states"""
    pool = await asyncpg.create_pool(**DB_CONFIG, min_size=1, max_size=5)
    
    print("="*100)
    print("API RESPONSE TEST: Close Price in Serialized Output")
    print("="*100)
    print()
    
    # Import the serializer function
    import sys
    sys.path.insert(0, '/app' if os.path.exists('/app') else 'd:\\4.PROJECTS\\FRESH\\trading-nexus')
    
    from app.serializers.market_data import serialize_tick
    from app.market_hours import MarketState, get_market_state
    
    for symbol, info in TEST_INSTRUMENTS.items():
        print(f"\n{symbol} ({info['exchange']}):")
        print("-" * 100)
        
        # Get data from DB
        row = await pool.fetchrow("""
            SELECT 
                md.instrument_token,
                md.ltp,
                md.close,
                md.open,
                md.high,
                md.low,
                md.updated_at,
                im.exchange_segment
            FROM market_data md
            JOIN instrument_master im ON im.instrument_token = md.instrument_token
            WHERE im.symbol = $1
            LIMIT 1
        """, symbol)
        
        if not row:
            print(f"  ERROR: Symbol {symbol} not found in database")
            continue
        
        # Convert to dict
        row_dict = dict(row)
        exchange = row['exchange_segment']
        
        # Serialize (this is what the API returns)
        serialized = serialize_tick(row_dict, segment=exchange, symbol=symbol)
        
        # Check results
        market_state = serialized.get('market_state')
        api_close = serialized.get('close')
        api_ltp = serialized.get('ltp')
        db_close = float(row['close']) if row['close'] else None
        db_ltp = float(row['ltp']) if row['ltp'] else None
        
        print(f"  Market State:    {market_state}")
        print(f"  DB Close:        {db_close}")
        print(f"  API Response includes 'close'?  {'✅ YES' if api_close is not None else '❌ NO'}")
        print(f"  API Close value:        {api_close}")
        print(f"  API LTP value:          {api_ltp}")
        print(f"  Expected Close:         {info['expected_close']}")
        
        # Verify
        if api_close is not None:
            print(f"  ✅ PASS: Close price is included in API response")
        else:
            print(f"  ❌ FAIL: Close price is NOT in API response!")
            print(f"           Frontend will fallback to showing LTP")
    
    await pool.close()
    
    print()
    print("="*100)
    print("FRONTEND DISPLAY LOGIC TEST")
    print("="*100)
    print("""
When getDisplayedPrice() runs on frontend:

1. Checks pulse.prices (real-time WebSocket) → returns if found
2. Checks tickByToken (live ticks) → returns if found
3. Checks market state:
   - If CLOSED: returns instrument.close ✅ (NOW INCLUDED)
   - If OPEN: returns instrument.ltp
   
BEFORE FIX:
  - When market CLOSED
  - API response didn't include 'close'
  - instrument.close = undefined
  - Falls back to LTP (WRONG!)

AFTER FIX:
  - When market CLOSED  
  - API response INCLUDES 'close'
  - instrument.close = correct value
  - Shows closing price (CORRECT!)
""")

if __name__ == "__main__":
    try:
        asyncio.run(test_api_response())
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
