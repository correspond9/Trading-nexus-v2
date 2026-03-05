import asyncio, asyncpg

DB_CONNECTIONS = [
    'postgresql://postgres:postgres@72.62.228.112:5432/trading_nexus_db',
    'postgresql://tradinguser:Trading_23$@139.84.170.213:5432/tradingnexus',
    'postgresql://postgres:postgres@72.62.228.112:5432/trading_nexus',
    'postgresql://postgres:postgres@72.62.228.112:5432/trading_terminal',
]

async def explore(db_url):
    print(f'\n=== Trying: {db_url} ===')
    try:
        conn = await asyncpg.connect(db_url, timeout=8)
    except Exception as e:
        print(f'  Failed: {e}'); return False
    try:
        user = await conn.fetchrow(
            'SELECT id, first_name, last_name, mobile, email FROM users WHERE mobile = $1', '6666666666')
        if not user:
            print('  User 6666666666 NOT FOUND'); await conn.close(); return False
        print(f'  User: id={user["id"]} name={user["first_name"]} {user["last_name"]}')
        user_id = user['id']
        tables = await conn.fetch(
            'SELECT tablename FROM pg_tables WHERE schemaname=$1 ORDER BY tablename', 'public')
        tnames = [t['tablename'] for t in tables]
        print(f'  Tables: {tnames}')
        ptables = [t for t in tnames if any(x in t for x in ['position','trade','order','holding'])]
        print(f'  Relevant: {ptables}')
        for tbl in ptables:
            cols = await conn.fetch(
                'SELECT column_name FROM information_schema.columns WHERE table_name=$1', tbl)
            cnames = [c['column_name'] for c in cols]
            uid_col = 'user_id' if 'user_id' in cnames else ('userId' if 'userId' in cnames else None)
            if uid_col:
                rows = await conn.fetch(f'SELECT * FROM {tbl} WHERE {uid_col} = $1', user_id)
                print(f'  {tbl}: {len(rows)} rows for user')
                for row in rows: print(f'    {dict(row)}')
        await conn.close(); return True
    except Exception as e:
        print(f'  Error: {e}'); 
        try: await conn.close()
        except: pass
        return False

async def main():
    for db_url in DB_CONNECTIONS:
        if await explore(db_url): break

asyncio.run(main())
