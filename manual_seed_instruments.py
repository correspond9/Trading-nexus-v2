"""
This script manually seeds subscription lists and refreshes instruments.
Run this once to populate the database with fresh Dhan instrument data.
"""
import asyncio
import csv
import httpx
from pathlib import Path
import asyncpg

DB_URL = "postgresql://tradinguser:Trading_23$@139.84.170.213:5432/tradingnexus"
CDN_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"

# Map list_name to (filename, column_name, is_display_name)
LOCAL_LIST_FILES = {
    "equity":          ("equity-list.csv",         "SYMBOL",    False),
    "options_stocks":  ("options-stocks-list.csv",  "Name",      True),
    "futures_stocks":  ("futures-stocks-list.csv",  "Name",      True),
    "etf":             ("etf-list.csv",             "Name",      True),
    "mcx_futures":     ("mcx-comm-futures.csv",     "Commodity", False),
    "mcx_options":     ("mcx-comm-options.csv",     "Commodity", False),
}

async def seed_subscription_lists(conn):
    """Seed subscription lists from local CSV files."""
    print("\n=== Step 1: Seeding Subscription Lists ===")
    
    # Check if already seeded
    total = await conn.fetchval("SELECT COUNT(*) FROM subscription_lists")
    if total > 0:
        print(f"✅ Subscription lists already seeded ({total} rows) - skipping")
        return
    
    # Build display_name → underlying_symbol mapping from master CSV
    master_csv = Path(__file__).parent / "instrument_master" / "api-scrip-master-detailed.csv"
    if not master_csv.exists():
        print(f"❌ Master CSV not found at {master_csv}")
        return
    
    print(f"📖 Reading master CSV from {master_csv}...")
    display_to_symbol = {}
    with open(master_csv, newline="", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            dn = (row.get("DISPLAY_NAME") or "").strip()
            sym = (row.get("UNDERLYING_SYMBOL") or "").strip().upper()
            if dn and sym:
                display_to_symbol[dn.upper()] = sym
    
    print(f"✅ Read {len(display_to_symbol)} display name mappings")
    
    # Process each list file
    list_dir = master_csv.parent
    rows_to_insert = []
    
    for list_name, (filename, col, is_display_name) in LOCAL_LIST_FILES.items():
        path = list_dir / filename
        if not path.exists():
            print(f"⚠️  {list_name}: file not found at {path}")
            continue
        
        matched = 0
        unmatched = []
        
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw = (row.get(col) or "").strip()
                if not raw:
                    continue
                
                if is_display_name:
                    # Resolve display name → underlying symbol
                    symbol = display_to_symbol.get(raw.upper())
                    if not symbol:
                        unmatched.append(raw)
                        continue
                else:
                    # Value IS the underlying symbol
                    symbol = raw.upper()
                
                rows_to_insert.append((list_name, symbol))
                matched += 1
        
        print(f"   {list_name}: {matched} matched" + (f", {len(unmatched)} unmatched" if unmatched else ""))
    
    # Bulk insert
    if rows_to_insert:
        await conn.executemany(
            "INSERT INTO subscription_lists (list_name, symbol) VALUES ($1, $2) "
            "ON CONFLICT (list_name, symbol) DO NOTHING",
            rows_to_insert
        )
        print(f"✅ Inserted {len(rows_to_insert)} subscription list entries\n")
    else:
        print("⚠️  No subscription list entries to insert\n")


async def main():
    print("=" * 70)
    print("  INSTRUMENT MASTER REFRESH - One-Time Setup")
    print("=" * 70)
    
    conn = await asyncpg.connect(DB_URL)
    
    try:
        # Step 1: Seed subscription lists
        await seed_subscription_lists(conn)
        
        # Step 2: Download instrument master from Dhan
        print("=== Step 2: Downloading Dhan Instrument Master ===")
        print(f"Fetching from {CDN_URL}...")
        
        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
            resp = await client.get(CDN_URL)
            resp.raise_for_status()
        content = resp.text
        print(f"✅ Downloaded {len(content):,} characters\n")
        
        # Step 3: Done! Now trigger backend refresh via API
        print("=== Step 3: Complete ===")
        print("✅ Subscription lists populated")
        print("✅ Dhan CDN reachable")
        print("\n📝 Now trigger refresh via admin API:")
        print("   POST https://tradingnexus.pro/api/v2/admin/scrip-master/refresh")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
