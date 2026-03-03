import asyncio
from app.database import init_db, get_pool

async def check():
    await init_db()
    pool = get_pool()
    
    # Check total orders
    total = await pool.fetchval('SELECT COUNT(*) FROM paper_orders')
    print(f'Total orders: {total}')
    
    # Check order statuses
    statuses = await pool.fetch('SELECT status, COUNT(*) as cnt FROM paper_orders GROUP BY status')
    print(f'\nOrder statuses:')
    for row in statuses:
        print(f'  {row["status"]}: {row["cnt"]}')
    
    # Check archived orders
    archived = await pool.fetchval('SELECT COUNT(*) FROM paper_orders WHERE archived_at IS NOT NULL')
    print(f'\nArchived orders: {archived}')
    non_archived = await pool.fetchval('SELECT COUNT(*) FROM paper_orders WHERE archived_at IS NULL')
    print(f'Non-archived orders: {non_archived}')
    
    # Check sample filled orders
    sample = await pool.fetch('SELECT order_id, user_id, symbol, status, placed_at, archived_at FROM paper_orders WHERE status = $1 LIMIT 5', 'FILLED')
    print(f'\nSample FILLED orders:')
    if sample:
        for row in sample:
            print(f'  {row["symbol"]}: {row["status"]} (archived: {row["archived_at"]})')
    else:
        print('  (none)')

asyncio.run(check())
