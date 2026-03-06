#!/bin/bash
DB="db-x8gg0og8440wkgc8ow0ococs-145803824898"
PSQL="docker exec $DB psql -U postgres -d trading_terminal"

echo "=== STEP 1: Check paper_positions table structure ==="
$PSQL -c "\d paper_positions"

echo ""
echo "=== STEP 2: Check paper_trades table (if exists) ==="
$PSQL -c "\d paper_trades" 2>/dev/null || echo "paper_trades table not found"

echo ""
echo "=== STEP 3: Current positions snapshot ==="
$PSQL -c "SELECT position_id, symbol, qty, avg_price, status, realized_pnl, trade_expense, net_pnl, opened_at::date, closed_at::date FROM paper_positions WHERE user_id = '6785692d-8f36-4183-addb-16c96ea95a88' ORDER BY opened_at;"

echo ""
echo "=== STEP 4: Check existing trades for SUNDARAM ==="
$PSQL -c "SELECT * FROM paper_trades WHERE position_id = '2acd403c-aaee-47dc-9bc2-bc9251bbeee4' LIMIT 10;" 2>/dev/null || echo "no paper_trades or no rows"

echo ""
echo "=== STEP 5: User created_at ==="
$PSQL -c "SELECT id, name, mobile, created_at FROM users WHERE id = '6785692d-8f36-4183-addb-16c96ea95a88';"
