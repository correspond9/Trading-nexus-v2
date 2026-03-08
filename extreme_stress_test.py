"""
EXTREME stress test - maximum concurrency to find race conditions
"""
import asyncio
import aiohttp
import time
from datetime import datetime
from collections import Counter
import psycopg2

BASE_URL = "http://localhost:8000/api/v2"
LOGIN_CREDENTIALS = {"mobile": "6666666666", "password": "super123"}

# EXTREME test parameters
CONCURRENT_BATCHES = 20   # 20 batches
ORDERS_PER_BATCH = 20     # 20 orders each
TOTAL_REQUESTS = CONCURRENT_BATCHES * ORDERS_PER_BATCH  # 400 total

ORDER_TEMPLATE = {
    "symbol": "Amara Raja Energy & Mobility",
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

results = {
    "total_sent": 0,
    "success_responses": 0,
    "error_responses": 0,
    "response_codes": Counter(),
    "response_times": [],
    "start_time": None,
    "end_time": None,
    "order_ids": [],
    "duplicate_ids": []
}


async def login_and_get_token(session):
    """Login and get JWT token"""
    async with session.post(f"{BASE_URL}/auth/login", json=LOGIN_CREDENTIALS) as resp:
        if resp.status == 200:
            data = await resp.json()
            return data.get("access_token")
        raise Exception(f"Login failed: {resp.status}")


async def place_order(session, token, batch_id, order_num):
    """Place a single order"""
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    
    try:
        async with session.post(
            f"{BASE_URL}/trading/orders",
            json=ORDER_TEMPLATE,
            headers=headers
        ) as resp:
            elapsed = time.time() - start_time
            results["response_times"].append(elapsed)
            results["response_codes"][resp.status] += 1
            
            response_data = await resp.json()
            
            if resp.status in [200, 201]:
                results["success_responses"] += 1
                if isinstance(response_data, dict) and "order_id" in response_data:
                    results["order_ids"].append(response_data["order_id"])
            elif resp.status == 403:
                # Market closed - order likely still created as REJECTED
                results["error_responses"] += 1
            else:
                results["error_responses"] += 1
            
            return {"batch": batch_id, "order": order_num, "status": resp.status, "time": elapsed}
            
    except Exception as e:
        results["error_responses"] += 1
        return {"batch": batch_id, "order": order_num, "error": str(e)}


async def stress_test_batch(session, token, batch_id):
    """Send a batch of concurrent orders"""
    tasks = [place_order(session, token, batch_id, i) for i in range(ORDERS_PER_BATCH)]
    return await asyncio.gather(*tasks)


async def run_extreme_test():
    """Main test orchestration"""
    print(f"\n{'='*70}")
    print(f"EXTREME CONCURRENCY STRESS TEST")
    print(f"{'='*70}")
    print(f"Configuration:")
    print(f"  - Concurrent Batches: {CONCURRENT_BATCHES}")
    print(f"  - Orders per Batch: {ORDERS_PER_BATCH}")
    print(f"  - TOTAL REQUESTS: {TOTAL_REQUESTS}")
    print(f"  - Symbol: {ORDER_TEMPLATE['symbol']}")
    print(f"{'='*70}\n")
    
    results["start_time"] = time.time()
    
    # Get initial DB state
    initial_count = get_order_count_from_db()
    print(f"Initial orders in DB: {initial_count}")
    
    async with aiohttp.ClientSession() as session:
        print("Authenticating...")
        token = await login_and_get_token(session)
        print(f"✓ Authenticated\n")
        
        print(f"LAUNCHING {TOTAL_REQUESTS} CONCURRENT ORDERS...")
        start = time.time()
        
        # Fire all batches at once
        batch_tasks = [stress_test_batch(session, token, i) for i in range(CONCURRENT_BATCHES)]
        all_results = await asyncio.gather(*batch_tasks)
        
        elapsed = time.time() - start
        print(f"✓ All requests completed in {elapsed:.3f}s ({TOTAL_REQUESTS/elapsed:.1f} req/sec)\n")
        
        results["total_sent"] = TOTAL_REQUESTS
        results["end_time"] = time.time()
        
        # Wait for DB commits
        await asyncio.sleep(1)
        
        final_count = get_order_count_from_db()
        db_new_orders = final_count - initial_count
        
        return db_new_orders, initial_count, final_count


def get_order_count_from_db():
    """Query database for total order count"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="trading_nexus",
            user="postgres", password="postgres123"
        )
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE mobile = %s", (LOGIN_CREDENTIALS["mobile"],))
        user_result = cur.fetchone()
        
        if user_result:
            user_id = user_result[0]
            cur.execute("SELECT COUNT(*) FROM paper_orders WHERE user_id = %s", (user_id,))
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            return count
        
        cur.close()
        conn.close()
        return 0
    except Exception as e:
        print(f"DB error: {e}")
        return 0


def check_duplicates():
    """Check for duplicate order_ids in database"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="trading_nexus",
            user="postgres", password="postgres123"
        )
        cur = conn.cursor()
        
        # Get user UUID
        cur.execute("SELECT id FROM users WHERE mobile = %s", (LOGIN_CREDENTIALS["mobile"],))
        user_result = cur.fetchone()
        
        if user_result:
            user_id = user_result[0]
            
            # Check for duplicate order_ids
            cur.execute("""
                SELECT order_id, COUNT(*) as count 
                FROM paper_orders 
                WHERE user_id = %s 
                  AND placed_at > NOW() - INTERVAL '5 minutes'
                GROUP BY order_id 
                HAVING COUNT(*) > 1
            """, (user_id,))
            
            duplicates = cur.fetchall()
            cur.close()
            conn.close()
            
            return duplicates
        
        cur.close()
        conn.close()
        return []
    except Exception as e:
        print(f"DB error checking duplicates: {e}")
        return []


