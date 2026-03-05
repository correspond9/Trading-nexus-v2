#!/bin/bash
# DEPLOYMENT INSTRUCTIONS - Order Execution Price Fix
# Execute these commands on the server to deploy the critical fix

echo "=========================================="
echo "CRITICAL FIX DEPLOYMENT"
echo "=========================================="
echo ""
echo "This script deploys the order execution price validation fix"
echo "Status: Code committed to main branch and ready for deployment"
echo ""

# STEP 1: Navigate to application directory
echo "[1/5] Navigating to application directory..."
cd /app || cd /root/app || cd ~/app
if [ ! -d ".git" ]; then
    echo "ERROR: Could not find application directory"
    exit 1
fi
echo "✓ Found application directory"

# STEP 2: Pull latest code
echo ""
echo "[2/5] Pulling latest code from GitHub..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to pull from git"
    exit 1
fi
echo "✓ Code updated"

# STEP 3: Rebuild Docker image
echo ""
echo "[3/5] Rebuilding Docker image with fixed code..."
docker-compose -f docker-compose.prod.yml build --no-cache backend
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build Docker image"
    exit 1
fi
echo "✓ Docker image rebuilt"

# STEP 4: Restart the application
echo ""
echo "[4/5] Restarting application with fixed code..."
docker-compose -f docker-compose.prod.yml up -d
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to restart application"
    exit 1
fi
echo "✓ Application restarted"
echo "⏳ Waiting for application to be ready (30 seconds)..."
sleep 30

# STEP 5: Execute database correction
echo ""
echo "[5/5] Correcting existing wrongly executed orders..."
docker exec -i trading-nexus-app python fix_wrong_execution_prices.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ DEPLOYMENT COMPLETE"
    echo "=========================================="
    echo ""
    echo "What was done:"
    echo "  ✅ Latest code pulled from GitHub"
    echo "  ✅ Docker image rebuilt with fix"
    echo "  ✅ Application restarted"
    echo "  ✅ Database corrected"
    echo ""
    echo "System is now protected from:"
    echo "  • BUY orders executing above limit price"
    echo "  • SELL orders executing below limit price"
    echo ""
    echo "All future orders will execute at correct prices!"
    exit 0
else
    echo ""
    echo "⚠️  DATABASE CORRECTION MAY HAVE ISSUES"
    echo "But application is deployed and protected."
    echo "Check container logs for details."
    exit 1
fi
