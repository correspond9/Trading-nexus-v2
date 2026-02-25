# 🔴 MIGRATION 028 FIX - Function Signature Mismatch

## Problem Identified

**Error:** 
```
asyncpg.exceptions.UndefinedFunctionError: function calculate_position_margin(bigint, character varying, character varying, integer, character varying) does not exist
```

**Root Cause:**
The `calculate_position_margin()` function in migration 028 was defined with an `INTEGER` parameter for `instrument_token`, but the schema defines `instrument_token` as `BIGINT` throughout the entire codebase.

```sql
-- ❌ WRONG (Migration 028 - as originally written)
CREATE OR REPLACE FUNCTION calculate_position_margin(
    p_instrument_token INTEGER,  -- ← MISMATCH! Schema uses BIGINT
    p_symbol VARCHAR,
    p_exchange_segment VARCHAR,
    p_quantity INTEGER,
    p_product_type VARCHAR
)

-- ✅ CORRECT (Fixed)
CREATE OR REPLACE FUNCTION calculate_position_margin(
    p_instrument_token BIGINT,  -- ← Matches schema!
    p_symbol VARCHAR,
    p_exchange_segment VARCHAR,
    p_quantity INTEGER,
    p_product_type VARCHAR
)
```

## Impact

- **When Called:** Any endpoint that tries to calculate margins fails
  - POST `/api/orders` (order placement)
  - GET `/api/margin/summary` (margin queries)
  - GET `/api/baskets/*/positions` (position queries)

- **Why It Fails:** PostgreSQL treats `INTEGER` (4 bytes / int4) and `BIGINT` (8 bytes / int8) as completely different types. The function signature doesn't match the call signature.

## Files Modified

### 1. Migration File
**File:** [migrations/028_fix_margin_calculation_consistency.sql](migrations/028_fix_margin_calculation_consistency.sql)

**Changes:**
- Line 24: `p_instrument_token INTEGER` → `p_instrument_token BIGINT`
- Line 191: `COMMENT ON FUNCTION...INTEGER...` → `COMMENT ON FUNCTION...BIGINT...`

### 2. Hotfix Script
**File:** [hotfix_migration_028.py](hotfix_migration_028.py)

Automates the fix process:
1. Drops the incorrect function (INTEGER signature)
2. Drops dependent views
3. Re-runs the corrected migration (BIGINT signature)

## How to Apply the Fix

### Option A: Automatic (Recommended)
```bash
cd /path/to/trading-nexus
python3 hotfix_migration_028.py
```

**Then restart the backend:**
```bash
# If using Docker
docker-compose restart backend

# If using Coolify - redeploy the application
```

### Option B: Manual (If SSH/VPS Access)

1. **Drop the incorrect function:**
```sql
DROP FUNCTION IF EXISTS calculate_position_margin(INTEGER, VARCHAR, VARCHAR, INTEGER, VARCHAR);
DROP VIEW IF EXISTS v_user_margin_summary;
DROP VIEW IF EXISTS v_positions_with_margin;
```

2. **Re-run the corrected migration:**
```bash
# SSH into VPS
ssh -i your_key root@your_vps

# Run migration in the container
docker exec trading_nexus_backend python -m alembic upgrade head
# OR
docker exec trading_nexus_db psql -U appuser -d trading_nexus -f /path/to/migration/028_fix_margin_calculation_consistency.sql
```

### Option C: Via Database UI
If you have a PostgreSQL client (pgAdmin, DBeaver, etc.):

1. Open SQL editor
2. Run:
```sql
-- Drop incorrect function and views
DROP FUNCTION IF EXISTS calculate_position_margin(INTEGER, VARCHAR, VARCHAR, INTEGER, VARCHAR);
DROP VIEW IF EXISTS v_user_margin_summary;
DROP VIEW IF EXISTS v_positions_with_margin;
```

3. Copy the entire corrected migration file content and execute it

## Verification

After applying the fix, verify it worked:

```sql
-- Check function exists with correct signature
SELECT proname, pg_get_functiondef(oid) 
FROM pg_proc 
WHERE proname = 'calculate_position_margin';

-- Should show: calculate_position_margin(bigint, character varying, character varying, integer, character varying)
```

Or via API:
```bash
# Try to place an order or get margin summary
curl -X GET http://localhost:8000/api/margin/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Schema Reference

All `instrument_token` columns in the database are `BIGINT`:

- `instrument_master.instrument_token` - BIGINT PRIMARY KEY
- `market_data.instrument_token` - BIGINT PRIMARY KEY
- `paper_positions.instrument_token` - BIGINT NOT NULL
- `paper_orders.instrument_token` - BIGINT NOT NULL
- `span_margin_cache.instrument_token` - IMPLIED FROM JOINS

This is why the function parameter must be `BIGINT`.

## Prevention

For future migrations with functions:
1. Always check the parameter types match the schema columns they'll receive
2. Use the schema as the source of truth for data types
3. Test function definitions before migrating:
```sql
-- Test the function signature matches column types
SELECT 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'paper_positions' 
  AND column_name LIKE 'instrument%';
```

---

**Status:** ✅ Fixed in migration file  
**Action Required:** Run hotfix script or manual SQL steps above  
**Testing:** Verify with API call after restart