def analyze_timing():
    """Analyze order placement timing from database"""
    try:
        conn = psycopg2.connect(
            host="localhost", port=5432, database="trading_nexus",
            user="postgres", password="postgres123"
        )
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE mobile = %s", (LOGIN_CREDENTIALS["mobile"],))
        user_result = cur.fetchone()
        
        if user_result:
            user_id = user_result[0]
            
            # Get timing statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    MIN(placed_at) as first_order,
                    MAX(placed_at) as last_order,
                    MAX(placed_at) - MIN(placed_at) as time_span
                FROM paper_orders 
                WHERE user_id = %s 
                  AND placed_at > NOW() - INTERVAL '5 minutes'
            """, (user_id,))
            
            timing = cur.fetchone()
            cur.close()
            conn.close()
            
            return timing
        
        cur.close()
        conn.close()
        return None
    except Exception as e:
        print(f"DB error analyzing timing: {e}")
        return None


def print_extreme_report(db_new_orders, initial_count, final_count):
    """Print comprehensive test results"""
    duration = results["end_time"] - results["start_time"]
    avg_response_time = sum(results["response_times"]) / len(results["response_times"]) if results["response_times"] else 0
    
    print(f"\n{'='*70}")
    print(f"EXTREME STRESS TEST RESULTS")
    print(f"{'='*70}\n")
    
    print(f"Performance:")
    print(f"  - Total Duration: {duration:.3f}s")
    print(f"  - Throughput: {results['total_sent']/duration:.2f} req/sec")
    print(f"  - Avg Response Time: {avg_response_time*1000:.2f}ms")
    print(f"  - Min Response Time: {min(results['response_times'])*1000:.2f}ms")
    print(f"  - Max Response Time: {max(results['response_times'])*1000:.2f}ms")
    
    print(f"\nRequest Summary:")
    print(f"  - Total Sent: {results['total_sent']}")
    print(f"  - Error Responses: {results['error_responses']}")
    for code, count in sorted(results['response_codes'].items()):
        print(f"    - HTTP {code}: {count}")
    
    print(f"\nDatabase Results:")
    print(f"  - Orders before: {initial_count}")
    print(f"  - Orders after: {final_count}")
    print(f"  - New orders: {db_new_orders}")
    print(f"  - Expected: {results['total_sent']}")
    
    # Check for duplicates
    duplicates = check_duplicates()
    
    print(f"\n{'='*70}")
    print(f"RACE CONDITION ANALYSIS")
    print(f"{'='*70}")
    
    if duplicates:
        print(f"\n⚠⚠⚠ CRITICAL: DUPLICATE ORDER IDs DETECTED ⚠⚠⚠")
        print(f"Found {len(duplicates)} duplicate order_ids:")
        for order_id, count in duplicates:
            print(f"  - {order_id}: created {count} times")
    else:
        print(f"\n✓ NO DUPLICATE order_ids detected")
        print(f"  All {db_new_orders} orders have unique IDs")
    
    if db_new_orders == results['total_sent']:
        print(f"\n✓ PERFECT CONSISTENCY")
        print(f"  DB count matches request count exactly")
    elif db_new_orders < results['total_sent']:
        print(f"\n⚠ MISSING ORDERS")
        print(f"  {results['total_sent'] - db_new_orders} orders not persisted")
    else:
        print(f"\n⚠ EXTRA ORDERS")
        print(f"  {db_new_orders - results['total_sent']} extra orders in DB")
    
    # Timing analysis
    timing = analyze_timing()
    if timing:
        total, first, last, span = timing
        print(f"\nTiming Analysis:")
        print(f"  - First order: {first}")
        print(f"  - Last order: {last}")
        print(f"  - Time span: {span}")
        print(f"  - Orders created: {total}")
    
    print(f"\n{'='*70}")
    print(f"FINAL VERDICT")
    print(f"{'='*70}")
    
    if not duplicates and db_new_orders == results['total_sent']:
        print(f"\n✓✓✓ PASSED - NO RACE CONDITIONS DETECTED ✓✓✓")
        print(f"\n  - {TOTAL_REQUESTS} concurrent requests handled perfectly")
        print(f"  - Zero duplicate order executions")
        print(f"  - Perfect database consistency")
        print(f"  - System is robust under extreme load")
    else:
        issues = []
        if duplicates:
            issues.append(f"{len(duplicates)} duplicate order IDs")
        if db_new_orders != results['total_sent']:
            issues.append(f"count mismatch ({db_new_orders} vs {results['total_sent']})")
        
        print(f"\n⚠⚠⚠ FAILED - ISSUES DETECTED ⚠⚠⚠")
        for issue in issues:
            print(f"  - {issue}")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    print(f"\nStarting EXTREME stress test at {datetime.now().strftime('%H:%M:%S')}")
    db_new_orders, initial_count, final_count = asyncio.run(run_extreme_test())
    print_extreme_report(db_new_orders, initial_count, final_count)
    print(f"Test completed at {datetime.now().strftime('%H:%M:%S')}\n")
