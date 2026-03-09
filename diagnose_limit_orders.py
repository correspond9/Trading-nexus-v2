"""
CRITICAL DIAGNOSIS: Why Limit Orders Are Not Executing
========================================================
Check all potential failure points in the limit order execution chain.
"""
import requests
import json
from decimal import Decimal

# Production API
API_BASE = "https://api.tradingnexus.pro/api/v2"

print("="*80)
print("LIMIT ORDER EXECUTION - CRITICAL DIAGNOSIS")
print("="*80)

# ──────────────────────────────────────────────────────────────────────────────
# 1. CHECK MOCK MODE (PAPER TRADING MODE)
# ──────────────────────────────────────────────────────────────────────────────
print("\n[1] Checking PAPER MODE / MOCK MODE Setting...")
print("    (This controls whether limit orders are processed)")
try:
    resp = requests.get(f"{API_BASE}/admin/mode", timeout=10)
    if resp.status_code == 200:
        mode_data = resp.json()
        paper_mode = mode_data.get("paper_mode")
        
        print(f"\n    📊 Current Mode: {'PAPER (Mock)' if paper_mode else 'LIVE (Real)'}")
        print(f"    📊 paper_mode flag: {paper_mode}")
        
        if not paper_mode:
            print("\n    ❌ CRITICAL ISSUE FOUND!")
            print("    ❌ Paper mode is DISABLED (_mock_mode = False)")
            print("    ❌ This means the tick processor will NOT process limit orders!")
            print("    ❌ on_tick() returns immediately without checking fillable orders")
            print("\n    ✅ SOLUTION:")
            print("       Call: POST /api/v2/admin/mode with {\"paper_mode\": true}")
            print("       This will enable _mock_mode and allow limit order execution")
        else:
            print("\n    ✅ Paper mode is ENABLED - limit orders should be processed")
    else:
        print(f"    ❌ API Error: {resp.status_code}")
        print(f"    Response: {resp.text[:200]}")
except Exception as e:
    print(f"    ❌ Connection Error: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# 2. CHECK PENDING ORDERS IN SYSTEM
# ──────────────────────────────────────────────────────────────────────────────
print("\n[2] Checking Pending LIMIT Orders...")
try:
    # This would need authentication - showing the query structure
    print("    Query: SELECT * FROM paper_orders WHERE status='PENDING' AND order_type='LIMIT'")
    print("    (Requires database access or authenticated API call)")
except Exception as e:
    print(f"    Error: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# 3. CHECK MARKET DATA FOR SUNDARAM (instrument_token = 18931)
# ──────────────────────────────────────────────────────────────────────────────
print("\n[3] Checking Market Data for SUNDARAM (token 18931)...")
try:
    # This endpoint may require authentication
    print("    Checking if market data exists with bid/ask depth...")
    print("    Query: SELECT ltp, bid_depth, ask_depth FROM market_data WHERE instrument_token=18931")
    print("    (Requires database access)")
    print("\n    Key Points:")
    print("    - If bid_depth/ask_depth are NULL or empty arrays, orders won't fill")
    print("    - If ltp is NULL, fallback price won't work")
    print("    - NSE_EQ instruments may have limited depth data in paper trading")
except Exception as e:
    print(f"    Error: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. CHECK TICK PROCESSOR STATUS
# ──────────────────────────────────────────────────────────────────────────────
print("\n[4] Checking Tick Processor Status...")
print("    The tick processor must be RUNNING for limit orders to execute")
print("    It calls execution_engine.on_tick() for each market data update")
print("\n    Verification points:")
print("    - Is STARTUP_START_STREAMS=true in environment?")
print("    - Is tick_processor.start() being called at startup?")
print("    - Are WebSocket connections active to receive market data?")

# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY OF FINDINGS
# ──────────────────────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("DIAGNOSIS SUMMARY")
print("="*80)
print("""
ROOT CAUSE ANALYSIS:
--------------------
Limit orders fail to execute when ANY of these conditions are true:

1. ❌ _mock_mode = False (most common issue)
   Located in: app/execution_simulator/execution_engine.py
   Line 130-132: if not _mock_mode: return
   
   This completely disables tick processing for limit orders.
   Can be toggled via: POST /api/v2/admin/mode {"paper_mode": true/false}

2. ❌ Tick processor not running
   Started by: app/main.py -> tick_processor.start()
   Controlled by: STARTUP_START_STREAMS environment variable
   
3. ❌ No market data or empty depth
   - bid_depth/ask_depth must have non-empty arrays
   - For NSE_EQ equity stocks, depth may be limited
   - WebSocket must be connected and receiving ticks

4. ❌ Order not properly queued
   - Orders must be in order_queue_manager._book structure
   - Check via: order_queue_manager.pending_count()

IMMEDIATE FIX:
--------------
If paper_mode is False, enable it:

   curl -X POST https://api.tradingnexus.pro/api/v2/admin/mode \\
        -H "Content-Type: application/json" \\
        -d '{"paper_mode": true}'

This will set _mock_mode = True and enable limit order execution.
""")

print("="*80)
print("NEXT STEPS")
print("="*80)
print("""
1. Run this diagnostic on the production server to check actual state
2. If paper_mode is False, enable it via the API endpoint
3. Verify tick processor is running (check logs for "Tick processor started")
4. Check market_data table for SUNDARAM to ensure depth exists
5. Monitor order execution after enabling paper_mode
""")
