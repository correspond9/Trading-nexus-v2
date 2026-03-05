import asyncio, asyncpg

DB_LIST = [
    ('postgresql://postgres:postgres@72.62.228.112:5432/trading_nexus_db', 'db1'),
    ('postgresql://tradinguser:Trading_23$@139.84.170.213:5432/tradingnexus', 'db2'),
    ('postgresql://postgres:postgres@72.62.228.112:5432/trading_terminal', 'db4'),
]

async def probe(url, name):
    print('--- Trying:', name, '---')
    try:
        conn = await asyncpg.connect(url, timeout=8)
        print('  OK connected')
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
        tnames = [t['tablename'] for t in tables]
        print('  Tables:', tnames)
        u = await conn.fetchrow("SELECT id, first_name, last_name, mobile FROM users WHERE mobile='6666666666'")
        if u: print('  USER FOUND id=', u['id'], u['first_name'], u['last_name'])
        else: print('  No user with 6666666666')
        await conn.close()
        return True
    except Exception as e:
        print('  FAIL:', e)
        return False

async def main():
    for url, name in DB_LIST:
        await probe(url, name)

asyncio.run(main())