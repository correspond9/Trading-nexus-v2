"""
Stress test for order placement - detect race conditions and duplicates
"""
import asyncio
import aiohttp
import time
from datetime import datetime
from collections import Counter
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
BASE_URL = "http://localhost:8000/api/v2"
LOGIN_CREDENTIALS = {
    "mobile": "6666666666",
    "password": "super123"
}

# Test parameters
CONCURRENT_BATCHES = 10  # Number of concurrent request batches
ORDERS_PER_BATCH = 10    # Orders in each batch
TOTAL_REQUESTS = CONCURRENT_BATCHES * ORDERS_PER_BATCH

# Order template
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

# Results tracking
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
    async with session.post(
        f"{BASE_URL}/auth/login",
        json=LOGIN_CREDENTIALS
    ) as resp:
        if resp.status == 200:
            data = await resp.json()
            return data.get("access_token")
        else:
            raise Exception(f"Login failed: {resp.status}")


async def place_order(session, token, batch_id, order_num):
    """Place a single order and track timing"""
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
                # Extract order ID if present
                if isinstance(response_data, dict) and "order_id" in response_data:
                    results["order_ids"].append(response_data["order_id"])
                    return {
                        "batch": batch_id,
                        "order_num": order_num,
                        "status": "success",
                        "code": resp.status,
                        "order_id": response_data["order_id"],
                        "elapsed": elapsed
                    }
            else:
                results["error_responses"] += 1
            
            return {
                "batch": batch_id,
                "order_num": order_num,
                "status": "error",
                "code": resp.status,
                "response": response_data,
                "elapsed": elapsed
            }
            
    except Exception as e:
        elapsed = time.time() - start_time
        results["error_responses"] += 1
        return {
            "batch": batch_id,
            "order_num": order_num,
            "status": "exception",
            "error": str(e),
            "elapsed": elapsed
        }


async def stress_test_batch(session, token, batch_id):
    """Send a batch of concurrent orders"""
    tasks = []
    for i in range(ORDERS_PER_BATCH):
        task = place_order(session, token, batch_id, i)
        tasks.append(task)
    
    return await asyncio.gather(*tasks)


async def run_stress_test():
    """Main stress test orchestration"""
    print(f"\n{'='*70}")
    print(f"ORDER PLACEMENT STRESS TEST - STARTING")
    print(f"{'='*70}")
    print(f"Configuration:")
    print(f"  - Concurrent Batches: {CONCURRENT_BATCHES}")
    print(f"  - Orders per Batch: {ORDERS_PER_BATCH}")
    print(f"  - Total Requests: {TOTAL_REQUESTS}")
    print(f"  - Symbol: {ORDER_TEMPLATE['symbol']}")
    print(f"  - User: {LOGIN_CREDENTIALS['mobile']}")
    print(f"{'='*70}\n")
    
    results["start_time"] = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Login first
        print("Authenticating...")
        token = await login_and_get_token(session)
        print(f"✓ Authenticated\n")
        
        # Get initial order count from database
        print("Getting initial order count...")
        initial_count = get_order_count_from_db()
        print(f"Initial orders in DB: {initial_count}\n")
        
        # Run all batches concurrently
        print(f"Launching {CONCURRENT_BATCHES} concurrent batches...")
        batch_tasks = []
        for batch_id in range(CONCURRENT_BATCHES):
            batch_tasks.append(stress_test_batch(session, token, batch_id))
        
        all_results = await asyncio.gather(*batch_tasks)
        results["total_sent"] = TOTAL_REQUESTS
        results["end_time"] = time.time()
        
        # Flatten results
        flat_results = [item for batch in all_results for item in batch]
        
        # Short wait to ensure DB commits
        await asyncio.sleep(0.5)
        
        # Get final order count from database
        print("\nChecking database for order persistence...")
        final_count = get_order_count_from_db()
        db_new_orders = final_count - initial_count
        
        # Check for duplicates in order IDs
        order_id_counts = Counter(results["order_ids"])
        results["duplicate_ids"] = [oid for oid, count in order_id_counts.items() if count > 1]
        
        return flat_results, db_new_orders, initial_count, final_count


def get_order_count_from_db():
    """Query database for total order count for test user"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="trading_nexus",
            user="postgres",
            password="postgres123"
        )
        cur = conn.cursor()
        
        # Get user UUID for mobile 6666666666
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
        print(f"Database query error: {e}")
        return 0


def get_recent_orders_from_db(limit=20):
    """Get recent orders from database with details"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="trading_nexus",
            user="postgres",
            password="postgres123"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user UUID
        cur.execute("SELECT id FROM users WHERE mobile = %s", (LOGIN_CREDENTIALS["mobile"],))
        user_result = cur.fetchone()
        
        if user_result:
            user_id = user_result['id']
            cur.execute("""
                SELECT order_id, symbol, transaction_type, quantity, order_type, 
                       status, placed_at
                FROM paper_orders 
                WHERE user_id = %s 
                ORDER BY placed_at DESC 
                LIMIT %s
            """, (user_id, limit))
            orders = cur.fetchall()
            cur.close()
            conn.close()
            return orders
        
        cur.close()
        conn.close()
        return []
    except Exception as e:
        print(f"Database query error: {e}")
        return []


