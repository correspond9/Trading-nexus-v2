#!/usr/bin/env python3
"""
Debug: Check what charges are actually in database
"""
import asyncio
from app.database import get_pool, init_db

async def check_charges():
    await init_db()
    pool = get_pool()
    
    if not pool:
        print("❌ Database pool not initialized")
        return
    
    try:
        # Check recent closed positions with charges
        rows = await pool.fetch("""
            SELECT 
                position_id,
                symbol,
                exchange_segment,
                product_type,
                instrument_type,
                quantity,
                avg_price,
                realized_pnl,
                trade_expense,
                stt_ctt_charge,
                exchange_charge,
                stamp_duty,
                sebi_charge,
                gst_charge,
                platform_cost,
                total_charges,
                charges_calculated,
                charges_calculated_at
            FROM paper_positions
            WHERE status = 'CLOSED'
            AND closed_at > NOW() - INTERVAL '30 days'
            ORDER BY closed_at DESC
            LIMIT 10
        """)
        
        print("\n" + "="*120)
        print("RECENT CLOSED POSITIONS WITH CHARGES")
        print("="*120)
        for row in rows:
            print(f"\n{row['symbol']} | {row['exchange_segment']} {row['product_type']} {row['instrument_type']} | Qty {row['quantity']}")
            print(f"  Trade Expense Breakdown:")
            print(f"    STT/CTT:      ₹{row['stt_ctt_charge']:.2f}")
            print(f"    Stamp Duty:   ₹{row['stamp_duty']:.2f}")
            print(f"    Exchange:     ₹{row['exchange_charge']:.2f}")
            print(f"    SEBI:         ₹{row['sebi_charge']:.2f}")
            print(f"    GST:          ₹{row['gst_charge']:.2f}")
            print(f"  TOTAL Trade Expense: ₹{row['trade_expense']:.2f}")
            print(f"  Platform Cost: ₹{row['platform_cost']:.2f}")
            print(f"  Total Charges: ₹{row['total_charges']:.2f}")
            print(f"  Calculated: {row['charges_calculated']} at {row['charges_calculated_at']}")
        
        # Check for uniform trade_expense values
        uniform_check = await pool.fetch("""
            SELECT trade_expense, COUNT(*) as count
            FROM paper_positions
            WHERE status = 'CLOSED'
            AND charges_calculated = TRUE
            AND trade_expense > 0
            GROUP BY trade_expense
            ORDER BY count DESC
            LIMIT 10
        """)
        
        print("\n" + "="*120)
        print("MOST COMMON TRADE EXPENSE VALUES (SUSPICIOUS IF SAME ACROSS DIFFERENT TRADES)")
        print("="*120)
        for row in uniform_check:
            print(f"  ₹{row['trade_expense']:.2f}: {row['count']} positions")
        
        # Check nil brokerage plan users
        nil_brokerage_positions = await pool.fetch("""
            SELECT 
                pp.position_id,
                pp.symbol,
                pp.trade_expense,
                pp.charges_calculated,
                u.mobile,
                bp.flat_fee,
                bp.percent_fee
            FROM paper_positions pp
            JOIN users u ON u.id = pp.user_id
            LEFT JOIN brokerage_plans bp ON bp.plan_id = u.brokerage_plan_equity_id
            WHERE pp.status = 'CLOSED'
            AND pp.closed_at > NOW() - INTERVAL '30 days'
            AND (bp.flat_fee = 0 OR bp.flat_fee IS NULL)
            AND (bp.percent_fee = 0 OR bp.percent_fee IS NULL)
            LIMIT 10
        """)
        
        print("\n" + "="*120)
        print("NIL BROKERAGE PLAN POSITIONS (SHOULD STILL HAVE TRADE EXPENSE)")
        print("="*120)
        for row in nil_brokerage_positions:
            print(f"  {row['symbol']} | User {row['mobile']}")
            print(f"    Brokerage: flat={row['flat_fee']}, percent={row['percent_fee']}")
            print(f"    Trade Expense: ₹{row['trade_expense']:.2f}")
            print(f"    Calculated: {row['charges_calculated']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(check_charges())
