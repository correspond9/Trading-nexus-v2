#!/usr/bin/env python3
"""
Fix Coolify Docker Network - Connect backend to coolify network
"""
import subprocess
import sys
import getpass

VPS_IP = "72.62.228.112"
APP_UUID = "p488ok8g8swo4ockks040ccg"

print("=" * 80)
print("  COOLIFY DOCKER NETWORK FIX")
print("=" * 80)
print()

# Ask for password
print(f"Connecting to VPS: {VPS_IP}")
print("You'll be prompted for the root password for each command.")
print()

def run_ssh_command(command, description):
    """Run SSH command and return output"""
    print(f"\n[{description}]")
    print(f"Command: {command}")
    print("-" * 80)
    
    ssh_cmd = f'ssh -o StrictHostKeyChecking=accept-new root@{VPS_IP} "{command}"'
    
    try:
        result = subprocess.run(
            ssh_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return result.stdout.strip()
        else:
            print(f"Error (exit code {result.returncode}):")
            print(result.stderr)
            return None
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

# Step 1: Find containers
print("\nStep 1: Finding application containers...")
containers = run_ssh_command(
    f"docker ps --format '{{{{.Names}}}}' | grep {APP_UUID}",
    "List containers"
)

if not containers:
    print("\n❌ No containers found!")
    print("\nTrying to list all containers:")
    run_ssh_command("docker ps --format 'table {{.Names}}\\t{{.Status}}'", "All containers")
    sys.exit(1)

print(f"\n✅ Found containers:")
for container in containers.split('\n'):
    print(f"  - {container}")

# Step 2: Find backend
backend = None
for container in containers.split('\n'):
    if 'backend' in container:
        backend = container
        break

if not backend:
    print("\n❌ No backend container found")
    sys.exit(1)

print(f"\n✅ Backend container: {backend}")

# Step 3: Check networks
print("\nStep 2: Checking current networks...")
networks = run_ssh_command(
    f"docker inspect {backend} --format '{{{{range $network, $config := .NetworkSettings.Networks}}}}{{{{$network}}}} {{{{end}}}}'",
    "Current networks"
)

print(f"Networks: {networks}")

# Step 4: Check if on coolify network
if networks and 'coolify' in networks:
    print("\n✅ Backend is already on coolify network!")
    print("\nThe network is correct. Checking Traefik labels...")
    
    labels = run_ssh_command(
        f"docker inspect {backend} --format '{{{{range $key, $value := .Config.Labels}}}}{{{{if contains $key \"traefik\"}}}}{{{{$key}}}}={{{{$value}}}}{{{{\"\\n\"}}}}{{{{end}}}}{{{{end}}}}'",
        "Traefik labels"
    )
    print(labels)
    
else:
    print("\n❌ Backend NOT on coolify network")
    print("\nStep 3: Connecting to coolify network...")
    
    result = run_ssh_command(
        f"docker network connect coolify {backend}",
        "Connect to network"
    )
    
    if result is not None:
        print("\n✅ Successfully connected to coolify network!")
    else:
        print("\n❌ Failed to connect")
        sys.exit(1)
    
    # Verify
    print("\nStep 4: Verifying connection...")
    networks = run_ssh_command(
        f"docker inspect {backend} --format '{{{{range $network, $config := .NetworkSettings.Networks}}}}Network: {{{{$network}}}} (IP: {{{{$config.IPAddress}}}}){{{{\"\\n\"}}}}{{{{end}}}}'",
        "Verify networks"
    )

# Step 5: Test endpoint
print("\nStep 5: Testing API endpoint...")
print("Testing: http://api.tradingnexus.pro/health")
print("-" * 80)

import requests
try:
    response = requests.get("http://api.tradingnexus.pro/health", timeout=5)
    print(f"✅ SUCCESS! HTTP {response.status_code}")
    print(f"Response: {response.text[:200]}")
except requests.exceptions.RequestException as e:
    print(f"❌ Failed: {e}")

print("\n" + "=" * 80)
print("  DIAGNOSTIC COMPLETE")
print("=" * 80)
