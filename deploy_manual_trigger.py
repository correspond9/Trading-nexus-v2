#!/usr/bin/env python3
"""
Trigger Coolify deployment using direct Docker rebuild after git push.
Since API token is invalid, we use Docker directly.
"""

import subprocess
import sys
import time

VPS_IP = "72.62.228.112"
VPS_USER = "root"
APP_DIR = "/data/coolify/applications/x8gg0og8440wkgc8ow0ococs"

def log_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def log_success(msg):
    print(f"✅ {msg}")

def log_error(msg):
    print(f"❌ {msg}")

def log_info(msg):
    print(f"ℹ️  {msg}")

def run_ssh_command(cmd, description):
    """Run command on VPS via SSH"""
    print(f"\n→ {description}...")
    full_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", f"{VPS_USER}@{VPS_IP}", cmd]
    
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        log_error(f"Command timed out: {description}")  
        return 1, "", "timeout"
    except Exception as e:
        log_error(f"SSH failed: {e}")
        return 1, "", str(e)

log_section("TRIGGER COOLIFY REBUILD VIA DOCKER")

print(f"Target: {VPS_IP}")
print(f"Application: {APP_DIR}")

# Step 1: Verify git changes were pushed
log_info("Changes have been pushed to GitHub (verify locally)")
code, out, err = run_ssh_command(
    "cat /data/coolify/applications/x8gg0og8440wkgc8ow0ococs/README.md",
    "Check deployment metadata"
)
if code == 0:
    print(out)
    print()

# Step 2: Check if we can access Coolify logs  
code, out, err = run_ssh_command(
    f"ls -lh {APP_DIR}/logs/ 2>/dev/null | tail -10 || echo 'No logs yet'",
    "Check deployment logs"
)
print(out or "No logs directory")

# Step 3: Attempt to trigger rebuild through Coolify's update mechanism
# Coolify should have a way to register for GitHub webhooks or manually trigger redeploy
log_section("DEPLOYMENT OPTIONS")

print("""
Since the Coolify API token is invalid (401 Unauthorized), here are your options:

OPTION 1 (Recommended): Use Coolify Web Dashboard
  1. Go to http://72.62.228.112:3000
  2. Log in as admin
  3. Find "Trading Nexus V2" application
  4. Click the "Redeploy" or "Deploy" button
  5. Monitor the build progress

OPTION 2: Generate New API Token
  1. Log into Coolify web dashboard: http://72.62.228.112:3000
  2. Go to Settings → API tokens
  3. Create a new API token
  4. Provide token to AI for automated deployment

OPTION 3: Wait for GitHub Webhook (if configured)
  - If Coolify is hooked to listen for push events on GitHub,
    it may auto-trigger in ~5 minutes

OPTION 4: Manual Docker Command
  - If Coolify has source code checked out locally,
    we can rebuild manually via SSH (requires knowing Dockerfile location)

═══════════════════════════════════════════════════════════════════════════════

NEXT STEPS:
1. Log into Coolify dashboard: http:// 72.62.228.112:3000
2. Manually trigger "Deploy" for Trading Nexus V2 application
3. OR: Create a new API token and provide to AI
4. OR: Wait 5 minutes for webhook to trigger auto-deploy

⏱️  Latest changes committed: 87d41b0, 77c9a1f, ede48a3 (pushed to GitHub main)
""")

log_section("DEPLOYMENT CHECKLIST")

print("""
After deployment completes in Coolify:

□ Docker images rebuilt (check timestamp in logs)
□ Backend container running (docker ps should show healthy status)
□ Database migrations executed (check logs)
□ Portal users table created (migration 027)
□ Portal signup endpoints available (/auth/portal/signup, /auth/portal/users)
□ SuperAdmin Portal Signups tab visible
□ https://learn.tradingnexus.pro accessible
□ https://learn.tradingnexus.pro/signup form loads  
□ Traefik routing working (learn subdomain)
□ TLS certificate provisioned (auto via Let's Encrypt)

TESTING AFTER DEPLOYMENT:
  1. Visit https://learn.tradingnexus.pro/signup
  2. Submit the form
  3. Check SuperAdmin Panel → Portal Signups tab
  4. Verify signup appears in the table
""")

print("\n✨ Instructions provided above. Deploy via Coolify dashboard.")
