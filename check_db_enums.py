#!/usr/bin/env python3
"""Check what enum values are in the database."""

import asyncio
from app.database import get_pool, create_pool

async def check_db():
    pool = get_pool()
    if pool is None:
        await create_pool()
        pool = get_pool()
    
    result = await pool.fetch('''
        SELECT DISTINCT exchange_segment, product_type, COUNT(*) as cnt
        FROM paper_positions
        WHERE status = 'CLOSED'
        GROUP BY exchange_segment, product_type
        ORDER BY cnt DESC
        LIMIT 20
    ''')
    
    print('Database enum values in closed positions:')
    for row in result:
        exch = str(row[0] or '(null)')
        prod = str(row[1] or '(null)')
        print(f'  exchange_segment={exch:25} product_type={prod:12} count={row[2]}')
    
    # Check charges_calculated status
    uncalc = await pool.fetchval('SELECT COUNT(*) FROM paper_positions WHERE status = %s AND charges_calculated = %s', 'CLOSED', False)
    calc = await pool.fetchval('SELECT COUNT(*) FROM paper_positions WHERE status = %s AND charges_calculated = %s', 'CLOSED', True)
    
    print(f'\nCharges calculation status in CLOSED positions:')
    print(f'  Not calculated (charges_calculated=FALSE): {uncalc}')
    print(f'  Already calculated (charges_calculated=TRUE): {calc}')
    
    # Check trade_expense status
    zero_expense = await pool.fetchval('SELECT COUNT(*) FROM paper_positions WHERE status = %s AND trade_expense = 0', 'CLOSED')
    nonzero_expense = await pool.fetchval('SELECT COUNT(*) FROM paper_positions WHERE status = %s AND trade_expense > 0', 'CLOSED')
    
    print(f'\nTrade expense status in CLOSED positions:')
    print(f'  Zero trade_expense: {zero_expense}')
    print(f'  Non-zero trade_expense: {nonzero_expense}')

asyncio.run(check_db())
