#!/usr/bin/env python3
"""
Diagnose deployment issues by checking Coolify logs
"""
import requests
import json

API_BASE = "http://72.62.228.112:8000/api/v1"
TOKEN = "2|7ZrALjw36qMZj0y5ukoLpgIAxibac5yvbNXolQKE0b2ae2f7"
APP_UUID = "zccs8wko40occg44888kwooc"

headers = {"Authorization": f"Bearer {TOKEN}"}

print("=" * 80)
print("DIAGNOSTIC REPORT")
print("=" * 80)
print()

# Get app status
print("1. APPLICATION STATUS")
print("-" * 80)
try:
    r = requests.get(f"{API_BASE}/applications/{APP_UUID}", headers=headers, timeout=5)
    if r.status_code == 200:
        app = r.json()
        print(f"  Status: {app.get('status')}")
        print(f"  Online: {app.get('is_online')}")
        print(f"  Server: {app.get('server_status')}")
        print(f"  Health Check Enabled: {app.get('health_check_enabled')}")
        print(f"  Health Check Path: {app.get('health_check_path')}")
        print(f"  Health Check Host: {app.get('health_check_host')}")
        print(f"  Health Check Port: {app.get('health_check_port')}")
    else:
        print(f"  Error: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

print()
print("2. DOCKER COMPOSE LOCATION")
print("-" * 80)
try:
    r = requests.get(f"{API_BASE}/applications/{APP_UUID}", headers=headers, timeout=5)
    if r.status_code == 200:
        app = r.json()
        print(f"  Compose File: {app.get('docker_compose_location')}")
        print(f"  Git Repo: {app.get('git_repository')}")
        print(f"  Git Branch: {app.get('git_branch')}")
except Exception as e:
    print(f"  Error: {e}")

print()
print("3. ENVIRONMENT VARIABLES")
print("-" * 80)
print("  To view env vars, check Coolify dashboard at:")
print("  → http://72.62.228.112:8000/")
print("  → Projects → trade-nexuss → production → trade-nexus-v2")
print("  → Environment tab")

print()
print("4. RECOMMENDED ACTIONS")
print("-" * 80)
print("  Option A: Check Backend Logs")
print("    1. Go to: http://72.62.228.112:8000/")
print("    2. Find: Projects → trade-nexuss → production → trade-nexus-v2")
print("    3. Click: 'Logs' tab")
print("    4. Look for: Error messages, startup failures, port mismatches")
print()
print("  Option B: Verify Docker is Running")
print("    SSH to VPS and run:")
print("    docker ps | grep zccs8wko")
print()
print("  Option C: Check Traefik Configuration")
print("    Docker Compose defines:")
print("    - Traefik labels for api.tradingnexus.pro")
print("    - Rules matching Host routes")
print("    - Service port mapping (8000)")
print()
print("  Option D: Disable Health Checks (Temporary)")
print("    If health checks are failing:")
print("    1. Go to application settings in Coolify")
print("    2. Disable health check (temporarily)")
print("    3. Redeploy")
print("    4. Check if endpoint becomes accessible")

print()
print("=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
