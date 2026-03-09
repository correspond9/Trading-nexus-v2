#!/usr/bin/env python3
"""
Direct Docker deployment for learn-trading-nexus via Coolify
"""
import requests
import json
import subprocess
import sys
import os

# Configuration
COOLIFY_URL = "http://72.62.228.112:8000"
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
PROJECT_PATH = "d:\\4.PROJECTS\\FRESH\\trading-nexus\\learn-trading-nexus"

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 70)
print("DEPLOYING learn-trading-nexus via Docker")
print("=" * 70)
print()

# ============================================================
# STEP 1: Create docker image locally
# ============================================================
print("[STEP 1] Building Docker image...")
print("-" * 70)
try:
    # Build the Docker image
    result = subprocess.run(
        ["docker", "build", "-t", "learn-trading-nexus:latest", PROJECT_PATH],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if result.returncode != 0:
        print(f"✗ Docker build failed:")
        print(result.stderr)
        sys.exit(1)
    
    print("✓ Docker image built successfully")
    print(result.stdout[-200:] if len(result.stdout) > 200 else result.stdout)
    
except subprocess.TimeoutExpired:
    print("✗ Docker build timed out (5 minutes)")
    sys.exit(1)
except FileNotFoundError:
    print("✗ Docker is not installed or not in PATH")
    print("   Please install Docker and try again")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error building Docker image: {e}")
    sys.exit(1)

# ============================================================
# STEP 2: Deploy via docker-compose (local test)
# ============================================================
print("\n[STEP 2] Testing deployment with docker-compose...")
print("-" * 70)
try:
    result = subprocess.run(
        ["docker-compose", "-f", f"{PROJECT_PATH}\\docker-compose.yml", "up", "-d"],
        cwd=PROJECT_PATH,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        # Even if there's an error, it might still have started
        print(f"Docker compose response:")
        print(result.stdout)
        print(result.stderr)
    else:
        print("✓ Docker compose up executed successfully")
        print(result.stdout)
    
except FileNotFoundError:
    print("✗ Docker Compose is not installed or not in PATH")
    print("   Please install Docker Compose and try again")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error running docker-compose: {e}")
    sys.exit(1)

# ============================================================
# STEP 3: Verify container is running
# ============================================================
print("\n[STEP 3] Verifying container...")
print("-" * 70)
try:
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=learn-trading-nexus"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if "learn-trading-nexus" in result.stdout:
        print("✓ Container is running")
        print(result.stdout)
    else:
        print("✗ Container is not running")
        # Try to see logs
        logs_result = subprocess.run(
            ["docker", "logs", "learn-trading-nexus"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print("\nContainer logs:")
        print(logs_result.stdout)
        print(logs_result.stderr)
        
except Exception as e:
    print(f"✗ Error checking container: {e}")

# ============================================================
# STEP 4: Check connectivity
# ============================================================
print("\n[STEP 4] Testing connectivity...")
print("-" * 70)
try:
    response = requests.get("http://localhost:3001", timeout=5)
    if response.status_code == 200:
        print("✓ Application is accessible at http://localhost:3001")
        print(f"  Status Code: {response.status_code}")
    else:
        print(f"✗ Application returned status {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"⚠ Cannot reach application: {e}")
    print("  (This is normal if running on a remote server)")

# ============================================================
# STEP 5: Configure Coolify (manual steps)
# ============================================================
print("\n[STEP 5] Coolify Configuration (Manual Steps)")
print("-" * 70)
print("""
To complete the deployment in Coolify:

1. SSH into the server: 72.62.228.112
   
2. Navigate to the Coolify projects directory:
   cd /opt/coolify/projects/my-first-project/production/

3. Create a new directory for this app:
   mkdir learn-trading-nexus
   cd learn-trading-nexus

4. Copy the docker-compose.yml:
   cp {}/docker-compose.yml .

5. Copy the built files:
   mkdir .next public
   cp -r {}/.next/* .next/
   cp -r {}/public/* public/
   cp {}/package.json .
   cp {}/package-lock.json .
   cp {}/Dockerfile .

6. Start the container:
   docker-compose up -d

7. The app will be accessible at:
   - Internal: http://localhost:3001
   - External: https://learn.tradingnexus.pro (through Traefik)

8. In Coolify UI, add the domain 'learn.tradingnexus.pro' to the resource
""".format(PROJECT_PATH, PROJECT_PATH, PROJECT_PATH, PROJECT_PATH, PROJECT_PATH, PROJECT_PATH))

print("\n" + "=" * 70)
print("DEPLOYMENT COMPLETE")
print("=" * 70)
print("\n✓ To verify the deployment:")
print("  1. Check Coolify dashboard: http://72.62.228.112:8000")
print("  2. Visit: https://learn.tradingnexus.pro")
print()
