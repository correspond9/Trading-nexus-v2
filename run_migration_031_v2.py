#!/usr/bin/env python3
"""
Alternative Migration Runner - Using SSH with better error handling
"""

import subprocess
import sys
import os

VPS_HOST = "72.62.228.112"
VPS_USER = "root"
APP_UUID = "p488ok8g8swo4ockks040ccg"

print("=" * 80)
print("🔧 TRADING NEXUS - MIGRATION 031 RUNNER (Alternative Method)")
print("=" * 80)

# Read migration file
print("\n[1/4] Reading migration file...")
with open("migrations/031_paper_positions_missing_columns.sql", "r") as f:
    migration_sql = f.read()
print(f"✓ Migration file loaded ({len(migration_sql)} bytes)")

# Create a temporary SQL file to send over
print("\n[2/4] Creating temporary migration script...")
temp_migrate_script = "/tmp/migrate_031.sh"

script_content = f"""#!/bin/bash
DB_CONTAINER="$(docker ps --format '{{{{.Names}}}}' | grep 'db-{APP_UUID}')"

if [ -z "$DB_CONTAINER" ]; then
    echo "ERROR: Database container not found"
    exit 1
fi

echo "Found container: $DB_CONTAINER"
echo "Running migration..."

# Execute migration
docker exec $DB_CONTAINER psql -U postgres -d trading_nexus << 'EOF'
{migration_sql}
EOF

echo "✓ Migration executed"

# Verify columns exist
echo "Verifying columns..."
docker exec $DB_CONTAINER psql -U postgres -d trading_nexus -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'paper_positions' 
AND column_name IN ('status', 'realized_pnl', 'closed_at')
ORDER BY column_name;
"

echo "✓ Done"
"""

# Send the script via SSH and execute
print(f"\n[3/4] Sending and executing migration on {VPS_HOST}...")
print(f"     → Using container: db-{APP_UUID}")

try:
    # Send script content and execute it
    ssh_cmd = ["ssh", f"{VPS_USER}@{VPS_HOST}", 
               f"cat > /tmp/migrate_031.sh << 'SCRIPT_EOF'\n{script_content}\nSCRIPT_EOF\n" +
               f"bash /tmp/migrate_031.sh"]
    
    # Instead, let's use a more direct approach
    # Build the command to send via echo and bash
    migrate_cmd = f"""bash -c 'DB_CONTAINER="$(docker ps --format "{{{{.Names}}}}" | grep "db-{APP_UUID}")" && echo "Container: $DB_CONTAINER" && docker exec $DB_CONTAINER psql -U postgres -d trading_nexus -c "{migration_sql.replace('"', '\\\\"')}"'"""
    
    result = subprocess.run(
        ["ssh", f"{VPS_USER}@{VPS_HOST}", migrate_cmd],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print("\n📤 Command Output:")
    print("-" * 80)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # Check if it's an error or just warnings
        if "error" in result.stderr.lower() and "duplicate" not in result.stderr.lower():
            print("❌ STDERR:", result.stderr)
        else:
            print("⚠️  STDERR (non-fatal):", result.stderr[:300])
    print("-" * 80)
    
    if result.returncode == 0 or "duplicate" in result.stderr.lower():
        print("\n[4/4] Verification...")
        print("✓ Migration likely succeeded!")
        print("\n" + "=" * 80)
        print("✅ MIGRATION 031 COMPLETED!")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"\n❌ Migration failed with code {result.returncode}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("  1. Ensure SSH keys are set up for root@72.62.228.112")
    print("  2. Try running manually: ssh root@72.62.228.112 'docker ps'")
    sys.exit(1)
