#!/usr/bin/env python3
"""Query database to check symbol values"""

import asyncpg
import asyncio
import json

async def check_instruments():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='TradingNexus@2024',
        database='trading_nexus_db'
    )
    
    # Check a few sample instruments
    rows = await conn.fetch('''
        SELECT instrument_token, symbol, display_name, instrument_type, exchange_segment
        FROM instrument_master
        WHERE symbol LIKE '%RELIANCE%'
        LIMIT 5
    ''')
    
    print('Sample RELIANCE instruments:')
    for row in rows:
        print(f'Token: {row["instrument_token"]}')
        print(f'  Symbol: {row["symbol"]}')
        print(f'  Display: {row["display_name"]}')
        print(f'  Type: {row["instrument_type"]}')
        print()
    
    await conn.close()

asyncio.run(check_instruments())
