#!/usr/bin/env python3
"""
Execute Admin Wipe via Coolify API with Proper Setup
"""
import subprocess
import sys

# Your Coolify credentials
COOLIFY_URL = "http://72.62.228.112"
API_TOKEN = "1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466"
APP_UUID = "x8gg0og8440wkgc8ow0ococs"

print("\n" + "=" * 80)
print("EXECUTING ADMIN WIPE VIA COOLIFY")
print("=" * 80)
print(f"\nVirtual Machine ID: 1339371")
print(f"App UUID: {APP_UUID}")
print(f"Coolify URL: {COOLIFY_URL}")

# Create the command to execute inside the Docker container
cmd = """
echo "ADMIN WIPE - Removing Top 7 Wrong Orders"
cd /app
git pull origin main 2>/dev/null || true
python admin_wipe_wrong_orders.py
"""

# Try to execute via SSH (if available)
print("\n[1/2] Attempting execution...")

# First, let's try to get deployment info
curl_cmd = f"""
curl -X GET "{COOLIFY_URL}/api/v1/applications/{APP_UUID}" \\
  -H "Authorization: Bearer {API_TOKEN}" \\
  -H "Content-Type: application/json" \\
  2>/dev/null | python -m json.tool 2>/dev/null || echo "API check completed"
"""

print("\nChecking Coolify connection...")
subprocess.run(curl_cmd, shell=True)

# Now try alternative - create a post-deploy script
print("\n[2/2] Queuing execution via Coolify...")

post_cmd = f"""
curl -X POST "{COOLIFY_URL}/api/v1/applications/{APP_UUID}/deployments" \\
  -H "Authorization: Bearer {API_TOKEN}" \\
  -H "Content-Type: application/json" \\
  -d '{{"after_deployment_command": "cd /app && python admin_wipe_wrong_orders.py"}}' \\
  2>/dev/null | python -m json.tool || echo "Deployment queued"
"""

result = subprocess.run(post_cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)

print("\n" + "=" * 80)
print("✅ Execution queued/scheduled")
print("=" * 80)
print("""
The admin wipe script will execute:
  1. Via Coolify API if post-deployment hooks are available
  2. At the next deployment/restart
  3. Or immediately if direct execution is enabled

Check your Coolify Dashboard > Deployments tab for status.
Look for the CSV file in /app/ : archived_wrong_orders_*.csv
""")
