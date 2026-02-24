import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://tradinguser:Trading_23$@139.84.170.213:5432/tradingnexus')
    
    # Search by LENSKART (correct spelling)
    print("\n=== Searching for LENSKART (correct spelling) ===")
    rows = await conn.fetch("""
        SELECT instrument_token, symbol, company_name, display_name, exchange_segment, instrument_type
        FROM instrument_master
        WHERE symbol ILIKE '%LENSKART%'
        LIMIT 5
    """)
    for r in rows:
        print(f"Token: {r['instrument_token']}")
        print(f"Symbol (search field): {r['symbol']}")
        print(f"Company Name: {r['company_name']}")
        print(f"Display Name: {r['display_name']}")
        print(f"Exchange: {r['exchange_segment']}")
        print(f"Type: {r['instrument_type']}")
        print('---')
    
    # Search by LENSCART (user's typo)
    print("\n=== Searching for LENSCART (user's typo with C) ===")
    rows = await conn.fetch("""
        SELECT instrument_token, symbol, company_name, display_name, exchange_segment, instrument_type
        FROM instrument_master
        WHERE symbol ILIKE '%LENSCART%'
        LIMIT 5
    """)
    print(f"Found {len(rows)} results")
    
    await conn.close()

asyncio.run(main())
