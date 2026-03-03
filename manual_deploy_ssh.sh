#!/bin/bash
# Manual deployment script for Trading Nexus
# Run this on the VPS via SSH

cd /home/user/trading-nexus  # Adjust path as needed

# Pull latest code
git pull origin main

# Rebuild and redeploy with docker-compose
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 30

# Verify deployment
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend is up"
curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend is up"
