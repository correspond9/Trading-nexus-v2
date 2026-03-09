"""
Deep Diagnostic: Check actual database state for limit order execution
========================================================================
This script will execute SQL queries on the production database via Coolify
to diagnose why limit orders are not executing.
"""
import requests
import json

COOLIFY_URL = 'http://72.62.228.112:8000'
API_TOKEN = '1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466'
APP_UUID = 'bsgc4kwsk88s04kgws0408c4'

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

# ──────────────────────────────────────────────────────────────────────────────
# SQL QUERIES TO RUN ON PRODUCTION DATABASE
# ──────────────────────────────────────────────────────────────────────────────

queries = [
    {
        "name": "Check SUNDARAM market data",
        "sql": """
SELECT 
    instrument_token,
    symbol,
    ltp,
    bid_depth::text,
    ask_depth::text,
    updated_at
FROM market_data 
WHERE symbol ILIKE '%SUNDARAM%'
LIMIT 5;
""",
        "purpose": "See if SUNDARAM has market data with bid/ask depth"
    },
    {
        "name": "Check specific token 18931 market data",
        "sql": """
SELECT 
    instrument_token,
    symbol,
    ltp,
    CASE 
        WHEN bid_depth IS NULL THEN 'NULL'
        WHEN bid_depth::text = '[]' THEN 'EMPTY ARRAY'
        ELSE 'HAS DATA'
    END as bid_status,
    CASE 
        WHEN ask_depth IS NULL THEN 'NULL'
        WHEN ask_depth::text = '[]' THEN 'EMPTY ARRAY'  
        ELSE 'HAS DATA'
    END as ask_status,
    updated_at
FROM market_data 
WHERE instrument_token = 18931;
""",
        "purpose": "Check if token 18931 has depth data"
    },
    {
        "name": "Check pending LIMIT orders",
        "sql": """
SELECT 
    order_id,
    user_id,
    symbol,
    side,
    order_type,
    quantity,
    limit_price,
    status,
    placed_at,
    updated_at
FROM paper_orders 
WHERE status = 'PENDING' 
  AND order_type = 'LIMIT'
ORDER BY placed_at DESC
LIMIT 10;
""",
        "purpose": "See all pending LIMIT orders"
    },
    {
        "name": "Check SUNDARAM pending orders specifically",
        "sql": """
SELECT 
    order_id,
    user_id,
    symbol,
    side,
    order_type,
    quantity,
    limit_price,
    filled_qty,
    remaining_qty,
    status,
    placed_at
FROM paper_orders 
WHERE symbol ILIKE '%SUNDARAM%'
  AND status = 'PENDING'
ORDER BY placed_at DESC;
""",
        "purpose": "Check the specific SUNDARAM order we see in the UI"
    },
    {
        "name": "Check instrument master for SUNDARAM",
        "sql": """
SELECT 
    instrument_token,
    tradingsymbol,
    name,
    exchange,
    exchange_segment,
    instrument_type,
    lot_size,
    tick_size
FROM instrument_master 
WHERE tradingsymbol ILIKE '%SUNDARAM%'
   OR name ILIKE '%SUNDARAM%'
LIMIT 10;
""",
        "purpose": "Get instrument details"
    },
    {
        "name": "Check if tick processor has processed recent ticks",
        "sql": """
SELECT 
    instrument_token,
    symbol,
    COUNT(*) as tick_count,
    MAX(updated_at) as last_update
FROM market_data 
WHERE updated_at > NOW() - INTERVAL '5 minutes'
GROUP BY instrument_token, symbol
ORDER BY tick_count DESC
LIMIT 20;
""",
        "purpose": "Verify tick processor is updating market_data table"
    }
]

print("="*80)
print("PRODUCTION DATABASE DIAGNOSTIC")
print("="*80)
print("\nThis will execute SQL queries on the production database")
print("to diagnose the limit order execution issue.\n")

# Create a Python script that can be executed inside the container
script_content = """
import asyncpg
import asyncio
import json
import sys
from decimal import Decimal

DATABASE_URL = sys.argv[1] if len(sys.argv) > 1 else None

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

async def run_diagnostics():
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not provided")
        return
        
    conn = await asyncpg.connect(DATABASE_URL)
    
    queries = """ + json.dumps(queries) + """
    
    for query_info in queries:
        print("\\n" + "="*70)
        print(f"QUERY: {query_info['name']}")
        print(f"PURPOSE: {query_info['purpose']}")
        print("="*70)
        
        try:
            rows = await conn.fetch(query_info['sql'])
            
            if not rows:
                print("❌ NO RESULTS FOUND")
            else:
                print(f"✅ Found {len(rows)} row(s):")
                for i, row in enumerate(rows, 1):
                    print(f"\\n  Row {i}:")
                    for key in row.keys():
                        value = row[key]
                        print(f"    {key}: {value}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    await conn.close()

asyncio.run(run_diagnostics())
"""

# Save the diagnostic script to a file
with open('temp_db_diagnostic.py', 'w') as f:
    f.write(script_content)

print("\n🔧 Diagnostic script created: temp_db_diagnostic.py")
print("\n📋 MANUAL EXECUTION REQUIRED:")
print("-" * 80)
print("\nTo run this diagnostic on the production server:")
print("\n1. Get the DATABASE_URL from the backend container:")
print('   docker exec backend-bsgc4kwsk88s04kgws0408c4-040735389971 env | grep DATABASE_URL')
print("\n2. Copy the diagnostic script to the container:")
print('   docker cp temp_db_diagnostic.py backend-bsgc4kwsk88s04kgws0408c4-040735389971:/tmp/')
print("\n3. Run the diagnostic:")
print('   docker exec backend-bsgc4kwsk88s04kgws0408c4-040735389971 python /tmp/temp_db_diagnostic.py "$DATABASE_URL"')
print("\n" + "="*80)

print("\n📊 EXPECTED FINDINGS:")
print("-" * 80)
print("""
If limit orders are not executing, you will likely find ONE of these:

1. ❌ NO MARKET DATA for SUNDARAM (token 18931)
   - market_data table has no row for this token
   - OR ltp is NULL
   - Solution: Ensure WebSocket is subscribed to this instrument

2. ❌ EMPTY DEPTH ARRAYS
   - bid_depth = [] or NULL
   - ask_depth = [] or NULL  
   - Solution: NSE_EQ instruments may not have depth in DhanHQ feed
   - Workaround: Use LTP-based fills instead of depth-based

3. ❌ ORDER NOT IN DATABASE
   - paper_orders table has no PENDING LIMIT order for SUNDARAM
   - Solution: Check order placement logic

4. ❌ NO RECENT TICK UPDATES
   - market_data.updated_at is old (>5 min)
   - Solution: Check if tick processor is running
   - Check STARTUP_START_STREAMS environment variable

5. ✅ EVERYTHING LOOKS GOOD
   - If all data exists, the issue may be in the matching logic
   - Check execution_engine.py on_tick() processing
""")
