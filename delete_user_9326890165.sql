-- Count before deletion
SELECT 
    (SELECT COUNT(*) FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS positions,
    (SELECT COUNT(*) FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS orders,
    (SELECT COUNT(*) FROM paper_trades WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS trades,
    (SELECT COUNT(*) FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS ledger;

-- Delete in correct order
DELETE FROM ledger_entries WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');
DELETE FROM paper_trades WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');
DELETE FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');
DELETE FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165');

-- Verify deletion
SELECT 
    (SELECT COUNT(*) FROM paper_positions WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS remaining_positions,
    (SELECT COUNT(*) FROM paper_orders WHERE user_id = (SELECT id FROM users WHERE mobile = '9326890165')) AS remaining_orders;
