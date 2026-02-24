-- ============================================================================
-- MANUAL DELETE ALL POSITIONS FOR USER 9326890165
-- Run this SQL script directly in PostgreSQL when API endpoint fails
-- ============================================================================

-- Step 1: Get user information
SELECT id, mobile, name, role, created_at 
FROM users 
WHERE mobile = '9326890165';

-- Step 2: Count current records (before deletion)
SELECT 
    (SELECT COUNT(*) FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS positions,
    (SELECT COUNT(*) FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS orders,
    (SELECT COUNT(*) FROM paper_trades WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS trades,
    (SELECT COUNT(*) FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS ledger_entries;

-- Step 3: View positions before deletion (optional)
SELECT 
    pp.id,
    pp.symbol,
    pp.quantity,
    pp.avg_price,
    pp.status,
    pp.opened_at,
    pp.position_type
FROM paper_positions pp
WHERE pp.user_id = (SELECT id FROM users WHERE mobile = '9326890165')
ORDER BY pp.opened_at DESC;

-- ============================================================================
-- DELETION COMMANDS (Execute in correct order)
-- ============================================================================

-- IMPORTANT: Delete in this order to respect foreign key constraints:
-- 1. ledger_entries
-- 2. paper_trades  
-- 3. paper_orders
-- 4. paper_positions

-- ⚠️  UNCOMMENT BELOW WHEN READY TO DELETE ⚠️

-- 1. Delete ledger entries
-- DELETE FROM ledger_entries 
-- WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');

-- 2. Delete paper trades
-- DELETE FROM paper_trades 
-- WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');

-- 3. Delete paper orders
-- DELETE FROM paper_orders 
-- WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');

-- 4. Delete paper positions
-- DELETE FROM paper_positions 
-- WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');

-- ============================================================================
-- VERIFICATION (After deletion)
-- ============================================================================

-- Count remaining records
SELECT 
    (SELECT COUNT(*) FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS remaining_positions,
    (SELECT COUNT(*) FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS remaining_orders,
    (SELECT COUNT(*) FROM paper_trades WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS remaining_trades,
    (SELECT COUNT(*) FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS remaining_ledger;

-- ============================================================================
-- ALTERNATIVE: Delete specific position by ID
-- ============================================================================

-- First, list positions to get the ID:
-- SELECT id, symbol, quantity, avg_price, status, opened_at 
-- FROM paper_positions 
-- WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');

-- Then delete specific position (replace <position_id> with actual UUID):
-- DELETE FROM ledger_entries WHERE position_id = '<position_id>';
-- DELETE FROM paper_trades WHERE position_id = '<position_id>';
-- DELETE FROM paper_orders WHERE position_id = '<position_id>';
-- DELETE FROM paper_positions WHERE id = '<position_id>';

-- ============================================================================
-- QUICK EXECUTION COMMAND (via SSH)
-- ============================================================================

-- ssh root@72.62.228.112
-- docker exec -it <postgres_container> psql -U trading_user -d trading_terminal
-- \i /path/to/this/file.sql

-- OR run directly:
-- docker exec -i <postgres_container> psql -U trading_user -d trading_terminal < manual_delete_positions.sql
