import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect('postgres://postgres:postgres@72.62.228.112:5432/trading_nexus_db')
    row = await conn.fetchrow("SELECT * FROM instrument_master WHERE symbol LIKE '%DILIP%' LIMIT 10")
    if row:
        print(dict(row))
    else:
        print("Not found")
    await conn.close()

asyncio.run(check())
