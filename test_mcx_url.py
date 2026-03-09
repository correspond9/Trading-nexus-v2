"""
Test MCX SPAN file URL accessibility.
"""

import httpx
from datetime import datetime, timedelta, timezone

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

# Base URL from updated code
MCX_RPF_BASE = "https://www.mcxccl.com/risk-management/daily-span-risk-parameter-file"

# Test different URL patterns
async def test_urls():
    """Test various MCX SPAN URL patterns."""
    
    today = datetime.now(tz=IST).date()
    
    # Build month name
    month_names = [
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december"
    ]
    month_name = month_names[today.month - 1]
    date_str = today.strftime("%Y%m%d")
    year = today.strftime("%Y")
    
    # Test URLs
    test_cases = [
        # Original pattern from code
        f"{MCX_RPF_BASE}/{year}/{month_name}/mcxrpf-{date_str}-0506-01-i.zip",
        
        # Try without year/month path
        f"{MCX_RPF_BASE}/mcxrpf-{date_str}-0506-01-i.zip",
        
        # Try base URL to see if it's accessible
        MCX_RPF_BASE,
        
        # Try root domain
        "https://www.mcxccl.com/",
    ]
    
    print("Testing MCX SPAN URL accessibility...")
    print("=" * 80)
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        for i, url in enumerate(test_cases, 1):
            print(f"\n[{i}] Testing: {url}")
            try:
                resp = await client.get(url)
                print(f"    Status: {resp.status_code}")
                print(f"    Content-Type: {resp.headers.get('content-type', 'N/A')}")
                print(f"    Content-Length: {len(resp.content):,} bytes")
                
                if resp.status_code == 200:
                    print(f"    ✅ SUCCESS!")
                    # Show first 200 chars if text
                    if 'text' in resp.headers.get('content-type', ''):
                        preview = resp.text[:200].replace('\n', ' ')
                        print(f"    Preview: {preview}...")
            except Exception as exc:
                print(f"    ❌ Error: {exc}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_urls())
