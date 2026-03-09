import paramiko
import time

# SSH connection details
hostname = "72.62.228.112"
username = "root"
key_path = r"C:\Users\Sufyan Ansari\.ssh\id_ed25519"

# Database details
db_container = "db-x8gg0og8440wkgc8ow0ococs-064710036566"
db_name = "trading_nexus"
db_user = "postgres"

mobile = "9326890165"

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Load private key
    private_key = paramiko.Ed25519Key.from_private_key_file(key_path)
    
    # Connect
    print(f"Connecting to {hostname}...")
    ssh.connect(hostname, username=username, pkey=private_key, timeout=10)
    print("✅ Connected successfully\n")
    
    # SQL query to get complete user report
    sql_query = f"""
DO $$
DECLARE
    v_user_id INTEGER;
    v_mobile VARCHAR;
    v_created_at TIMESTAMP;
    v_is_active BOOLEAN;
    v_margin_allotted NUMERIC;
    v_account_created TIMESTAMP;
    v_total_used_margin NUMERIC := 0;
    v_available_margin NUMERIC;
    pos_record RECORD;
    order_record RECORD;
    trade_record RECORD;
    v_total_realized NUMERIC := 0;
    v_total_invested NUMERIC := 0;
    v_total_positions_value NUMERIC := 0;
    v_unrealized_pnl NUMERIC;
    v_pending_count INTEGER := 0;
    v_completed_count INTEGER := 0;
    v_cancelled_count INTEGER := 0;
BEGIN
    -- Get user info
    SELECT u.id, u.mobile, u.created_at, u.is_active
    INTO v_user_id, v_mobile, v_created_at, v_is_active
    FROM users u
    WHERE u.mobile = '{mobile}';
    
    IF v_user_id IS NULL THEN
        RAISE NOTICE '❌ No user found with mobile {mobile}';
        RETURN;
    END IF;
    
    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'COMPLETE USER REPORT FOR MOBILE: %', '{mobile}';
    RAISE NOTICE '================================================================================';
    RAISE NOTICE '';
    RAISE NOTICE '1. USER BASIC INFORMATION';
    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'User ID: %', v_user_id;
    RAISE NOTICE 'Mobile: %', v_mobile;
    RAISE NOTICE 'Created At: %', v_created_at;
    RAISE NOTICE 'Active: %', CASE WHEN v_is_active THEN '✅ Yes' ELSE '❌ No' END;
    
    -- Get margin info
    SELECT pa.margin_allotted, pa.created_at
    INTO v_margin_allotted, v_account_created
    FROM paper_accounts pa
    WHERE pa.user_id = v_user_id;
    
    RAISE NOTICE '';
    RAISE NOTICE '2. MARGIN INFORMATION';
    RAISE NOTICE '================================================================================';
    IF v_margin_allotted IS NULL THEN
        RAISE NOTICE '❌ No paper account found';
        v_margin_allotted := 0;
    ELSE
        RAISE NOTICE 'Margin Allotted: ₹%', v_margin_allotted;
        RAISE NOTICE 'Account Created: %', v_account_created;
    END IF;
    
    -- Calculate used margin from positions
    FOR pos_record IN 
        SELECT 
            pp.symbol,
            pp.exchange_segment,
            pp.quantity,
            pp.product_type,
            pp.average_price,
            pp.last_price,
            pp.instrument_token,
            calculate_position_margin(
                pp.instrument_token,
                pp.symbol,
                pp.exchange_segment::text,
                pp.quantity,
                pp.product_type::text
            ) as margin_used
        FROM paper_positions pp
        WHERE pp.user_id = v_user_id AND pp.status = 'OPEN'
    LOOP
        v_total_used_margin := v_total_used_margin + COALESCE(pos_record.margin_used, 0);
        v_total_invested := v_total_invested + (COALESCE(pos_record.average_price, 0) * pos_record.quantity);
        v_total_positions_value := v_total_positions_value + (COALESCE(pos_record.last_price, 0) * pos_record.quantity);
    END LOOP;
    
    v_available_margin := v_margin_allotted - v_total_used_margin;
    v_unrealized_pnl := v_total_positions_value - v_total_invested;
    
    RAISE NOTICE 'Used Margin: ₹%', v_total_used_margin;
    RAISE NOTICE 'Available Margin: ₹%', v_available_margin;
    RAISE NOTICE 'Usage Percentage: %%', CASE WHEN v_margin_allotted > 0 THEN ROUND((v_total_used_margin/v_margin_allotted*100)::numeric, 2) ELSE 0 END;
    
    -- Open positions
    RAISE NOTICE '';
    RAISE NOTICE '3. OPEN POSITIONS';
    RAISE NOTICE '================================================================================';
    FOR pos_record IN 
        SELECT 
            pp.symbol,
            pp.exchange_segment,
            pp.quantity,
            pp.product_type,
            pp.average_price,
            pp.last_price,
            calculate_position_margin(
                pp.instrument_token,
                pp.symbol,
                pp.exchange_segment::text,
                pp.quantity,
                pp.product_type::text
            ) as margin_used,
            (COALESCE(pp.last_price, 0) - COALESCE(pp.average_price, 0)) * pp.quantity as pnl
        FROM paper_positions pp
        WHERE pp.user_id = v_user_id AND pp.status = 'OPEN'
        ORDER BY pp.created_at DESC
    LOOP
        RAISE NOTICE 'Symbol: % | Exchange: % | Qty: % | Avg Price: ₹% | Last Price: ₹% | P&L: ₹% | Margin: ₹%',
            pos_record.symbol,
            pos_record.exchange_segment,
            pos_record.quantity,
            ROUND(pos_record.average_price::numeric, 2),
            ROUND(pos_record.last_price::numeric, 2),
            ROUND(pos_record.pnl::numeric, 2),
            ROUND(pos_record.margin_used::numeric, 2);
    END LOOP;
    
    -- Closed positions
    RAISE NOTICE '';
    RAISE NOTICE '4. CLOSED POSITIONS (Last 10)';
    RAISE NOTICE '================================================================================';
    FOR pos_record IN 
        SELECT 
            pp.symbol,
            pp.exchange_segment,
            pp.quantity,
            pp.average_price,
            pp.realized_pnl,
            pp.closed_at
        FROM paper_positions pp
        WHERE pp.user_id = v_user_id AND pp.status = 'CLOSED'
        ORDER BY pp.closed_at DESC
        LIMIT 10
    LOOP
        v_total_realized := v_total_realized + COALESCE(pos_record.realized_pnl, 0);
        RAISE NOTICE 'Symbol: % | Qty: % | Avg Price: ₹% | Realized P&L: ₹% | Closed: %',
            pos_record.symbol,
            pos_record.quantity,
            ROUND(pos_record.average_price::numeric, 2),
            ROUND(pos_record.realized_pnl::numeric, 2),
            pos_record.closed_at;
    END LOOP;
    
    -- Count orders by status
    SELECT 
        COUNT(*) FILTER (WHERE status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')),
        COUNT(*) FILTER (WHERE status IN ('FILLED', 'EXECUTED')),
        COUNT(*) FILTER (WHERE status IN ('CANCELLED', 'REJECTED'))
    INTO v_pending_count, v_completed_count, v_cancelled_count
    FROM paper_orders
    WHERE user_id = v_user_id;
    
    RAISE NOTICE '';
    RAISE NOTICE '5. ALL ORDERS';
    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'Total Orders: %', v_pending_count + v_completed_count + v_cancelled_count;
    RAISE NOTICE '  Pending/Open: %', v_pending_count;
    RAISE NOTICE '  Completed: %', v_completed_count;
    RAISE NOTICE '  Cancelled/Rejected: %', v_cancelled_count;
    
    -- Pending orders
    IF v_pending_count > 0 THEN
        RAISE NOTICE '';
        RAISE NOTICE '--- PENDING/OPEN ORDERS ---';
        FOR order_record IN 
            SELECT 
                po.id, po.symbol, po.side, po.order_type, po.quantity,
                po.price, po.status, po.filled_quantity, po.created_at
            FROM paper_orders po
            WHERE po.user_id = v_user_id 
              AND po.status IN ('PENDING', 'OPEN', 'PARTIALLY_FILLED')
            ORDER BY po.created_at DESC
        LOOP
            RAISE NOTICE 'Order #% | % - % | % @ ₹% | Status: % | Filled: %/% | Created: %',
                order_record.id,
                order_record.symbol,
                order_record.side,
                order_record.order_type,
                COALESCE(order_record.price, 0),
                order_record.status,
                order_record.filled_quantity,
                order_record.quantity,
                order_record.created_at;
        END LOOP;
    END IF;
    
    -- Recent completed orders
    RAISE NOTICE '';
    RAISE NOTICE '--- COMPLETED ORDERS (Last 10) ---';
    FOR order_record IN 
        SELECT 
            po.id, po.symbol, po.side, po.order_type, po.quantity,
            po.price, po.average_price, po.filled_quantity, po.created_at
        FROM paper_orders po
        WHERE po.user_id = v_user_id 
          AND po.status IN ('FILLED', 'EXECUTED')
        ORDER BY po.created_at DESC
        LIMIT 10
    LOOP
        RAISE NOTICE 'Order #% | % - % | Qty: % | Avg Price: ₹% | Created: %',
            order_record.id,
            order_record.symbol,
            order_record.side,
            order_record.quantity,
            ROUND(COALESCE(order_record.average_price, 0)::numeric, 2),
            order_record.created_at;
    END LOOP;
    
    -- Recent trades
    RAISE NOTICE '';
    RAISE NOTICE '6. RECENT TRADES (Last 20)';
    RAISE NOTICE '================================================================================';
    FOR trade_record IN 
        SELECT 
            pt.id, pt.order_id, po.symbol, po.side,
            pt.quantity, pt.price, pt.executed_at
        FROM paper_trades pt
        JOIN paper_orders po ON pt.order_id = po.id
        WHERE po.user_id = v_user_id
        ORDER BY pt.executed_at DESC
        LIMIT 20
    LOOP
        RAISE NOTICE 'Trade #% (Order #%) | % - % | Qty: % @ ₹% | Executed: %',
            trade_record.id,
            trade_record.order_id,
            trade_record.symbol,
            trade_record.side,
            trade_record.quantity,
            ROUND(trade_record.price::numeric, 2),
            trade_record.executed_at;
    END LOOP;
    
    -- Portfolio summary
    SELECT COALESCE(SUM(realized_pnl), 0)
    INTO v_total_realized
    FROM paper_positions
    WHERE user_id = v_user_id AND status = 'CLOSED';
    
    RAISE NOTICE '';
    RAISE NOTICE '7. PORTFOLIO SUMMARY';
    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'Number of Open Positions: %', (SELECT COUNT(*) FROM paper_positions WHERE user_id = v_user_id AND status = 'OPEN');
    RAISE NOTICE 'Total Invested Value: ₹%', ROUND(v_total_invested::numeric, 2);
    RAISE NOTICE 'Current Portfolio Value: ₹%', ROUND(v_total_positions_value::numeric, 2);
    RAISE NOTICE 'Unrealized P&L: ₹% (%%)', 
        ROUND(v_unrealized_pnl::numeric, 2),
        CASE WHEN v_total_invested > 0 THEN ROUND((v_unrealized_pnl/v_total_invested*100)::numeric, 2) ELSE 0 END;
    RAISE NOTICE 'Total Realized P&L (All Time): ₹%', ROUND(v_total_realized::numeric, 2);
    RAISE NOTICE 'Total P&L: ₹%', ROUND((v_unrealized_pnl + v_total_realized)::numeric, 2);
    
    RAISE NOTICE '';
    RAISE NOTICE '================================================================================';
    RAISE NOTICE 'END OF REPORT';
    RAISE NOTICE '================================================================================';
END $$;
"""
    
    # Execute via docker
    docker_cmd = f'docker exec {db_container} psql -U {db_user} -d {db_name} -c "{sql_query}"'
    
    print("Generating report...\n")
    stdin, stdout, stderr = ssh.exec_command(docker_cmd, get_pty=True)
    
    # Read output
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    # Print output
    if output:
        # Extract NOTICE messages
        for line in output.split('\n'):
            if 'NOTICE:' in line:
                print(line.replace('NOTICE:', '').strip())
            elif line.strip() and not line.startswith('DO') and 'psql' not in line.lower():
                print(line)
    
    if error and 'NOTICE' not in error:
        print(f"\n⚠️ Errors:\n{error}")
        
finally:
    ssh.close()
    print("\n✅ Connection closed")
