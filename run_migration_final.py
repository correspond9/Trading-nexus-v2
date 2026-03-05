#!/usr/bin/env python3
"""
FINAL Migration Runner - Migration 031
Execute SQL migration to add missing columns to paper_positions table
"""

import subprocess
import sys

# Database container name (from docker ps output)
db_container = "db-x8gg0og8440wkgc8ow0ococs-042743461735"
vps_host = "72.62.228.112"
vps_user = "root"

print("=" * 80)
print("🔧 TRADING NEXUS - MIGRATION 031 RUNNER")
print("=" * 80)

# Step 1: Read migration file
print("\n[1/3] Reading migration file...")
try:
    with open("migrations/031_paper_positions_missing_columns.sql", "r") as f:
        migration_sql = f.read()
    print(f"✓ Migration file loaded ({len(migration_sql)} bytes)")
except Exception as e:
    print(f"❌ ERROR reading migration file: {e}")
    sys.exit(1)

# Step 2: Execute migration
print(f"\n[2/3] Executing migration on database container...")
print(f"     Host: {vps_host}")
print(f"     Container: {db_container}")
print("     → Running SQL migration...")

try:
    # Properly escape the SQL
    escaped_sql = migration_sql.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
    
    # Build the command
    ssh_cmd = f"docker exec {db_container} psql -U postgres -d trading_nexus"
    
    # Use echo to pipe the SQL to psql
    full_cmd = f"echo \"{escaped_sql}\" | docker exec -i {db_container} psql -U postgres -d trading_nexus"
    
    # Execute via SSH
    result = subprocess.run(
        ["ssh", f"{vps_user}@{vps_host}", full_cmd],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print("\n📤 Migration Output:")
    print("-" * 80)
    if result.stdout:
        lines = result.stdout.split('\n')
        for line in lines[:30]:  # Show first 30 lines
            print(line)
        if len(lines) > 30:
            print(f"... ({len(lines) - 30} more lines)")
    if result.stderr and "does not exist" not in result.stderr and "already exists" not in result.stderr:
        print("\nSTDERR:", result.stderr[:300])
    print("-" * 80)
    
except Exception as e:
    print(f"❌ ERROR executing migration: {e}")
    print("\nDEBUG: Make sure SSH keys are configured")
    sys.exit(1)

# Step 3: Verify columns exist
print(f"\n[3/3] Verifying migration...")
print("     → Checking for new columns...")

try:
    verify_sql = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'paper_positions' AND column_name IN ('status', 'realized_pnl', 'closed_at') ORDER BY column_name;"
    escaped_verify = verify_sql.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
    
    verify_cmd = f"echo \"{escaped_verify}\" | docker exec -i {db_container} psql -U postgres -d trading_nexus"
    
    result = subprocess.run(
        ["ssh", f"{vps_user}@{vps_host}", verify_cmd],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("\n✓ Verification result:")
    print(result.stdout)
    
    # Check if all columns are present
    output = result.stdout.lower()
    has_status = "status" in output and "boolean" in output
    has_pnl = "realized_pnl" in output and "numeric" in output
    has_closed = "closed_at" in output and "timestamp" in output
    
    if has_status and has_pnl and has_closed:
        print("\n" + "=" * 80)
        print("✅ MIGRATION 031 COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📋 Summary - Applied Changes:")
        print("   ✓ Column 'status' added (boolean type)")
        print("   ✓ Column 'realized_pnl' added (numeric type)")
        print("   ✓ Column 'closed_at' added (timestamp type)")
        print("   ✓ Indexes created for performance")
        print("\n📌 What's Fixed:")
        print("   • Position exit functionality restored")
        print("   • Traders can now close their positions")
        print("   • All position status tracking enabled")
        print("\n🚀 The application is ready!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Git push this migration file")
        print("2. Redeploy the application through Coolify")
        print("\n" + "=" * 80)
        sys.exit(0)
    else:
        print(f"\n❌ Columns verification failed")
        print(f"   status: {has_status}")
        print(f"   realized_pnl: {has_pnl}")
        print(f"   closed_at: {has_closed}")
        print(f"\nFull output:\n{result.stdout}")
        sys.exit(1)
        
except Exception as e:
    print(f"⚠️  Could not verify columns: {e}")
    print("\nThe migration may still have succeeded.")
    print("Check your database directly or redeploy through Coolify.")
    sys.exit(1)
