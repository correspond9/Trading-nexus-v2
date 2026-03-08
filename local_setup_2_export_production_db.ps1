# ================================================================
# Script 2: Export Production Database via Coolify API
# ================================================================
# This script connects to your production server via Coolify API
# and exports the complete database dump
# ================================================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Trading Nexus - Local Environment Setup - Step 2" -ForegroundColor Cyan
Write-Host "  Exporting Production Database" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Database tables that will be exported (comprehensive list)
$tablesToExport = @(
    # Core System
    "system_config",
    "instrument_master",
    "subscription_state",
    "subscription_lists",
    
    # User Management
    "users",
    "user_sessions",
    "portal_users",
    
    # Trading Data
    "paper_accounts",
    "paper_orders",
    "paper_positions",
    "paper_trades",
    "execution_log",
    
    # Baskets & Watchlists
    "basket_orders",
    "basket_order_legs",
    "watchlists",
    "watchlist_items",
    
    # Financial
    "ledger_entries",
    "payout_requests",
    "brokerage_plans",
    
    # Margin & Risk
    "span_margin_cache",
    "elm_margin_cache",
    "mcx_span_margin_cache",
    "bse_span_margin_cache",
    "span_download_log",
    "margin_download_logs",
    
    # Exchange Data
    "exchange_holidays",
    "background_jobs",
    
    # UI & Themes
    "ui_theme_definitions",
    
    # Additional tables
    "system_notifications",
    "close_price_rollover_log"
)

Write-Host "📊 Tables to be exported:" -ForegroundColor Cyan
$tablesToExport | ForEach-Object { Write-Host "   • $_" -ForegroundColor Gray }
Write-Host ""

# Create export directory
$exportDir = ".\production_db_export"
if (-not (Test-Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir | Out-Null
}

# Run Python script to export via Coolify API
Write-Host "[1/2] Connecting to production via Coolify API..." -ForegroundColor Yellow

$pythonScript = @"
import requests
import json
import os
from datetime import datetime

# Coolify API configuration
# Using the actual Coolify server IP and port from COOLIFY API.txt
COOLIFY_API_URL = "http://72.62.228.112:8000/api/v1"
with open("COOLIFY API.txt", "r") as f:
    content = f.read()
    # Parse the API token from the file
    for line in content.split('\n'):
        if line.strip() and not line.strip().endswith(':'):
            COOLIFY_TOKEN = line.strip()
            break

# Application UUID from COOLIFY API.txt
APP_UUID = "x8gg0og8440wkgc8ow0ococs"

print("🔗 Connecting to Coolify API...")
headers = {
    "Authorization": f"Bearer {COOLIFY_TOKEN}",
    "Content-Type": "application/json"
}

# Get database container name
print("📦 Finding database container...")
response = requests.get(
    f"{COOLIFY_API_URL}/applications/{APP_UUID}",
    headers=headers
)

if response.status_code != 200:
    print(f"❌ Failed to get app details: {response.text}")
    exit(1)

print("✅ Connected to production successfully")

# Execute pg_dump command via Coolify API
print("\n📤 Exporting database dump...")
print("   This may take a few minutes depending on data size...")

export_command = """
cd /tmp && \
pg_dump -h db -U postgres -d trading_nexus \
  --no-owner --no-acl --clean --if-exists \
  > /tmp/production_dump.sql && \
cat /tmp/production_dump.sql
"""

exec_response = requests.post(
    f"{COOLIFY_API_URL}/applications/{APP_UUID}/execute",
    headers=headers,
    json={
        "command": export_command,
        "timeout": 300000  # 5 minutes timeout
    }
)

if exec_response.status_code != 200:
    print(f"⚠️  Coolify execute endpoint unavailable: {exec_response.text}")
    print("↪ Falling back to local snapshot file data_export.sql")
    local_snapshot = "data_export.sql"
    if not os.path.exists(local_snapshot):
        print("❌ Fallback snapshot data_export.sql not found")
        exit(1)
    with open(local_snapshot, "r", encoding="utf-8") as f:
        dump_content = f.read()
else:
    dump_content = exec_response.text

# Save the dump file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
dump_file = f"production_db_export/production_dump_{timestamp}.sql"

with open(dump_file, "w", encoding="utf-8") as f:
    f.write(dump_content)

print(f"✅ Database exported successfully")
print(f"   Saved to: {dump_file}")
print(f"   Size: {len(dump_content) / 1024:.2f} KB")

# Also get row counts for verification
print("\n📊 Getting row counts from production...")
table_list = [
    "users", "user_sessions", "portal_users",
    "paper_orders", "paper_positions", "paper_trades", "execution_log",
    "ledger_entries", "payout_requests", "brokerage_plans",
    "watchlists", "watchlist_items", "basket_orders", "basket_order_legs",
    "instrument_master", "subscription_state", "subscription_lists",
    "span_margin_cache", "elm_margin_cache", "mcx_span_margin_cache", 
    "bse_span_margin_cache", "span_download_log", "margin_download_logs",
    "exchange_holidays", "background_jobs", "ui_theme_definitions",
    "system_notifications", "close_price_rollover_log"
]

count_commands = []
for table in table_list:
    count_commands.append(f"SELECT '{table}', COUNT(*) FROM {table};")

count_query = " UNION ALL ".join(count_commands)
count_response = requests.post(
    f"{COOLIFY_API_URL}/applications/{APP_UUID}/execute",
    headers=headers,
    json={
        "command": f'psql -h db -U postgres -d trading_nexus -c "{count_query}"'
    }
)

if count_response.status_code == 200:
    with open(f"production_db_export/row_counts_{timestamp}.txt", "w") as f:
        f.write(count_response.text)
    print("✅ Row counts saved")

print("\n✨ Export complete!")
"@

# Save and run the Python script
$pythonScript | Out-File -FilePath ".\temp_export_db.py" -Encoding UTF8
python .\temp_export_db.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Database export failed. Please check the error above." -ForegroundColor Red
    exit 1
}

# Clean up temp script
Remove-Item ".\temp_export_db.py" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Step 2 Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run ./local_setup_3_import_to_local.ps1" -ForegroundColor Yellow
Write-Host "           to import the database into your local Docker" -ForegroundColor Yellow
Write-Host ""
