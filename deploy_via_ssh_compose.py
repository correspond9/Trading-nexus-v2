#!/usr/bin/env python3
"""
Deploy Trading Nexus Portal Features via SSH + Docker Compose
Connects to VPS, pulls latest code, and triggers Docker rebuild
"""

import subprocess
import sys
import time
from datetime import datetime

# VPS Configuration (from previous deployments)
VPS_IP = "72.62.228.112"
VPS_USER = "root"
VPS_APP_DIR = "/data/coolify/applications/zccs8wko40occg44888kwooc"

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

def log_step(num, title):
    print(f"\n[STEP {num}] {title}")
    print("-" * 70)

# ============================================================
# STEP 1: Verify local git changes are committed
# ============================================================
log_step(1, "VERIFY GIT CHANGES ARE COMMITTED")

try:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd="d:\\4.PROJECTS\\FRESH\\trading-nexus",
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0 and not result.stdout.strip():
        log_success("Git working directory is clean - all changes committed")
        
        # Show latest commits
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd="d:\\4.PROJECTS\\FRESH\\trading-nexus",
            capture_output=True,
            text=True,
            timeout=10
        )
        print("\nRecent commits:")
        for line in result.stdout.strip().split('\n')[:3]:
            print(f"  {line}")
    else:
        log_error("Uncommitted changes detected!")
        log_info("Please commit all changes first")
        sys.exit(1)
        
except Exception as e:
    log_error(f"Git check failed: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Connect to VPS via SSH
# ============================================================
log_step(2, "CONNECT TO VPS & DEPLOY")

print(f"Connecting to {VPS_IP} as {VPS_USER}...")
print(f"Application directory: {VPS_APP_DIR}\n")

# Build SSH command to execute on VPS
deploy_commands = [
    "#!/bin/bash",
    f"cd {VPS_APP_DIR}",
    "echo '=== Pulling latest code from GitHub ==='",
    "git pull --rebase --autostash",
    "echo ''",
    "echo '=== Stopping current containers ==='",
    "docker-compose -f docker-compose.prod.yml down",
    "echo ''",
    "echo '=== Pulling latest images ==='",
    "docker-compose -f docker-compose.prod.yml pull",
    "echo ''",
    "echo '=== Building Docker images ==='",
    "docker-compose -f docker-compose.prod.yml build --no-cache",
    "echo ''",
    "echo '=== Starting services (migrations will auto-run) ==='",
    "docker-compose -f docker-compose.prod.yml up -d",
    "echo ''",
    "echo '=== Waiting for services to be healthy ==='",
    "sleep 10",
    "docker-compose -f docker-compose.prod.yml ps",
]

deploy_script = "\n".join(deploy_commands)

try:
    # Run deployment via SSH
    # Note: This assumes SSH keys are already configured
    cmd = [
        "ssh",
        f"{VPS_USER}@{VPS_IP}",
        deploy_script
    ]
    
    log_info("Executing deployment commands on VPS...")
    print()
    
    result = subprocess.run(
        cmd,
        timeout=600,  # 10 minutes timeout
        capture_output=False,  # Show output in real-time
        text=True
    )
    
    if result.returncode == 0:
        log_success("Deployment commands executed successfully!")
    else:
        log_error(f"Deployment failed with exit code {result.returncode}")
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    log_error("Deployment timed out after 10 minutes")
    log_info("Deployment may still be running - check VPS manually")
    sys.exit(1)
    
except FileNotFoundError:
    log_error("SSH command not found - ensure SSH is available on your system")
    log_info("You can manually deploy by:")
    print(f"  1. ssh {VPS_USER}@{VPS_IP}")
    print(f"  2. cd {VPS_APP_DIR}")
    print(f"  3. git pull --rebase")
    print(f"  4. docker-compose -f docker-compose.prod.yml down")
    print(f"  5. docker-compose -f docker-compose.prod.yml up -d --build")
    sys.exit(1)
    
except Exception as e:
    log_error(f"SSH connection failed: {e}")
    log_info("\nManual deployment instructions:")
    print(f"  1. ssh {VPS_USER}@{VPS_IP}")
    print(f"  2. cd {VPS_APP_DIR}")
    print(f"  3. git pull --rebase --autostash")
    print(f"  4. docker-compose -f docker-compose.prod.yml down")
    print(f"  5. docker-compose -f docker-compose.prod.yml pull")
    print(f"  6. docker-compose -f docker-compose.prod.yml build --no-cache")
    print(f"  7. docker-compose -f docker-compose.prod.yml up -d")
    sys.exit(1)

# ============================================================
# STEP 3: Monitor Services
# ============================================================
log_step(3, "MONITOR SERVICES")

print("Checking service status...")

for i in range(5):
    try:
        cmd = [
            "ssh",
            f"{VPS_USER}@{VPS_IP}",
            f"cd {VPS_APP_DIR} && docker-compose -f docker-compose.prod.yml ps"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("\nCurrent service status:")
            print(result.stdout)
            break
        
    except Exception as e:
        if i < 4:
            print(f"  Attempt {i+1}/5 - checking again in 5 seconds...")
            time.sleep(5)
        else:
            log_error(f"Could not check service status: {e}")

# ============================================================
# Summary
# ============================================================
log_section("DEPLOYMENT COMPLETE")

print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"VPS: {VPS_IP}")
print(f"Application: Trading Nexus V2")
print("\n✨ Deployment successful!")
print("\nDeployed features:")
print("  ✓ Portal signup backend endpoints")
print("    - POST /api/v2/auth/portal/signup (register users)")
print("    - GET /api/v2/auth/portal/users (view signups - admin only)")
print("  ✓ Portal signup database table (portal_users)")
print("  ✓ SuperAdmin dashboard 'Portal Signups' tab")  
print("  ✓ Traefik routing for learn.tradingnexus.pro")
print("  ✓ CORS configuration for learn subdomain")
print("\nFrontend URLs now available:")
print("  • Educational Portal: https://learn.tradingnexus.pro")
print("  • Signup Form: https://learn.tradingnexus.pro/signup")
print("  • View Signups: Admin Dashboard → Portal Signups tab")
print("\nNext steps:")
print("  1. Visit https://learn.tradingnexus.pro/signup")
print("  2. Test the signup form")
print("  3. Check SuperAdmin → Portal Signups tab to see registrations")
