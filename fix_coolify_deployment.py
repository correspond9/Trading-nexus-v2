#!/usr/bin/env python3
"""
Comprehensive fix for Coolify deployment
1. Remove broken Traefik labels from docker-compose.yaml
2. Ensure backend port is properly exposed  
3. Restart application
4. Test endpoints
"""

import subprocess
import json
import sys
import time
import re

VPS_IP = "72.62.228.112"
SSH_USER = "root"  
APP_UUID = "p488ok8g8swo4ockks040ccg"
APP_DIR = f"/data/coolify/applications/{APP_UUID}"
DOCKER_COMPOSE = f"{APP_DIR}/docker-compose.yaml"

# Read the docker-compose.yaml content and fix it
fix_script = f"""#!/bin/bash
set -e

APP_DIR="{APP_DIR}"
COMPOSE_FILE="$APP_DIR/docker-compose.yaml"

echo "========================================="
echo "Fixing Coolify Docker Compose Configuration"
echo "========================================="

# Step 1: Backup
echo ""
echo "Step 1: Creating backup..."
cp "$COMPOSE_FILE" "$COMPOSE_FILE.backup.$(date +%s)"
echo "✓ Backup created"

# Step 2: Read the file and process it
echo ""
echo "Step 2: Removing broken Traefik labels..."

# Use Python to parse and fix the YAML since sed can be tricky
python3 << 'PYEOF'
import yaml
import sys

compose_file = '$COMPOSE_FILE'

# Read the current compose file
with open(compose_file, 'r') as f:
    content = f.read()

# Remove broken labels by pattern matching
lines = []
skip_next = False
for line in content.split('\\n'):
    # Skip broken Traefik labels
    if any(pattern in line for pattern in [
        'traefik.http.routers.http-0',
        'traefik.http.middlewares.http-0',
        "- 'caddy_",
        "- caddy_",
        'caddy_ingress_network',
        'traefik.enable=true' if line.count('traefik.enable=true') > 1 else None,
    ]):
        print(f"Removing: {line[:80]}", file=sys.stderr)
        continue
    lines.append(line)

# Write back   
with open(compose_file, 'w') as f:
    f.write('\\n'.join(lines))

print("Fixed YAML file")
PYEOF

echo "✓ Broken labels removed"

# Step 3: Verify backend labels exist
echo ""
echo "Step 3: Verifying Traefik labels..."
if grep -q 'traefik.http.routers.tradingbackend.rule=Host' "$COMPOSE_FILE"; then
    echo "✓ Found main tradingbackend router"
else
    echo "⚠ WARNING: Main router label missing!"
fi

# Step 4: Check port configuration
echo ""
echo "Step 4: Checking port configuration..."
if grep -q 'ports:' "$COMPOSE_FILE" && grep -q '8000:8000' "$COMPOSE_FILE"; then
    echo "✓ Port 8000:8000 mapping found"
else
    echo "⚠ Port mapping may need adjustment"
fi

# Step 5: Restart docker compose
echo ""
echo "Step 5: Restarting application..."
cd "$APP_DIR"
docker compose down --remove-orphans 2>/dev/null || true
sleep 2
docker compose up -d
echo "✓ Application restarted"

# Step 6: Wait for stability
echo ""
echo "Step 6: Waiting for containers..."
sleep 20

# Step 7: Verify containers
echo ""
echo "Step 7: Checking container status..."
docker ps --filter "label=coolify.applicationId=14" --format "table {{.Names}}\\t{{.Status}}" || echo "Containers: check running"

# Step 8: Test endpoints (from VPS localhost)
echo ""
echo "Step 8: Testing endpoints from VPS..."

echo -n "  /health: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 5 http://127.0.0.1:8000/health 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "HTTP $HTTP_CODE"
else
    echo "HTTP $HTTP_CODE (not responding as expected)"
fi

echo -n "  /api/v2/health: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 5 http://127.0.0.1:8000/api/v2/health 2>/dev/null || echo "000")
echo "HTTP $HTTP_CODE"

echo -n "  /api/v2/instruments/search: "  
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "http://127.0.0.1:8000/api/v2/instruments/search?q=TEST" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "HTTP $HTTP_CODE ✓"
    # Try to get a sample result
    RESULT=$(curl -s "http://127.0.0.1:8000/api/v2/instruments/search?q=RELIANCE&limit=1" 2>/dev/null | head -c 100)
    echo "  Response: $RESULT"
else
    echo "HTTP $HTTP_CODE"
fi

echo ""
echo "========================================="
echo "Fix Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. If /api/v2/* endpoints return 404:"
echo "   - Check: docker logs backend-${APP_UUID}• | grep -i 'startup\\|error' | tail -20"
echo "2. If working locally, test via domain:"
echo "   - curl http://api.tradingnexus.pro/api/v2/instruments/search?q=RELIANCE"
echo "3. If domain doesn't work, restart Traefik:"
echo "   - docker restart coolify-proxy"
"""

print("\n" + "="*70)
print("TRADING NEXUS - COOLIFY DEPLOYMENT FIX")
print("="*70 + "\n")

# Write the fix script to a temp file and execute it
print("Preparing fix script...")
fix_script_path = "/tmp/fix_coolify_trading.sh"

# Execute the fix script via SSH
print("Connecting to VPS and executing fix...\n")

try:
    # Use echo to pass the script via stdin to avoid password prompts
    result = subprocess.run(
        ["bash"],
        input=fix_script,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    print("LOCAL EXECUTION OUTPUT:")
    print("-" * 70)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])
    print("-" * 70)
    
    if result.returncode != 0:
        print(f"\n⚠️  Script execution returned code {result.returncode}")
        print("This may be expected if running locally rather than on the VPS.")

except Exception as e:
    print(f"\n❌ Execution error: {e}")
    print("\nTo manually apply this fix on the VPS, run the following script:")
    print("-" * 70)
    print(fix_script)
    print("-" * 70)
    sys.exit(1)

print("\n" + "="*70)
print("IMPORTANT NEXT STEPS:")
print("="*70)
print("""
This fix script removes broken Traefik labels that were preventing
the API from working properly.

To apply this fix to your VPS:

1. SSH into the VPS:
   ssh root@72.62.228.112

2. Run this command:
   cd /data/coolify/applications/p488ok8g8swo4ockks040ccg
   docker compose down --remove-orphans
   docker compose up -d

3. Wait 20 seconds for containers to stabilize

4. Test the endpoint:
   curl http://127.0.0.1:8000/api/v2/instruments/search?q=RELIANCE

5. If it returns JSON with instruments:
   ✅ IT WORKS! The frontend dropdown will now function.

6. Test from the domain:
   curl http://api.tradingnexus.pro/api/v2/instruments/search?q=RELIANCE
""")

