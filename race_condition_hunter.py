"""
RACE CONDITION HUNTER
Fire massive concurrent requests with zero delay to force race conditions
"""
import asyncio
import aiohttp
import time
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

BASE_URL = "http://localhost:8000/api/v2"
CREDENTIALS = {"mobile": "6666666666", "password": "super123"}

# Ultra-aggressive parameters
SIMULTANEOUS_REQUESTS = 100  # All fire at exact same instant

ORDER = {
    "symbol": "Emami Paper Mills",
    "exchange_segment": "NSE_EQ",
    "transaction_type": "BUY",
    "quantity": 1,
    "order_type": "MARKET",
    "product_type": "MIS",
    "price": 0,
    "trigger_price": 0,
    "disclosed_quantity": 0,
    "validity": "DAY"
}


async def login(session):
    async with session.post(f"{BASE_URL}/auth/login", json=CREDENTIALS) as resp:
        if resp.status == 200:
            return (await resp.json())["access_token"]
        raise Exception(f"Login failed: {resp.status}")


async def fire_order(session, token, req_id):
    """Fire single order request"""
    headers = {"Authorization": f"Bearer {token}"}
    start = time.perf_counter()
    
    try:
        async with session.post(
            f"{BASE_URL}/trading/orders",
            json=ORDER,
            headers=headers
        ) as resp:
            elapsed = time.perf_counter() - start
            status = resp.status
            data = await resp.json()
            
            return {
                "req_id": req_id,
                "status": status,
                "elapsed_ms": elapsed * 1000,
                "response": data
            }
    except Exception as e:
        return {
            "req_id": req_id,
            "error": str(e)
        }


async def simultaneous_barrage(token, count):
    """Fire all requests at the exact same instant"""
    print(f"\nPreparing {count} simultaneous requests...")
    
    # Create session with connection pooling
    connector = aiohttp.TCPConnector(limit=200, limit_per_host=200)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # Create all tasks upfront
        tasks = [fire_order(session, token, i) for i in range(count)]
        
        print(f"FIRING ALL {count} REQUESTS NOW...")
        start = time.perf_counter()
        
        # Fire everything at once
        results = await asyncio.gather(*tasks)
        
        elapsed = time.perf_counter() - start
        print(f"✓ All {count} requests completed in {elapsed:.4f}s")
        
        return results, elapsed


