#!/usr/bin/env python3
"""
Fix broken Traefik labels in docker-compose.yaml
Uses sed to remove malformed http-0 router configurations
"""

import subprocess
import sys
import time

VPS_IP = "72.62.228.112"
SSH_USER = "root"
APP_UUID = "p488ok8g8swo4ockks040ccg"
APP_DIR = f"/data/coolify/applications/{APP_UUID}"
COMPOSE_FILE = f"{APP_DIR}/docker-compose.yaml"

def run_ssh_no_password(cmd):
    """Run SSH command without password prompt"""
    try:
        # Use ssh with BatchMode to avoid password prompt
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", 
             f"{SSH_USER}@{VPS_IP}", cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        print(f"SSH Error: {e}")
        return "", str(e), -1

def main():
    print("\n" + "="*70)
    print("FIXING BROKEN TRAEFIK LABELS")
    print("="*70 + "\n")
    
    # Step 1: Show current broken configuration
    print("Step 1: Identifying broken rules...")
    cmd = f'grep -c "traefik.http.routers.http-0" {COMPOSE_FILE}'
    stdout, stderr, code = run_ssh_no_password(cmd)
    if stdout.strip().isdigit() and int(stdout.strip()) > 0:
        count = stdout.strip()
        print(f"  ❌ Found {count} broken http-0 router labels")
        
        # Show examples
        cmd = f'grep -n "traefik.http.routers.http-0" {COMPOSE_FILE} | head -3'
        stdout, stderr, _ = run_ssh_no_password(cmd)
        for line in stdout.split('\n'):
            if line.strip():
                print(f"     {line}")
    else:
        print("  ✅ No broken http-0 routers found")
        return 0
    
    print("\n" + "-"*70)
    print("Step 2: Creating backup and applying fixes...")
    
    # Create a multi-line sed script that removes all problematic labels
    fix_commands = f"""
cd {APP_DIR}

# Backup
cp {COMPOSE_FILE} {COMPOSE_FILE}.backup.$(date +%s)
echo "Backup created"

# Remove broken http-0 router labels
sed -i '/- traefik.http.routers.http-0-/d' {COMPOSE_FILE}
echo "Removed traefik.http.routers.http-0-* labels"

# Remove broken middleware labels
sed -i '/traefik.http.middlewares.http-0-/d' {COMPOSE_FILE}
echo "Removed traefik.http.middlewares.http-0-* labels"

# Remove caddy labels (also broken)
sed -i "/- 'caddy_/d" {COMPOSE_FILE}
sed -i '/- caddy_/d' {COMPOSE_FILE}
echo "Removed caddy labels"

# Remove caddy_ingress_network  
sed -i '/caddy_ingress_network/d' {COMPOSE_FILE}
echo "Removed caddy_ingress_network"

echo "Configuration fixed!"
"""
    
    cmd = f'bash -c "{fix_commands}"'
    stdout, stderr, code = run_ssh_no_password(cmd)
    
    print(stdout)
    if stderr and "Backup" not in stderr:
        print(f"  Stderr: {stderr[:200]}")
    
    print("\n" + "-"*70)
    print("Step 3: Verifying fixes...")
    
    cmd = f'grep -c "traefik.http.routers.http-0" {COMPOSE_FILE} 2>/dev/null || echo "0"'
    stdout, stderr, _ = run_ssh_no_password(cmd)
    remaining = int(stdout.strip()) if stdout.strip().isdigit() else 0
    
    if remaining == 0:
        print(f"  ✅ All broken labels removed")
    else:
        print(f"  ⚠️  Still found {remaining} problematic labels")
    
    # Show remaining Traefik labels
    cmd = f'grep "traefik.http.routers\\." {COMPOSE_FILE} | head -5'
    stdout, stderr, _ = run_ssh_no_password(cmd)
    if stdout:
        print("\n  Remaining Traefik routers:")
        for line in stdout.split('\n'):
            if line.strip():
                # Extract just the rule
                if 'rule=' in line:
                    rule = line.split('rule=')[1] if 'rule=' in line else line
                    print(f"    {rule[:80]}")
    
    print("\n" + "-"*70)
    print("Step 4: Restarting application...")
    
    restart_cmd = f"""
cd {APP_DIR}
docker compose down --remove-orphans
sleep 3
docker compose up -d
sleep 15
echo "Application restarted"
"""
    
    cmd = f'bash -c "{restart_cmd}"'
    stdout, stderr, _ = run_ssh_no_password(cmd)
    print(stdout)
    
    print("\n" + "-"*70)
    print("Step 5: Testing endpoints...")
    
    test_cmd = """
echo "Testing /health:"
curl -s http://127.0.0.1:8000/health | python3 -m json.tool 2>/dev/null | head -5

echo ""
echo "Testing /api/v2/health:"
curl -s http://127.0.0.1:8000/api/v2/health | python3 -m json.tool 2>/dev/null | head -5

echo ""
echo "Testing /api/v2/instruments/search:"
RESULT=$(curl -s -w "\\n%{http_code}" http://127.0.0.1:8000/api/v2/instruments/search?q=RELIANCE&limit=3)
HTTP_CODE=$(echo "$RESULT" | tail -1)
BODY=$(echo "$RESULT" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ HTTP 200 - SUCCESS!"
  echo "Response: $(echo "$BODY" | python3 -m json.tool 2>/dev/null | head -10)"
else
  echo "❌ HTTP $HTTP_CODE"
  echo "Response: $BODY" | head -c 200
fi
"""
    
    cmd = f'bash -c "{test_cmd}"'
    stdout, stderr, _ = run_ssh_no_password(cmd)
    print(stdout)
    
    if stderr and "curl" not in stderr:
        print(f"\n  Stderr: {stderr[:300]}")
    
    print("\n" + "="*70)
    print("TRAEFIK FIX COMPLETE")
    print("="*70 + "\n")
    
    print("If /api/v2/instruments/search still returns 404:")
    print("  1. Restart Traefik: docker restart coolify-proxy")
    print("  2. Check Traefik logs: docker logs coolify-proxy | tail -50")
    print("  3. Verify containers on coolify network: docker network inspect coolify")
    print("")
    print("If 200: ✅ The fix worked! Test from your local machine:")
    print("  curl http://api.tradingnexus.pro/api/v2/instruments/search?q=RELIANCE")
    print("")

if __name__ == "__main__":
    main()
