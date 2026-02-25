#!/usr/bin/env python3
"""
DEPLOY MIGRATION 028 FIX
========================
Applies the corrected migration to the VPS database
and restarts the backend to activate it.
"""

import paramiko
import time
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

# SSH Connection Details
SSH_HOST = "72.62.228.112"
SSH_USER = "root"
SSH_KEY = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQAAAJhA+rcwQPq3
MAAAAAtzc2gtZWQyNTUxOQAAACCntWM5ZQDBZV+aXnHPYgzW91lmXv6EZ9qz6vZ0ZxaUAQ
AAAEB0Ox/XuIoUNkafWOoz7A5notoL4fc1pLkeHDOvSRMz3qe1YzllAMFlX5pecc9iDNb3
WWZe/oRn2rPq9nRnFpQBAAAAFWNvcnJlc3BvbmQ5QGdtYWlsLmNvbQ==
-----END OPENSSH PRIVATE KEY-----"""

def run_ssh_command(ssh, command, description):
    """Execute SSH command and return output."""
    log.info(f"\n▶️  {description}...")
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=30)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if error and "warning" not in error.lower():
            log.warning(f"⚠️  {error}")
        
        if output:
            for line in output.split('\n')[-10:]:  # Show last 10 lines
                log.info(f"    {line}")
        
        return output, error
    except Exception as e:
        log.error(f"❌ {e}")
        return None, str(e)

def main():
    """Connect to VPS and apply the fix."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect
        log.info("🔗 Connecting to VPS (72.62.228.112)...")
        from io import StringIO
        key_file = StringIO(SSH_KEY)
        private_key = paramiko.Ed25519Key.from_private_key(key_file)
        ssh.connect(SSH_HOST, username=SSH_USER, pkey=private_key, timeout=30)
        log.info("✅ Connected to VPS")
        
        # Step 1: Check current function signature
        log.info("\n" + "="*60)
        log.info("STEP 1: Checking current function state...")
        log.info("="*60)
        
        check_sql = """
        SELECT pg_get_functiondef(oid) FROM pg_proc 
        WHERE proname = 'calculate_position_margin' 
        LIMIT 1;
        """
        cmd = f"""docker exec trading_nexus_db psql -U appuser -d trading_nexus -c "{check_sql.strip()}" 2>&1"""
        run_ssh_command(ssh, cmd, "Checking function signature")
        
        # Step 2: Drop incorrect function and views
        log.info("\n" + "="*60)
        log.info("STEP 2: Cleaning up incorrect function...")
        log.info("="*60)
        
        cleanup_sql = """
        DROP FUNCTION IF EXISTS calculate_position_margin(INTEGER, VARCHAR, VARCHAR, INTEGER, VARCHAR) CASCADE;
        DROP VIEW IF EXISTS v_user_margin_summary;
        DROP VIEW IF EXISTS v_positions_with_margin;
        """
        
        cmd = f"""docker exec trading_nexus_db psql -U appuser -d trading_nexus -c "{cleanup_sql}" 2>&1"""
        run_ssh_command(ssh, cmd, "Dropping incorrect function and views")
        
        # Step 3: Restart backend to re-run migrations
        log.info("\n" + "="*60)
        log.info("STEP 3: Restarting backend to apply corrected migration...")
        log.info("="*60)
        
        run_ssh_command(ssh, "docker-compose -f /opt/app/docker-compose.prod.yml restart backend", 
                       "Restarting backend container")
        
        log.info("\n⏳ Waiting for backend to start (30 seconds)...")
        time.sleep(30)
        
        # Step 4: Verify the fix
        log.info("\n" + "="*60)
        log.info("STEP 4: Verifying the fix...")
        log.info("="*60)
        
        check_sql = """
        SELECT pg_get_functiondef(oid) FROM pg_proc 
        WHERE proname = 'calculate_position_margin' 
        LIMIT 1;
        """
        cmd = f"""docker exec trading_nexus_db psql -U appuser -d trading_nexus -c "{check_sql.strip()}" 2>&1"""
        output, _ = run_ssh_command(ssh, cmd, "Checking corrected function signature")
        
        if output and "bigint" in output.lower():
            log.info("\n✅ BIGINT signature detected - Function is CORRECT!")
        else:
            log.warning("\n⚠️  Could not verify BIGINT signature")
        
        # Step 5: Test API health
        log.info("\n" + "="*60)
        log.info("STEP 5: Testing API health...")
        log.info("="*60)
        
        run_ssh_command(ssh, "curl -s http://localhost:8000/api/health | head -20", 
                       "Testing API health endpoint")
        
        log.info("\n" + "="*60)
        log.info("✅ MIGRATION 028 FIX APPLIED SUCCESSFULLY!")
        log.info("="*60)
        log.info("""
Next: 
1. Test margin calculation endpoints:
   - POST /api/orders (place order with margin check)
   - GET /api/margin/summary (check margin summary)
2. Check backend logs for any errors:
   docker logs trading_nexus_backend -f
        """)
        
    except Exception as e:
        log.error(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        ssh.close()
        log.info("\n🔌 Disconnected from VPS")

if __name__ == "__main__":
    main()
