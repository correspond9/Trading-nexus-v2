"""
Test MCX SPAN margin data download and parsing.

This script manually triggers MCX margin download to verify the parsing implementation.
"""

import asyncio
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, ".")

from app.margin import mcx_margin_data


async def test_mcx_download():
    """Test MCX margin download and parsing."""
    print("=" * 80)
    print("MCX SPAN Margin Download Test")
    print("=" * 80)
    
    # Attempt download for today
    print("\n[1] Attempting MCX SPAN download for today...")
    result = await mcx_margin_data.download_and_refresh()
    
    print(f"\n[2] Download result:")
    print(f"    Success: {result.get('success')}")
    print(f"    Symbol count: {result.get('symbol_count', 0)}")
    print(f"    Download date: {result.get('download_date')}")
    print(f"    Source: {result.get('source', 'fresh_download')}")
    if 'error' in result:
        print(f"    Error: {result['error']}")
    
    # Check in-memory cache
    margins = mcx_margin_data.get_all_margins()
    print(f"\n[3] In-memory cache: {len(margins)} commodities loaded")
    
    if margins:
        print("\n[4] Sample MCX margin data (first 5):")
        for i, (symbol, entry) in enumerate(list(margins.items())[:5]):
            print(f"    {symbol:12} | Ref: ₹{entry.ref_price:>10.2f} | "
                  f"SPAN: ₹{entry.price_scan:>10.2f} | CVF: {entry.cvf:>6.0f} | "
                  f"ELM: {entry.elm_pct:.2f}%")
        
        # Test margin calculation
        print("\n[5] Testing margin calculation for CRUDEOIL (1 lot):")
        if 'CRUDEOIL' in margins:
            margin_calc = await mcx_margin_data.get_margin('CRUDEOIL', 1, is_sell=True)
            print(f"    Symbol: {margin_calc.get('symbol')}")
            print(f"    SPAN margin: ₹{margin_calc.get('span_margin', 0):,.2f}")
            print(f"    ELM margin:  ₹{margin_calc.get('elm_margin', 0):,.2f}")
            print(f"    Total margin: ₹{margin_calc.get('total_margin', 0):,.2f}")
        else:
            print("    CRUDEOIL not found in parsed data")
            print(f"    Available symbols: {', '.join(list(margins.keys())[:10])}...")
    else:
        print("\n[!] No MCX margin data available after download attempt")
    
    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_mcx_download())
