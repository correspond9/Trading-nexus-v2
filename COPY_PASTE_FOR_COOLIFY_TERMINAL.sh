#!/bin/bash
# Quick Copy-Paste Command for Coolify Terminal
# Just copy and paste this ENTIRE block into your Coolify Terminal

echo ""
echo "=========================================="
echo "ADMIN WIPE - Wrong Orders Removal"
echo "=========================================="
echo ""

# Pull latest code (includes admin script)
echo "[1/3] Pulling latest code..."
cd /app && git pull origin main

# Execute the admin wipe
echo ""
echo "[2/3] Executing admin wipe..."
python admin_wipe_wrong_orders.py

echo ""
echo "[3/3] Done!"
echo "=========================================="
echo "Check for CSV file: archived_wrong_orders_*.csv"
echo "=========================================="