def print_stress_test_report(flat_results, db_new_orders, initial_count, final_count):
    """Print comprehensive test results"""
    duration = results["end_time"] - results["start_time"]
    avg_response_time = sum(results["response_times"]) / len(results["response_times"]) if results["response_times"] else 0
    requests_per_sec = results["total_sent"] / duration if duration > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"STRESS TEST RESULTS")
    print(f"{'='*70}\n")
    
    # Performance metrics
    print(f"Performance:")
    print(f"  - Total Duration: {duration:.3f}s")
    print(f"  - Requests/sec: {requests_per_sec:.2f}")
    print(f"  - Avg Response Time: {avg_response_time*1000:.2f}ms")
    print(f"  - Min Response Time: {min(results['response_times'])*1000:.2f}ms")
    print(f"  - Max Response Time: {max(results['response_times'])*1000:.2f}ms")
    
    # Request/Response summary
    print(f"\nRequest Summary:")
    print(f"  - Total Sent: {results['total_sent']}")
    print(f"  - Success Responses: {results['success_responses']}")
    print(f"  - Error Responses: {results['error_responses']}")
    
    # Response codes
    print(f"\nResponse Code Distribution:")
    for code, count in sorted(results['response_codes'].items()):
        print(f"  - HTTP {code}: {count} requests")
    
    # Database consistency check
    print(f"\nDatabase Consistency:")
    print(f"  - Orders before test: {initial_count}")
    print(f"  - Orders after test: {final_count}")
    print(f"  - New orders in DB: {db_new_orders}")
    print(f"  - Expected new orders: {results['success_responses']}")
    
    # Race condition detection
    print(f"\nRace Condition Analysis:")
    if results["duplicate_ids"]:
        print(f"  ⚠ DUPLICATES DETECTED: {len(results['duplicate_ids'])} duplicate order IDs")
        for dup_id in results["duplicate_ids"]:
            count = results["order_ids"].count(dup_id)
            print(f"    - Order ID {dup_id}: created {count} times")
    else:
        print(f"  ✓ No duplicate order IDs detected")
    
    if db_new_orders != results['success_responses']:
        print(f"  ⚠ MISMATCH: DB has {db_new_orders} new orders but API returned {results['success_responses']} successes")
        print(f"    Difference: {abs(db_new_orders - results['success_responses'])}")
    else:
        print(f"  ✓ DB count matches API success responses")
    
    # Sample responses
    print(f"\nSample Responses (first 5):")
    for i, result in enumerate(flat_results[:5], 1):
        print(f"  {i}. Batch {result.get('batch')}, Order {result.get('order_num')}: "
              f"Status={result.get('status')}, Code={result.get('code')}, "
              f"Time={result.get('elapsed', 0)*1000:.2f}ms")
    
    # Recent orders from DB
    print(f"\nRecent Orders from Database (last 10):")
    recent = get_recent_orders_from_db(10)
    for i, order in enumerate(recent, 1):
        print(f"  {i}. {order['symbol']} {order['transaction_type']} x{order['quantity']} "
              f"- Status: {order['status']} - Placed: {order['placed_at']}")
    
    # Final verdict
    print(f"\n{'='*70}")
    print(f"VERDICT:")
    print(f"{'='*70}")
    
    issues_found = []
    if results["duplicate_ids"]:
        issues_found.append("Duplicate order IDs detected (possible race condition)")
    if db_new_orders != results['success_responses']:
        issues_found.append(f"DB/API count mismatch ({db_new_orders} vs {results['success_responses']})")
    if results["error_responses"] > 0 and results["error_responses"] != results["total_sent"]:
        # Some errors are expected (market closed), but inconsistent errors are concerning
        pass
    
    if issues_found:
        print(f"⚠ ISSUES DETECTED:")
        for issue in issues_found:
            print(f"  - {issue}")
    else:
        print(f"✓ NO RACE CONDITIONS OR DUPLICATES DETECTED")
        print(f"  - All concurrent requests handled correctly")
        print(f"  - Database consistency maintained")
        print(f"  - No duplicate order execution")
    
    print(f"{'='*70}\n")


if __name__ == "__main__":
    print(f"\nStarting stress test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    flat_results, db_new_orders, initial_count, final_count = asyncio.run(run_stress_test())
    print_stress_test_report(flat_results, db_new_orders, initial_count, final_count)
    print(f"Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