def check_database_integrity():
    """Deep check for race conditions in database"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="trading_nexus",
            user="postgres", password="postgres123"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user ID
        cur.execute("SELECT id FROM users WHERE mobile = %s", (CREDENTIALS["mobile"],))
        user_id = cur.fetchone()["id"]
        
        # Count recent orders
        cur.execute("""
            SELECT COUNT(*) as total
            FROM paper_orders 
            WHERE user_id = %s 
              AND placed_at > NOW() - INTERVAL '2 minutes'
        """, (user_id,))
        total = cur.fetchone()["total"]
        
        # Check for duplicates
        cur.execute("""
            SELECT order_id, COUNT(*) as dup_count
            FROM paper_orders 
            WHERE user_id = %s 
              AND placed_at > NOW() - INTERVAL '2 minutes'
            GROUP BY order_id 
            HAVING COUNT(*) > 1
        """, (user_id,))
        duplicates = cur.fetchall()
        
        # Get timing distribution
        cur.execute("""
            SELECT 
                DATE_TRUNC('millisecond', placed_at) as ms_bucket,
                COUNT(*) as orders_in_ms
            FROM paper_orders 
            WHERE user_id = %s 
              AND placed_at > NOW() - INTERVAL '2 minutes'
            GROUP BY ms_bucket
            ORDER BY orders_in_ms DESC
            LIMIT 5
        """, (user_id,))
        timing_dist = cur.fetchall()
        
        # Check for identical timestamps (exact collisions)
        cur.execute("""
            SELECT placed_at, COUNT(*) as collision_count
            FROM paper_orders 
            WHERE user_id = %s 
              AND placed_at > NOW() - INTERVAL '2 minutes'
            GROUP BY placed_at
            HAVING COUNT(*) > 1
            ORDER BY collision_count DESC
        """, (user_id,))
        collisions = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            "total_orders": total,
            "duplicates": duplicates,
            "timing_distribution": timing_dist,
            "timestamp_collisions": collisions
        }
        
    except Exception as e:
        print(f"DB check error: {e}")
        return None


async def run_race_condition_hunt():
    """Main test runner"""
    print("\n" + "="*70)
    print("RACE CONDITION HUNTER - EXTREME CONCURRENT LOAD TEST")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  - Simultaneous Requests: {SIMULTANEOUS_REQUESTS}")
    print(f"  - Symbol: {ORDER['symbol']}")
    print(f"  - Strategy: Fire all at exact same instant")
    print("="*70)
    
    # Login once
    async with aiohttp.ClientSession() as session:
        print("\nAuthenticating...")
        token = await login(session)
        print("✓ Token obtained")
    
    # Wait a moment
    await asyncio.sleep(0.5)
    
    # Get initial state
    print("\nGetting initial DB state...")
    initial_check = check_database_integrity()
    initial_count = initial_check["total_orders"] if initial_check else 0
    print(f"Initial orders: {initial_count}")
    
    # Fire the barrage
    results, elapsed = await simultaneous_barrage(token, SIMULTANEOUS_REQUESTS)
    
    # Wait for DB commits
    print("\nWaiting for database commits...")
    await asyncio.sleep(2)
    
    # Check final state
    print("Analyzing database integrity...")
    final_check = check_database_integrity()
    
    return initial_count, results, elapsed, final_check


def print_race_report(initial_count, results, elapsed, final_check):
    """Print race condition analysis"""
    print("\n" + "="*70)
    print("RACE CONDITION ANALYSIS REPORT")
    print("="*70)
    
    # Response analysis
    status_counts = {}
    for r in results:
        status = r.get("status", "error")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print(f"\nRequest Results:")
    print(f"  - Total Requests: {len(results)}")
    for status, count in sorted(status_counts.items()):
        print(f"  - Status {status}: {count}")
    
    response_times = [r["elapsed_ms"] for r in results if "elapsed_ms" in r]
    if response_times:
        print(f"\nResponse Timing:")
        print(f"  - Avg: {sum(response_times)/len(response_times):.2f}ms")
        print(f"  - Min: {min(response_times):.2f}ms")
        print(f"  - Max: {max(response_times):.2f}ms")
        print(f"  - Spread: {max(response_times) - min(response_times):.2f}ms")
    
    # Database analysis
    if final_check:
        new_orders = final_check["total_orders"] - initial_count
        
        print(f"\nDatabase Results:")
        print(f"  - Orders Before: {initial_count}")
        print(f"  - Orders After: {final_check['total_orders']}")
        print(f"  - New Orders: {new_orders}")
        print(f"  - Expected: {SIMULTANEOUS_REQUESTS}")
        
        # Critical checks
        print(f"\n" + "="*70)
        print("CRITICAL RACE CONDITION CHECKS")
        print("="*70)
        
        issues = []
        
        # Check 1: Duplicates
        if final_check["duplicates"]:
            print(f"\n⚠⚠⚠ DUPLICATE ORDER IDs DETECTED ⚠⚠⚠")
            for dup in final_check["duplicates"]:
                print(f"  Order {dup['order_id']}: {dup['dup_count']} copies")
            issues.append("Duplicate order IDs")
        else:
            print(f"\n✓ CHECK 1: NO DUPLICATE ORDER IDs")
            print(f"  All {new_orders} orders have unique identifiers")
        
        # Check 2: Count consistency
        if new_orders == SIMULTANEOUS_REQUESTS:
            print(f"\n✓ CHECK 2: PERFECT COUNT CONSISTENCY")
            print(f"  {SIMULTANEOUS_REQUESTS} requests = {new_orders} persisted orders")
        else:
            print(f"\n⚠ CHECK 2: COUNT MISMATCH")
            print(f"  Expected {SIMULTANEOUS_REQUESTS}, got {new_orders}")
            print(f"  Difference: {abs(new_orders - SIMULTANEOUS_REQUESTS)}")
            issues.append(f"Count mismatch ({new_orders} vs {SIMULTANEOUS_REQUESTS})")
        
        # Check 3: Timestamp collisions
        if final_check["timestamp_collisions"]:
            print(f"\n📊 CHECK 3: TIMESTAMP COLLISION ANALYSIS")
            print(f"  Found {len(final_check['timestamp_collisions'])} microsecond collisions:")
            for idx, col in enumerate(final_check["timestamp_collisions"][:5], 1):
                print(f"    {idx}. {col['placed_at']}: {col['collision_count']} orders")
            print(f"\n  ✓ Collisions are NORMAL for concurrent requests")
            print(f"    What matters: each order still got unique ID")
        else:
            print(f"\n✓ CHECK 3: NO TIMESTAMP COLLISIONS")
            print(f"  All orders have unique microsecond timestamps")
        
        # Check 4: Timing distribution
        if final_check["timing_distribution"]:
            print(f"\n📊 CHECK 4: TIMING DISTRIBUTION")
            print(f"  Top millisecond buckets:")
            for idx, bucket in enumerate(final_check["timing_distribution"], 1):
                print(f"    {idx}. {bucket['ms_bucket']}: {bucket['orders_in_ms']} orders")
        
        # Final verdict
        print(f"\n" + "="*70)
        print("FINAL VERDICT")
        print("="*70)
        
        if not issues and new_orders == SIMULTANEOUS_REQUESTS:
            print(f"\n✅✅✅ RACE CONDITION TEST: PASSED ✅✅✅")
            print(f"\n  System successfully handled {SIMULTANEOUS_REQUESTS} simultaneous requests")
            print(f"  - Zero duplicate order executions")
            print(f"  - Perfect database consistency") 
            print(f"  - All orders received unique IDs")
            print(f"  - No data corruption detected")
            print(f"\n  ✓ System is RACE CONDITION RESISTANT")
        else:
            print(f"\n❌ RACE CONDITION TEST: FAILED ❌")
            print(f"\n  Issues detected:")
            for issue in issues:
                print(f"  - {issue}")
    
    print(f"\n" + "="*70 + "\n")


if __name__ == "__main__":
    print(f"\n🔍 Starting Race Condition Hunt at {datetime.now().strftime('%H:%M:%S')}")
    
    initial_count, results, elapsed, final_check = asyncio.run(run_race_condition_hunt())
    
    print_race_report(initial_count, results, elapsed, final_check)
    
    print(f"🏁 Test completed at {datetime.now().strftime('%H:%M:%S')}\n")
